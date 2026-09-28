"""Make PDF links portable, package deliverables and verify their saved bytes."""
from pathlib import Path
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlparse, unquote, quote
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

HERE = Path(__file__).resolve().parent
OUT = HERE / 'submission'
pdf = OUT / 'part-one-report.pdf'
reader = PdfReader(pdf)
writer = PdfWriter()
writer.clone_document_from_reader(reader)
for page in writer.pages:
    for ref in page.get('/Annots', []):
        action = ref.get_object().get('/A')
        if action and str(action.get('/URI', '')).endswith('the-dolly-zoom.gif'):
            action[NameObject('/URI')] = TextStringObject('the-dolly-zoom.gif')
        elif action and str(action.get('/URI', '')).startswith('file:'):
            url = urlparse(str(action['/URI']))
            local = Path(unquote(url.path).lstrip('/'))
            relative = local.relative_to(HERE.parent).as_posix()
            target = 'https://aaajamesxie.github.io/Perspective-Through-the-Lens/' + quote(relative, safe='/')
            if url.fragment:
                target += '#' + url.fragment
            action[NameObject('/URI')] = TextStringObject(target)
writer.add_metadata({'/Title': 'SYDE 671 Assignment 1 - Part One', '/Author': 'James Xie', '/Subject': 'Portrait perspective, architectural compression and dolly zoom'})
temp = OUT / 'report-portable.pdf'
with temp.open('wb') as stream:
    writer.write(stream)
temp.replace(pdf)

reader = PdfReader(pdf)
assert len(reader.pages) == 3
checks = json.loads((HERE.parent / 'qa/part-one/website-export-checks.json').read_text())
normalize = lambda t: re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', t)).lower()
for page, check in zip(reader.pages, checks):
    assert normalize(check['mainText']) in normalize(page.extract_text()), f"Website text differs in study {check['study']}"
text = ' '.join(page.extract_text() for page in reader.pages).lower()
for expected in ['james xie', '100 cm', '200 mm', '257 mm', 'dolly zoom', '35 mm']:
    assert expected in text, expected
for page in reader.pages:
    for ref in page.get('/Annots', []):
        assert 'file:' not in str(ref.get_object().get('/A', {}))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(OUT / 'the-dolly-zoom.gif') == digest(HERE.parent / '3/media/the-dolly-zoom.gif')
assert Image.open(OUT / 'the-dolly-zoom.gif').n_frames == 7
files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.suffix != '.zip' and p.name != 'SHA256SUMS.txt')
(OUT / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(OUT).as_posix()}\n' for p in files), encoding='utf-8')
archive = OUT / 'part-one-submission.zip'
with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
    for p in files + [OUT / 'SHA256SUMS.txt']:
        z.write(p, p.relative_to(OUT).as_posix())
with ZipFile(archive) as z:
    assert z.testzip() is None
    for p in files:
        assert hashlib.sha256(z.read(p.relative_to(OUT).as_posix())).hexdigest() == digest(p)
    entries = len(z.namelist())
qa = HERE.parent / 'qa/part-one'
result = {'pdf_pages': 3, 'website_text_matches': True, 'gif_frames': 7, 'gif_matches_original': True, 'zip_entries': entries, 'zip_crc_and_sha256': 'passed', 'pdf_bytes': pdf.stat().st_size, 'zip_bytes': archive.stat().st_size, 'public_webpage': 'https://aaajamesxie.github.io/Perspective-Through-the-Lens/index.html', 'learn_uploaded': False}
(qa / 'package-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
