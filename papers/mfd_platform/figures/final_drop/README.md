# Final Figure Drop Folder

Put final or near-final figure assets into the subfolders here.

Preferred convention for each main figure folder:
- keep the editable slide as `draft_figure.odp`
- keep or generate the sidecar export as `draft_figure.pdf`
- the render script will prefer `draft_figure.pdf` when present and will regenerate it from `draft_figure.odp` when needed

Current main-figure order in the manuscript:

1. `Fig1_openmfd_design` -> `figures/rendered/openmfd_design.pdf`
2. `Fig2_insert_bonding` -> `figures/rendered/insert_bonding.pdf`
3. `Fig4_mold_casts_package` -> `figures/rendered/mold_casts_package.pdf`
4. `Fig5_plate_layout_validation` -> `figures/rendered/validation.pdf`
5. `Fig6_generalizability` -> `figures/rendered/generalizability.pdf`
6. `Supp_FigS1_noLP360` -> `figures/rendered/supp_fig_s1_no_lp360.pdf`
7. `Supp_FigS2_delamination` -> `figures/rendered/supp_fig_s2_delamination.pdf`

Current recommendation: use one major validation figure rather than separate engineering and CTB figures.

That means:
- put both the 3-day dye test and the CTB demonstration in `Fig5_plate_layout_validation`
- use `Optional_split_ctb_overflow` only if you later split the biology back out again
- keep the old `Fig1_workflow` slide out of the main sequence unless it becomes a graphical abstract or supplementary overview

For that panel, dump:
- a day 0 image
- a day 3 image
- any merged 488/568 image
- any annotation showing that Alexa 488 slowly leaks one way while 568 does not

Short mapping:
- `Fig1_openmfd_design`: OpenMFD preset, actual photomask DXFs, actual wafer-mask DXF, generated insert STLs, generated frame STL, and assembled-device photo
- `Fig2_insert_bonding`: transfer photo, non-stretched equal-scale insert-lock/skirt detail, bonding stack, clamped-fixture photo, glued interface, and real SUEX lock micrograph
- `Fig4_mold_casts_package`: mold photos, PDMS cast photos, packaged framed device; rendered as main Figure 3
- `Fig5_plate_layout_validation`: whole-device brightfield, routing/layout view, dye isolation / leak test, neuronal culture, axon extension, CTB retrograde tracing; rendered as main Figure 4
- `Fig6_generalizability`: two additional distinct literature-derived devices shown as DXF + STL outputs beyond the validated compartmentalized platform; rendered as main Figure 5
- `Fig1_workflow`: retired main-figure source; optional graphical abstract or supplementary overview
- `Fig2_insert_alignment`: retired generated source; its OpenMFD and insert STL panels moved to `Fig1_openmfd_design`
- `Fig3_bonding_fixture`: retired generated source folder used only for existing bonding photos; the active generated composite is `Fig2_insert_bonding`
- `Optional_split_ctb_overflow`: optional overflow folder only if you later split the biology back out
- `Supp_FigS1_noLP360`: ridge artifact failure image
- `Supp_FigS2_delamination`: SU-8 delamination failure image(s)
