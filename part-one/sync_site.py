"""Sync the three public study pages to the approved PDF's HTML source."""
from pathlib import Path
import re


def sync_site():
    root = Path(__file__).resolve().parent.parent
    source = (root / 'part-one/submission/webpage/index.html').read_text(encoding='utf-8')
    css = re.search(r'<style>(.*?)</style>', source, re.S).group(1)
    pages = re.findall(r'<section class="page">.*?</section>', source, re.S)
    if len(pages) != 5:
        raise ValueError('Expected the five approved report pages')
    # The live GIF adds screen-only height; reserve space above the absolute footer.
    css += '\n@media screen{.page{padding-bottom:100px}}\n'
    (root / 'part-one/report.css').write_text(css, encoding='utf-8')
    for folder, title, selected in [
        ('1', 'Portrait Study', pages[:2]),
        ('2', 'Architectural Perspective', pages[2:4]),
        ('3', 'The Dolly Zoom', pages[4:]),
    ]:
        content = ''.join(selected).replace('src="media/', 'src="../part-one/submission/webpage/media/')
        content = content.replace('../the-dolly-zoom.gif', './media/the-dolly-zoom.gif')
        # Keep one document heading; continuation-page headings retain the report style.
        first_end = content.index('</h1>') + len('</h1>')
        content = content[:first_end] + content[first_end:].replace('<h1>', '<h2 class="continuation-title">').replace('</h1>', '</h2>')
        links = [('Home', '../index.html'), ('Portrait', '../1/index.html'),
                 ('Architecture', '../2/index.html'), ('Dolly Zoom', '../3/index.html'),
                 ('PDF report', '../part-one/submission/part-one-report.pdf')]
        nav = ' · '.join(f'<a href="{href}"' + (' aria-current="page"' if href == f'../{folder}/index.html' else '') + f'>{label}</a>' for label, href in links)
        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — SYDE 671 Part One</title>
  <link rel="stylesheet" href="../part-one/report.css">
  <style>.continuation-title{{font-size:32pt;line-height:1.04;letter-spacing:-1.4px;margin:0 0 16px}}@media screen and (max-width:820px){{.continuation-title{{font-size:28pt}}}}</style>
</head>
<body>
  <nav class="screen-nav" aria-label="Part One navigation">{nav}</nav>
  <main>{content}</main>
</body>
</html>
'''
        (root / folder / 'index.html').write_text(html, encoding='utf-8')
    print('Synced public study pages 1, 2 and 3 to the approved report.')


if __name__ == '__main__':
    sync_site()
