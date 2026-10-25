# Figure 4

`../../generate_validation_figure.py` renders `draft_figure.png` and
`draft_figure.pdf` for V10. The ODP files and `archive_full_validation/` are
earlier versions, not editable copies of the current figure.

- A: the original 24-device tracer montages at 0 and 72 hours. The approximate
  5 mm bars use the known 9 mm well-centre spacing within the first device;
  montage gutters are excluded from that estimate. Acquisition metadata for
  these exports has not been recovered.
- B: three baseline CTB views from the saved supplementary-biology package.
  The 500 um bars use the original acquisition scale, 1.18675253 um/pixel.
  Background subtraction and contrast normalization affect display only.
- C: all 72 saved DMSO device counts, including five flagged counting artifacts
  shown as red crosses. Plate summaries exclude the flagged devices: n = 22,
  21 and 24; means +/- sample SD = 177.7 +/- 43.7, 269.3 +/- 62.3 and
  203.6 +/- 32.4. All plates came from one embryo.

The baseline count table, representative display images, width crops and
source metadata are retained in `../../../supplementary/validation/`.
All 72 counts were checked against their original per-device CSVs. The later
`_analysis_final` exports are a different analysis and do not supply the counts
in this figure.

`channel_widths.png` and `.pdf` show the nine existing brightfield rulers for
Supplementary Figure S3. The widths are visible wall-band-centre distances,
10.7-13.1 um, not channel-depth measurements.

Regenerate the figures from retained inputs:

```sh
/usr/bin/python3 papers/mfd_platform/figures/generate_validation_figure.py
```

The original import and its 72-count verification are historical work from
commit `f4f2111`; their source paths, hash, calibration and verification are
retained in `../../../supplementary/validation/sources.json`. The completed
one-shot importer and old V10 DOCX converter have been retired. The renderer now
reads retained CSV/JSON once into typed measurement and image records. Inclusion
classes own summary membership and point style; downstream plots do not inspect
raw inclusion strings or dictionary keys.

The published document Figure 4 still contains the older September composite.
The October authored source described above has 67 included devices, while the
author intends 69 for cell counts. Do not regenerate or publish this figure until
the endpoint-specific exclusion reasons are reconciled. Structural decoder changes
do not authorize changing a measurement, inclusion flag, calibration or artwork.
