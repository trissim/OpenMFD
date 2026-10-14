# September neurite-outgrowth-only figure

Open [the PDF](figure_output_september_outgrowth_20260924/September_outgrowth_stitched.pdf)
for review, or the PNG for quick viewing. The editable PowerPoint, separate
panel PNGs/SVGs, exact plotted tables, source hashes, and a figure legend are in
`figure_output_september_outgrowth_20260924/`.

The quantitative panels G–J use the same MetaXpress-exported workbook as the
September axotomy-and-outgrowth figure, but omit EpoB and EpoB+FC-A. The
underlying `outgrowth_wells.csv` retains the full source inventory for audit;
only the plotted condition set is filtered. No axotomy data enter this figure.

Panels A–F show complete nine-site FITC and DAPI mosaics for DMSO (matched vehicle),
F04 20 µM, 06-049 40 µM, 08-115 5 µM, Y27 40 µM, and FC-A 40 µM. The
thick outline of each mosaic matches its condition color in panels G–J. The
original physical wells and coded inputs were matched by exact pixel equality
at FITC and DAPI site 1 after the blinded OpenHCS stitch completed; the builder checks
this identity again. This post-run identification was not used to tune the
neurite pipeline. Selection is illustrative, not a statistical-representative
claim. No segmentation overlays or provisional OpenHCS measurements enter the
figure.

FITC is shown in green with a two-stage shared-stack display recipe. First,
the six entire stitched mosaics share one 0th–99.9th percentile raw window.
Each normalized mosaic receives a large 192-pixel-radius rolling-ball
background estimate computed at one-eighth resolution; only 70% of that
estimate is subtracted so faint processes are not lost. A second, shared
35th–99.9th-percentile asinh stretch (scale 0.0015, gamma 0.80) darkens the
uniform background and preserves full highlight headroom. DAPI is shown in
blue after a separate shared 90th–99.9th percentile window across all six
complete DAPI mosaics (gamma 0.55). No original site is normalized separately,
and these display-only
operations do not alter the quantitative measurements. The 500 µm scale bars use
the original acquisition metadata's 1.3556 µm/pixel spatial calibration;
stitching preserves pixel scale. The stitched TIFFs themselves do not retain
that calibration tag, so this is also recorded explicitly in the manifest.
The manifest also records each final mosaic's green brightness distribution,
bright-pixel fraction, and blue-signal fraction as presentation diagnostics;
these are not biological detection scores.

The workbook does not declare the exported length units or the exact
aggregation of its well summaries, so the graphs retain “export units.” DMSO
positions are matched dilutions, not a molar DMSO concentration. There are no
inferential statistics or biological-replicate claims.

Build from the project root:

```sh
.venv/bin/python papers/mfd_platform/supplementary_bio/generate_september_outgrowth_figure.py
.venv/bin/python -m pytest tests/unit/test_september_outgrowth_figure.py --no-cov -q
```

The builder accepts `--workbook`, `--stitched-root`, `--raw-root`,
`--coded-root`, and `--output-dir`.
It reads source files without modifying them. See `figure_manifest.json` for
the exact source TIFF/workbook hashes, identity checks, display parameters,
and output hashes. A checksum-verified copy of the small MetaXpress workbook
is retained under `sources/`; the large stitched TIFFs are referenced by hash
but not duplicated into the figure folder.
