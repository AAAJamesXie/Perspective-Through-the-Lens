# Verification - 2026-09-26

- The new unit test module first failed because `colorize` did not exist. After implementation, all 7 tests passed in 0.319 seconds. Tests use real arrays/images, not mocks.
- The existing `tests/test_site.py` module passed all 3 end-to-end tests in 0.905 seconds, with real local HTTP requests. No repository-wide test command was run.
- One full batch processed 18 supplied images with both low-resolution metrics and original-resolution NCC pyramids. Two separately downloaded Library of Congress scans used the same settings.
- Provided-image alignment time: 0.07778110000072047 to 2.74133509999956 seconds per image, for G and R combined, excluding output encoding/I/O. Six input images are high resolution.
- All provided and additional output previews were visually inspected. Their main structures are broadly aligned, with remaining physical borders, local color fringes and source damage. There is no ground-truth accuracy claim.
- An independent read-only review checked sign conventions, shared scoring support, split/composition order, pyramid scaling, recorded input hashes and output sizes. No required core correction was identified. Optional generalization improvements were noted: source records could be keyed by filename rather than order; detailed-experiment IDs could be centralized; the Python API could reject integer-valued floating-point radii more explicitly. These do not affect the verified dataset or integer-valued CLI interface.
- Browser QA loaded 59/59 report images and checked 70 internal links, with no JavaScript page errors or horizontal overflow at 390 pixels. Desktop and mobile screenshots are retained in the ignored local `qa/` directory.
- The browser-generated PDF was reopened with pypdf and rasterized with Poppler for visual inspection. Images and tables are present and readable; pages have no observed overlap or clipping.
- The source ZIP is reopened and checked using `ZipFile.testzip()` after creation.
- No changes were made to the supplied dataset or the pre-existing untracked GIF. No commit, push, public deployment or LEARN submission has been performed.

## Scope

At the time of the September 26 verification, this was the required L2/NCC baseline with a handwritten pyramid. The following September 29 extension adds three post-processing methods; edge-feature alignment remains outside the implementation.

## Bells & Whistles - 2026-09-29

- Added detected-border cropping, shared 1st/99th-percentile contrast stretching and gray-world white balance, using the existing NumPy and Pillow dependencies.
- Six new real-array unit tests initially failed because enhancement functions were absent. The first crop implementation then failed the known-border test: unsigned texture differences inflated the edge threshold. Measuring coherent signed transitions addressed that cause without changing the tests. The final targeted run of `test_enhance` and `test_colorize` passed all 13 tests in 0.222 seconds. No repository-wide test discovery was run.
- All 18 provided and two additional source hashes matched the saved baseline records. Original inputs were recomposed with saved shifts; all five variants per image had finite values in [0, 1]. Saved artifacts were independently reopened: 20 unique JSON records and 120 JPEGs (100 previews, 20 full-resolution combined images), plus a contact sheet.
- The contact sheet was visually inspected. Cropping removes much of the frame but can leave thin colored remnants; gray-world reduces the blue-purple building cast in 31421v, while 00125v acquires an unconvincing pink sky. Both the useful example and the failure are discussed on the webpage. No historical color-accuracy claim is made.
- Local Edge browser checks passed at 1440 and 390 pixels: all 73 page images loaded, all local links and section anchors resolved, no horizontal overflow and no JavaScript errors. QA records and screenshots are in `qa/bells-whistles/` at the repository root. Desktop cropping and white-balance sections were visually inspected.
- The webpage and source archive include this extension. The PDF was subsequently regenerated and visually checked: 31 pages, including the three methods and their comparisons. The latest local filename is `submission/part-two-v2.pdf`. Original scans and baseline outputs were retained. No commit, push or deployment was performed.
