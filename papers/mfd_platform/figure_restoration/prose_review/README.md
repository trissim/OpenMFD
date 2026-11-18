# MFD: reading copy and prose review

- **Read:** `MFD_for_Alyson_reading.docx` or `MFD_for_Alyson_reading.pdf`.
- **Review edits:** `MFD_for_Alyson_prose_redline.docx`.

All three show only Tristan's five original figures. The reading files are exact copies of the checked clean manuscript: Alyson's V14 prose with the agreed corrections, original figures and matching captions/callouts/references.

The prose redline deliberately fixes the final figures on both sides of the comparison. Wording, captions and reference corrections remain tracked. Accept All gives the reading text; Reject All gives Alyson's original prose **with the same final figures**. It does not undo the artwork restoration. Track Changes remains enabled and review comments are retained.

The previous full comparison, including the five deleted pictures and five replacements, remains untouched at `../MFD_original_figures_tracked.docx`. The untouched returned V14 is also preserved. `comparison_inputs/` contains the text-comparison baseline, not another reading draft.

`verification.json` records the five drawings, zero picture revisions, native accept/reject checks, reference preservation and file hashes.

Reproduce into a new output directory using the existing papers-only environment and shared `paper_build.compare`:

```text
python papers/mfd_platform/figure_restoration/recipe/prose_review.py --root papers/mfd_platform --output NEW_DIRECTORY
```
