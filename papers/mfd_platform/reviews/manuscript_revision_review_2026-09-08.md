# Manuscript Revision and Remaining Issues

Reviewed and revised 8 September 2026. Source: `papers/mfd_platform/paper.md`,
the active supplementary protocols/tables, figure sources, and the generated
manuscript DOCX/PDF. The separate biology/axotomy paper was not revised.

## Verdict

The revised manuscript has a coherent engineering-platform narrative and a
functional Methods structure. It is **not yet submission-ready**. The remaining
major issues are missing experimental provenance/reporting and unverified
quantitative figure inputs, not a requirement to imitate a molecular-biology
article. Do not treat successful document generation as scientific validation.

## Revisions Applied

- Kept substantial hybrid-mold fabrication detail and the critical numerical
  conditions; consolidated repeated geometry, layer and alignment descriptions.
- Organized Methods into design, mold fabrication, casting/assembly,
  characterization, tracer testing, culture/tracing, imaging/analysis and
  statistics. Combined the additional design examples with design generation.
- Put casting, demolding, trimming, glass bonding, autoclaving, frame assembly
  and final plasma treatment in chronological order. Kept the two distinct
  plasma treatments explicit. Moved secondary HIPS printing details to the
  already-existing Table S6 rather than duplicating them.
- Added the known shrinkage factor, 1.0226 at 100 C, to Methods and S2. **Correction
  to the earlier comparison:** this was already in Table S3, and is confirmed
  by `PDMSConfiguration.scale_factor()`. It was not an unresolved experimental
  parameter. The study-specific version/file provenance still needs completion.
- Moved qualitative adhesive observations from Methods to Results; removed
  their duplication from S1. Distinguished visual observations from measured
  cytotoxicity, durability and dimensional fidelity.
- Removed the unmeasured moisture-uptake claim and its mismatched ABS-moisture
  and surface-contact-angle citations. Retained the observed frame-printing
  comparison, without converting it into a materials-property measurement.
- Replaced sustained-72-hour-flow language with the actual two-time-point
  tracer observation in the abstract, Methods, Results, conclusion and Figure 4
  title. Added the limits on flow-rate and isolation inference.
- Qualified the single unframed control: frame, adhesive/seal and dish
  environment all changed, so it does not identify a single causal component.
- Made one-donor technical replication and the perimeter limitation explicit
  in the abstract/discussion/conclusion. Removed an unsupported implication of
  prospectively defined device selection from S1.
- Explicitly identified all three additional layouts as unfabricated and
  unvalidated, including the Figure 5 caption and Table S3.
- Corrected Table S5 wording so inserts and SU-8/SUEX features remain on the
  mold, rather than appearing to be components retained in the PDMS cast.
- Added `--skip-figures` to the existing document builder for text-only builds.
  Preserved the existing 3D figures; regenerated only Figure 4's wording.

## Remaining Issues, in Priority Order

### 1. CTB analysis and Figure 4C are not independently reproducible

`figures/generate_validation_figure.py` imports
`plate_bar_var_Cell_Before.png`; it does not calculate means or error bars from
per-device observations. The raster reports N = 69 but does not establish the
error-bar definition. The old reviewer checklist also explicitly leaves that
definition unconfirmed. The current draft's **SD interpretation remains
provisional**, not verified by this revision. The same applies to the supplied
plate means and the exact three excluded devices.

The fill-in handoff for the original analysis agent is
[CTB_ANALYSIS_HANDOFF.md](CTB_ANALYSIS_HANDOFF.md).

**Author clarification, 2026-09-09:** the 69 observations are pre-axotomy CTB
counts from the February three-plate DMSO-only cohort on the NVMe, with three
of 72 devices excluded. Cohort identity and the total exclusion count are
resolved. Plates 1/2 used 35 sites and Plate 3 used 42 to cover a rightward
placement offset and more microchannel exits for the biology study. All plates
were registered and cropped to the same soma-counting area; the larger field
did not change that area. Main Methods and S1 now reflect this distinction.

Required: the actual table for this MFD experiment, plate/device identifiers,
the three exclusion IDs/reasons, original plotting calculation, and the
counting pipeline/configuration. Confirm software/version, stitching and
registration, segmentation and positivity rules, and any manual corrections.
Do not transplant the later axotomy analysis's OpenHCS version or exclusions
into this experiment without evidence. Regenerate Figure 4C from the verified
table and update Methods, caption and S1 together.

### 2. Ethics and author declarations remain incomplete

The E18 tissue source lacks the applicable ethics committee, guidelines and
approval/procurement details. Obtain the actual facts, including whether tissue
was obtained under another laboratory's approval. Full affiliations,
corresponding-author email, contributions, funding and competing-interest
declarations also require author input. No approval identifier or declaration
of no conflicts has been invented. See the current
[RSC author responsibilities](https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities)
and [journal guidance](https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/lab-on-a-chip).

### 3. Protocol and measurement clarifications

Author clarification after the initial review: routine neuronal culture is
covered by the cited original protocol. Routine fabrication follows the
manufacturers' instructions, with the modifications already described in
Methods and S2. Neither requires duplicating the standard instructions or
listing culture-maintenance settings as an outstanding revision.

The author confirmed autoclaving at 121 C for 15 min and a tracer assay using
1:1000 antibody dilutions in PBS, with devices kept in the cell-culture
incubator for 72 h. These details have been added to Methods, S1 and the
relevant captions. Autoclave duration, tracer diluent and incubation location
are resolved.

The author also confirmed that all pin heights were measured individually with
a micrometer. Methods, Table S1 and S2 now identify the instrument and the
96-position measurement procedure. This reporting item is resolved; no
instrument model, precision or reference datum has been invented.

The author clarified the adhesive screen as a simple qualitative criterion:
did the primary cortical-neuron cultures survive to the experimental endpoint?
Only LOCTITE SI 5140 passed; all other screened adhesives failed. Methods,
Results and S1 now use this bounded description. The earlier granular adhesive
comparison was condensed, and a standardized quantitative toxicity-screen
protocol is no longer requested for this claim. No sample numbers, viability
percentages or toxicity thresholds have been invented.

### 4. Source-data and image provenance need a submission check

Availability still promises a future versioned archive and CTB table. Complete
the deposits and identify the exact study preset/source revision and analysis
inputs. The count plot should not remain raster-only evidence. Check original
microscopy acquisition/panel lineage, contrast processing, crop locations and
scale bars; do not infer physical scale from resized composite images. Current
source panels were preserved, not reprocessed from raw acquisitions.

The prior project checklist also requests coordination of image/data reuse
with the related biology manuscript. Establish any shared dataset and describe
the distinct questions transparently; this review has not established duplicate
publication or audited the other manuscript.

### 5. Residual scientific limitations are stated, not eliminated

One donor preparation does not establish biological reproducibility. Restricting
analysis to interior devices does not validate all 48 devices for equivalent
long-term culture. A single unframed control cannot identify why perimeter
conditions differ. Two fluorescence endpoints do not quantify isolation or
continuous flow; differently conjugated antibody tracers are not interchangeable
calibrated concentration measurements. More than 50 usable casts is a cumulative
count, not a yield percentage without all attempted casts. These limits do not
negate the fabrication demonstration, but broader claims would require further
evidence.

## Verification

- Built the manuscript and active supplementary material through
  `build_docx.py --skip-figures`; inspected rendered Methods and figure pages.
- Confirmed all five main figure references resolve and seven image objects
  (five main and two supplementary) are embedded in the DOCX.
- Checked DOCX archive/XML integrity and PDF text against page bounds.
- Recalculated Table S1: n = 96; mean 5.5507708 mm; sample SD 26.67997 um;
  range 116 um, consistent with the reported rounding.
- Confirmed the code's 100 C horizontal scale factor is 1.0226.
- The current PDF places the large Figure 4 image and its long caption on
  adjacent pages. This is not image cropping, but final journal layout should
  keep the legend convenient to the image; original-resolution figure files
  remain available separately.
- No raw CTB recount, error-bar verification, new assay, full external
  citation-by-citation audit or peer-review acceptance assessment was performed.

## Outputs

- `../paper.md`: revised source.
- `../build/paper_review.docx`: editable manuscript with supplementary material.
- `../build/paper_review.pdf`: rendered review copy.
- Historical comparison remains under `methods_comparison_2026-09-08/`; its
  checksum and old line references describe the pre-revision source.
