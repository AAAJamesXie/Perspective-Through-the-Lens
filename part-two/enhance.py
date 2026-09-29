"""Optional automatic photographic restoration after alignment."""
import numpy as np
from colorize import normalize


def _rgb(image):
    a = normalize(image)
    if a.ndim != 3 or a.shape[2] != 3:
        raise ValueError('Expected a nonempty RGB image in [0, 1].')
    return a


def _border_depth(strips, max_fraction):
    """Detect a coherent transition following a mostly border-like prefix."""
    n, width, _ = strips.shape
    limit = int(n * max_fraction)
    if limit < 1 or width < 5:
        return 0
    # Sample the central 60% of each strip so perpendicular borders do not vote.
    band = strips[:, width//5:width-width//5]
    band = band[:, ::max(1, band.shape[1]//512)]
    median = np.median(band, axis=1)
    spread = np.max(np.quantile(band, .9, axis=1)-np.quantile(band, .1, axis=1), axis=1)
    border_like = ((spread < .12) | (median.min(axis=1) > .9)
                   | (median.max(axis=1) < .1)
                   | (np.ptp(median, axis=1) > .35))
    # Signed changes cancel texture; a coherent edge has a consistent direction.
    jump = np.max(np.abs(np.median(np.diff(band, axis=0), axis=1)), axis=1)
    interior = jump[n//4:max(n//4+1, 3*n//4)]
    threshold = max(.035, float(np.median(interior))*4)
    candidates = [d for d in range(1, min(limit, len(jump))+1)
                  if jump[d-1] > threshold and border_like[:d].mean() >= .6]
    return max(candidates, default=0)


def auto_crop(image, max_fraction=.15):
    """Content-derived box; 15% is a search bound, never a fixed crop margin."""
    a = _rgb(image)
    if not 0 < max_fraction < .5:
        raise ValueError('max_fraction must be between 0 and .5.')
    h, w = a.shape[:2]
    top = _border_depth(a, max_fraction)
    bottom = _border_depth(a[::-1], max_fraction)
    left = _border_depth(a.transpose(1, 0, 2), max_fraction)
    right = _border_depth(a.transpose(1, 0, 2)[::-1], max_fraction)
    box = [left, top, w-right, h-bottom]
    return a[top:h-bottom, left:w-right].copy(), {
        'box_xyxy': box, 'margins_ltrb': [left, top, right, bottom],
        'retained_fraction': (h-top-bottom)*(w-left-right)/(h*w),
        'max_search_fraction': max_fraction}


def auto_contrast(image, percentiles=(1, 99)):
    """A shared affine stretch avoids three independent channel remappings."""
    a = _rgb(image)
    low, high = percentiles
    if not 0 <= low < high <= 100:
        raise ValueError('Percentiles must satisfy 0 <= low < high <= 100.')
    lo, hi = np.percentile(a, [low, high])
    out = a.copy() if hi-lo <= 1e-7 else np.clip((a-lo)/(hi-lo), 0, 1)
    return out.astype(np.float32), {'percentiles': [low, high],
        'endpoints': [float(lo), float(hi)],
        'clipped_sample_fraction': float(np.mean((a < lo) | (a > hi)))}


def white_balance(image):
    """Gray-world diagonal gains, capped to avoid amplifying near-empty channels."""
    a = _rgb(image)
    means = a.mean(axis=(0, 1), dtype=np.float64)
    target = float(means.mean())
    gains = np.divide(target, means, out=np.ones(3), where=means > 1e-7)
    gains = np.clip(gains, .5, 2)
    corrected = a*gains
    scale = max(1., float(corrected.max()))
    return (corrected/scale).astype(np.float32), {
        'illuminant_rgb': means.tolist(), 'gains_rgb': gains.tolist(),
        'global_highlight_scale': scale}
