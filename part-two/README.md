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
python run_enhancements.py --data "../../syde671 assignment 1 data/data"
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
- The baseline uses no per-image tuning or edge-feature alignment. Optional color enhancements are described below and shown separately from the baseline galleries.

## Bells & Whistles

Three automatic post-processing methods are implemented in `enhance.py`, using only the existing NumPy and Pillow dependencies:

- **Automatic cropping:** detect coherent signed RGB transitions near the four edges, supported by uniform, extreme-brightness or strongly colored outer strips. The outer 15% is a search bound, not a fixed crop margin. The detected crop may retain a side unchanged. See the webpage for all thresholds and failure modes.
- **Automatic contrasting:** stretch the pooled RGB 1st and 99th percentiles to zero and one using the same affine mapping for all channels. This resists isolated extreme pixels but clips some highlights and shadows. Constant images are left unchanged.
- **Automatic white balance:** estimate a gray-world illuminant from the RGB means, apply diagonal gains limited to [0.5, 2], and uniformly rescale if highlights exceed one. Zero channels keep unit gain. Dominant scene colors can violate the assumption; the report shows a river landscape where this correction is less convincing.

`run_enhancements.py` verifies each original scan's saved SHA-256 hash and recomposes it with the saved pyramid shifts. It processes all 18 provided and two additional scans, without rerunning alignment or reading compressed baseline outputs. Single-method comparisons apply each method independently to the aligned RGB image; the combined pipeline is crop, white balance, contrast. All scans use the same parameters.

Run the enhancement tests with `python -m unittest test_enhance -v`. Six real-array tests cover detected borders of varying colors and widths, unbordered and constant images, shared contrast mapping, known color casts, zero channels and invalid inputs. Existing alignment tests remain in `test_colorize.py`.

Generated artifacts:

- `results/enhancements.json`: crop coordinates, retained area, percentile endpoints, clipping fractions, illuminant estimates, gains and source hashes.
- `results/enhancements/`: five previews per scan (baseline, crop, contrast, balance, combined), a contact sheet and full-resolution combined results.
- `index.html#bells-whistles`: English explanations, formulas, single-method comparisons, a failure example and combined results.

## Saved artifacts

- `results/provided.json`: input hashes, shifts, timings and level traces for all 18 provided plates.
- `results/additional.json`: same records for two external examples.
- `results/full/`: RGB outputs at original pixel scale after valid-support cropping.
- `results/media/`: web previews, unaligned composites and both single-scale methods.
- `results/provided-contact.jpg`: complete provided-image visual overview.
- `data/sources.json`: official source records and download URLs for additional scans.
- `index.html`: report page.
- `submission/part-two-v2.pdf`: webpage PDF.
- `submission/part-two-code.zip`: code, tests, provenance and additional sample data.

## Interpretation and limitations

Timings measure alignment of both channels; pyramid timings include construction, but exclude file I/O, compositing and saving. Single-scale timings exclude the preliminary resize. The run is a sequential measurement, not a statistically controlled benchmark.

Successful execution is not an accuracy score. There is no ground-truth registration for these scans. The page records visual assessment, residual fringes, physical borders and damaged emulsion. The first plate has different scratches/blotches in each source channel; alignment cannot restore the missing image data. Moving subjects, non-translational geometry and cross-channel brightness differences can also leave artifacts.

The handout references 5/20 examples and legacy names, but the provided directory contains 18 numbered JPEGs (12 small, 6 large). All 18 are included, along with two separately sourced collection examples. Three provided plates show detailed intermediate stages; all 18 have both low-resolution metrics and full-resolution pyramid results.

## Submission status

Local artifacts can be reviewed before publication. Git push, public deployment and upload to LEARN are separate actions; they have not been performed by the experiment scripts.
