# PI revisions, 2 October 2026

Scope: expand the biology Figure S1 legend and discuss the additional generated
layouts in the OpenMFD manuscript, citing Figure 5. No measurements or images
were changed, and no scientific analysis was rerun.

The edited sources are in this isolated checkout:
`/home/ts/wt/mfd-pi-legend-discussion-20261002`.
The shared checkout's tracked manuscript and build changes were left untouched.
Existing local changes to the build declaration, build requirements, and two
figure helpers were copied here as build inputs, without modifying or committing
those changes.

The biology legend was checked against the current figure, figure manifest,
and axotomy protocol in the shared project. It distinguishes 48-device plate
geometry from the 24 devices assessed per plate, technical from biological
replication, and CTβ-dependent exclusions from the full axon and nuclear counts.
Immediate cut-verification images in F are separate pre-treatment acquisitions.

Build: `papers/mfd_platform/build/run-20261002T185214-06a42b89`.
The existing shared paper-build environment generated manuscript, supplement,
and combined-review PDF/DOCX files. Build status reported current with no changed
inputs. Revised Discussion text was verified in both manuscript and review DOCX
files and in the manuscript PDF; the PDF Discussion page was visually inspected.
Existing figure receipts passed, and DOCX ZIP integrity checks passed.

The generated build files and legend are delivered in
`/home/ts/code/projects/mfd/papers/mfd_platform/pi_review_20261002`.
The figure-output directory also receives the expanded legend as Markdown and
Arial 11-point DOCX. The shared project's older `current` build is not switched;
use the dated PI-review files for this revision.

Retained output ownership: this revision owns the worktree, its build run,
Discussion page preview, and dated PI-review delivery directory. The checkout is
retained for the revised sources and reproducible build; no temporary source
checkout or new package installation was used.

Follow-up edits: renamed the Methods heading to "Fluorescent tracer assay" and
removed the pixel-calibration detail from the biology figure legend. Measurement
units and scale bars remain in the legend; calibration remains in the axotomy
protocol. Panel F and its shortened description remain present. The new heading
was verified in the rebuilt PDF and both manuscript and review DOCX files.
