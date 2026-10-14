# Combined axotomy supplementary figure

This compact version combines the existing four-plate drug-assay figure with
the no-drug control reproducibility measurements. CTB-647 is used only for the
PRE cell-body count and for axon/PRE normalization.

## Layout

```text
A  B
C  D
E  F
G  G
H  I
J  K
```

- A is the shared OpenMFD plate and device schematic.
- B shows the selected drug-assay plate mosaics. The recommended version shows
  Drug Plates 1-3.
- C-F retain the drug-assay quantitative panels.
- G retains the drug-assay representative images.
- H-K reproduce control panels C-F: PRE CTB-positive cells, regenerating axon
  measurement, Hoechst 33342 loading control, and axon measurement per PRE
  CTB-positive cell.
- No no-drug representative images are included.
- The no-drug plate mosaic is omitted from the merged figure; only the drug
  plate mosaic is retained.
- Plate 1 `R03C02` and `R06C02` are PRE segmentation exclusions identified by
  plate-mosaic review, in addition to the three source-table PRE exclusions.

## Rebuild

```bash
source .venv/bin/activate
python papers/mfd_platform/supplementary_bio/generate_combined_axotomy_supplementary_figure.py \
  --control-asset-root /path/to/no_drug_reproducibility \
  --drug-mosaic-plates p1 p2 p3
```

Use `--drug-mosaic-plates p1`, `p1 p2`, or `p1 p2 p3 p4` for the other panel-B
variants. This option changes only the displayed drug mosaic. Quantitative
panels C-F continue to use all four drug plates. Panel G uses Plates 1 and 2
because only those acquisitions contain the full PRE stitched CTB image needed
for its inset. Control panels H-K use all three no-drug plates.

The output includes a PNG, PDF, manifest, individual panel files, and an
editable PowerPoint in which every panel and panel letter is a separate object.
