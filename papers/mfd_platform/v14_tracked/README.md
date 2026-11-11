# MFD V14 — bounded tracked-edit delivery

Start with **MFD_V14_tracked.docx**, **Supplementary_Protocol_1_V14_tracked.docx** and **Supplementary_Protocol_2_V14_tracked.docx**. These are editable Word review files with real insertion/deletion revisions and continued Track Changes recording enabled. Existing revisions have not been accepted.

The corresponding `_revised.pdf` files are clean reading companions. `_tracked.pdf` files display markup; image replacements/moves show both old and new placements until accepted. `_original.docx` files are byte-identical returned V14 archive members, not regenerated Markdown. The workbook is also byte-identical to the returned workbook.

## Changes and verification

`edit_manifest.json` records the finite agreed edits, comment texts, hashes, image-change bounds and native Writer comparison results. No broad Discussion rewrite was applied. Unknown historical image-analysis settings, native frame settings and archive availability are questions in comments, not invented methods.

- Original archive SHA256: `659f5c216d96fcc1e2e0c52a30a808e8016dce2350a81ed69227ca13ff27a332`.
- Main tracked SHA256: `9d2501e242c138f6afb6ca49b299c20d9458ddd9f3d4eb4197bff7689d3b63f3`.
- Protocol 1 tracked SHA256: `78b98b5ed4a59f2b8626872075231c87e68f3ef87536a2d84b74779828634430`.
- Protocol 2 tracked SHA256: `a8f2bd9f45b1f73d101fa8dcc105a8539f30f0a352ec688b99a025c10fe00449`.

Actual revision counts are main 25 insertions/30 deletions; Protocol 1 5/5; Protocol 2 6/6. Existing `paper_build.compare.compare_documents` ran native Writer Accept All and Reject All and checked text and embedded-image sequences. Rejecting restores V14 text and original Figure 1; accepting produces the revised copies. Original/revised reference tokens match. Independent readers additionally checked raw XML projections, original data/reference preservation and actual comment ranges.

`accepted_text_and_comments.json` exposes the final files' accepted wording and seven exact comment selections, including the Figure 1C wafer-scale photomask passage. This read-only XML projection supplements, not replaces, the native comparison checks.

`PDF_INSPECTION.md` records inspection of all 60 PDF pages as contact sheets and nine changed/figure pages at full size. `pdf_export_checks.json` records PDF hashes, page dimensions/text and render paths. The manuscript is 19 pages, Protocol 1 six pages, Protocol 2 five pages, in both reading and markup exports.

## Reproduce from returned V14

The recipe is in `recipe/apply_v14_edits.py`. It reads the returned archive, edits clean OOXML copies while preserving other ZIP parts, then calls the existing shared comparison owner. It does not duplicate comparison/revision machinery or regenerate the older manuscript.

Using the existing interpreter and library checkout:

```bash
PYTHONPATH=/home/ts/code/projects/papers-only \
  /home/ts/code/projects/papers-only/.venv/bin/python recipe/apply_v14_edits.py \
  --archive /home/ts/code/projects/mfd/papers/mfd_platform/review/MFDV14.zip \
  --output /path/to/a/new/output-directory
```

Use `--prepare-only` to inspect clean edits without native comparison. `--document MFD_V14` updates only the manuscript in an existing complete output directory; this was used for the final comment-anchor correction. Redline author is Tristan Simas.

Export PDFs from the resulting clean and tracked DOCXs using LibreOffice headless, an isolated `-env:UserInstallation=file:///absolute/profile/path`, and `--convert-to 'pdf:writer_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},"ReduceImageResolution":{"type":"boolean","value":"false"}}' --outdir OUTPUT DOCX...`. Export does not rewrite the DOCX inputs.

Generate the readable inspection receipts with the same shared-library `PYTHONPATH`:

```bash
python recipe/inspect_tracked_text.py --directory OUTPUT
python recipe/inspect_pdfs.py --directory OUTPUT
```

The native comparison itself uses system Python's UNO bindings. No environment was created for this pass. Observed build versions: Python 3.12.0, Pillow 12.3.0, PyMuPDF 1.28.2, LibreOffice 26.8.1.1. Shared library checkout observed at `96bc7bb94b0bfffbaa04d8728777906f5469c7be`; `paper_build/compare.py` SHA256 `db7abb2090e8c2ee234a52f34d5ae47a88ca84a03da9a2f536f86b252cc658d4`. These identify what ran, not a new dependency pin. Comparison timestamps and generated package metadata can change on replay; the verified semantic endpoints are the required invariant.

## Commit state

This package is built and reviewed, **not committed yet**. The canonical MFD checkout remains unchanged at `0c4a832c27a848ca239fe44f37d820aed2f8127b`. Supported allocation refuses writes there; no editable MFD worktree exists to reuse. The owner has asked Tristan for one supported commit-only worktree, without a new agent or environment. Do not mistake the finished documents for a completed commit.
