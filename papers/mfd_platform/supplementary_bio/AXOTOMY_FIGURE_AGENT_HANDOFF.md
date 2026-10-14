# Axotomy supplementary figure agent handoff

## Objective

Use `generate_axotomy_supplementary_figure.py` to build the seven-panel axotomy
assay figure from a replacement quantitative table and replacement device-level
TIFF images. The archive preserves the repository paths expected by the script,
the OpenMFD geometry code used by panel A, and the exact generated DXFs used by
the original figure.

## Setup

Use Python 3.10 or newer. Extract the archive so that `papers/`, `openmfd/`,
`designs/`, and `plates/` remain under one repository root. From that root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r papers/mfd_platform/supplementary_bio/figure_requirements.txt
python papers/mfd_platform/supplementary_bio/generate_axotomy_supplementary_figure.py
```

On Windows, activate the environment with `.venv\Scripts\activate` before
running the same `pip` and `python` commands.

## Replacement-data layout

Place the new data under `papers/mfd_platform/supplementary_bio/`:

```text
supplementary_bio/
  data.csv
  p1/
    overlay/*.tiff
    no_overlay/*.tiff
  p2/
    overlay/*.tiff
    no_overlay/*.tiff
  p3/
    overlay/*.tiff
    no_overlay/*.tiff
  p4/
    overlay/*.tiff
    no_overlay/*.tiff
```

`data_schema.csv` contains the required header. The production generator expects
these columns:

- `plate`: `p1` through `p4`.
- `well`: coordinate such as `R02C02`.
- `row`: row identifier such as `R02`.
- `col`: numeric device column such as `02`.
- `condition`: one of `DMSO`, `FC-A`, `F04`, `EpoB`, or `EpoB + FCA`.
- `dapi_count`: endpoint nuclear count. Update the panel-E display label if the
  replacement experiment did not use Hoechst 33342.
- `pre_cell_count`: pre-axotomy CTB-positive cell count.
- `post_cell_count`: retained for source completeness but not plotted.
- `total_axon_count`: endpoint axon measurement.
- `outlier`: `TRUE` or `FALSE`.

Each overlay filename must contain its plate and well and end in
`_overlay.tiff`. Each no-overlay filename must end in `_no_overlay.tiff`.
Outlier image filenames must also contain `_outlier_`, matching the CSV flag.

## Current geometry and plate assumptions

- Panel A imports the same `DxfSources`, bounds handling, and layer rendering
  used by the main OpenMFD Figure 1 generator.
- The plate contains a 6 x 8 array of 48 two-compartment devices and 96 wells.
- Each assay plate contains the 24 interior devices at rows `R02`-`R07` and
  device columns `C02`-`C05`.
- The production script validates exactly four plates and 96 rows. If the new
  experiment changes plate count, conditions, coordinate range, or device
  count, update `PLATES`, `CONDITIONS`, `validate_inputs`, and `save_panel_b`
  together rather than bypassing validation.

## Panel logic

- A: actual OpenMFD plate and single-device DXF schematic.
- B: every overlay TIFF in plate coordinates; excluded devices remain visible
  with red outlines.
- C: `pre_cell_count`.
- D: `total_axon_count`.
- E: `dapi_count`, displayed as the endpoint nuclear stain.
- F: `total_axon_count / pre_cell_count`.
- G: one non-outlier representative per condition, selected by minimum squared
  median-absolute-deviation distance across C-F metrics.

The quantitative panels show a mean bar, standard-deviation error bar, and all
retained device points grouped and colored by plate. No inferential significance
annotations are generated.

## Outputs and validation

Outputs are written to `supplementary_bio/figure_output/`:

- composite PNG and PDF;
- one editable PowerPoint slide;
- individual A-G PNGs and SVGs for generated vector panels;
- a JSON manifest recording source hash, counts, and representative devices.

The PowerPoint keeps each panel and panel letter as a separate object. Plot
content is regenerated from the CSV rather than edited inside PowerPoint.

Before delivery, inspect the composite and PowerPoint render at native
resolution, confirm all image/table keys and exclusions, verify the physical
unit of `total_axon_count`, and record donor count and treatment details in the
caption or accompanying methods.
