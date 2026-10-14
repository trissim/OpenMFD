# CTB Analysis Handoff: MFD Manuscript Figure 4C

Updated 2026-09-09 with author clarification following the 2026-09-08 audit of
acquisition XML, archived pipeline files, count tables, plotting code and the
imported raster. This is a provenance audit, not a new segmentation run.
The September reanalysis remains separate.

**Bottom line:** the author confirms that N=69 comes from the February
three-plate DMSO-only axotomy cohort, with three of 72 devices excluded. These
are PRE CTB counts, not post-axotomy counts. The supplied acquisition XML is
byte-identical to February Plate 1's record. P1-P3 images and count-table versions
are available, but the exact table, three exclusions and plotting invocation
behind the imported N=69 raster are not yet established. Do not replace them
with the later no-drug axotomy figure's exclusions. One acquisition correction
is verified: P3 used 42 sites (7 x 6), whereas P1 and P2 used 35 (7 x 5).

**Author-confirmed acquisition rationale:** Plate 3's device layout was shifted
slightly rightward during gluing. The larger field captured more microchannel
exits to document ablation for the biology paper; 35 sites were sufficient for
cell counting. Stitched images were registered and cropped to the same
soma-counting area regardless of site count. This resolves the cohort and
counting-area questions, but not the original table/version or excluded IDs.

## Scope and Existing Files

This is the **MFD platform manuscript's DIV11 CTB-positive soma count**, not the
separate drug/no-drug axotomy supplementary figure.

- Manuscript: [paper.md](../paper.md), Image acquisition and analysis, Statistics,
  and Figure 4 caption.
- Protocol: [S1](../supplementary/Supplementary_Protocol_S1_device_assembly_culture_and_CTB.md), sections F-G.
- Figure assembly: [generate_validation_figure.py](../figures/generate_validation_figure.py).
- Imported plot: [plate_bar_var_Cell_Before.png](../figures/final_drop/Fig5_plate_layout_validation/plate_bar_var_Cell_Before.png).

The assembly script crops an existing plot image; it does not calculate its
means or error bars. The original image says "Cell Before" and N = 69.
Its ICC/pairwise annotations are omitted from the manuscript, which reports
descriptive plate summaries only. Do not restore inferential annotations by default.

## 1. Confirmed Cohort and Source Records

Current draft: one E18 donor preparation, three technical plates, 48 devices
per plate, 24 interior devices per plate, 72 eligible interior devices and
69 analyzed after three exclusions. CTB-647 was added distally at DIV10 and
somata counted at DIV11. On 2026-09-09 the author confirmed the February
DMSO-only cohort and 72-to-69 inclusion count. The exact observation table and
individual excluded IDs still require linkage to the original plot.

- Dataset root: [February acquisitions](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03>).
  Each acquisition below has `Images/Index.xml` and its source images.

| Source plate | Acquisition directory | Measurement ID | Indexed images / sites |
|---|---|---|---|
| P1 | `TS_MFD_PRE_P1_20260203__2026-02-03T19_23_43-Measurement 1` | `b81d766b-1106-4c2b-b3d1-0447f965b2e2` | 1680 / 35 |
| P2 | `TS_MFD_PRE_P2_20260203__2026-02-03T19_50_17-Measurement 1` | `50df545f-07c3-48f4-be4e-52418b861d55` | 1678 / 35 |
| P3 | `TS_MFD_PRE_P3_20260203__2026-02-03T20_12_32-Measurement 1` | `8d984873-a4df-4e76-9db9-fe9cf879cc8c` | 2014 / 42 |

- The [supplied XML](../supplementary/Opera_Phenix_acquisition_index.xml)
  matches P1 exactly. All three records contain 24 interior device coordinates,
  rows 2-7 and columns 2-5, on an 8 x 6 device map. Each site has brightfield
  (channel 1) and Alexa 647 (channel 2), with one plane and timepoint.
- P2 lacks field 10 in both channels at R07C02; P3 lacks field 23 in both
  channels at R04C04. These are absent indexed acquisitions, not established
  Figure 4C exclusions. Their effect on the final counting crop was not assessed
  in this audit.
- Source P1/P2/P3 belong to the author-confirmed plotted cohort. The original
  plotting input is still needed to link individual count-table versions to
  the displayed plate summaries. P1's acquisition-to-supplementary-record
  mapping is also independently confirmed directly.
- The records establish February 3 acquisition dates and 72 interior device
  coordinates. They do not establish donor identity, DIV, CTB-addition time,
  exclusion reasons or the individual members of the final 69-device set.
  The cohort and exclusion total are now author-confirmed. One E18 preparation,
  DIV10 application and DIV11 imaging are currently investigator/protocol
  statements, not independently confirmed culture records.

If records disagree with the draft, report the discrepancy rather than forcing
the analysis to total 69. Do not borrow drug-assay exclusions or software
versions merely because those files are in the same project.

## 2. Describe the Actual Counting Method

- Software: the recovered tables and pipelines are OpenHCS outputs. The exact
  OpenHCS version that generated the imported raster's counts is **not verified**.
  The [older handoff](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/figure_handoff/HANDOFF.md>)
  mentions v0.7.21 plus a hotfix as its then-current environment, explicitly for
  possible reanalysis; that is not provenance for the earlier plot.
- Recovered configurations:
  [pre_state.py](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/pre_state.py>)
  describes a P1 stitching session;
  [pre_analysis.py](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/final_scripts/pre_analysis.py>)
  and [pre_analysis_v2.py](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/final_scripts/pre_analysis_v2.py>)
  describe candidate counting configurations. The latter relocates parameters
  into `SimpleCellSegmentationConfig`. Neither file is yet linked conclusively
  to all counts in Figure 4C.
- Acquisition XML confirms 10x/0.30 NA, 2 x 2 binning, 1080 x 1080-pixel tiles,
  1.1867525299 um/pixel, 10 ms brightfield and 100 ms Alexa 647 exposures.
  P1/P2 use 7 x 5 sites; P3 uses 7 x 6. The saved stitching session enhances
  channel 2 for ASHLAR position estimation, returns to the pipeline input for
  percentile enhancement, then assembles tiles and projects Z. Its explicit
  ASHLAR `pixel_size=2.0` argument differs from the acquisition calibration;
  do not report that argument as the microscope pixel size.
- The candidate counting configuration aligns the two-channel image using a
  brightfield template (`cellbody_sobel.tif`), then crops x=3196, y=228,
  width=2292, height=3700 pixels. The v2 template is archived at
  `Stitched_Plates/cellbody_sobel.tif`; older source contains a historical mount
  path rather than the current dataset path.
- On channel 2 it performs percentile normalization (0.1-99.99%), white top-hat
  filtering (radius 35 pixels) and `count_cells_simple`. Explicit settings are
  maximum area 2000 pixels, maximum eccentricity 0.9, watershed enabled for
  objects above 200 pixels and watershed seed separation 10 pixels.
- The threshold method and some size/foreground defaults are not explicit in
  that saved source. Without its matching historical implementation, do not
  supply today's defaults as the original CTB-positivity rule. No separate
  manual CTB-positive/negative classification record or manual correction log
  was located. Image-edge treatment is also not established for the plot.
- Fixed parameters across the three plotted plates are **not verified**.
  A further file named `pre_stich.py` actually contains another counting variant
  (99.9% upper percentile, eccentricity 0.975, seed distance 3, among other
  differences). The archived configurations cannot be treated as interchangeable.

A saved configuration plus a concise explanation is sufficient; no need to
rewrite routine software documentation. If counting was manual, describe that
instead of supplying a segmentation algorithm that was not used.

## 3. Supply Counts and Exclusions

Link the original table, preserving original identifiers and missing values.
Ideally provide an export with these fields (equivalent existing column names
are fine): `plate_id`, `device_id`, `ctb_soma_count`, `included`,
`exclusion_reason`, and `source_image`.

- Exact Figure 4C input table: **not identified**. Available candidate tables:
  [Pre/Data](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/Pre/Data>)
  and [Pre/Data-final](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/Pre/Data-final>),
  each containing `metaxpress_style_summary_p1.csv` through `p3.csv`.
  [aggregated_data.csv](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/figure_handoff/reference/aggregated_data.csv>)
  retains 72 records with PRE counts and later axotomy-related fields/flags.
- `R02C02`, for example, means device-map row 2, column 2. This is the
  microscope's 8 x 6 device map, not an unverified direct mapping onto the 96
  separate access-well coordinates. One measured image region supplies one
  device's soma count.
- Exact three Figure 4C exclusions/reasons: **not identified**. The later
  axotomy handoff, R script and reviewed `control_reproducibility_data.csv`
  carry different endpoint-specific or magnitude-based exclusions. None was
  imported into this manuscript handoff as a Figure 4C exclusion.
- Interior restriction: all three acquisition records already select the 24
  interior devices. The protocol states that perimeter culture conditions
  differed; the date and decision record establishing that restriction were
  not located. The XML alone does not establish its biological rationale.
- No values were dropped, corrected, imputed or normalized for this audit.
  The diagnostic summaries below use every available row in the indicated
  table, not an invented 69-device subset. No new included/excluded CSV was
  created because Figure 4C inclusion status remains unresolved.

Retain excluded records with their status/reason; do not silently drop them or
substitute zero for a missing or uninterpretable count.

## 4. Verify the Plot

The current caption calls the error bars **SD**, but this has not been confirmed.

- Imported raster SHA-256:
  `ae6d55b9682549ee7056aac25d8d83848c96ffa170c6f22477f915be9f8c28c8`.
  It explicitly displays N=69 and ICC/pairwise annotations. Those annotations
  remain omitted from the manuscript assembly.
- Error-bar definition for this raster: **not yet verified**.
  [generate_plots_2.R](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-02-03/Stitched_Plates/figure_handoff/reference/generate_plots_2.R>)
  calculates arithmetic means and R's sample `sd` (denominator n-1), then plots
  mean +/- SD. However, it uses different exclusions, p1/p2/p3 labels,
  quasirandom points and different output filenames; it does not establish the
  convention used by `plate_bar_var_Cell_Before.png`.
- The same-named image inside
  [plots.zip](</run/media/ts/0BA20E780BA20E78/plots.zip>) has a March 2 archive
  timestamp but differs from the manuscript image in both hash and pixels.
  Direct inspection shows **N=62 and ICC=0.172**, versus N=69 and ICC=0.124
  in the manuscript raster. This is a different analysis version, not merely
  a different image encoding. The archive contains raster plots only, not
  their source data or R script.
- Original plotting invocation and matching editable PDF/SVG: **not located**.
  `generate_validation_figure.py` only crops the supplied image; it cannot
  reproduce its underlying statistics. No replacement plot was generated.
- Verified Figure 4C summary values remain unresolved:

| Figure plate | Included n | Excluded n | Mean CTB-positive somata/device | Error-bar value | Definition |
|---|---:|---:|---:|---:|---|
| 1 | Not verified | Not verified | Not verified | Not verified | Original input required |
| 2 | Not verified | Not verified | Not verified | Not verified | Original input required |
| 3 | Not verified | Not verified | Not verified | Not verified | Original input required |

For comparison only, direct arithmetic checks of the recovered tables give:

| Candidate table | Source plate | Available n | Mean | Sample SD |
|---|---|---:|---:|---:|
| `Pre/Data` | P1 | 24 | 173.708333 | 44.179947 |
| `Pre/Data` | P2 | 24 | 253.000000 | 73.484101 |
| `Pre/Data` | P3 | 24 | 203.625000 | 32.391374 |
| `Pre/Data-final` | P1 | 24 | 174.166667 | 46.270158 |
| `Pre/Data-final` | P2 | 24 | 2738.958333 | 7221.210777 |
| `Pre/Data-final` | P3 | 24 | 111.875000 | 30.423550 |
| P3 `stitched_testcount/images_results/metaxpress_style_summary.csv` | P3 | 24 | 314.875000 | 44.348730 |

These were calculated from the CSV's `Mean Cell Count...` column, skipping its
metadata/header lines, retaining all device rows, and using sample SD (n-1).
The P3 test-count summary is visually compatible with the third bar, but that
alone does not prove its inclusion or identify the other plates. None of the
complete table sets above reproduces the three-bar plot. No raster digitization
or search for exclusions that force a numerical match was performed.

Reuse the original analysis code. Do not estimate values by digitizing the
raster when the original observations are available.

## 5. Return Manuscript-Ready Text

**Short image-analysis Methods paragraph:**

No fully verified segmentation Methods paragraph can yet be supplied for the
specific 69 observations. The following acquisition correction is supported
by the records and the author's cohort/common-crop confirmation, and is now
incorporated into the main Methods and S1:

> Images were acquired in a 7 x 5 site grid for Plates 1 and 2 and a 7 x 6 site
> grid for Plate 3. Brightfield and Alexa 647 images were acquired at each site.
> The three acquisition records cover 24 interior devices per plate.
> The larger Plate 3 field accommodated a lateral placement offset and captured
> more microchannel exits. All stitched images were registered and cropped to
> the same soma-counting area, irrespective of acquisition site count.

The candidate workflow in section 2 supplies the recovered crop, preprocessing
and explicit segmentation parameters. Resolve its count-table/version linkage
before converting that description into past-tense claims about Figure 4C.

**Correct Figure 4C caption/statistics wording:**

Until the original observations and error-bar rule are recovered, a provisional
caption that does not add an unverified definition is:

> (C) Mean CTB-positive soma count per analyzed device for each of three plates.

Keep the investigator's one-donor/technical-replication description; the cohort
is now confirmed. Add n per plate and the verified error-bar
definition together; the visible N=69 annotation does not establish either.
The existing assertion that the bars are SD remains pending verification,
not disproven. No inferential annotations need to be restored.

**Any unresolved discrepancies or corrections needed elsewhere:**

1. Confirm which observation table and script generated the imported raster,
   including the mapping to figure plates and the three excluded device IDs.
2. Confirm the original OpenHCS version/configuration and CTB threshold rule.
3. **Resolved 2026-09-09:** corrected the all-plates 35-site statement in the
   main Methods and S1 F.5. P3 used 42 sites; all plates used a common counting
   crop. The author confirmed the February cohort and the coverage rationale.
4. Assess the two incomplete acquisition patterns without assuming they are
   the manuscript exclusions.
5. Verify the error-bar rule before retaining SD in Statistics, Results and
   the Figure 4 caption. Do not substitute later axotomy exclusions to get 69.
6. Culture/donor/DIV statements still rely on investigator records. This audit
   did not independently verify the notebook or reanalyze February images.

The initial audit edited only this handoff. The 2026-09-09 clarification also
updates the main Methods, S1 and manuscript revision review. Figure generation,
source data and separate axotomy files remain unchanged. Tables and code are linked
above; the exact Figure 4C table and plotting code remain the missing link.

## External-Drive Search Record

A second search included hidden and ignored files throughout the external SSD,
the February result folders, Windows Recycle Bin records, and archive indexes.
The SSD's `lab_pc_backup_oct_15_2025` and `New folder` directories are empty.
The February all-versions figure archive contains an additional `code/plot.r`,
but that script analyzes the four-plate drug dataset from `data.csv`; it is
not the generator of the three-plate `Cell_Before` raster.

The strongest remaining location lead is the original plotting project named
in the SSD handoff:

`C:\Users\uscope\Desktop\mfdplots\FCA-Ep_B-regeneration-assay-main`

Its copied `data_2/aggregated_data.csv` and `generate_plots_2.R` are already
linked above. A copy of the complete project, including earlier plotting
scripts or data versions, has not been located on the mounted SSD. This search
did not restore deleted files, alter source data, or run a February analysis.

## September Treatment Correction (Separate Experiment)

On September 9, the September microfluidic experiment's assignments were corrected
from the user's plate metadata: B/G = DMSO, C = FC-A, D = F04, E = EpoB and
F = EpoB+FC-A, for both P1 and P2. A/H and doses remain unassigned.

The current [September report](</run/media/ts/0BA20E780BA20E78/axotomy_testing/2026-09-04-(complete)/openhcs_reanalysis_20260908/results/treatment_corrected_20260909/REPORT.md>)
links corrected measurements, treatment summaries, plots, availability and the
paired-image index. All 672 numerical/QC rows and 35 PRE/POST pairs are preserved;
31 ratios remain eligible. Only treatment assignments and their derived reporting
changed. The earlier July-derived labels are retained in superseded outputs.

This correction does not alter the February CTB cohort or the Figure 4C evidence
discussed above.
