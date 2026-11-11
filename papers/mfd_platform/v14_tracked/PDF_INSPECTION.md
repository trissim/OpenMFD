# V14 PDF inspection

Reviewed all 60 exported pages as contact sheets: revised and tracked main manuscript (19 pages each), Protocol 1 (6 each), Protocol 2 (5 each). Opened nine changed/figure pages at full size as well. No cropped artwork, overlapping body text, missing panels or broken symbol rendering was seen on those pages.

- Main revised p14: Figure 1C's conflicting second recipe line is absent; the other inscription, layout, masks, models and plate photograph remain. Main tracked p14 deliberately shows the deleted original image crossed out above its replacement. This is a genuine image replacement revision, not two figures in the accepted document.
- Main revised/tracked p16: Figure 3 and its extended caption are readable. The added sentence explicitly describes the procedure in Supplementary Protocol 1D; no new invisible schematic layer is claimed.
- Main revised p18: all Figure 5 panels, three plate/device IDs, yellow overlays, 500 µm scale bars and counts are present. The caption continues onto p19, where its ending is intact.
- Protocol 1 revised/tracked p4: the SUEX/S1 discussion, original image and caption precede the SU-8/S2 discussion, original image and caption. Tracked p5 contains the deleted old S1 placement, as expected for a move. Accept All leaves one S1 block, not two.
- Protocol 2 revised p2: corrected casting steps 3–8 are consecutive and readable, following steps 1–2 on p1. All original actions remain. The tracked PDF displays old and new numerals together, as expected.

PDFs ending `_revised.pdf` are clean reading companions. PDFs ending `_tracked.pdf` show markup and therefore repaginate paragraphs and may show both old and new image placements. The `_tracked.docx` files remain the editable review documents, including comments and continued Track Changes recording. Export did not accept their revisions or rewrite their DOCX bytes.

`pdf_export_checks.json` identifies every PDF by SHA256, records page dimensions/text, and names the contact sheets under `pdf-review/`. The full-size inspected PNGs are also there. `accepted_text_and_comments.json` identifies the actual tracked DOCXs and exact comment selections; `edit_manifest.json` records the input, edits and native comparison checks.

Editorial and scientific readers approved the final main DOCX SHA256 `9d2501e242c138f6afb6ca49b299c20d9458ddd9f3d4eb4197bff7689d3b63f3`; protocol hashes did not change after the Figure 1C comment-anchor correction.

Commit is not complete: the canonical checkout's supported allocation is read/launch-only, no editable MFD worktree exists to reuse, and the owner has been asked to permit one supported worktree solely for committing. No allocation bypass was used.
