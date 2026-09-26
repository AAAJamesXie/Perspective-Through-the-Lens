"""Handwritten translation alignment for vertically stacked B/G/R glass plates.

Only NumPy and Pillow are required. All public shifts are (x, y), positive
right/down, and describe the translation APPLIED to the moving channel.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image


def normalize(image: np.ndarray) -> np.ndarray:
    a = np.asarray(image)
    if a.size == 0 or not np.isfinite(a).all():
        raise ValueError('Image must be nonempty and finite.')
    if np.issubdtype(a.dtype, np.unsignedinteger):
        return a.astype(np.float32) / np.iinfo(a.dtype).max
    a = a.astype(np.float32)
    if a.min() < 0 or a.max() > 1:
        raise ValueError('Floating-point images must be in [0, 1].')
    return a


def split_plate(image: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    a = normalize(image)
    if a.ndim == 3:
        # The provided scans are grayscale; tolerate grayscale stored as RGB.
        if a.shape[2] not in (3, 4):
            raise ValueError('Expected grayscale or RGB image.')
        a = a[:, :, :3].mean(axis=2)
    if a.ndim != 2 or a.shape[0] < 3 or a.shape[1] < 1:
        raise ValueError('Expected a nonempty vertically stacked B/G/R plate.')
    h = a.shape[0] // 3
    return a[:h], a[h:2*h], a[2*h:3*h]


def resize_gray(a: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Low-pass resampling is permitted; pyramid construction is explicit below."""
    return np.asarray(Image.fromarray(a).resize((shape[1], shape[0]), Image.Resampling.BILINEAR))


def search_shift(reference: np.ndarray, moving: np.ndarray, radius: int = 15,
                 center: tuple[int, int] = (0, 0), metric: str = 'ncc',
                 border: float = .12) -> tuple[tuple[int, int], float]:
    """Exhaustive search; all candidates use the SAME reference support.

    For a trial (dx,dy), compare B[y,x] with moving[y-dy,x-dx].
    NCC maximizes the cosine similarity specified in the assignment (no mean
    subtraction). L2 minimizes sqrt(sum((B-moving)**2)). No rolled/wrapped
    pixels or padded values participate in scoring.
    """
    if reference.ndim != 2 or reference.shape != moving.shape:
        raise ValueError('Channels must be equal-size 2D arrays.')
    if radius < 0 or int(radius) != radius or not 0 <= border < .5:
        raise ValueError('Radius must be a nonnegative integer; border must be in [0, .5).')
    if metric not in ('ncc', 'l2'):
        raise ValueError('Metric must be ncc or l2.')
    if not np.isfinite(reference).all() or not np.isfinite(moving).all():
        raise ValueError('Channels must contain finite values.')
    h, w = reference.shape
    cx, cy = map(int, center)
    mx = max(math.ceil(w*border), abs(cx)+radius)
    my = max(math.ceil(h*border), abs(cy)+radius)
    if h-2*my < 4 or w-2*mx < 4:
        raise ValueError('Search window leaves fewer than four interior pixels per axis.')
    a = np.asarray(reference[my:h-my, mx:w-mx], dtype=np.float32)
    norm_a = float(np.einsum('ij,ij->', a, a, dtype=np.float64))
    # Prefer the smallest refinement when otherwise tied, including blank images.
    candidates = [(x, y) for y in range(cy-radius, cy+radius+1)
                  for x in range(cx-radius, cx+radius+1)]
    candidates.sort(key=lambda xy: ((xy[0]-cx)**2+(xy[1]-cy)**2, xy[1], xy[0]))
    best, best_value = (cx, cy), -float('inf') if metric == 'ncc' else float('inf')
    for dx, dy in candidates:
        b = np.asarray(moving[my-dy:h-my-dy, mx-dx:w-mx-dx], dtype=np.float32)
        if metric == 'ncc':
            norm_b = float(np.einsum('ij,ij->', b, b, dtype=np.float64))
            denom = math.sqrt(norm_a*norm_b)
            value = float(np.einsum('ij,ij->', a, b, dtype=np.float64))/denom if denom else 0.0
            better = value > best_value + 1e-12
        else:
            diff = a-b
            value = math.sqrt(float(np.einsum('ij,ij->', diff, diff, dtype=np.float64)))
            better = value < best_value - 1e-12
        if better:
            best, best_value = (dx, dy), value
    return best, best_value


def pyramid_align(reference: np.ndarray, moving: np.ndarray, metric: str = 'ncc',
                  radius: int = 15, refine_radius: int = 2, min_size: int = 160,
                  border: float = .12) -> tuple[tuple[int, int], list[dict]]:
    if reference.ndim != 2 or reference.shape != moving.shape:
        raise ValueError('Channels must be equal-size 2D arrays.')
    if min_size < 32 or refine_radius < 0:
        raise ValueError('min_size must be at least 32; refinement radius must be nonnegative.')
    levels = [(reference, moving)]
    while min(levels[-1][0].shape) > min_size:
        a, b = levels[-1]
        shape = ((a.shape[0]+1)//2, (a.shape[1]+1)//2)
        levels.append((resize_gray(a, shape), resize_gray(b, shape)))
    shift, previous, trace = (0, 0), None, []
    for a, b in reversed(levels):
        if previous is not None:
            shift = (round(shift[0]*a.shape[1]/previous[1]),
                     round(shift[1]*a.shape[0]/previous[0]))
        shift, score = search_shift(a, b, radius if previous is None else refine_radius,
                                    shift, metric, border)
        trace.append({'shape_hw': list(a.shape), 'shift_xy': list(shift),
                      'score': score, 'radius': radius if previous is None else refine_radius})
        previous = a.shape
    return shift, trace


def compose(b: np.ndarray, g: np.ndarray, r: np.ndarray, g_shift: tuple[int, int],
            r_shift: tuple[int, int], crop: bool = True) -> np.ndarray:
    if b.ndim != 2 or b.shape != g.shape or b.shape != r.shape:
        raise ValueError('Channels must be equal-size 2D arrays.')
    rgb = np.stack((np.roll(r, (r_shift[1], r_shift[0]), (0, 1)),
                    np.roll(g, (g_shift[1], g_shift[0]), (0, 1)), b), axis=-1)
    if crop:
        h, w = b.shape
        x0, x1 = max(0, g_shift[0], r_shift[0]), w+min(0, g_shift[0], r_shift[0])
        y0, y1 = max(0, g_shift[1], r_shift[1]), h+min(0, g_shift[1], r_shift[1])
        if x0 >= x1 or y0 >= y1:
            raise ValueError('Shifts leave no common image support.')
        rgb = rgb[y0:y1, x0:x1]
    return rgb


def save_rgb(rgb: np.ndarray, path: Path, max_width: int | None = None) -> None:
    image = Image.fromarray(np.round(np.clip(rgb, 0, 1)*255).astype(np.uint8))
    if max_width is not None and image.width > max_width:
        image = image.resize((max_width, round(image.height*max_width/image.width)), Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--method', choices=('single', 'pyramid'), default='pyramid')
    parser.add_argument('--metric', choices=('ncc', 'l2'), default='ncc')
    parser.add_argument('--radius', type=int, default=15)
    args = parser.parse_args()
    start = perf_counter()
    with Image.open(args.input) as im:
        b, g, r = split_plate(np.asarray(im))
    align = search_shift if args.method == 'single' else pyramid_align
    gs, _ = align(b, g, metric=args.metric, radius=args.radius)
    rs, _ = align(b, r, metric=args.metric, radius=args.radius)
    save_rgb(compose(b, g, r, gs, rs), args.output)
    print(json.dumps({'g_shift_xy': gs, 'r_shift_xy': rs, 'seconds': perf_counter()-start}))


if __name__ == '__main__':
    main()
