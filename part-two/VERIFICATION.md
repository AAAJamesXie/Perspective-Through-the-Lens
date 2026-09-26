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

This is the required L2/NCC baseline with a handwritten pyramid, not a full restoration system. Optional white balance, detected-border cropping, contrast enhancement and edge-feature alignment are deliberately absent and explicitly identified as unimplemented on the project page.
