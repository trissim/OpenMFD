# Figure 4

`../../generate_validation_figure.py` renders `draft_figure.png` and
`draft_figure.pdf` for V10. The ODP files and `archive_full_validation/` are
earlier versions, not editable copies of the current figure.

- A: the original 24-device tracer montages at 0 and 72 hours. The approximate
  5 mm bars use the known 9 mm well-centre spacing within the first device;
  montage gutters are excluded from that estimate. Acquisition metadata for
  these exports has not been recovered.
- B: original stitched CTB images cropped using saved match coordinates and
  the fixed-crop declaration, paired with their original counting outlines.
  All three pairs have been visually inspected for cell/outline alignment.
  The 500 um bars use the acquisition XML scale, 1.18675253 um/pixel.
  Background subtraction, normalization and downsampling affect display only.
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

Redraw Figure 4 from its retained inputs in the existing desktop environment:

```sh
.venv/bin/python papers/mfd_platform/figures/generate_validation_figure.py
```

This does not run segmentation, change counts or regenerate Supplementary
Figure S3. Inspect the drawing before selectively publishing its declared pair.

The original import and its 72-count verification are historical work from
commit `f4f2111`; their source paths, hash, calibration and verification are
retained in `../../../supplementary/validation/sources.json`. The completed
one-shot importer and old V10 DOCX converter have been retired. The renderer now
reads retained CSV/JSON once into typed measurement and image records. Inclusion
classes own summary membership and point style; downstream plots do not inspect
raw inclusion strings or dictionary keys.

The original October 15 author answers confirm all five cell-count exclusions
and the 67-device selection, superseding the earlier 69-device interpretation.
The paired black-on-white views and mean bars behind device dots are restored
through `CtbView` and `PlateCounts`; no old raster statistics are imported. The
real desktop CLI completed at `73c940b`, its final PNG was inspected, and both
source and published pairs were committed at `f5b9d18`. The apparent-width pair
was byte-identical before and after. Placed-page inspection follows the new
reading build. Earlier pairs are preserved in checkpoint `8e51fb0` and tracked
history through `3cc8034`.

Exact historical software/run configuration, positivity and manual corrections
remain unverified, as do ethics details; see
`../../../reviews/CTB_ANALYSIS_HANDOFF.md`. Display reconstruction and the
confirmed exclusions do not supply those missing facts. Neither later
`_analysis_final` measurements nor default settings from a current OpenHCS
installation may substitute for them.
