# Axotomy assay supplementary figure

## Purpose

This folder contains the quantitative data and device-level image overlays for
the chemical axotomy assay. The target is one large supplementary figure with
the following layout:

```text
A  B
C  D
E  F
G  G
```

The final deliverables are a high-resolution composed figure, individual panel
files, and an editable PowerPoint in which panels A-G and their letter labels
remain separate objects.

## Authoritative inputs

- `data.csv`: authoritative quantitative table. Its SHA-256 hash is identical
  to `data.csv` inside `OneDrive_1_8-24-2026.zip`.
- `p1`-`p4/overlay/*.tiff`: 96 device-level analysis overlays, 24 per plate.
- `p1`-`p4/no_overlay/*.tiff`: matching source-image composites without the
  analysis overlay.
- `plot.r`: exploratory plotting script and the source of the requested metric
  definitions. Its exclusion rule is retained, but the production figure is
  generated in Python because the R dependencies are not installed locally and
  the PowerPoint assembly is Python-based.
- `mock_figure_outline.jpeg`: PI's hand-drawn layout reference.
- `aggregated_data.csv`: older, numerically different table. It is not used in
  the figure because it does not match the CSV supplied in the source archive.
- `../supplementary/Axotomy_Assay_Protocol_for_Biology_Paper.md`: assay,
  acquisition, and analysis context.
- `../figures/generate_openmfd_design_figure.py` and generated v27 DXFs: shared
  OpenMFD geometry and DXF-rendering infrastructure used for panel A.

## Data audit

- Four technical plates are present: `p1`, `p2`, `p3`, and `p4`.
- Each plate contains 24 acquired interior devices at rows `R02`-`R07` and
  device columns `C02`-`C05`.
- The complete OpenMFD plate contains 48 devices in a 6 x 8 array. The acquired
  6 x 4 interior region omits the outer device rows and columns.
- All 96 table keys have exactly one overlay and one no-overlay image.
- Filename `_outlier` markers agree with the `outlier` field in `data.csv` for
  all images.
- Quantitative panels exclude rows where `outlier == TRUE`. Panel B retains all
  images and marks excluded devices so the plate-level acquisition remains
  transparent.

### Devices retained after exclusion

| Condition | Plate 1 | Plate 2 | Plate 3 | Plate 4 | Total retained | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| DMSO | 8 | 4 | 7 | 6 | 25 | 7 |
| FC-A | 4 | 4 | 3 | 3 | 14 | 2 |
| F04 | 4 | 2 | 2 | 1 | 9 | 7 |
| EpoB | 4 | 4 | 4 | 3 | 15 | 1 |
| EpoB + FCA | 3 | 4 | 4 | 4 | 15 | 1 |
| **All conditions** | **23** | **18** | **20** | **17** | **78** | **18** |

The exclusions are strongly unbalanced across conditions, particularly for
F04. The figure therefore shows every retained device point and plate identity
and does not add inferential significance annotations.

## Panel specification

### A. OpenMFD plate and device schematic

Show the 48-device, 96-well plate layout and a magnified two-compartment device.
Use `TwoCompartmentDeviceConfig` and the actual generated v27 single-device top
and bottom DXFs. Highlight the 24-device interior imaging region.

### B. Plate-scale image mosaics

Show all 96 overlay TIFFs in four plate mosaics. Place each image at its actual
row and column. Preserve the full-device image aspect ratio, label each plate,
and outline excluded devices in red rather than dropping them.

### C. Pre-axotomy CTB-positive cell count

- Source column: `pre_cell_count`.
- Interpretation: CTB-647-positive somata before chemical axotomy.

### D. Total axon measurement

- Source column: `total_axon_count`.
- Interpretation: endpoint axon measurement used by the supplied analysis.

### E. Nuclear count

- Source column: `dapi_count`.
- Manuscript-facing label: `Nuclear count (Hoechst 33342)` because the assay
  protocol identifies Hoechst 33342 as the endpoint nuclear stain. The CSV's
  `dapi_count` name is retained only as the source-field name.

### F. Axon measurement per pre-axotomy CTB-positive cell

- Formula: `total_axon_count / pre_cell_count`.
- This corresponds to `neurite_per_pre` in `plot.r`.

### Quantitative panel grammar

- X-axis order: DMSO, FC-A, F04, EpoB, EpoB + FCA.
- Background bar: mean across retained devices.
- Error bar: standard deviation across retained devices.
- Points: individual devices, horizontally grouped and colored by plate.
- No p-values or pairwise brackets are included in this figure draft.
- Devices are technical observations. Biological-donor count is not encoded in
  the supplied files and must be stated separately before inferential claims.

### G. Representative analysis overlays

Show one enlarged non-outlier overlay for each condition. To avoid manual
cherry-picking, select the device closest to the condition median across
`pre_cell_count`, `total_axon_count`, `dapi_count`, and
`total_axon_count / pre_cell_count`, using squared median-absolute-deviation
distance.

Representative images are selected from Plates 1 and 2 because these plates
contain the full PRE stitched CTB image needed to show the axon-compartment
inset consistently for every condition. Plates 3 and 4 contain only the PRE
soma crop. This image-availability restriction applies only to panel G; all
four plates remain in the plate mosaics and quantitative summaries.

| Condition | Selected device |
|---|---|
| DMSO | `p1_R07C02` |
| FC-A | `p1_R03C02` |
| F04 | `p2_R04C05` |
| EpoB | `p2_R05C03` |
| EpoB + FCA | `p2_R06C03` |

## Assay context represented by the figure

- Primary E18 rat cortical neurons were cultured in two-compartment OpenMFD
  devices.
- CTB-647 was added to the distal compartment on DIV10 and pre-axotomy CTB-647
  images were acquired on DIV11.
- Chemical axotomy used 0.25% trypsin and 0.0125% Triton X-100 for 10 min,
  followed by three washes.
- Endpoint imaging was performed 72 h after axotomy after calcein-AM and
  Hoechst 33342 labeling.
- Imaging used an Opera Phenix Plus in widefield mode with a 10x/0.30 NA
  objective, 2 x 2 camera binning, laser autofocus, and 1.187 um effective
  pixels. OpenHCS 0.5.15 was used for stitching, registration, device cropping,
  and device-level analysis.

## Information still needed for a final caption or biological claim

- Number of source animals represented by these four plates.
- Exact physical unit represented by `total_axon_count` (for example, pixels,
  area, skeleton length, or another OpenHCS measurement).
- Full names, suppliers, concentrations, and dosing schedule for FC-A, F04,
  EpoB, and EpoB + FCA.
- Confirmation that all listed outliers satisfy the intended exclusion rule and
  were defined before condition-level comparison.

These missing items do not prevent construction of a descriptive figure, but
they should be resolved before submission or inferential interpretation.

## Rebuilding the figure

Run the generator from the repository root using the project environment:

```bash
papers/mfd_platform/supplementary_bio/install_figure_dependencies.sh
source .venv/bin/activate
python papers/mfd_platform/supplementary_bio/generate_axotomy_supplementary_figure.py
```

The generator validates the table/image correspondence before rendering. It
then writes:

- `figure_output/axotomy_supplementary_figure.png`: 5400 x 6520 pixel composite.
- `figure_output/axotomy_supplementary_figure.pdf`: print-oriented composite.
- `figure_output/axotomy_supplementary_figure_editable.pptx`: one portrait
  slide with panels A-G and all panel letters as separate objects.
- `figure_output/panels/panel_A.png` through `panel_G.png`: reusable panel
  images. Vector SVG versions are also written for panels A and C-F.
- `figure_output/figure_manifest.json`: source hash, counts, panel paths, and
  representative-device selection record.

The PowerPoint keeps panel placement and labels editable. The microscopy
panels and plotted panels remain image objects; the supplied CSV, SVG chart
exports, and generator are retained for content-level revisions.
