# Full-site visual redesign

Approved scope: homepage, all three Part One study pages and Part Two. Reference: Wix AI Blog (Abstract), https://www.wix.com/website-template/view/html/wh-1329 . Independently implemented as static HTML/CSS in the existing site; no Wix runtime or new dependency is used.

Design: warm light-gray paper, black text and thick horizontal rules; stacked serif wordmark, right-aligned vertical navigation, oversized bold sans-serif headlines and black hero panels. Existing course photography and computational results replace the template's stock content. Part One uses three image-led homepage cards; Part Two receives a larger featured study and a report section index. All four navigation links remain available on narrow screens.

Scope boundaries: preserve the Part One main content, images, GIF, reduced-motion poster, Part Two algorithms, dataset and saved measurements. Rebuild the generated Part Two HTML through its builder so subsequent rebuilds retain the design. Refresh its source ZIP and PDF. No publication or remote push is part of this local redesign.

Validation: real-browser checks cover five pages at 1440, 768, 390 and 320 pixels, image loading, internal links/anchors, visible navigation, horizontal overflow, a real anchor click and reduced-motion GIF fallback. Desktop/mobile screenshots and machine-readable check results are saved under ignored `qa/`. The existing site-test module is also run; the algorithm tests need not be rerun because the algorithm is unchanged.

## Verified outcome

- All 20 page/viewport combinations passed. Four navigation links are visible throughout; no horizontal overflow, missing image, invalid internal destination or browser error was found in the final layout checks.
- The existing three site E2E tests passed. All three Part One main sections match their pre-redesign Git versions exactly.
- The 20 source hashes and final result dimensions match the saved experiment records. Alignment code, measurements and original images were not edited.
- The regenerated Part Two PDF contains 23 pages and all 20 result identifiers. It was rasterized and visually inspected; no text/image overlap or clipping was observed. The updated source ZIP is CRC-verified and includes the current shared CSS, report CSS and page builder.
- Homepage study cards use the photographs' original 3:4 aspect ratio to retain faces and the stop sign in the thumbnails. Desktop and mobile screenshot checks confirmed the final card framing.
- Independent redesign review was requested, but the review agent could not finish because of a usage limit. The primary agent performed the final source and visual review. The earlier independent algorithm review remains separate from this visual redesign.
- Local redesign is complete. No remote publication, Git push or LEARN submission was performed.
