"""Recompose original scans using saved shifts, then run three enhancements."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from colorize import split_plate, compose, save_rgb
from enhance import auto_crop, auto_contrast, white_balance

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=HERE.parent.parent/'syde671 assignment 1 data/data')
    args = parser.parse_args()
    records = []
    contact = Image.new('RGB', (1000, 180*20), 'white')
    draw = ImageDraw.Draw(contact)
    for group, folder in [('provided', args.data), ('additional', HERE/'data/additional')]:
        baseline = json.loads((HERE/f'results/{group}.json').read_text())
        for row in baseline['records']:
            source = folder/row['file']
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if digest != row['sha256']:
                raise ValueError(f'Input changed since alignment: {source}')
            with Image.open(source) as im:
                b, g, r = split_plate(np.asarray(im))
            p = row['pyramid']
            rgb = compose(b, g, r, p['g_shift_xy'], p['r_shift_xy'])
            cropped, crop_info = auto_crop(rgb)
            contrast, contrast_info = auto_contrast(rgb)
            balanced, balance_info = white_balance(rgb)
            cropped_balanced, combined_balance = white_balance(cropped)
            combined, combined_contrast = auto_contrast(cropped_balanced)
            variants = {'baseline': rgb, 'crop': cropped, 'contrast': contrast,
                        'balance': balanced, 'combined': combined}
            paths = {}
            y = len(records)*180
            for col, (name, array) in enumerate(variants.items()):
                assert np.isfinite(array).all() and array.min() >= 0 and array.max() <= 1
                path = Path(f'results/enhancements/{group}/{row["id"]}-{name}.jpg')
                save_rgb(array, HERE/path, max_width=900)
                paths[name] = path.as_posix()
                thumb = Image.fromarray(np.round(array*255).astype('uint8'))
                thumb.thumbnail((195, 150))
                contact.paste(thumb, (col*200, y+25))
                draw.text((col*200+3, y+4), f'{row["id"]} / {name}', fill='black')
            full = Path(f'results/enhancements/full/{group}/{row["id"]}.jpg')
            save_rgb(combined, HERE/full)
            records.append({'id': row['id'], 'group': group, 'sha256': digest,
                'input_shape_hw': list(rgb.shape[:2]), 'crop': crop_info,
                'contrast': contrast_info, 'white_balance': balance_info,
                'combined_white_balance': combined_balance,
                'combined_contrast': combined_contrast, 'images': paths,
                'full_combined': full.as_posix()})
            print(f'{group}/{row["id"]}: margins {crop_info["margins_ltrb"]}', flush=True)
    contact.crop((0, 0, 1000, len(records)*180)).save(HERE/'results/enhancements/contact.jpg', quality=90)
    output = {'count': len(records), 'order': ['crop', 'white_balance', 'contrast'],
        'input': 'Original scans with SHA-256 verification; saved baseline shifts; no JPEG intermediate.',
        'records': records}
    (HERE/'results/enhancements.json').write_text(json.dumps(output, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
