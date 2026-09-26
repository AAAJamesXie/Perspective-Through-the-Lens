"""Package source and the two additional inputs; exclude generated large outputs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
out = root/'submission/part-two-code.zip'
out.parent.mkdir(exist_ok=True)
files = [*root.glob('*.py'), *root.glob('*.md'), root/'report.css',
         root/'export_report.cjs', root/'data/sources.json',
         *root.glob('data/additional/*.jpg')]
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for file in sorted(files):
        archive.write(file, 'part-two/'+file.relative_to(root).as_posix())
    archive.write(root.parent/'style.css', 'part-two/site-style.css')
with ZipFile(out) as archive:
    assert archive.testzip() is None
    print(f'Verified {len(archive.namelist())} entries: {out.name} ({out.stat().st_size} bytes)')
