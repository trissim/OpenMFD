# Figure Plan

This file maps the current manuscript figures to source assets and generated outputs.

## Main Figure Order

1. OpenMFD design-to-device overview
2. Insert-array registration and wafer bonding
3. Hybrid mold, PDMS casts, and packaged device
4. Combined validation: fluidic isolation, neuronal culture, and CTB tracing
5. Platform generalizability across published device geometries

The previous workflow overview slide is no longer part of the main figure sequence. Keep `papers/mfd_platform/figures/final_drop/Fig1_workflow/` as an optional graphical-abstract or supplementary source if needed.

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

- **Purpose:** Show non-stretched equal-scale insert-lock registration, source-derived skirt/glue footprint, source-derived bonding-stack geometry, transfer/clamp photographs, glued interface, and real SUEX lock micrograph after Figure 1 establishes the generated outputs.
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
- **Status:** Reproducible generated composite. It uses actual single-insert STL projection, actual top-layer DXF lock geometry, source-derived skirt/insert/pin/platform dimensions, equal-aspect XY rendering, bonding fixture photographs, and interface micrographs.

### Figure 3. Hybrid mold, PDMS casts, and packaged device

- **Purpose:** Show the finished hybrid mold, representative PDMS casts, parallel casting, and framed plate-format assembly.
- **Source assets:** `papers/mfd_platform/figures/final_drop/Fig4_mold_casts_package/`
- **Generated post-mold assembly panel:** `papers/mfd_platform/figures/final_drop/Fig4_mold_casts_package/assembly_protocol_schematic.pdf` from `papers/mfd_platform/figures/generate_device_assembly_protocol.py`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/mold_casts_package.pdf`
- **Status:** Current composite supports the mold-to-device transition after the insert-bonding figure.

### Figure 4. Combined platform validation

- **Purpose:** Show fluidic isolation behavior, long-term neuronal culture, endpoint CTB tracing, and plate-level cell metrics.
- **Source assets:** `papers/mfd_platform/figures/final_drop/Fig5_plate_layout_validation/`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/validation.pdf`
- **Status:** Current merged validation slide supports the primary engineering and biological validation claims.

### Figure 5. Platform generalizability across published geometries

- **Purpose:** Show that the same design-rule and hybrid-mold workflow can be applied beyond the validated compartmentalized neuron device.
- **Generated source:** `papers/mfd_platform/figures/generate_generalizability_figure.py`
- **Generated input assets:**
- `designs/open_chamber/openmfd_legacy_ports/myelination/*_single_top.dxf`
- `designs/open_chamber/openmfd_legacy_ports/myelination/*_single_bottom.dxf`
- `designs/open_chamber/openmfd_legacy_ports/myelination/*_aligned.dxf`
- `designs/open_chamber/openmfd_legacy_ports/myelination/*_single_insert.scad`
- `designs/open_chamber/openmfd_legacy_ports/myelination/*_wells_insert.scad`
- `designs/open_chamber/openmfd_legacy_ports/myelination/wall_*.scad`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/*_single_top.dxf`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/*_single_bottom.dxf`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/*_aligned.dxf`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/*_single_insert.scad`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/*_wells_insert.scad`
- `designs/open_chamber/openmfd_legacy_ports/axon_guidance/wall_*.scad`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/generalizability.pdf`
- **Status:** Current figure is generated from the same plotting/file-rendering infrastructure as Figure 1 and now uses the new legacy open-chamber DXF outputs plus generated insert/wall preview meshes directly.

## Supplementary Figures

### Supplementary Figure S1. No-LP360 ridge artifact failure mode

- **Best current asset:** `papers/mfd_platform/figures/drafts/molds/nolp360filter.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S1_LP360_filter.md`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/supp_fig_s1_no_lp360.pdf`

### Supplementary Figure S2. SU-8 delamination without flood-exposed base layer

- **Best current assets:**
- `papers/mfd_platform/figures/drafts/molds/delamination1.png`
- `papers/mfd_platform/figures/drafts/molds/delamination2.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S2_base_layer_adhesion.md`
- **Rendered asset:** `papers/mfd_platform/figures/rendered/supp_fig_s2_delamination.pdf`
