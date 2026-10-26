# Figure Plan

This file maps the current manuscript figures to source assets and generated outputs.

## Main Figure Order

1. OpenMFD design-to-device overview
2. Insert-array registration and wafer bonding
3. Post-mold device replication and assembly
4. Combined validation: directional fluidic bias and distal CTB uptake
5. Platform generalizability across published device geometries

The previous workflow overview slide is no longer part of the main figure sequence. Keep `papers/mfd_platform/figures/final_drop/Fig1_workflow/` as an optional graphical-abstract or supplementary source if needed.

## Shared authoring and print layout

Figures 1, 2 and 5 are authored at 6.5 inches wide and placed at that width. `TextStyle` in `generate_openmfd_design_figure.py` owns 8.5 pt details and drawing; `HeadingText` supplies 10.5 pt headings. Coordinate and label behavior are inherited rather than recovered from role enums and lookup tables. Panel letters use plain ink without boxes, and headers sit above their content. Figure 5 uses less row whitespace while preserving useful panel size and geometry. The parameter panel spans Figure 1's top row so its labels and values have room.

`Photo.read()` owns file lifetime. `CroppedContrastPhoto` composes cropping followed by the existing 1% autocontrast; the assembled-device photo uses contrast without cropping. For all five source images, processed RGB pixel arrays match the preceding crop/contrast implementation exactly; figure placement and resampling change with the layout. PDF exports retain 600 dpi raster content; composite PNGs use 300 dpi. Shared panel export hides adjacent panels while cropping and does not delete unrelated files.

`DxfPanel` and `InsertPanel` own Figure 5's drawing procedures. Labeled main panels compose these with `LabeledPanel`; clean subfigures use the same content procedures without labels. The unused alternative mesh reconstruction and frame-only rendering path have been removed. CAD files and biological count/validation assets are unchanged.

## Main Figures

### Figure 1. OpenMFD design-to-device overview

- **Purpose:** Show that one editable OpenMFD preset generates matched photomask DXFs, insert STLs, package/frame CAD, wafer-scale masks, and a real assembled plate-format device from shared geometry.
- **Generated source:** `papers/mfd_platform/figures/generate_openmfd_design_figure.py`
- **Generated input assets:**
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_single_top.dxf`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_single_bottom.dxf`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_aligned.dxf`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_single_insert.stl`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_wells_insert.stl`
- `plates/96_well_plate_reservoirs_print_hips_2/96_well_plate_reservoirs_print_hips_2.stl`
- assembled-device photograph source: `papers/mfd_platform/figures/final_drop/Fig1_openmfd_design/assembled_device_photo.png`
- `openmfd.devices.presets.TwoCompartmentDeviceConfig`
- **Rendered assets:**
- `papers/mfd_platform/figures/final_drop/Fig1_openmfd_design/draft_figure.pdf`
- `papers/mfd_platform/figures/rendered/openmfd_design.pdf`
- `papers/mfd_platform/figures/rendered_docx/openmfd_design.png`
- **Status:** Reproducible generated overview backed by actual v27 SUEX-200 DXF/STL outputs, package STL output, the current preset defaults, and an existing assembled-device photo.

### Figure 2. Insert-array registration and wafer bonding

- **Purpose:** Show non-stretched equal-scale pin–alignment-hole registration, source-derived skirt/glue footprint, source-derived bonding-stack geometry, transfer/clamp photographs, glued interface, and real SUEX alignment-hole micrograph after Figure 1 establishes the generated outputs.
- **Generated source:** `papers/mfd_platform/figures/generate_bonding_fixture_figure.py`
- **Input assets:**
- `papers/mfd_platform/figures/final_drop/Fig3_bonding_fixture/clamp_assembly.jpg`
- `papers/mfd_platform/figures/final_drop/Fig3_bonding_fixture/clamp_assembly_seperated.jpg`
- `papers/mfd_platform/figures/final_drop/Fig2_insert_bonding/glued.png`
- `papers/mfd_platform/figures/final_drop/Fig2_insert_bonding/real_suex.png`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_single_insert.stl`
- `designs/open_chamber/2_compartment_96_well_300um_suex200_v27/*_single_top.dxf`
- `openmfd.devices.presets.TwoCompartmentDeviceConfig`
- **Rendered assets:**
- `papers/mfd_platform/figures/final_drop/Fig2_insert_bonding/draft_figure.pdf`
- `papers/mfd_platform/figures/rendered/insert_bonding.pdf`
- `papers/mfd_platform/figures/rendered_docx/insert_bonding.png`
- **Status:** Reproducible generated composite. It uses actual single-insert STL projection, actual top-layer DXF alignment-hole geometry, source-derived skirt/insert/pin/platform dimensions, equal-aspect XY rendering, bonding fixture photographs, and interface micrographs.

### Figure 3. Post-mold device replication and assembly

- **Purpose:** Show the repeated nine-panel workflow from a completed hybrid mold to a framed, plasma-cleaned PDMS device, including rack-based degassing and curing, paper-guillotine trimming, glass bonding and autoclaving, and subsequent inverted frame assembly.
- **Generated source:** `papers/mfd_platform/figures/generate_device_assembly_protocol.py`
- **Primary source asset:** `papers/mfd_platform/figures/final_drop/Fig4_mold_casts_package/assembly_protocol_schematic.pdf`
- **Supporting photo composite retained in source folder:** `papers/mfd_platform/figures/final_drop/Fig4_mold_casts_package/draft_figure.pdf`
- **Rendered assets:** `papers/mfd_platform/figures/rendered/mold_casts_package.pdf` and `papers/mfd_platform/figures/rendered_docx/mold_casts_package.png`.
- **Layout:** Author at 6.5 × 6.2 inches and place at 6.5 inches wide. Headings are 10.5 pt; process details and annotations are 8.5 pt. Both output formats use the declared 720 dpi for raster content.
- **Implementation:** Each `Step` owns its scene and annotations. Shared mold views and loaded-rack geometry are inherited; the declared protocol sequence determines numbering and placement. The common Blender renderer fits the physical axes frame, not its normalized coordinate ratio.
- **Status:** The generated schematic is the main figure. The earlier photo composite remains available as supporting fabrication documentation.

### Figure 4. Combined platform validation

- **Purpose:** Show the qualitative directional dye-bias test, endpoint CTB tracing, and descriptive plate-level CTB-positive soma counts.
- **Source assets:** `papers/mfd_platform/figures/final_drop/Fig5_plate_layout_validation/`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/validation.pdf`
- **Status:** Frozen September15 published A-C composite, with two CTB views and a bar plot labeled69. The October authored source has three views and67 included devices; it is not the published figure. The published bars also disagree with the retained pre-count summaries, so changing the inclusion total alone cannot reconcile them. The publication declaration retains and verifies the existing PDF/PNG pair without running the validation producer. Measurement source and endpoint-specific inclusion still require author confirmation; neither version is scientifically accepted.

### Figure 5. Platform generalizability across published geometries

- **Purpose:** Show matching generated photomasks and insert arrays for myelination, axon-guidance and three-compartment layouts. These are design-generation examples.
- **Generated source:** `papers/mfd_platform/figures/generate_generalizability_figure.py`
- **Generated input assets:**
- `designs/open_chamber/openmfd_legacy_ports/myelination/`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/`
- `designs/open_chamber/openmfd_legacy_ports/three_compartment/`
- Each directory supplies single-device, plate-layout and wafer-scale top/bottom DXFs plus the single-insert STL. The array preview repeats the retained single-insert mesh at the declared grid positions with the existing PDMS scale correction.
- **Rendered asset:** `papers/mfd_platform/figures/rendered/generalizability.pdf`
- **Status:** Generated from retained DXF/STL assets through the shared typography and panel owners. The main figure shows mask and insert outputs; it does not show frame renderings or fabricated additional devices.

## Supplementary Figures

### Supplementary Figure S1. LP360 filtering reduces surface ridges

- **Best current asset:** `papers/mfd_platform/figures/drafts/molds/nolp360filter.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S1_LP360_filter.md`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/supp_fig_s1_no_lp360.pdf`

### Supplementary Figure S2. SU-8 delamination before adding the pre-SUEX bake

- **Best current assets:**
- `papers/mfd_platform/figures/drafts/molds/delamination1.png`
- `papers/mfd_platform/figures/drafts/molds/delamination2.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S2_base_layer_adhesion.md`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/supp_fig_s2_delamination.pdf`

### Supplementary Figure S3. Apparent microchannel widths

- **Source pair:** `final_drop/Fig5_plate_layout_validation/channel_widths.pdf` and `.png`.
- **Target note:** `supplementary/Supplementary_Note_S3_apparent_channel_widths.md`.
- **Published pair:** `rendered/channel_widths.pdf` and `rendered_docx/channel_widths.png`.
- **Publication owner:** `AuthoredFigure` publishes the existing pair; it has no executable producer. `GeneratedFigure` shares its source/copy behavior but adds regeneration only for the four declared design/casting producers.
- **Data:** Supplementary Data S4 supplies all nine apparent widths from three devices, native pixel coordinates/calibration, image crops and their bounds. The bounds are a reader projection of the existing `WidthCrop` records, not new measurements.
- **Scope:** Retained planar wall-band-centre observations, not channel depth, complete cross-sectional metrology or a fresh CTB analysis. Figure 4 stays frozen.
