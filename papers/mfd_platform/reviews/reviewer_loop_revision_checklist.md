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

- [ ] Move the main manuscript toward a result-first structure. Figures 1-3
  should become technology-overview/result figures rather than living inside
  Materials and Methods.
- [ ] Add a main or supplementary QC table with denominators: molds attempted,
  molds passing visible QC, mechanically broken molds, casts attempted, usable
  casts, failed casts, and definition of "usable".
- [ ] Add quantitative dye-retention analysis: fluorescence ratios, timepoints,
  n, chamber definition, and analysis criteria.
- [ ] Add biological validation denominators: plate count, device/well count,
  interior positions analyzed, edge positions excluded, CTB-positive counts or
  rates, and failure criteria.
- [ ] Add microscope acquisition details and analysis/statistics methods for
  Figure 4 plots, including the source of N, ICC, and significance labels.
- [ ] Decide whether the prior-art comparison should be main Table 1 or remain
  Supplementary Table S2; avoid keeping duplicate table sources.

## Figure-specific remaining edits

- [ ] Decide whether Figure 3 should remain a photo composite with the
  post-mold schematic as a supporting/generated panel, or be redesigned as a
  two-lane "one-time mold fabrication / repeated device assembly" workflow.
- [ ] Add or verify panel labels, arrows, and material labels on the Figure 3
  photo composite.
- [ ] If Figure 5 remains in the main text, keep its caption explicit that the
  myelination and axon-guidance designs are generated design-file examples,
  not fabricated or biologically validated devices.

## Supplement-specific remaining edits

- [ ] Fill any local cleanroom-specific values missing from Supplementary
  Protocol S2, especially resin printer exposure/wash/post-cure settings and
  any measured lateral registration data if available.
- [ ] Confirm Protocol S1 still matches the lab's current bench protocol after
  the 1 h PDMS cure and frame-sterilization edits.
- [ ] Add source-data paths for pin-height, Figure 4 measurements, dye-retention
  images, and culture replicate metadata.
