"""Build the static project page from saved measurements, without rerunning alignment."""
from html import escape
import json
from pathlib import Path
import statistics
from enhancement_report import render_enhancements

HERE = Path(__file__).resolve().parent


def image(src, alt, caption='', full=None):
    tag = f'<img src="{escape(src)}" alt="{escape(alt)}" loading="eager">'
    if full:
        tag = f'<a href="{escape(full)}">{tag}</a>'
    return f'<figure>{tag}<figcaption>{caption}</figcaption></figure>'


def media(row, suffix):
    return f"results/media/{row['group']}/{row['id']}-{suffix}.jpg"


def shifts(p):
    return f"G {tuple(p['g_shift_xy'])} · R {tuple(p['r_shift_xy'])}"


def main():
    report = json.loads((HERE/'results/provided.json').read_text())
    extra = json.loads((HERE/'results/additional.json').read_text())
    sources = json.loads((HERE/'data/sources.json').read_text())['sources']
    rows = report['records']
    timings = [r['pyramid']['seconds'] for r in rows]
    detail = []
    explanations = [
        'The church and hillside become much easier to read after registration. The colored speckles remain: the separate source exposures contain different scratches and blotches. A translation cannot restore missing emulsion.',
        'The skyline, church and riverbank provide stable geometric structure. The two metrics select the same shifts at this reduced resolution. Narrow colored bands remain near the original plate edges.',
        'Tree trunks and roof lines provide alignment cues. The negative vertical shifts are valid: these channels must move upward relative to blue. The two metrics again select the same low-resolution shifts.'
    ]
    for i, row in enumerate(rows[:3]):
        channels = ''.join(image(media(row, 'channel-'+c), f'{c.upper()} exposure', c.upper()+' channel') for c in ('b', 'g', 'r'))
        comparisons = ''.join(image(media(row, suffix), caption, caption) for suffix, caption in (
            ('low-before', 'Unaligned RGB'), ('single-l2', 'Single-scale L2'), ('single-ncc', 'Single-scale NCC')))
        detail.append(f'''<article class="experiment" id="experiment-{i+1}">
          <p class="eyebrow">Detailed experiment {i+1:02d}</p><h3>{escape(row['file'])}</h3>
          <div class="triple">{channels}</div><div class="triple">{comparisons}</div>
          <p class="measurement">Low-resolution shifts: {shifts(row['single']['ncc'])}; same for L2 and NCC.</p>
          <p>{explanations[i]}</p></article>''')
    single_table = []
    gallery = []
    pyramid_table = []
    for i, row in enumerate(rows, 1):
        n, l, p = row['single']['ncc'], row['single']['l2'], row['pyramid']
        single_table.append(f'''<tr><th><a href="#plate-{i}">Plate {i:02d}</a></th>
          <td>{tuple(n['g_shift_xy'])}<br>{tuple(n['r_shift_xy'])}</td>
          <td>{tuple(l['g_shift_xy'])}<br>{tuple(l['r_shift_xy'])}</td>
          <td>{n['seconds']:.3f} / {l['seconds']:.3f}</td>
          <td><a href="{media(row,'single-ncc')}">NCC</a> · <a href="{media(row,'single-l2')}">L2</a></td></tr>''')
        pyramid_table.append(f'''<tr><th><a href="#plate-{i}">Plate {i:02d}</a></th>
          <td>{tuple(p['g_shift_xy'])}</td><td>{tuple(p['r_shift_xy'])}</td>
          <td>{len(p['g_trace'])}</td><td>{p['seconds']:.3f}</td></tr>''')
        note = ''
        if i == 1:
            note = '<p class="caveat">Source damage remains visible as colored blotches.</p>'
        elif row['id'] in ('01522v', '01597v', '01598v', '01657u', '01861a'):
            note = '<p class="caveat">Inspect faces, hands and foliage for local residual color fringes; a single translation cannot model independently moving subjects.</p>'
        gallery.append(f'''<article class="result" id="plate-{i}">
          <div class="result-heading"><div><p class="eyebrow">Plate {i:02d} / provided</p><h3>{row['file']}</h3></div>
          <p>{row['input_size_wh'][0]} × {row['input_size_wh'][1]} input<br>{p['seconds']:.3f} s alignment</p></div>
          <div class="pair">{image(media(row,'before'), 'Unaligned '+row['file'], 'Before · unaligned RGB')}
          {image(media(row,'pyramid'), 'NCC pyramid '+row['file'], 'After · NCC pyramid', f"results/full/provided/{row['id']}.jpg")}</div>
          <p class="measurement">{shifts(p)} · applied at original resolution</p>{note}</article>''')
    additional = []
    for row, source in zip(extra['records'], sources):
        p = row['pyramid']
        additional.append(f'''<article class="result"><p class="eyebrow">Additional collection example</p>
          <h3>{row['file']}</h3><p>{escape(source['title'])}</p>
          <div class="pair">{image(media(row,'before'), 'Unaligned additional plate', 'Before · unaligned RGB')}
          {image(media(row,'pyramid'), 'Aligned additional plate', 'After · NCC pyramid', f"results/full/additional/{row['id']}.jpg")}</div>
          <p class="measurement">{shifts(p)} · {p['seconds']:.3f} s</p>
          <p><a href="{source['item_url']}">Official catalog record</a> · <a href="data/additional/{row['file']}">Original grayscale scan</a> ·
          <a href="{media(row,'single-ncc')}">Single-scale NCC</a> · <a href="{media(row,'single-l2')}">Single-scale L2</a></p></article>''')
    trace_row = rows[3]
    trace = ''.join(f"<tr><td>{g['shape_hw'][1]} × {g['shape_hw'][0]}</td><td>{tuple(g['shift_xy'])}</td><td>{tuple(r['shift_xy'])}</td><td>±{g['radius']}</td></tr>"
                    for g, r in zip(trace_row['pyramid']['g_trace'], trace_row['pyramid']['r_trace']))
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Handwritten L2/NCC alignment and coarse-to-fine image pyramids for Prokudin-Gorskii glass plates.">
<title>Recovering Color — SYDE 671 Part Two</title><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="report.css"></head>
<body class="color-page"><header class="site-header shell"><a class="brand" href="../index.html"><span class="brand-mark">◎</span><span>Perspective<br><small>through the lens</small></span></a>
<nav class="header-nav" aria-label="Main navigation"><a href="../index.html">Home <span aria-hidden="true">↗</span></a><a href="../index.html#part-one">Part One <span aria-hidden="true">↗</span></a><a href="./index.html" aria-current="page">Part Two <span aria-hidden="true">↗</span></a><a href="../index.html#about">About <span aria-hidden="true">↗</span></a></nav></header>
<main>
<section class="report-hero shell"><div><p class="eyebrow">SYDE 671 · Assignment 1 · Part Two</p>
<h1>Three exposures.<br><em>One world in color.</em></h1>
<p class="lead">Reconstructing the Prokudin-Gorskii collection through channel alignment, exhaustive search and coarse-to-fine image pyramids.</p>
<p class="byline">James Xie · University of Waterloo · Fall 2026</p>
<div class="stats"><div><strong>18 + 2</strong><span>Provided + additional plates</span></div><div><strong>6</strong><span>High-resolution input scans</span></div><div><strong>{max(timings):.2f} s</strong><span>Slowest provided alignment</span></div></div></div>
{image('results/media/provided/00458u-pyramid.jpg', 'Reconstructed locomotive photograph', 'Handwritten NCC pyramid · original scan processed at 3741 × 9715')}
</section>
<nav class="report-index shell" aria-label="Report sections"><a href="#method">01 / Method</a><a href="#single">02 / Experiments</a><a href="#pyramid">03 / Pyramid</a><a href="#gallery">04 / Results</a><a href="#additional">05 / More examples</a><a href="#bells-whistles">06 / Bells &amp; Whistles</a><a href="#discussion">07 / Discussion</a></nav>
<section class="shell report-section" id="method"><p class="eyebrow">01 / Method</p><h2>Recover the alignment,<br>then recover the color.</h2>
<p>The inputs are grayscale scans containing three vertically stacked exposures in blue, green and red order. The program divides each scan into three equal-height arrays, discards at most two trailing rows, keeps blue fixed and translates green and red. The final channel order is red, green, blue.</p>
<div class="workflow"><span>Stacked B / G / R</span><b>→</b><span>Split & normalize</span><b>→</b><span>Estimate G / R shifts</span><b>→</b><span>Compose RGB</span></div>
<div class="method-grid"><article><h3>Single-scale search</h3><p>For each moving channel, try all 961 integer shifts in a ±15-pixel window. Compare a fixed interior region of blue against the shifted channel. Exclude a 12% scoring border on every side, expanding the exclusion when needed to keep every tested coordinate in bounds.</p>
<p>All candidates at a level use exactly the same reference pixels. This avoids favoring shifts that compare a smaller overlap or introduce wraparound.</p></article>
<article><h3>Two baseline metrics</h3><p class="formula">L2 = √Σ(B − C<sub>shifted</sub>)²</p><p>Choose the smallest distance. L2 is sensitive to differences in brightness across color filters.</p>
<p class="formula">NCC = Σ(B · C<sub>shifted</sub>) / (‖B‖ ‖C<sub>shifted</sub>‖)</p><p>Choose the largest similarity. This is the normalized dot product in the handout, without mean subtraction. It compensates for multiplicative intensity changes, but not arbitrary color-dependent changes.</p></article></div>
<p>Convert unsigned integer pixels to floating point using their dtype range. Use Pillow only for reading, writing and resizing; NumPy performs the manual search and array operations. No automatic registration or pyramid-building library is used.</p>
</section>
<section class="shell report-section" id="single"><p class="eyebrow">02 / Single-scale experiments</p><h2>Start small. Make each step visible.</h2>
<p>Every provided plate receives a low-resolution experiment using channels resized to 320 pixels wide. Both L2 and NCC run on the same pixels and search window. The three examples below show the separated exposures, unaligned composite and two aligned composites. Offsets here are in <strong>low-resolution pixels</strong>.</p>
{''.join(detail)}
<div class="table-block"><h3>All low-resolution experiments</h3><p>Each shift cell lists G first, then R. Times are NCC / L2 in seconds. Plate numbers map to the labeled results below.</p>
<table><thead><tr><th>Plate</th><th>NCC shifts</th><th>L2 shifts</th><th>Time (s)</th><th>Images</th></tr></thead><tbody>{''.join(single_table)}</tbody></table></div></section>
<section class="shell report-section" id="pyramid"><p class="eyebrow">03 / Coarse-to-fine alignment</p><h2>Large shifts.<br>Small searches.</h2>
<p>Explicitly build a list of progressively smaller images using bilinear downsampling by about two. Stop when the shorter channel dimension is at most 160 pixels. At the smallest level, search ±15 pixels. At each finer level, multiply the estimate by the actual width/height ratios, round to integer pixels and refine within ±2 pixels. Using actual ratios handles odd image sizes.</p>
<p>All 18 provided scans are processed at their original resolution. The same NCC metric and parameters apply to every image; no per-image tuning is used. A finer level tests only 25 candidates per moving channel, instead of exhaustively searching for shifts exceeding 100 pixels at full size.</p>
<div class="table-block"><h3>A pyramid in motion</h3><p>Intermediate estimates for {trace_row['file']}; offsets are measured in pixels of the indicated level.</p>
<table><thead><tr><th>Channel size</th><th>G shift</th><th>R shift</th><th>Search radius</th></tr></thead><tbody>{trace}</tbody></table></div>
<p>Output cropping removes only pixels without support in all three shifted channels. This is a geometric validity crop, <strong>not</strong> automatic detection of the original photographic borders; colored plate borders therefore remain visible.</p>
<div class="table-block"><h3>Original-resolution offsets and runtime</h3><p>Shifts are (x, y), positive right/down, applied to G and R relative to B. Timing covers both channel alignments, including pyramid construction, but excludes loading, compositing and image saving. Median: {statistics.median(timings):.3f} s; range: {min(timings):.3f}–{max(timings):.3f} s on this Windows environment. No full-resolution brute-force timing comparison was performed.</p>
<table><thead><tr><th>Plate</th><th>G shift</th><th>R shift</th><th>Levels</th><th>Time (s)</th></tr></thead><tbody>{''.join(pyramid_table)}</tbody></table></div></section>
<section class="shell report-section" id="gallery"><p class="eyebrow">04 / All provided images</p><h2>The complete reconstruction set.</h2>
<p>Each pair shows the unaligned composite and the NCC pyramid result. Click an aligned image to open the saved result at original pixel scale, after the common-support crop. Web previews are at most 900 pixels wide.</p>{''.join(gallery)}</section>
<section class="shell report-section" id="additional"><p class="eyebrow">05 / Additional collection examples</p><h2>Beyond the supplied dataset.</h2>
<p>Two additional three-frame grayscale JPEGs were downloaded from the Library of Congress, rather than using its finished color restorations. Both use exactly the same pipeline and parameters as the provided set. These examples are low-resolution scans; the large-image demonstration comes from the six supplied high-resolution scans.</p>{''.join(additional)}</section>
{render_enhancements(HERE, image)}
<section class="shell report-section" id="discussion"><p class="eyebrow">07 / Discussion & limitations</p><h2>Alignment is only part<br>of restoration.</h2>
<p><strong>Visual assessment:</strong> the reconstructed previews show broadly aligned scene structure. This is a qualitative inspection, not a ground-truth accuracy score. The saved high-resolution outputs remain available for closer inspection.</p>
<p><strong>Damaged exposures:</strong> the first detailed experiment has visible scratches and blotches in its individual grayscale channels. Their disagreement produces colored speckles after composition. Searching for a different global displacement cannot reconstruct these missing details.</p>
<p><strong>Local residuals:</strong> faces, foliage and object boundaries can retain colored fringes. Motion between sequential exposures, channel-dependent brightness and departures from pure translation are plausible causes; the current experiment does not isolate their individual contributions. The model cannot correct local motion, rotation or scale change.</p>
<p><strong>Border artifacts:</strong> excluding borders from the score prevents them dominating the alignment, but does not restore or remove the physical borders in the final image. The common-support crop only removes wrapped pixels.</p>
<p><strong>Enhancement scope:</strong> the Bells &amp; Whistles section implements detected-border cropping, contrast enhancement and gray-world white balance. The earlier L2/NCC galleries retain their original intensities for comparison. These post-processing methods cannot repair missing emulsion or local misalignment, and a more vivid result is not evidence of historically accurate color.</p>
<p><strong>Dataset discrepancy:</strong> the handout mentions both 5 and 20 examples and legacy image names; the supplied directory contains 18 numbered JPEGs. All 18 were processed, and three selected plates receive detailed experiments.</p>
</section>
<section class="shell report-section" id="reproduce"><p class="eyebrow">08 / Reproducibility</p><h2>Measurements & reproducibility.</h2>
<p>Seven synthetic-image unit tests cover channel order, 16-bit normalization, L2/NCC shift recovery, large displacements on odd dimensions, RGB composition, valid-support cropping, blank-image tie handling and invalid inputs. No mock tests are used.</p>
<p>Six additional unit tests exercise variable-width black, white and colored borders, images without borders, shared contrast endpoints, recovery of a known gray-world cast, finite outputs for constant and zero-channel images, and invalid inputs. The enhancement batch also checks source hashes and finite output ranges for every scan.</p>
<p>Run instructions are in the project README. Saved records include input SHA-256 hashes, channel dimensions, discarded rows, offsets, per-level scores and timings. NCC/L2 scores at different pyramid levels use different pixels and should not be interpreted as one comparable accuracy curve.</p>
<p>Environment: Python {report['versions']['python']}, NumPy {report['versions']['numpy']}, Pillow {report['versions']['pillow']}. Measurements were collected with one sequential batch, not a statistical performance benchmark.</p>
</section>
<section class="shell report-section" id="references"><p class="eyebrow">09 / References</p><h2>Design & image sources.</h2>
<ol>
<li><p><strong>Website design reference:</strong> <a href="https://www.wix.com/website-template/view/html/wh-1329">Wix — AI Blog (Abstract)</a>. Visual reference for the independently implemented static website.</p></li>
<li><p><strong>Additional photograph:</strong> <a href="{escape(sources[0]['item_url'])}">{escape(sources[0]['title'])}</a>. Prokudin-Gorskii photograph collection, Library of Congress, Prints and Photographs Division.</p></li>
<li><p><strong>Additional photograph:</strong> <a href="{escape(sources[1]['item_url'])}">{escape(sources[1]['title'])}</a>. Prokudin-Gorskii photograph collection, Library of Congress, Prints and Photographs Division.</p></li>
</ol>
</section></main><footer class="site-footer shell"><span>Perspective, Through the Lens</span><a href="../index.html">Back to all studies ↗</a></footer></body></html>'''
    (HERE/'index.html').write_text(html, encoding='utf-8')
    print(f'Built webpage: {len(rows)} provided + {len(extra["records"])} additional images.')


if __name__ == '__main__':
    main()
