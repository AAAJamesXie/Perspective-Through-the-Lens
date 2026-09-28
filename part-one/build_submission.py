"""Assemble the Part One submission from existing local photographs."""
from pathlib import Path
from html import escape
from PIL import Image
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'submission'
WEB = OUT / 'webpage'
MEDIA = WEB / 'media'
MEDIA.mkdir(parents=True, exist_ok=True)

portraits = ['01-near', '02-step-back', '03-middle', '04-farther', '05-far']
streets = ['01-far-zoom', '02-step-forward', '03-middle', '04-near-wide']
for name in portraits:
    shutil.copy2(ROOT / '1/media' / (name + '-retouched.jpg'), MEDIA / ('portrait-' + name + '.jpg'))
for name in streets:
    shutil.copy2(ROOT / '2/media' / (name + '.jpg'), MEDIA / ('street-' + name + '.jpg'))
shutil.copy2(ROOT / '3/media/the-dolly-zoom.gif', OUT / 'the-dolly-zoom.gif')
gif = Image.open(OUT / 'the-dolly-zoom.gif')
assert gif.n_frames == 7
for i in range(gif.n_frames):
    gif.seek(i)
    gif.convert('RGB').save(MEDIA / f'dolly-{i+1:02d}.jpg', quality=92)

def fig(src, title, caption):
    return f'<figure><img src="media/{src}" alt="{escape(title)}"><figcaption><b>{title}</b><span>{caption}</span></figcaption></figure>'

def page(number, label, title, body):
    return f'<section class="page"><header><span>SYDE 671 / ASSIGNMENT 1 / PART ONE</span><span>JAMES XIE</span></header><p class="eyebrow">{label}</p><h1>{title}</h1>{body}<footer><span>Perspective, Through the Lens · University of Waterloo</span><span>{number} / 5</span></footer></section>'

pages = []
pages.append(page(1, '01 / PORTRAIT STUDY', 'Selfie: The Wrong Way<br>vs. The Right Way',
    '<p class="lead">Camera distance changes facial proportions. Zoom adjusts the framing.</p>'
    '<p>My classmate helped take the photographs, stepping back and increasing zoom to keep my face approximately the same size. The closest and farthest views show the clearest contrast.</p>'
    '<div class="grid two">' +
    fig('portrait-01-near.jpg', 'Close up', '10 cm · 0.5× · 14 mm equivalent') +
    fig('portrait-05-far.jpg', 'Stepped back', '100 cm · 4.0× · 99 mm equivalent') + '</div>'
    '<h2>What changes?</h2><p>In the close portrait, the nose appears larger relative to the ears and the sides of the face. In the farther portrait, the facial proportions look flatter and more balanced. The face remains roughly comparable in size, although pose and framing are not identical.</p>'
    '<div class="takeaway">Moving back changes perspective; zooming in keeps the subject prominent.</div>'))

caps = [('10 cm', '0.5× · 14 mm'), ('15 cm', '0.8× · 20 mm'), ('20 cm', '1.2× · 28 mm'), ('40 cm', '2.0× · 48 mm'), ('100 cm', '4.0× · 99 mm')]
pages.append(page(2, '01 / PORTRAIT STUDY / CONTINUED', 'Five positions.<br>One face.',
    '<div class="grid five">' + ''.join(fig('portrait-'+name+'.jpg', f'{i+1:02d} / {caps[i][0]}', caps[i][1]) for i,name in enumerate(portraits)) + '</div>'
    '<p class="caption">Sequence from near to far. Distances and on-screen zoom settings are the photographer’s notes; all focal lengths are 35 mm equivalents verified in the original HEIC metadata.</p>'
    '<h2>Why the proportions change</h2><p>In a pinhole-camera model, projected size is proportional to focal length divided by depth: <b>image size ∝ f / Z</b>. The nose is closer to the camera than the ears. At a short camera-to-face distance, that depth difference is a large fraction of the total distance, so the nose is magnified more strongly.</p>'
    '<p>After stepping back, the distances to the nose and ears become more similar in relative terms. Increasing focal length then enlarges the whole face in the image without restoring the close-up perspective.</p>'
    '<h2>What zoom alone would do</h2><p>From a fixed camera position, changing focal length changes the field of view and image scale. In the ideal projection model, it does not change the relative perspective of the facial features. The change in viewpoint is therefore essential to this comparison.</p>'
    '<h2>Capture notes</h2><p>The sequence spans 10–100 cm and 14–99 mm equivalent. This PDF retains the existing webpage’s retouched portrait exports. The experiment is a qualitative visual comparison, not a calibrated measurement of facial geometry; pose, framing, lens processing and retouching are not independently controlled.</p>'
    '<div class="takeaway">Perspective follows camera position. Focal length controls image scale.</div>'))

pages.append(page(3, '02 / ARCHITECTURAL PERSPECTIVE', 'The street<br>folds inward.',
    '<p class="lead">A campus path appears compressed from farther away and more expansive from closer up.</p>'
    '<p>I began with a distant, zoomed-in view, then walked forward along the path while widening the field of view. The sidewalk, trees and roadside sign provide fixed landmarks for comparison.</p>'
    '<div class="grid two">' + fig('street-01-far-zoom.jpg', 'Farther / narrow view', '200 mm equivalent') + fig('street-04-near-wide.jpg', 'Closer / wide view', '24 mm equivalent') + '</div>'
    '<h2>What changes?</h2><p>In the farther view, the trees, sign and background appear more crowded together. In the closer view, the foreground sidewalk spreads outward and the route into the distance feels longer. The comparison is approximate: the framing is not perfectly matched.</p>'
    '<div class="takeaway">The scene stays in place. Changing the viewpoint changes its apparent depth.</div>'))

streetcaps = [('200 mm', 'IMG_7887'), ('164 mm', 'IMG_7889'), ('100 mm', 'IMG_7890'), ('24 mm', 'IMG_7891')]
pages.append(page(4, '02 / ARCHITECTURAL PERSPECTIVE / CONTINUED', 'Four positions.<br>One path.',
    '<div class="grid four">' + ''.join(fig('street-'+name+'.jpg', f'{i+1:02d} / {streetcaps[i][0]}', streetcaps[i][1]) for i,name in enumerate(streets)) + '</div>'
    '<p class="caption">Capture order while moving forward. All focal lengths are 35 mm equivalents verified in the original HEIC metadata. Camera-to-landmark distances were not measured.</p>'
    '<h2>Why the distant view looks compressed</h2><p>When the camera is far from both foreground and background features, the difference between their depths is relatively small compared with the overall viewing distance. Their apparent sizes become more similar, so the background appears closer to the foreground.</p>'
    '<p>Walking forward makes the near-to-far depth ratio more pronounced. Nearby sidewalk sections and roadside objects grow in the image more rapidly than distant objects. Zooming out keeps more of the scene visible, while the camera movement creates the new perspective.</p>'
    '<h2>How to compare the photographs</h2><p>Follow the stationary sign, tree trunks and sidewalk edges rather than the passerby in the second frame. The person moved between exposures and is not a stable reference. These images illustrate the effect qualitatively; they do not establish a measured compression ratio.</p>'
    '<div class="takeaway">A longer focal length is associated with this compressed view because the camera was also farther away.</div>'))

pages.append(page(5, '03 / THE DOLLY ZOOM', 'One sign.<br>A shifting background.',
    '<p class="lead">Seven still photographs combine changing viewpoint and zoom into a short animated sequence.</p>'
    '<p>The stop sign is stationary. The GIF orders the original photographs from a near, wide view toward a farther, zoomed-in view. Keeping the sign roughly comparable in size makes the changing background more noticeable.</p>'
    '<div class="grid four dolly">' + ''.join(fig(f'dolly-{i:02d}.jpg', f'Frame {i:02d}', 'Near / 24 mm' if i==1 else 'Far / 257 mm' if i==7 else 'Intermediate view') for i in range(1,8)) + '</div>'
    '<p class="caption">All seven GIF frames, in playback order. Endpoint focal lengths are 35 mm equivalents from the original HEIC metadata. Playback order: IMG_7875, IMG_7874, IMG_7872, IMG_7871, IMG_7873, IMG_7870, IMG_7869.</p>'
    '<h2>Why the background appears to move</h2><p>Moving back changes the relative scale of foreground and background. Increasing zoom compensates approximately for the shrinking subject, while the background grows relative to it. This combination produces the characteristic dolly-zoom effect.</p>'
    '<p>The handheld sequence has some variation in sign size and alignment, so the effect is not perfectly stabilized. It uses seven photographic frames; no generated or interpolated frames are added.</p>'
    '<div class="takeaway">Watch the animation: <a href="../the-dolly-zoom.gif">the-dolly-zoom.gif</a><br><span class="small">The PDF shows still frames. Open the accompanying GIF or the offline webpage to see motion.</span></div>'
    '<div class="animation"><img src="../the-dolly-zoom.gif" alt="Seven-frame dolly zoom animation"></div>'))

css = '''
*{box-sizing:border-box}body{margin:0;background:#e8e6e1;color:#202526;font-family:Arial,Helvetica,sans-serif;font-size:11pt;line-height:1.46}.page{width:210mm;min-height:297mm;margin:18px auto;padding:15mm 17mm 18mm;background:#fff;position:relative;page-break-after:always}header{display:flex;justify-content:space-between;font-size:8pt;letter-spacing:1px;border-bottom:2px solid #202526;padding-bottom:10px}.eyebrow{font-size:9pt;color:#48675f;letter-spacing:1.5px;font-weight:bold;margin:20px 0 8px}h1{font-size:32pt;line-height:1.04;letter-spacing:-1.4px;margin:0 0 16px}h2{font-size:15pt;margin:22px 0 6px}p{margin:9px 0}.lead{font-size:13pt;color:#48675f}.grid{display:grid;gap:13px;margin:20px 0 12px}.two{grid-template-columns:repeat(2,1fr)}.four{grid-template-columns:repeat(4,1fr)}.five{grid-template-columns:repeat(5,1fr)}figure{margin:0;break-inside:avoid}figure img{width:100%;height:auto;display:block;aspect-ratio:3/4;object-fit:contain;background:#f2f2ee}.two img{max-height:340px}figcaption{font-size:8.5pt;line-height:1.3;margin-top:7px}figcaption b,figcaption span{display:block}figcaption span{color:#566362;margin-top:3px}.five figcaption{font-size:8pt}.caption,.small{font-size:9pt;color:#596462}.takeaway{border-left:4px solid #48675f;background:#f0f3ef;padding:12px 15px;margin-top:20px;font-weight:bold}.takeaway .small{font-weight:normal}footer{position:absolute;bottom:10mm;left:17mm;right:17mm;display:flex;justify-content:space-between;font-size:8pt;color:#66716e;border-top:1px solid #cdd3ce;padding-top:7px}a{color:#315d52}.dolly{gap:10px;margin:14px 0 10px}.dolly img{max-height:130px}.dolly figcaption{font-size:8pt}.animation{text-align:center;margin-top:20px}.animation img{width:270px}.screen-nav{max-width:794px;margin:18px auto;font-size:11pt} @page{size:A4;margin:0}@media print{body{background:white}.page{margin:0;height:297mm;min-height:0;break-after:page}.page:last-child{break-after:auto}.animation,.screen-nav{display:none}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}@media screen and (max-width:820px){.page{width:100%;min-height:0;padding:22px 20px 55px}.grid{gap:8px}h1{font-size:28pt}.five{grid-template-columns:repeat(3,1fr)}.four{grid-template-columns:repeat(2,1fr)}footer{left:20px;right:20px;bottom:12px}.screen-nav{padding:0 20px}}
'''
(WEB / 'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SYDE 671 - Part One - James Xie</title><style>'+css+'</style></head><body><nav class="screen-nav">Part One submission · <a href="../part-one-report.pdf">PDF report</a> · <a href="../the-dolly-zoom.gif">Play Dolly Zoom GIF</a></nav>'+''.join(pages)+'</body></html>', encoding='utf-8')
(OUT / 'README.md').write_text('''# SYDE 671 Assignment 1 - Part One

James Xie | University of Waterloo

## Submission files

- `part-one-report.pdf`: five-page PDF version of the included submission webpage, covering all three experiments.
- `the-dolly-zoom.gif`: seven-frame animation; open separately because PDF does not play it.
- `webpage/index.html`: self-contained offline webpage with local images and animation. Extract the whole ZIP before opening it.

## Before submitting to LEARN

The assignment requires an online project webpage and a PDF version. Upload the PDF and provide the publicly accessible project webpage URL. The GIF and ZIP are supplementary; the ZIP does not replace online hosting.

The existing project has a Git remote at:
https://github.com/AAAJamesXie/Perspective-Through-the-Lens

Public website availability could not be verified from this environment. No website was published and no LEARN upload was performed during this packaging task. Confirm the actual public webpage URL before submission; a repository URL alone is not a hosted webpage URL.

## Content notes

The report reorganizes the existing three Part One pages for print. A classmate helped take the portrait photographs. It retains the webpage's retouched portrait exports and the existing architectural photographs. All seven GIF frames are reproduced as stills for PDF readers. The corrected GIF plays IMG_7875, IMG_7874, IMG_7872, IMG_7871, IMG_7873, IMG_7870, and IMG_7869 in that order; frame pixels, timing and looping are preserved. The submission includes an identical copy of the corrected project GIF.

Portrait distances and zoom settings come from the existing photographer notes. Portrait and architectural equivalent focal lengths, plus the dolly endpoint values, were checked against original HEIC metadata. Street distances were not recorded. Handheld framing and dolly stabilization are approximate. No new measurements, new photographs or synthetic animation frames were created.
''', encoding='utf-8')
print(WEB / 'index.html')
from sync_site import sync_site
sync_site()
