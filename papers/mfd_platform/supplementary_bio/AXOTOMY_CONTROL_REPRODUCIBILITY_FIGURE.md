# Axotomy control-reproducibility supplementary figure

## Purpose

This figure complements the FC-A/EpoB manuscript result with the no-drug
control experiment. It is intended to show the scale of the OpenMFD assay and
the device-to-device and plate-to-plate reproducibility of cell loading and
axon regeneration measurements.

The FC-A/EpoB comparison remains in the manuscript figure and is not repeated
here.

## Review decisions incorporated

Liz's 2026-08-26 review and the SSD handoff are implemented as follows:

- use the three all-DMSO control plates as the supplementary cohort;
- show all 72 devices in their physical 6 x 4 plate coordinates;
- use Arial at 11 pt for all figure text;
- use CTB-647 only for the PRE cell-body measurement and normalization;
- describe Hoechst 33342 as a cellular loading control, not as a direct cell
  death measurement;
- preserve the older four-plate drug figure and its generator as a separate,
  reproducible artifact.

## Cohort and inputs

- Plates: `p1`, `p2`, and `p3`.
- Devices: 24 per plate, 72 total.
- Coordinates: `R02`-`R07` and `C02`-`C05`.
- Treatment: all DMSO/no-drug control.
- Data: SSD `figure_handoff/reference/aggregated_data.csv`.
- PRE image: CTB-647 channel 2 from each `*_analysis_final/images` folder.
- PRE segmentation: step 2 ROI archive.
- POST image: axon channel 3 from each dedicated `*_axons/images` folder.
- POST skeleton: step 2 ROI archive.
- Immediate post-axotomy preview: channel-2 axon-compartment crop from each
  plate's `*_stitched_axon-crop/images` folder, displayed as a `0 h` inset.

All three image components are normalized independently with the same robust
2nd-98th percentile contrast stretch used for the current drug comparisons.
This preserves each acquisition's internal structure while avoiding the flat,
low-contrast appearance of the older no-drug exports.

The dedicated P2 `_axons` export stops after `R06C03` and contains 18 wells.
For `R06C04`, `R06C05`, and `R07C02`-`R07C05`, the batch driver uses the
matching channel-3 image and step-2 skeleton ROI from the complete P2
`*_openhcs` analysis. This fallback is recorded in `asset_manifest.json`.

The POST ROI ZIPs use a legacy ImageJ layout without a PolyStore metadata
sidecar. `generate_pre_post_comparison_v3.py` first uses the current PolyStore
loader and falls back to direct `roifile` parsing for these valid legacy files.

## Panel layout

```text
A  B
C  D
E  F
G  G
```

### A. OpenMFD plate and device

Show the full 48-device/96-well OpenMFD plate, highlight the 24-device imaging
region, and include the two-compartment device zoom. This panel reuses the
generated DXFs and Figure 1 rendering infrastructure.

### B. Plate-scale control mosaics

Show the 24 traced PRE/POST comparison images for each plate at their acquired
row and column. Every comparison includes the immediate post-axotomy
axon-compartment preview as a `0 h` inset. A red outline identifies a PRE
segmentation artifact already flagged in the authoritative table; the device
remains visible.

### C. Pre-axotomy CTB-positive cells

- Source: `pre_cell_count`.
- Bars: plate mean and standard deviation.
- Points: individual devices.
- Five PRE artifacts are shown as red x markers and excluded from the bar
  summary. Three originate in the source table; Plate 1 `R03C02` and `R06C02`
  were added after review of the plate mosaic.

### D. Regenerating axon measurement

- Source: `total_axon_count`.
- Bars: plate mean and standard deviation.
- Points: all 24 devices per plate.
- Unit label remains `source units` until the exported OpenHCS measurement is
  confirmed as skeleton length, pixels, or another quantity.

### E. Cellular loading control

- Source: `dapi_count`.
- Manuscript-facing label: `Hoechst 33342-positive nuclei`.
- Bars: plate mean and standard deviation.
- Points: all 24 devices per plate.

### F. Axon measurement per pre-axotomy CTB-positive cell

- Formula: `total_axon_count / pre_cell_count`.
- Bars: plate mean and standard deviation.
- Points: individual devices.
- PRE artifacts follow the panel C exclusion/display rule.

### G. Representative device close-ups

- One non-excluded device per DMSO plate, shown untraced and traced side by side.
- Regenerate the selected PRE cell-body and POST axon comparison TIFFs without
  embedded axotomy-check insets. No full-device raw image substitution.
- Select the closest device to the plate medians across the four plotted metrics,
  using squared deviations scaled by median absolute deviations. Break ties by
  well ID. Record selected IDs in the output manifest, not on panel G.
- Remove only the top well-ID heading from the comparison exports. Preserve the
  image titles and all microscopy content; use white margins, not black bars.
- Display-process PRE fluorescence in both the plate mosaics and representative
  panels with a 30 px white top-hat background
  subtraction and 0.1-99.9 percentile normalization. This changes only figure
  rendering; all plotted measurements remain the existing analysis values.
- Show nine representative immediate post-axotomy crops in panel B without
  treatment labels. Keep all three no-drug mosaics beside them and label
  flagged devices simply as `excluded`.

## DMSO-only rebuild, 2026-09-16

The new standalone A-G figure excludes the drug experiments entirely. Prior
drug and combined outputs remain unchanged. The three plates contribute 72
displayed devices, with the existing five PRE flags retained: C/F summaries
use 22, 21, and 24 devices; D/E use all 24 devices per plate. These counts are
specific to this supplementary analysis and are not substituted for the older
69-device main-manuscript CTB analysis.

```bash
.venv/bin/python papers/mfd_platform/supplementary_bio/generate_axotomy_control_supplementary_figure.py \
  --asset-root /run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/figure_handoff/no_drug_reproducibility \
  --output-dir papers/mfd_platform/supplementary_bio/figure_output_dmso_only_20260916
```

## Interpretation boundary

The three plates establish technical reproducibility for this control run.
They do not establish independent biological replication because the cultures
originated from one animal. The figure is descriptive and contains no
inferential significance brackets.

Hoechst labels nuclei and functions here as a loading control. A direct cell
death claim would require a validated viability or death measurement and is
not made in this figure.

## Rebuild

The image generator requires the OpenHCS environment because it imports
PolyStore and `roifile`:

```bash
/home/ts/code/projects/openhcs/.venv/bin/python \
  papers/mfd_platform/supplementary_bio/generate_control_reproducibility_assets.py \
  --dataset-root /path/to/Stitched_Plates \
  --output-root /path/to/no_drug_reproducibility \
  --workers 4
```

The figure generator uses the MFD project environment:

```bash
source .venv/bin/activate
python papers/mfd_platform/supplementary_bio/generate_axotomy_control_supplementary_figure.py \
  --asset-root /path/to/no_drug_reproducibility
```

The portable asset root contains:

```text
p1/{overlay,no_overlay}/
p2/{overlay,no_overlay}/
p3/{overlay,no_overlay}/
data.csv
asset_manifest.json
code/
```

The figure output contains the composed PNG/PDF, panels A-G, a manifest, and an
editable PowerPoint with each panel and panel letter as a separate slide object.
