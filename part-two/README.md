# SYDE 671 Assignment 1 - Part Two

Handwritten single-scale L2/NCC translation search and coarse-to-fine alignment of Prokudin-Gorskii B/G/R plates. The original input files are never modified.

## Environment

Tested with Python 3.13.5, NumPy 2.3.3 and Pillow 11.1.0 (see JSON for the exact measured Python version). Only NumPy and Pillow are needed for the algorithm, batch experiments and HTML generation. No automatic alignment or high-level pyramid API is used.

## Reproduce

Run from this directory, using a Python environment with NumPy and Pillow:

```powershell
python -m unittest test_colorize -v
python colorize.py "../../syde671 assignment 1 data/data/00458u.jpg" locomotive.jpg
python run_experiments.py --data "../../syde671 assignment 1 data/data"
python run_experiments.py --data data/additional --group additional
python build_report.py
```

For one single-scale experiment, pass `--method single --metric l2 --radius 15` to `colorize.py`, using a small input scan. A full-resolution single-scale search is intentionally not the batch default.

To use the source ZIP in a different location, replace the `--data` argument with the directory containing the 18 supplied scans. The ZIP includes the two additional scans and their source records, but not the original supplied dataset. The HTML builder writes a page that uses the existing site's parent `style.css`; a copy is included under `site-style.css` in the source ZIP for portability. Copy that file to the parent as `style.css` if building outside the site.

Serve the repository root with `python -m http.server 8000 --bind 127.0.0.1`, then open `http://127.0.0.1:8000/part-two/`. The page also works as a local file. Use the browser's Print / Save as PDF to export the full webpage with its print stylesheet.

## Method and conventions

- Input order: B, G, R from top to bottom. Split into equal bands and discard at most two trailing rows.
- Applied shifts: `(x, y)`, positive right/down. B is fixed. Output order: RGB.
- Single-scale experiments: resize each channel to width 320, search ±15 pixels, report L2 and NCC separately.
- NCC is the raw normalized dot product, without mean subtraction, as in the handout. L2 is the square root of the sum of squared differences.
- Compare the same reference interior for every candidate at a level. Exclude 12% of each dimension on each side, or more if the shift window requires it. Wrapped pixels never affect scoring.
- Build a pyramid explicitly with antialiased bilinear resizing. Coarsest shorter dimension ≤160; initial radius 15; refinement radius 2. Scale shifts using actual adjacent-level size ratios.
- Run every supplied input at its original resolution. Crop only to the common valid support after shifting. This is not detected-border cropping; physical plate borders remain.
- No per-image tuning, color balancing, contrast enhancement or edge-feature alignment is used.

## Saved artifacts

- `results/provided.json`: input hashes, shifts, timings and level traces for all 18 provided plates.
- `results/additional.json`: same records for two external examples.
- `results/full/`: RGB outputs at original pixel scale after valid-support cropping.
- `results/media/`: web previews, unaligned composites and both single-scale methods.
- `results/provided-contact.jpg`: complete provided-image visual overview.
- `data/sources.json`: official source records and download URLs for additional scans.
- `index.html`: report page.
- `submission/part-two-report.pdf`: webpage PDF.
- `submission/part-two-code.zip`: code, tests, provenance and additional sample data.

## Interpretation and limitations

Timings measure alignment of both channels; pyramid timings include construction, but exclude file I/O, compositing and saving. Single-scale timings exclude the preliminary resize. The run is a sequential measurement, not a statistically controlled benchmark.

Successful execution is not an accuracy score. There is no ground-truth registration for these scans. The page records visual assessment, residual fringes, physical borders and damaged emulsion. The first plate has different scratches/blotches in each source channel; alignment cannot restore the missing image data. Moving subjects, non-translational geometry and cross-channel brightness differences can also leave artifacts.

The handout references 5/20 examples and legacy names, but the provided directory contains 18 numbered JPEGs (12 small, 6 large). All 18 are included, along with two separately sourced collection examples. Three provided plates show detailed intermediate stages; all 18 have both low-resolution metrics and full-resolution pyramid results.

## Submission status

Local artifacts can be reviewed before publication. Git push, public deployment and upload to LEARN are separate actions; they have not been performed by the experiment scripts.
