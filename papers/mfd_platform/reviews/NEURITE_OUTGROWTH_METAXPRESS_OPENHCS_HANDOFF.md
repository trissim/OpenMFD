# Neurite outgrowth: MetaXpress versus OpenHCS

Purpose: compare drug-versus-control effects from the autonomous OpenHCS analysis
with the existing MetaXpress export, not tune OpenHCS to reproduce MetaXpress.
This file contains treatment identities. Freeze the blind pipeline, measurements,
exclusions, and raw-plus-overlay QC before the analysis agent reads this file or
the reference results. Preserve that run; any later tuning is a separate,
reference-informed development run, not blind autonomous acceptance.

## Reference files

Paths below are relative to `/home/ts/code/projects/mfd/`:

- Original workbook copy: `papers/mfd_platform/supplementary_bio/figure_output_september_outgrowth_20260924/sources/results.xlsx` (sheet `results`, two plate sections).
- Full well-level extraction: `papers/mfd_platform/supplementary_bio/figure_output_september_outgrowth_20260924/outgrowth_wells.csv` (120 wells; includes plate, well, condition, dose, and source Excel row).
- Group summaries: `papers/mfd_platform/supplementary_bio/figure_output_september_outgrowth_20260924/outgrowth_summary.csv`.
- Source treatment descriptions: `papers/mfd_platform/supplementary_bio/figure_output_september_outgrowth_20260924/workbook_plate_descriptions.csv`.
- Existing parser: `papers/mfd_platform/supplementary_bio/generate_september_axotomy_figure.py`, `read_outgrowth()`.
- Figure: `papers/mfd_platform/supplementary_bio/figure_output_september_outgrowth_20260924/September_outgrowth_stitched.pdf`. It omits EpoB and EpoB+FC-A; use the full well table for comparison.

Original acquisition/export directory:
`/run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-09-04-(complete)/neurite outgrowth/`.

## Treatments and controls

The workbook's `Description` cells own the plate map:

| Plate | Rows | Columns 2-6 | Columns 7-11 |
| --- | --- | --- | --- |
| 24098 | B-C | F04 | 09-027 |
| 24098 | D-E | 06-049 | 09-037 |
| 24098 | F-G | 08-115 | 09-079 |
| 24099 | B-C | Y27 | EpoB |
| 24099 | D-E | FC-A | EpoB+FC-A |
| 24099 | F-G | DMSO | DMSO |

Both five-column blocks run 40, 20, 10, 5, 0 uM left to right (user-supplied
dose series). Each compound/dose has two wells. Tristan confirmed that every
drug curve's zero-dose wells are DMSO controls: both plates therefore have DMSO.
These controls are in columns 6 and 11 for each curve's rows. The CSV retains
the curve's compound label at dose 0; interpret those wells as DMSO while
preserving their curve identity. Plate 24099 also has dedicated DMSO blocks in
rows F-G (four wells per series position); their dose labels are positions, not
molar DMSO concentrations. The combination's component-wise dose convention is
unknown. Use each curve's own zero-dose DMSO wells as its primary baseline;
do not substitute controls from another plate.

## Metrics and comparability

The export contains well summaries, not individual-cell records. The existing
CSV extracts these four fields; the workbook has additional measurements:

| CSV metric | Exact MetaXpress field |
| --- | --- |
| `mean_outgrowth` | `Mean Outgrowth Per Cell (Neurite Outgrowth)` |
| `median_process_length` | `Cell: Median Process Length (Neurite Outgrowth)` |
| `branches_per_cell` | `Mean Branches Per Cell (Neurite Outgrowth)` |
| `cell_count` | `Number of Cells (Neurite Outgrowth)` |

Compute corresponding OpenHCS endpoints only where the frozen pipeline supports
their definitions. Total neurite length / detected cells is a candidate for mean
outgrowth; branch count / cells requires an explicit branch definition. Do not
substitute a pooled segment-length median for the exported cell-process-length
summary. Label unmatched definitions as proxies or unavailable, not identical.

MetaXpress acquired nine sites per well. Its counts are fractional summaries,
not whole-well totals; exact site/cell aggregation and exported length units are
not declared. Use the same physical wells and sampled area. Prefer site-level
OpenHCS measurements with a declared well aggregation; a stitched-mosaic result
is a different measurement protocol unless shown otherwise. Acquisition metadata
records 1.3556 um/pixel; that does not prove MetaXpress exported micrometres.
Do not compare raw counts or lengths as equivalent until aggregation/units are
resolved. Missing/failed measurements stay missing, never zero.

## Comparison after the blind run is frozen

Join by verified original `(plate, well)`, not condition alone; establish any
coded-input mapping from the retained provenance. Within each method, compute
drug and baseline means from well summaries, then `delta = drug - baseline` and
`fractional_change = drug / baseline - 1` when baseline is positive and valid.
Primary baseline on both plates: the same drug curve's zero-dose DMSO wells.
Dedicated DMSO wells on plate 24099 can provide a secondary same-plate
comparison. Keep dose, curve identity, and baseline choice explicit; do not
silently pool all zero-dose controls or dedicated DMSO wells.

Compare effect direction, fractional-change magnitude, and dose-response shape
between methods. `OpenHCS fractional_change - MetaXpress fractional_change` is
a dimensionless effect discrepancy, not proof of equivalent segmentation.
Report raw deltas in each method's own units; subtract them across methods only
after units and definitions are matched. Report cell-count changes alongside
outgrowth to expose possible cell-loss effects, without claiming toxicity from
count alone. Do not use the figure's pooled DMSO reference line as the primary
baseline. Treat wells as technical replicates, not independent biological repeats.

Deliver a joined well table and a compact effect table with plate, condition,
dose, metric, baseline, valid-well counts, both methods' drug/control means,
deltas, fractional changes, and comparability/QC notes. Include mean and sample
SD plus well-level points; no unsupported biological significance claims.
