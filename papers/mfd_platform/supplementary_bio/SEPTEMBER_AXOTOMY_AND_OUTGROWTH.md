# September axotomy and neurite outgrowth

## Files to open

In the ZIP, the deliverables are under `figure/`:

- `September_axotomy_and_outgrowth.pdf`: complete figure for review.
- `September_axotomy_and_outgrowth_editable.pptx`: all ten panels placed on one
  slide; move/resize panels and edit their letter labels independently.
- `September_PI_data.xlsx`: individual plotted observations, summaries, QC,
  treatment/dose maps and representative identities.
- `panels/`: separate panel images and vector graph files.

## Figure scope

New September experiments only; July drug plates and February reproducibility
data are not pooled into these results. No device schematic is included.

- A: both September axotomy plate mosaics in physical device coordinates.
- B: pre-axotomy CTB-positive segmented-object count.
- C: endpoint regenerating-axon skeleton pixels, relative-half threshold method.
- D: endpoint nuclear segmented-object count.
- E: endpoint skeleton pixels divided by matched PRE CTB segmented objects.
- F: one QC-eligible representative pair per drug, PRE CTB and POST axon overlays.
- G-J: independent neurite-outgrowth concentration series: mean outgrowth per
  cell, exported median process length, mean branches per cell, and cell count.
  Each graph groups bars by drug across both plates, with separate bars for
  40, 20, 10 and 5 uM. One dotted line spans the graph at the pooled DMSO
  control mean; individual treatment/dose summaries are unchanged.

Treatment names are shown without an additional positive-control label. FC-A is
the user-identified positive control for both assays.

## Sources and mapping

Axotomy source:
`/run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-09-04-(complete)/openhcs_reanalysis_20260908/results/treatment_corrected_20260909/`

Use the corrected relative-half metric/QC table and corrected paired-image index.
Do not reuse the superseded July-derived treatment labels. Both September plates
have B/G = DMSO, C = FC-A, D = F04, E = EpoB, F = EpoB+FC-A.

Outgrowth source:
`/run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-09-04-(complete)/neurite outgrowth/results.xlsx`

Treatment assignments are parsed from each `Description` cell, not inferred from
the older supplementary figure. Plate 24098 contains F04 and five analogues;
plate 24099 contains Y27, EpoB, FC-A, FC-A+EpoB, and DMSO.

The user supplied the dose series on September 9: columns 2-6 and 7-11 each run
**40, 20, 10, 5, 0 uM** from left to right. Two row wells represent each
compound/dose. DMSO has two blocks, hence four wells at each matched series
position. These positions do not assert a molar DMSO concentration. Combination
doses are nominal; the component-wise concentration convention was not supplied.
No dose information for the axotomy plates was supplied in their corrected metadata.

## Quantification and display

All quantitative values are used as exported; no segmentation is rerun. Axotomy
metric-specific eligibility is retained, including cautions. Missing/incomplete
acquisitions and failed measurements remain missing, never zero. There are 35
complete paired image sets and 31 eligible skeleton/PRE ratios. Direct-metric
plots use all eligible acquisitions for that metric, not only matched pairs.

Axotomy plots show mean and sample SD with individual devices distinguished by
plate. Outgrowth plots show mean and sample SD at each dose, with individual well
summaries visible. Doses are not pooled and each compound's zero-dose wells remain
with their own series. No inferential tests or biological-replicate claims are added.

For outgrowth, source fields are:

| Display | Workbook field |
| --- | --- |
| Mean outgrowth per cell | Mean Outgrowth Per Cell (Neurite Outgrowth) |
| Median process length | Cell: Median Process Length (Neurite Outgrowth) |
| Branching per cell | Mean Branches Per Cell (Neurite Outgrowth) |
| Cell count | Number of Cells (Neurite Outgrowth) |

The median-process-length field is an exported well summary, not a recalculated
median over pooled individual cells. Counts are fractional exported summaries,
not total cells in a well. The acquisition declares nine sites per well. Exact
export aggregation and measurement length units are not declared in the workbook;
length axes therefore retain export units. Raw TIFF metadata uses active spatial
calibration in um (1.3556 um/pixel); this alone does not establish the export's
aggregation or measurement-unit setting.

Representative selection is deterministic: nearest condition median across B-E
using squared median-absolute-deviation-scaled distance, restricted to complete
eligible pairs. Ties resolve by plate/well. Identity and selection scores are saved
in CSV/Excel, but row/column codes are omitted from the representative panel.

Images reuse approved paired TIFFs with their existing independent panel contrast.
Only white figure margins, old captions and the oversized separator are removed;
the complete two image rectangles are retained, with crop boxes recorded.
No intensity comparison is implied. Missing pairs have explicit placeholders;
red mosaic borders denote ratio exclusion, not exclusion from every measurement.
The available paired images do not contain an immediate-post-axotomy inset, so
none is fabricated or substituted with a regeneration image.

## Build and deliverables

From the project root:

```sh
.venv/bin/python papers/mfd_platform/supplementary_bio/generate_september_axotomy_figure.py
.venv/bin/python -m pytest tests/unit/test_september_axotomy_figure.py --no-cov -q
```

The builder accepts `--source-root` and `--output-dir` for another machine.
Output: `figure_output_september_20260909/`. Includes full PNG/PDF, PowerPoint
with separately movable panel images and editable panel letters, individual panel
PNGs/SVGs, `September_PI_data.xlsx`, exact plotted CSVs, selected identities, source
tables/workbook, and a provenance manifest. Plot marks inside each panel are not
native editable PowerPoint charts; use the SVGs or rerun the supplied code for
changes within a graph.

### Portable handoff

`September_axotomy_and_outgrowth_PI_handoff.zip` contains `figure/` (deliverables,
source tables, prepared images and provenance), `code/` (the builder, its shared
renderers and tests), pinned `requirements.txt`, and `SHA256SUMS.json`.
The raw microscopy archive and original large paired TIFFs are not included.
The prepared images are sufficient to reproduce the current figure, but not to
rerun segmentation or choose different contrast settings.

After extracting the ZIP, from its root:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python code/papers/mfd_platform/supplementary_bio/generate_september_axotomy_figure.py \
  --prepared-inputs figure --output-dir regenerated
.venv/bin/python -m pytest code/tests/unit/test_september_axotomy_figure.py -q
```

To include the exported-file checks in that test run, set
`SEPTEMBER_FIGURE_OUTPUT="$PWD/regenerated"` before the pytest command. The raw-drive
workbook test is skipped when the acquisition drive is unavailable; the packaged
workbook is still checked against the regenerated tables.

The build was tested with Python 3.14. Arial must be installed separately for the
same typography; it is not redistributed in the archive. The script verifies
checksums before using prepared source tables or paired images. The `--package`
flag creates an updated handoff after a build. The shared CAD imports are deferred
until a schematic is requested, so this graph-only build does not need OpenMFD,
Blender or the wafer/plate model files.

## Figure legend

**Axotomy responses and neurite outgrowth in independent experiments.**
(A) PRE CTB and endpoint axon overlays arranged by device position for both
September axotomy plates. Grey positions lack a complete paired image set;
red borders mark exclusion from the skeleton/PRE ratio, not necessarily from
other metrics. (B-E) PRE CTB-positive segmented objects, endpoint axon skeleton
pixels, endpoint nuclear segmented objects, and matched skeleton pixels per PRE
CTB object. Bars show means with sample SD; points are devices, coloured by plate.
The number of eligible devices is printed for each group. (F) Representative
PRE CTB and endpoint axon overlays for each treatment; yellow contours show the
existing segmentation or axon traces. (G-J) Mean neurite outgrowth per cell,
exported median process length, branches per cell and exported cell-count
summaries across the nominal dose series. Both plates appear on the same axes,
with bars grouped and coloured by drug and doses labelled under each bar.
Zero-dose bars are omitted. The pooled mean of all DMSO wells is the shared
full-width dotted reference line, as requested; no further normalization is applied.
Bars show means with sample SD; points are well
summaries (two wells per compound/dose, four DMSO wells per series position).
Image contrast is adjusted independently in the source overlays; these images
are not used for quantitative intensity comparisons. The axotomy denominator is
PRE CTB, not endpoint CTB. No inferential statistics are shown.

Interpret the outgrowth/regeneration contrast descriptively. The analogue plate
is a separate assay and does not provide regeneration measurements for analogues
absent from the axotomy treatments. Concentrations, timepoints and measurement
units differ or remain incompletely documented; there is no numerical conversion
between the two assays in this figure.
