# Reviewer-loop revision checklist

Source: four read-only reviewer agents run on 2026-06-23 against `paper.md`,
the current figure set, and supplementary materials.

## Patch applied in this pass

- [x] Tighten "96-well" language to distinguish ANSI/SLAS footprint and 9 mm
  well pitch from full biological use of every edge position.
- [x] Remove untested liquid-handling robot compatibility from the main claim
  surface; keep multichannel pipetting and plate-format imaging.
- [x] Reframe fluidic isolation as directional fluidic bias under imposed
  50/25 uL loading, rather than strict compartmental isolation.
- [x] Clarify that CTB endpoint tracing uses the lower-volume distal/axon
  compartment under the soma-to-axon volume bias.
- [x] Reduce overclaiming around lateral registration: z seating was measured;
  lateral registration is constrained by CAD-defined pin/lock geometry.
- [x] State that nominal microchannel dimensions are pre-parylene and that
  post-coating dimensions were not measured in this study.
- [x] Align main Methods and Protocol S1 casting language around 10:1 Sylgard,
  degassing until bubbles are gone, and 1 h cure at 100 degrees C.
- [x] Retitle the generated protocol schematic as post-mold device replication
  and assembly, not full mold fabrication.
- [x] Add a Supplementary Protocol S2 draft for one-time hybrid mold
  fabrication so the main Methods can defer detailed bench procedure.
- [x] Add a Figure 5 constraint-check section to Supplementary Table S3.

## High-priority remaining edits

- [x] Move the main manuscript toward a result-first structure. Figures 1-3
  should become technology-overview/result figures rather than living inside
  Materials and Methods.
- [x] Add a main or supplementary QC table with denominators: molds attempted,
  molds passing visible QC, mechanically broken molds, casts attempted, usable
  casts, failed casts, and definition of "usable".
- [x] Reframe the dye-retention panel as a qualitative directional-bias test
  because calibrated fluorescence ratios were not acquired; do not imply a
  quantitative isolation coefficient or permeability measurement.
- [x] Add biological validation denominators: plate count, device/well count,
  interior positions analyzed, edge positions excluded, CTB-positive counts or
  rates, and failure criteria.
- [ ] Remove exploratory ICC and significance labels from Figure 4 and add the
  source of N, descriptive summary, error-bar definition, and no-inference
  statement. The labels, N, and no-inference statement are complete. Confirm
  from the original analysis whether the retained error bars are SD, SEM, or a
  confidence interval; SD is currently a documented provisional interpretation.
  Exact microscope acquisition settings also remain author-supplied.
- [x] Decide whether the prior-art comparison should be main Table 1 or remain
  Supplementary Table S2; avoid keeping duplicate table sources.

## Figure-specific remaining edits

- [x] Decide whether Figure 3 should remain a photo composite with the
  post-mold schematic as a supporting/generated panel, or be redesigned as a
  two-lane "one-time mold fabrication / repeated device assembly" workflow.
- [x] Use the generated six-step post-mold workflow as Figure 3; retain the
  earlier photo composite as supporting source material.
- [x] If Figure 5 remains in the main text, keep its caption explicit that the
  myelination and axon-guidance designs are generated design-file examples,
  not fabricated or biologically validated devices.

## Supplement-specific remaining edits

- [x] Fill retained local resin-printer, cleaning, and post-cure values in
  Supplementary Table S4 and Protocol S2. The SUEX PEB hold duration and
  measured lateral registration remain author-supplied because they are absent
  from the retained records.
- [ ] Confirm Protocol S1 still matches the lab's current bench protocol after
  the 1 h PDMS cure and frame-sterilization edits.
- [ ] Complete the source-data package. Repository paths are now stated for the
  pin-height measurements, Figure 4 source images, and Figure 4 build script.
  Add the per-position CTB count table and culture replicate metadata; the
  original count-analysis script was not located in the repository.

## Author confirmations before submission

- [ ] Add the institutional animal-use approval statement for the E18 rat
  cortical-neuron preparation.
- [ ] Add exact microscope, objective, exposure, autofocus, and field-layout
  settings used for the Figure 4 endpoint images.
- [ ] Confirm the Figure 4C error-bar definition against the original count
  analysis and deposit the per-position count table.
- [ ] Confirm the SUEX post-exposure-bake hold duration at 50 degrees C.
- [ ] Add measured lateral-registration data if it exists; otherwise retain the
  current bounded statement that lateral registration was constrained by the
  pin/lock seating geometry and was not measured directly.
- [ ] Confirm Supplementary Protocol S1 against the current bench record,
  especially the 1 h PDMS cure, dry-cycle autoclave step, ethanol frame
  sterilization, and 3-day Loctite cure.
- [ ] Complete affiliations, corresponding-author email, author contributions,
  funding, and competing-interest statements.
- [ ] Coordinate disclosure and image/data reuse with the other manuscript that
  may report material from the same one-donor validation experiment.
