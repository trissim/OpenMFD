# Figure Plan

This file maps the current manuscript figures to existing assets in the repository and highlights what still needs to be assembled or generated.

## Recommended main-figure order

The manuscript currently references figures out of numerical order (`Figure 7` appears before `Figure 5`, and `Figure X` is still unresolved). A cleaner final order would be:

1. Workflow overview
2. Insert design and lock-and-key registration
3. Bonding fixture and adhesive workflow
4. Hybrid mold, PDMS casts, and packaged device
5. Combined validation: plate-format layout, fluidic isolation, neuronal culture, and CTB tracing
6. Platform generalizability across published device geometries

## Main figures

### Figure 1. Workflow overview
- **Purpose:** End-to-end concept figure: OpenMFD design -> SU-8/SUEX fabrication -> resin inserts -> wafer bonding -> parylene -> PDMS casting -> framed device.
- **Best current asset:** `papers/mfd_platform/figures/drafts/molds/casting.png`
- **Status:** Usable as a draft, but likely needs panel labels and cleaner schematic composition.

### Figure 2. Insert design and lock-and-key registration
- **Purpose:** Show how the insert pin, SU-8 hole, and clearance budget work.
- **Existing source assets:**
  - `designs/open_chamber/2_compartment_96_well_300um_v12/2_compartment_96_well_300um_v12_single_aligned.dxf`
  - `designs/open_chamber/2_compartment_96_well_300um_v12/2_compartment_96_well_300um_v12_wells_insert.stl`
- **Current manuscript-linked image:** `papers/mfd_platform/figures/drafts/molds/clamp_assembly.jpg`
- **Status:** Not really finished. This is one of the most genuinely missing main figures because the paper wants a CAD/geometry figure, not just a photo.

### Figure 3. Bonding fixture and adhesive workflow
- **Purpose:** Show the detachable build plate, clamp stack, insert transfer, and epoxy interface.
- **Best current assets:**
  - `papers/mfd_platform/figures/drafts/molds/clamp_assembly.jpg`
  - `papers/mfd_platform/figures/drafts/molds/clamp_assembly_seperated.jpg`
- **Status:** Mostly present; likely just needs panel layout, labels, and a final caption.

### Figure 4. Hybrid mold, PDMS casts, and packaged device
- **Purpose:** Show the finished hybrid mold and representative PDMS output.
- **Best current asset:** `papers/mfd_platform/figures/drafts/molds/SUEX.jpg`
- **Helpful additional assets:**
  - `papers/mfd_platform/figures/drafts/pics/4x_brightfield.png`
  - `papers/mfd_platform/figures/drafts/pics/10x_bright_field.tif`
- **Status:** Partly present; likely needs one clean wide shot plus one or two close-ups.

### Figure 5. Combined platform validation
- **Purpose:** Show microtiter-style packaging, expected fluidic isolation behavior, long-term neuronal culture, and endpoint CTB tracing in one integrated validation figure.
- **Best current assets:**
  - `papers/mfd_platform/figures/final_drop/Fig5_plate_layout_validation/draft_figure.odp`
  - Supporting source assets in `papers/mfd_platform/figures/final_drop/Fig5_plate_layout_validation/`
- **Status:** The merged validation slide now looks like the correct primary Figure 5 candidate. It combines the dye-retention test, brightfield imaging, fluorescence panels, and plate-level cell metrics in one composite.

### Figure 6. Platform generalizability across published geometries
- **Purpose:** Show that the platform extends beyond the validated compartmentalized neuron device by supporting two additional literature-derived geometries.
- **Existing source assets:**
  - Myelination device: `designs/open_chamber/gradient_layout/devices_myelination_multi_device.dxf`
  - Related myelination STL / insert geometry
  - Guidance device: `designs/open_chamber/gradient_layout/devices_gradient_multi_device.dxf`
  - Related guidance STL / insert geometry: `designs/open_chamber/gradient_layout/2compartment_96_well_inserts_v9_1000um/wall_2_compartment_96_well_1000um.stl`
  - Draft slide: `papers/mfd_platform/figures/final_drop/Fig6_generalizability/draft_figure.odp`
- **Status:** The current slide already supports the intended claim well. It likely only needs caption alignment and light visual cleanup, plus explicit DXF/STL pairing if you want the figure to emphasize full design-to-fabrication generalizability.

## Supplementary figures

### Supplementary Figure S1. No-LP360 ridge artifact failure mode
- **Best current asset:** `papers/mfd_platform/figures/drafts/molds/nolp360filter.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S1_LP360_filter.md`
- **Status:** The image likely exists already; it mainly needs insertion and optional quantitation.

### Supplementary Figure S2. SU-8 delamination without flood-exposed base layer
- **Best current assets:**
  - `papers/mfd_platform/figures/drafts/molds/delamination1.png`
  - `papers/mfd_platform/figures/drafts/molds/delamination2.png`
- **Target note:** `papers/mfd_platform/supplementary/Supplementary_Note_S2_base_layer_adhesion.md`
- **Status:** The image likely exists already; it mainly needs insertion.

## What is actually missing vs already available

### Already available enough to assemble now
- Figure 1
- Figure 3
- Figure 4
- Most of Figure 5
- Supplementary Figures S1-S2

### Still needs real figure generation or composition work
- Figure 2: CAD-based lock-and-key figure
- Figure 6: DXF/STL generalizability composite

## Practical next steps

1. Renumber the manuscript figures in order of appearance.
2. Build Figure 2 and Figure 6 from existing DXF/STL outputs.
3. Rebuild Figure 5 so the panel content matches the merged validation story.
4. Insert the existing defect images into Supplementary Figures S1 and S2.
