"""Snapshot the current website for the Part One submission; never rewrite its content."""
from pathlib import Path
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'submission'
WEB = OUT / 'webpage'
WEB.mkdir(parents=True, exist_ok=True)
BASE = 'https://aaajamesxie.github.io/Perspective-Through-the-Lens/'
for folder in ('1', '2', '3'):
    shutil.copytree(ROOT / folder, WEB / folder, dirs_exist_ok=True)
    page = WEB / folder / 'index.html'
    page.write_text(page.read_text(encoding='utf-8').replace('../part-two/', BASE + 'part-two/'), encoding='utf-8')
shutil.copy2(ROOT / 'style.css', WEB / 'style.css')
home = (ROOT / 'index.html').read_text(encoding='utf-8')
(WEB / 'index.html').write_text(home.replace('./part-two/', BASE + 'part-two/'), encoding='utf-8')
shutil.copy2(ROOT / '3/media/the-dolly-zoom.gif', OUT / 'the-dolly-zoom.gif')
(OUT / 'README.md').write_text('''# SYDE 671 Assignment 1 - Part One

James Xie | University of Waterloo

## Submission files

- `part-one-report.pdf`: direct browser export of the current three project pages, in portrait / architecture / dolly order. Each experiment occupies one full-length page, preserving the desktop webpage layout and content without rewriting or A4 reflow.
- `the-dolly-zoom.gif`: corrected seven-frame animation. A PDF can only show a static frame; open this file or the webpage to watch motion.
- `webpage/index.html`: offline copy of the current homepage and all three Part One pages. Extract the complete ZIP before opening. Part Two links point to the public website and require internet access.
- `SHA256SUMS.txt`: file integrity manifest.

## Online project

https://aaajamesxie.github.io/Perspective-Through-the-Lens/index.html

The PDF is generated from the local `1/index.html`, `2/index.html`, and `3/index.html` pages using the current shared stylesheet. The original website is the source of truth. The independent five-page report has been replaced.

Upload the PDF to LEARN and provide the public project webpage URL. No LEARN upload is performed by the build scripts.
''', encoding='utf-8')
qa = ROOT / 'qa/part-one'
qa.mkdir(parents=True, exist_ok=True)
with Image.open(OUT / 'the-dolly-zoom.gif') as gif:
    gif.seek(0)
    gif.convert('RGB').save(qa / 'dolly-static.png')
print('Copied the current website into the submission package.')
