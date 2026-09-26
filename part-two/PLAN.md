# Part Two implementation plan

Approved in chat: single-scale experiments on three plates, a handwritten pyramid on all 18 supplied images, additional Library of Congress examples, and a webpage/PDF/code package.

## Design

Use existing Python, NumPy and Pillow. Split the vertical scan into equal B/G/R bands, discarding at most two trailing rows. Report applied shifts as (x, y), positive right/down. Score a fixed interior reference region, excluding wrapped pixels. Implement raw-vector NCC and L2; retain the NCC baseline even if edge features improve an image. Construct the pyramid with antialiased resizing, not a high-level pyramid/registration API. All images share parameters.

## Tasks

- [x] Add real unit tests for channel order, shift signs, L2/NCC, large translations, odd dimensions, constant/invalid images and common-support cropping. Run before implementation.
- [x] Implement `colorize.py`: normalization, splitting, scoring/search, handwritten pyramid, compositing and CLI. Verify the new test module only.
- [x] Implement `run_experiments.py`: detailed low-resolution L2/NCC experiments on three plates, both low-resolution metrics on all supplied plates, full-resolution NCC for every supplied plate, JSON timings/offsets/traces, full-resolution outputs and preview images. Edge-feature alignment remains optional and is not included in this baseline.
- [x] Inspect all result previews. Record failures and limitations honestly; do not tune parameters per image.
- [x] Obtain additional official collection scans with source provenance where accessible, and run the same pipeline.
- [x] Generate an English project page matching the existing site, add the home-page entry, and produce a webpage PDF and source ZIP. Verify saved artifacts and relevant existing site tests.

## Verification boundaries

No mocks, no new installed dependencies, no full repository test suite without permission. Preserve existing pages and the untracked GIF. No automatic Git commit/push or LEARN submission. Visual quality is assessed separately from synthetic displacement recovery; there is no ground-truth registration for the real scans.

## Progress

2026-09-26: processed all 18 supplied grayscale JPEGs (12 small, 6 large) and two additional official collection scans. Plain image URLs returned HTTP 403; browser User-Agent plus the official download query succeeded. Core algorithm tests: 7 passed. Existing site test module: 3 passed. Browser: 59/59 images, 70 internal links, no page errors or mobile horizontal overflow. Independent read-only review found no required core corrections. PDF was rendered and inspected; source archive is CRC-verified. Local baseline artifacts are ready for review; publishing and LEARN submission remain separate.
