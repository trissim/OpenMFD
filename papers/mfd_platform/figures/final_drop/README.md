# Final Figure Drop Folder

Put final or near-final figure assets into the subfolders here.

Preferred convention for each main figure folder:
- keep the editable slide as `draft_figure.odp`
- keep or generate the sidecar export as `draft_figure.pdf`
- the render script will prefer `draft_figure.pdf` when present and will regenerate it from `draft_figure.odp` when needed

Recommended figure order in the manuscript:

1. `Fig1_workflow`
2. `Fig2_insert_alignment`
3. `Fig3_bonding_fixture`
4. `Fig4_mold_casts_package`
5. `Fig5_plate_layout_validation`
6. `Fig6_generalizability`
7. `Supp_FigS1_noLP360`
8. `Supp_FigS2_delamination`

Current recommendation: use one major validation figure rather than separate engineering and CTB figures.

That means:
- put both the 3-day dye test and the CTB demonstration in `Fig5_plate_layout_validation`
- use `Optional_split_ctb_overflow` only if you later split the biology back out again
- renumber the manuscript afterward so generalizability follows the merged validation figure

For that panel, dump:
- a day 0 image
- a day 3 image
- any merged 488/568 image
- any annotation showing that Alexa 488 slowly leaks one way while 568 does not

Short mapping:
- `Fig1_workflow`: overview schematic of the whole process
- `Fig2_insert_alignment`: CAD / DXF / STL views of the lock-and-key insert geometry
- `Fig3_bonding_fixture`: clamp fixture, exploded bonding setup, epoxy interface
- `Fig4_mold_casts_package`: mold photos, PDMS cast photos, packaged framed device
- `Fig5_plate_layout_validation`: whole-device brightfield, routing/layout view, dye isolation / leak test, neuronal culture, axon extension, CTB retrograde tracing
- `Fig6_generalizability`: two additional distinct literature-derived devices shown as DXF + STL outputs beyond the validated compartmentalized platform
- `Optional_split_ctb_overflow`: optional overflow folder only if you later split the biology back out
- `Supp_FigS1_noLP360`: ridge artifact failure image
- `Supp_FigS2_delamination`: SU-8 delamination failure image(s)
