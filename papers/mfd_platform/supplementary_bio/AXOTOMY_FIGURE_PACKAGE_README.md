# Axotomy supplementary figure package

## Figure versions

- `figures/combined_1plate/`: compact combined figure with Drug Plate 1 shown
  in panel B.
- `figures/combined_2plates/`: compact combined figure with Drug Plates 1 and
  2 shown in panel B.
- `figures/combined_3plates/`: recommended combined figure with Drug Plates
  1-3 shown in panel B.
- `figures/combined_4plates/`: compact combined figure with all four drug
  plates shown in panel B.
- `figures/drug_only/`: original drug-assay supplementary figure.
- `figures/control_only/`: standalone no-drug reproducibility figure.

Changing panel B does not change the analyzed cohort. The combined versions do
not include a no-drug plate mosaic. Drug quantitative panels C-F use all four
drug plates, and panel G uses Plates 1 and 2 because only those acquisitions
include the full PRE stitched CTB image needed for its inset. Control
quantitative panels H-K use all three no-drug plates. No no-drug representative
image panel is included.

Every regenerated no-drug device comparison includes a `0 h` inset from the
immediate post-axotomy axon-compartment crop. PRE, POST, and inset microscopy
images use the same independent 2nd-98th percentile contrast stretch used by
the current drug-image renderer.

CTB-647 is used only for the PRE cell-body measurement and axon/PRE
normalization. POST imaging contributes the regenerating-axon measurement.
No-drug Plate 1 wells `R03C02` and `R06C02` are PRE segmentation exclusions
identified during mosaic review. They are excluded only from PRE-dependent
summaries and remain shown as red markers.

Each figure folder contains PNG, PDF, individual panel images, a manifest, and
an editable PPTX. Every panel and panel letter is a separate PowerPoint object.

## Rebuild

The `code/` folder contains the figure and asset generators. From the repository
root, install or verify the figure dependencies in the project environment:

```bash
papers/mfd_platform/supplementary_bio/install_figure_dependencies.sh
source .venv/bin/activate
```

The supplied PRE/POST comparison generator reads ImageJ ROI ZIP files directly
with `roifile`; `polystore` is not required. The combined generator accepts the
panel-B plate selection directly:

```bash
python generate_combined_axotomy_supplementary_figure.py \
  --control-asset-root /path/to/no_drug_reproducibility \
  --drug-mosaic-plates p1 p2 p3 \
  --output-dir /path/to/output
```

The portable control asset root is not included because its source TIFFs are
large. The PPTX files embed all images needed for figure editing.
