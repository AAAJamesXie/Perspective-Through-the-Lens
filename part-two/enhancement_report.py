"""English explanation and measured comparisons for Bells & Whistles."""
from html import escape
import json


def render_enhancements(root, image):
    data = json.loads((root/'results/enhancements.json').read_text())
    records = data['records']
    examples = {r['id']: r for r in records if r['group'] == 'provided'}
    crop, contrast, balance = (examples[key] for key in ('00163v', '00458u', '31421v'))

    def pair(row, variant, label):
        return '<div class="pair">'+image(row['images']['baseline'], 'Aligned baseline '+row['id'], 'Before · aligned RGB')+image(row['images'][variant], label+' '+row['id'], 'After · '+label)+'</div>'

    summary = []
    gallery = []
    for row in records:
        margins = ' / '.join(map(str, row['crop']['margins_ltrb']))
        gains = ' / '.join(f'{v:.3f}' for v in row['combined_white_balance']['gains_rgb'])
        summary.append(f'<tr><th>{escape(row["id"])}<br>{row["group"]}</th><td>{margins}</td><td>{100*row["crop"]["retained_fraction"]:.1f}%</td><td>{gains}</td></tr>')
        if row['id'] in ('00163v', '00458u', '31421v') and row['group'] == 'provided':
            gallery.append(f'<article class="result"><h3>{escape(row["id"])}</h3><div class="pair">'+
                image(row['images']['baseline'], 'Baseline '+row['id'], 'Before · aligned RGB')+
                image(row['images']['combined'], 'Combined enhancement '+row['id'], 'After · crop → white balance → contrast', row['full_combined'])+'</div></article>')
    lo, hi = contrast['contrast']['endpoints']
    means = ', '.join(f'{v:.3f}' for v in balance['white_balance']['illuminant_rgb'])
    gains = ', '.join(f'{v:.3f}' for v in balance['white_balance']['gains_rgb'])
    return f'''<section class="shell report-section" id="bells-whistles">
<p class="eyebrow">06 / Bells &amp; Whistles</p><h2>Beyond alignment.<br>Three automatic adjustments.</h2>
<p>Alignment brings the exposures together, but does not remove the photographic frame, expand a faded tonal range, or correct a global color cast. I implemented automatic cropping, automatic contrasting and automatic white balance with NumPy. Pillow handles image input, output and preview resizing. These libraries expose the pixel operations directly and require no additional dependencies.</p>
<p>All {data['count']} scans use the same parameters. The original scans are verified against their saved SHA-256 hashes and recomposed with the baseline shifts before enhancement; processing does not start from a compressed output JPEG. Each individual comparison below applies only its named method to the same aligned baseline. Combined results apply cropping, then white balance, then contrast, so frame pixels do not influence the final color and intensity statistics.</p>
<article class="experiment"><h3>1. Automatic cropping</h3>
<p><strong>What it does:</strong> inspect rows and columns from each of the four edges. For every candidate boundary, measure the median signed RGB change across the central 60% of the line, then take the largest absolute channel change. This favors a coherent border-to-scene transition while cancelling inconsistent texture changes. The central span reduces interference from perpendicular borders.</p>
<p>A transition must exceed both 0.035 normalized intensity and four times the typical interior transition. At least 60% of the preceding strips must look border-like: their within-channel 90th–10th percentile spread is below 0.12, all channel medians are above 0.9 or below 0.1, or the range across their channel medians exceeds 0.35. The innermost qualifying transition defines that side's crop. The outer 15% is a <strong>search limit, not a fixed margin</strong>; a side with no qualifying transition is retained. Subsampling wide strips keeps profile estimation inexpensive.</p>
<p><strong>Why use it:</strong> physical frames can be white, black or colored, so brightness alone is insufficient. Combining color uniformity with a spatial transition removes detected frame regions after the separate common-support crop used by alignment.</p>
{pair(crop, 'crop', 'detected-border crop')}
<p class="measurement">Example {crop['id']}: detected left / top / right / bottom margins = {' / '.join(map(str, crop['crop']['margins_ltrb']))} pixels; {100*crop['crop']['retained_fraction']:.1f}% of the aligned image area retained.</p>
<p class="caveat">Limitation: this is a heuristic for roughly rectangular frames. A flat sky or a strongly colored scene edge can resemble a frame; damaged, textured or very wide borders may remain. Retained area is a size measurement, not proof of correct segmentation.</p></article>
<article class="experiment"><h3>2. Automatic contrasting</h3>
<p><strong>What it does:</strong> collect intensities across all RGB channels, estimate their 1st and 99th percentiles, and apply one shared linear mapping to every channel.</p>
<p class="formula">I′ = clip((I − p₁) / (p₉₉ − p₁), 0, 1)</p>
<p><strong>Why use it:</strong> percentile endpoints are less sensitive than the absolute minimum and maximum to isolated scratches and extreme pixels. A common mapping avoids three independent channel stretches that could introduce an additional color cast. It preserves channel ordering, although subtracting a common offset can change saturation. Images with a negligible percentile range are left unchanged to avoid division by zero.</p>
{pair(contrast, 'contrast', '1–99% contrast stretch')}
<p class="measurement">Example {contrast['id']}: shared endpoints {lo:.4f} and {hi:.4f}; {100*contrast['contrast']['clipped_sample_fraction']:.2f}% of channel samples lie outside those endpoints.</p>
<p class="caveat">Limitation: clipping sacrifices extreme shadow and highlight detail and can emphasize blemishes. The recorded clipping fraction counts channel samples, not whole pixels. This global adjustment does not recover missing detail or adapt separately to locally bright and dark regions.</p></article>
<article class="experiment"><h3>3. Automatic white balance</h3>
<p><strong>What it does:</strong> use the gray-world assumption that a sufficiently varied scene has an approximately neutral average reflectance. Estimate the illuminant's relative RGB strength from the image's channel means μ. Set the neutral target t to their average and compensate with a diagonal channel scaling.</p>
<p class="formula">t = (μ<sub>R</sub> + μ<sub>G</sub> + μ<sub>B</sub>) / 3;&nbsp; g<sub>c</sub> = t / μ<sub>c</sub>;&nbsp; I′<sub>c</sub> = g<sub>c</sub>I<sub>c</sub></p>
<p>Gains are limited to [0.5, 2] to restrain amplification of weak channels; a channel with mean at most 10⁻⁷ keeps unit gain. If the corrected maximum exceeds one, divide the entire RGB image by that maximum, preserving the corrected channel ratios instead of clipping highlights independently.</p>
<p><strong>Why use it:</strong> it explicitly separates illuminant estimation from color compensation, needs no manually selected neutral patch, and is easy to reproduce. A weak average channel receives more gain; a dominant one receives less.</p>
{pair(balance, 'balance', 'gray-world white balance')}
<p class="measurement">Example {balance['id']}: estimated RGB means ({means}); RGB gains ({gains}).</p>
<p>Visual observation: the blue-purple cast on the building in this example is reduced. This is a qualitative preference, not a comparison against a calibrated reference.</p>
<p class="caveat">Limitation: green vegetation, blue water or a dominant colored surface can violate the gray-world assumption. Neutralizing their average can remove a real scene color. Gain limits may prevent exact neutrality, and common highlight scaling may darken the image. Because the scans have no calibrated camera response or known reference colors, this is a display-space visual correction, not a physical recovery of the historical illuminant.</p></article>
<article class="experiment"><h3>When gray-world is less convincing</h3>
{pair(examples['00125v'], 'balance', 'gray-world white balance')}
<p>In this river landscape, green vegetation and blue water contribute strongly to the average. The adjustment boosts red and suppresses green, leaving a pinker sky and a less natural-looking overall balance. This illustrates why equal channel means do not guarantee correct colors. The same fixed algorithm is retained for every scan; this failure is shown rather than tuned away.</p></article>
<h3>Combined results</h3><p>These pairs show the complete sequence on three examples. The baseline remains available for judging whether the result is preferable; improved contrast or a neutral mean alone does not establish historical color accuracy. Click an enhanced image for its original-pixel-scale result.</p>
{''.join(gallery)}
<div class="table-block"><h3>Measurements across all 20 scans</h3><p>Crop margins are measured in aligned-image pixels, ordered left / top / right / bottom. Gains are estimated after cropping for the combined pipeline and ordered R / G / B.</p>
<table><thead><tr><th>Plate</th><th>Detected margins</th><th>Area retained</th><th>Gray-world gains</th></tr></thead><tbody>{''.join(summary)}</tbody></table></div>
<p><a href="results/enhancements/contact.jpg">All 20 scans: baseline, crop, contrast, white balance and combined</a> · <a href="results/enhancements.json">Parameters and measured results (JSON)</a></p>
</section>'''
