"""Reproducible batch experiments, original-resolution outputs and audit records."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
from time import perf_counter

import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version
from colorize import split_plate, resize_gray, search_shift, pyramid_align, compose, save_rgb

HERE = Path(__file__).resolve().parent
PARAMETERS = {'metric': 'ncc', 'radius': 15, 'refine_radius': 2, 'min_size': 160, 'border': .12}


def process(path: Path, output: Path, group: str) -> dict:
    with Image.open(path) as im:
        original_size = list(im.size)
        b, g, r = split_plate(np.asarray(im))
    record = {'id': path.stem, 'file': path.name, 'group': group,
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'input_size_wh': original_size, 'channel_size_hw': list(b.shape),
              'discarded_bottom_rows': original_size[1] % 3}
    dest = output/'media'/group
    stem = path.stem
    save_rgb(compose(b, g, r, (0, 0), (0, 0)), dest/f'{stem}-before.jpg', 900)
    shape = (round(b.shape[0]*min(1, 320/b.shape[1])), min(b.shape[1], 320))
    small = [resize_gray(c, shape) for c in (b, g, r)]
    save_rgb(np.stack(small[::-1], axis=-1), dest/f'{stem}-low-before.jpg')
    # Keep separated low-resolution channels for the three detailed experiments.
    if stem in ('00056v', '00125v', '00163v'):
        for name, c in zip(('b', 'g', 'r'), small):
            save_rgb(np.repeat(c[:, :, None], 3, axis=2), dest/f'{stem}-channel-{name}.jpg')
    record['single'] = {}
    for metric in ('ncc', 'l2'):
        start = perf_counter()
        gs, gscore = search_shift(small[0], small[1], metric=metric)
        rs, rscore = search_shift(small[0], small[2], metric=metric)
        seconds = perf_counter()-start
        save_rgb(compose(*small, gs, rs), dest/f'{stem}-single-{metric}.jpg')
        record['single'][metric] = {'g_shift_xy': list(gs), 'r_shift_xy': list(rs),
                                     'scores': [gscore, rscore], 'seconds': seconds,
                                     'channel_size_hw': list(shape)}
    start = perf_counter()
    gs, gt = pyramid_align(b, g, **PARAMETERS)
    rs, rt = pyramid_align(b, r, **PARAMETERS)
    seconds = perf_counter()-start
    rgb = compose(b, g, r, gs, rs)
    save_rgb(rgb, output/'full'/group/f'{stem}.jpg')
    save_rgb(rgb, dest/f'{stem}-pyramid.jpg', 900)
    record['pyramid'] = {'g_shift_xy': list(gs), 'r_shift_xy': list(rs), 'seconds': seconds,
                         'g_trace': gt, 'r_trace': rt, 'output_size_hw': list(rgb.shape[:2])}
    print(f'{group}/{path.name}: G={gs} R={rs} pyramid={seconds:.3f}s', flush=True)
    return record


def contact_sheet(records: list[dict], output: Path, filename: str) -> None:
    width, height = 360, 350
    sheet = Image.new('RGB', (3*width, ((len(records)+2)//3)*height), '#f5f2eb')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(records):
        x, y = (i%3)*width, (i//3)*height
        path = output/'media'/row['group']/f"{row['id']}-pyramid.jpg"
        with Image.open(path) as im:
            im.thumbnail((width-12, height-48))
            sheet.paste(im, (x+(width-im.width)//2, y+24))
        draw.text((x+8, y+5), row['file'], fill='#252d29')
        p = row['pyramid']
        draw.text((x+8, y+height-18), f"G{p['g_shift_xy']} R{p['r_shift_xy']}  {p['seconds']:.2f}s", fill='#252d29')
    sheet.save(output/filename, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE/'results')
    parser.add_argument('--group', default='provided', choices=('provided', 'additional'))
    args = parser.parse_args()
    files = sorted(p for p in args.data.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.tif', '.tiff', '.png'))
    if not files:
        parser.error('No supported images in the data directory.')
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for path in files:
        records.append(process(path, args.output, args.group))
        report = {'parameters': PARAMETERS, 'single_width': 320,
                  'coordinate_convention': 'Applied shift (x,y): positive right/down; B is fixed.',
                  'timing_scope': 'Alignment of G and R only; excludes input/output, resize for single-scale, and compositing.',
                  'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'pillow': pillow_version},
                  'count': len(records), 'records': records}
        (args.output/f'{args.group}.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    contact_sheet(records, args.output, f'{args.group}-contact.jpg')


if __name__ == '__main__':
    main()
