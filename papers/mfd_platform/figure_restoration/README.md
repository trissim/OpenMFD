# MFD — Alyson's prose with original figures restored

## Reading files

- **Read:** [clean manuscript Word](prose_review/MFD_for_Alyson_reading.docx) or [PDF](prose_review/MFD_for_Alyson_reading.pdf) — 18 pages
- **Review wording:** [prose redline](prose_review/MFD_for_Alyson_prose_redline.docx) — only Tristan's five figures; wording, caption and reference corrections remain tracked
- [Earlier full comparison](MFD_original_figures_tracked.docx) — preserves deleted and replacement pictures; not the current reading/review copy
- [Tracked Protocol 1](Supplementary_Protocol_1_original_figures_tracked.docx) and [reading PDF](Supplementary_Protocol_1_original_figures_revised.pdf) — 6 pages
- [Tracked Protocol 2](Supplementary_Protocol_2_original_figures_tracked.docx) and [reading PDF](Supplementary_Protocol_2_original_figures_revised.pdf) — 5 pages
- [Supplementary Data File 1](OpenMFD_Supplementary_Data_File_1.xlsx) — original five sheets preserved; complete design table moved to S6

The prose redline fixes the final figures on both sides of the comparison: rejecting text edits restores Alyson's prose, not her pictures. See [the review notes](prose_review/README.md). All tracked files retain actual unaccepted text revisions and further Track Changes recording enabled. Original/revised copies and the previous delivery remain in `../v14_tracked/`. Files named `comparison_baseline` are comparison inputs, not reading copies.

## Changes

Alyson's returned `MFD_V14_AEF.docx` is the latest PI prose located. The previously approved finite corrections are retained. All five original composites from `../figures/rendered_docx/` and their original legends are restored, with narrow citation/scale qualifications retained. No old Markdown manuscript was regenerated over her prose.

Prose callouts now match the original panels: Figure 1's frame/inserts/plate, Figure 3 without a G plot, Figure 4's nine numbered steps, and Figure 5's fluid/representative image/count panels. The CTB description now matches the actual single P1/R03C04 example, while retaining the full three-plate quantitative cohort. First mentions are ordered 1–5 and S1–S3. Statistics formerly pointing to removed summary panels remain in the prose/data rather than gaining invented panel references.

Protocol 1's complete design table is now workbook S6. The reviewed eleven-approach fabrication comparison remains Supplementary Table S1 in Protocol 1. Images and all protocol actions remain; whether to promote that comparison to the main text is deferred for discussion.

## Checks and limits

`delivery_checks.json` records reference-token preservation, exact original main-image hashes, native Accept All/Reject All text/media checks, revision counts, comment ranges, figure order, unchanged original workbook cell/style parts, exact transferred design/fabrication rows, and PDF page checks. All 29 final pages were inspected on contact sheets; main pages 16–18 and the fabrication table were also opened at larger reading size. Each main composite and its complete legend fits one page; no blank or clipped pages were found.

For reliable native comparison, floating images are made inline and separated from caption text in both inputs. The comparison baseline's full text and image payloads are asserted identical to the untouched PI original. This is content/image tracking, not a claim that every layout-format change is redlined. Layout was adjusted to avoid obsolete section breaks and split legends.

The original five workbook sheets, shared strings and styles remain byte-identical. Only the workbook's sheet index/relationship/content-type parts and new S6 worksheet change. Historical CTB segmentation, native image/ROI/scale provenance, printer-profile inconsistency, ethics typography and prospective archive questions remain comments; no scientific reanalysis or new factual confirmation is claimed.

## Reproduce

Use the existing papers-only environment, LibreOffice, and its existing `paper_build.compare` owner. From the repository root, with papers-only also on `PYTHONPATH`:

```text
python papers/mfd_platform/figure_restoration/recipe/restore.py --root papers/mfd_platform --compare
```

Export the three `*_revised.docx` files to PDF using LibreOffice's `writer_pdf_Export` filter with lossless images and no resolution reduction. Then run:

```text
python papers/mfd_platform/figure_restoration/recipe/verify.py --root papers/mfd_platform
```

The shared comparison performs real native accept/reject checks before publishing a tracked DOCX. `restoration_manifest.json` records edits and hashes. Failed intermediate comparisons were retained in the author's `agent-scratch/mfd/figure-restoration/` logs; they were not delivered as finished documents.
