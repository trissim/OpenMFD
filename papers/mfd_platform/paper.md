# Hybrid SU-8 + resin-insert molding enables microtiter-plate-format PDMS microfluidics without manual punching (working title)

**Authors:** Tristan Simas, Yonatan Morocz, David Juncker, and Alyson Fournier  
**Affiliations:** McGill University  
**Corresponding author:** Tristan Simas

## Abstract
High-throughput microfluidic screening remains difficult for many academic labs. While microfluidic devices enable spatial compartmentalization and precise microenvironment control that are not readily achieved in standard multi-well plates, scaling these assays to 96-well format has generally required either commercial platforms or fabrication methods not commonly available in academic cleanrooms. The barrier is multiscale: cellular assays require micron-scale channels, but automation-compatible wells demand millimeter-scale features, a combination that standard SU-8 photolithography cannot efficiently produce and that often leads to manual well punching.

Here we present a hybrid mold-fabrication method that combines (i) SU-8 photolithography for fine microfeatures with (ii) adhesively bonded, resin 3D-printed well inserts for tall macrofeatures. Mold fabrication requires cleanroom access for photolithography, but the remaining steps (resin printing, insert bonding, PDMS casting, and device assembly) use standard benchtop laboratory equipment. Using low-cost resin printing, low-viscosity epoxy bonding, and a lock-and-key alignment scheme, we integrate millimeter-to-centimeter-tall wells with micrometer-scale SU-8 features on a single wafer mold. Wells are formed during PDMS casting rather than by post-processing, which removes the manual punching step and allows fabrication of 96-well-format versions of established microfluidic assays. The platform is compatible with automation, liquid handling, and higher-replicate experimental designs. We also provide an open-source layout generator (OpenMFD) that automates design-rule encoding and fabrication file generation. As a demonstration, we fabricate and validate a 96-well-format compartmentalized neuronal culture platform that supports long-term axon extension and retrograde cholera toxin B tracing.

## Introduction
Microfluidic devices enable experimental capabilities in cellular biology that are not readily achieved in standard multi-well plates, including spatial compartmentalization of cell populations, localized chemical perturbations, fluidic isolation of subcellular compartments, and controlled microenvironments for studying cell migration, differentiation, co-culture interactions, and responses to gradients. Decades of work have produced literature-validated device architectures for applications across neuroscience, stem cell biology, cancer research, immunology, and developmental biology (Taylor et al., 2005; Taylor et al., 2015; Wang et al., 2018; Coquinco et al., 2014), and several low-throughput designs are now commercially available (Xona Microfluidics, Ananda Devices). High-throughput plate-format versions also exist, but they are often too costly for routine academic use. In academic settings, most available platforms still provide only 1-4 independent culture chambers per device, require manual liquid handling, and are not readily compatible with multichannel pipettes, liquid-handling robots, or plate-format imaging systems.

The barrier is not conceptual but practical: the device geometries already exist, but fabrication at plate format remains difficult. Academic labs can fabricate low-throughput PDMS devices (1-4 chambers) using standard soft lithography, but scaling to 96-well format has typically required either (i) commercial platforms that offer limited design flexibility or (ii) hard-plastic microfabrication methods such as hot embossing, CNC milling, or injection molding that rely on specialized equipment not commonly available in university cleanrooms. This fabrication gap limits the ability of academic groups to perform replicate-rich studies, dose-response screens, and automated imaging workflows with custom microfluidic devices. Dependence on commercial platforms also limits the ability to modify existing designs or develop assay geometries tailored to specific biological questions.

The core fabrication challenge is multiscale: cellular microfluidic assays often require microchannels and barriers on the order of a few to tens of micrometers, while robust, pipette-accessible wells demand millimeter-scale depth and volume. SU-8 photolithography reliably yields micron-scale structures, but creating millimeter-tall, large-area wells in SU-8 is difficult and often replaced by manual punching of cured PDMS. Alternative approaches (e.g., laser ablation of PDMS, hot embossing + CNC-milled well layers, direct 3D printing of molds, or modular inserts) either trade away fine resolution, require specialized equipment, or introduce substantial time and alignment burden.

Table 1 summarizes representative strategies to combine micro-scale features with millimeter-scale wells/structures and highlights the trade-offs that motivate a plate-format, “no-punch” PDMS workflow.

**Table 1. Prior art: multiscale microfluidic fabrication strategies (microfeatures + tall wells).**

| Approach | Micro-scale features | Macro wells / tall structures | Plate / automation compatibility | What it typically costs you | Representative refs |
|---|---|---|---|---|---|
| Conventional PDMS soft lithography + manual punching | SU-8 photolithography (µm-scale channels) | Biopsy punch after casting | Limited by manual post-processing; punching becomes the throughput bottleneck | Manual labor, variability, edge defects, hard to scale to 96-well | (baseline approach; see e.g., Taylor et al., 2005) |
| CO₂ laser micromachining of PDMS | Maskless laser ablation; practical widths generally >100 µm | Laser-ablated reservoirs/wells/channels | Serial process; not ideal for dense plate arrays | Limited resolution and non-ideal cross-sections; thermal artifacts | Holle et al., 2007 |
| Micro–macro hybrid master via milling + hot embossing | Hot embossing for microfeatures | PMMA milled macrostructures (mm-scale) | Can replicate PDMS masters in quantity (not inherently plate-format) | Requires hot embosser + milling; multi-master workflow | Park et al., 2010 |
| Thick SU-8 molding + photolithography (single material) | Photolithography on molded SU-8 surface | Millimeter structures molded from 3D-printed master via PDMS mold | Demonstrated as micro-to-mm “seamless” structures (not plate workflows) | Surface roughness can degrade lithography; multi-step SU-8 handling | Tamura & Suzuki, 2019 |
| Direct 3D printing of PDMS onto photolithographic master (“printed soft lithography”) | Photolithographic master for microchannels | Printed PDMS walls/compartments | Removes punching for certain architectures; not inherently microtiter plate-format | Requires PDMS-printing hardware (bioprinter/extrusion) and ink tuning | Kajtez et al., 2020 |
| Aligned SLA printing onto patterned chips | SU-8 lithography on diced chips | SLA-printed micro/macro 3D features | Chip-scale alignment; not wafer-scale or plate-scale workflows | Requires dicing + alignment fixtures; first-layer overcure effects | Pan et al., 2022 |
| 3D-printed inserts bonded to SU-8 (lock-and-key) | SU-8 photolithography for microfeatures | Tall 3D-printed inserts + epoxy bonding | Works for open reservoirs; scaling limited by manual insert handling | Metal printing cost/availability; manual placement effort | Ristola et al., 2019 |
| Hard-plastic microtiter microfluidic plates (industrial) | Hot-embossed microchannels in COC | CNC-milled wells/compartments + fusion bonding | ANSI/SLAS compatible; automation-friendly | Requires specialized tooling/processes; not typical academic fab | Moll et al., 2024 |
| Commercial microfluidic titer plates (proprietary) | Proprietary | Proprietary | High-throughput, plate footprint | Limited design freedom; cost; opaque fab details | Spijkers et al., 2021 (OrganoPlate) |
| **This work: wafer-bonded resin well inserts + SU-8 microfeatures (with OpenMFD design rules)** | SU-8/SUEX photolithography for µm-scale microfeatures | Resin-printed well inserts adhesively bonded to wafer mold; wells formed during casting (no punching) | ANSI/SLAS footprint; demonstrated with HCS imaging + autofocus (Opera Phenix, ImageXpress) | Requires reliable bonding workflow + final mold insulation (e.g., parylene coating) | **This work** |

In this work, we address this multiscale fabrication bottleneck by integrating resin-printed well inserts onto an SU-8 wafer mold via adhesive bonding and mechanical self-alignment. The resulting hybrid mold produces PDMS devices with wells cast in place while preserving fine SU-8-defined microfeatures. The fabrication method is not limited to a single assay type: any microfluidic geometry that can be patterned in SU-8 can in principle be combined with 3D-printed well arrays to create plate-format devices. Because the technique introduces plate-format constraints (insert alignment features, keep-out zones, tiling, and standardized footprints), we provide an accompanying open-source Python layout generator (OpenMFD) to encode these design rules and generate fabrication-ready layouts. While we demonstrate the platform using a neuroscience application (compartmentalized neuronal culture and axon tracing), the approach is also compatible with assays requiring spatial compartmentalization, gradient generation, co-culture, or other controlled microenvironments.

![Figure 1: Plate-format microfluidic culture concept. Left: compatibility with multichannel liquid handling. Center: framed 96-well-format device assembly. Right: representative compartmentalized neuronal culture readout.](figures/rendered/workflow.pdf)

## Materials and Methods
### Design automation (open-source Python layout generator)
OpenMFD: an open-source Python layout generator for plate-format microfluidics and hybrid molds (`https://github.com/trissim/OpenMFD`).

OpenMFD provides parameterized geometric primitives (wells, chambers, channels), array/tiling utilities, and multi-layer alignment marks for plate-format PDMS microfluidics. The software generates fabrication outputs for both parts of the platform: (i) photolithography masks for SU-8/SUEX microfeatures and (ii) CAD for 3D-printed well inserts used to form tall wells without punching.

OpenMFD represents geometry as OpenSCAD models (via SolidPython) and supports export to:
- **OpenSCAD (`.scad`)** for inspection and as an intermediate format
- **DXF (`.dxf`)** for photomask printing (via OpenSCAD CLI conversion with DXF normalization using `ezdxf`)
- **STL (`.stl`)** for 3D printing and visualization (via OpenSCAD/viewscad tooling)

Layer separation is handled by exporting separate geometries for each fabrication layer (e.g., channel layer vs well/chamber layer), with corresponding **full vs hollow alignment marks** to support multi-layer registration. Features related to insert alignment are represented both as 3D insert geometry (pins, skirts, tapers) and as matching “lock” features (e.g., square holes) in the photolithographic layer(s).

### SU-8 fabrication of microfeatures
We fabricate fine microfeatures using a three-layer negative photoresist stack consisting of two thin SU-8 2005 layers (MicroChem) and a thick SUEX K200 dry-film layer (DJ MicroLaminates). Unless otherwise noted, processing steps for SU-8 2005 follow the manufacturer’s recommendations for a 5 µm target thickness.

Microchannels and thin well-rim features are patterned in SU-8 using standard photolithography on silicon wafers. Alignment marks are included for later lock-and-key registration with the 3D-printed inserts.

**Layer 1 (base):** SU-8 2005, 5 µm. The resist is flood-exposed (no mask) and is not developed. This layer serves as an adhesion promoter: without it, thin SU-8 microchannel features patterned directly on bare silicon can delaminate from the wafer surface during development or subsequent processing (Supplementary Note S2).

**Layer 2 (microchannels):** SU-8 2005, 5 µm. The resist is exposed through a photomask defining the microchannel layer, followed by development.

**Layer 3 (tall SU-8/SUEX features):** SUEX K200 (dry film, DJ MicroLaminates), 200 µm. Exposure is performed through a 360LP filter at a dose of 2800 mJ/cm². Post-exposure bake (PEB) is performed in an oven by ramping from room temperature to 50°C at 1°C/min, holding at 50°C, then ramping down by powering off the oven. Development is performed by submerging the wafer in developer and mixing for 20 min, with a developer exchange at 15 min. A hard bake is then performed by ramping from room temperature to 180°C at 3°C/min, holding for 30 min, and ramping down by powering off the oven.

We use 6" silicon wafers (UniversityWafer, ID857). SU-8 2005 is sourced from Kayaku Advanced Materials, and SUEX K200 (6") is sourced from DJ MicroLaminates. SU-8 layers are spin-coated using a Laurell WS-650-8B spin coater, and SUEX K200 is laminated using an SK 335R6 laminator. Photomask exposure/alignment is performed using an EVG620 mask aligner. No dehydration bake or HMDS treatment is used; the flood-exposed SU-8 base layer provides sufficient adhesion for the microchannel layer without additional surface preparation.

For development of both SU-8 and SUEX layers we use propylene glycol monomethyl ether acetate (PGMEA) supplied by the facility.

Use of the LP360 long-pass filter during SUEX exposure was important for achieving a flat top surface on the SUEX features. Without the LP360 filter, we observed ridge-like edge artifacts that prevented a uniform epoxy seal when bonding the resin inserts to the wafer mold, compromising the insert-wafer interface (Supplementary Note S1).

In practice, the dominant failure modes in the photolithographic stack were (i) delamination of 5 µm SU-8 microchannel features from bare silicon, (ii) ridge-like edge artifacts that produced a non-flat SUEX top surface and prevented uniform sealing to the resin inserts, and (iii) stress-induced lifting of the thick SUEX layer during thermal processing. These were mitigated by combining a flood-exposed SU-8 base layer beneath the microchannels, LP360-filtered SUEX exposure, and slow oven ramping during both post-exposure bake and hard bake. When any of these mitigations was omitted, wafers typically failed in development or at the subsequent insert-bonding step; when used together, the SU-8/SUEX stack reproducibly yielded flat, adherent substrates suitable for hybrid mold assembly.

### Resin 3D printing of well inserts
[TODO: layer height; post-processing; dimensional compensation]

Well inserts are printed using an Elegoo Mars 3 Pro resin printer and a high-temperature resin (Siraya Tech Sculpt, Clear).

Well inserts are printed as an array such that each insert contains a protruding alignment pin (“key”). The SU-8 design contains corresponding holes (“locks”) at the intended insert locations. Insert height sets the molded well depth during PDMS casting.

![Figure 2: Lock-and-key insert registration. Left: representative 3D-printed insert showing the 1.85 × 1.85 mm alignment pin used to define well position and depth during PDMS casting. Middle: matching 2.0 × 2.0 mm wafer cavities patterned in the photolithographic layer. Right: assembled insert-wafer interface after registration, illustrating the nominal 150 µm total clearance used to accommodate fabrication variation while preserving repeatable alignment.](figures/rendered/insert_alignment.pdf)

### Insert transfer, alignment, and adhesive bonding
To avoid time-consuming manual placement of individual inserts, inserts are printed in their correct relative positions on a detachable magnetic build plate (or equivalent transfer fixture). The insert array is then transferred onto a larger bonding plate suitable for clamping against a full wafer.

Low-viscosity epoxy is applied in excess to a cavity on the underside (pin side) of each insert. The wafer is placed with SU-8 features facing the insert pins and is aligned until all pins seat into their corresponding SU-8-defined holes, providing self-alignment across the full insert array. A second flat plate is placed above the wafer, and uniform pressure is applied using clamps to spread epoxy at the insert–wafer interface.

The lock-and-key alignment is designed with 150 µm total clearance: 1.85 × 1.85 mm pins seat into 2.0 × 2.0 mm square holes (75 µm per side). This tolerance accommodates expected fabrication variation in both SU-8 photolithography and resin 3D printing while maintaining repeatable mechanical registration across the full insert array. Alignment precision is geometry-limited by the CAD-defined clearances rather than manual placement.

To compensate for measured print-to-print and across-build-area variation in insert pin height (z) (Supplementary Table S1; peak-to-peak variation 116 µm across one 8×12 array), a compliant rubber sheet is placed between the insert array build plate and the clamping surface. This compliance equalizes pressure across the array and helps ensure all pins fully seat during alignment and bonding.

We use an EPDM rubber sheet (0.03125 in thickness, 60A durometer) positioned between the fixed magnet on the clamping build plate and the removable magnetic build plate carrying the inserts. This allows locally taller inserts to sink into the rubber under clamping, helping ensure the pin bases and bonded insert–wafer interface are flat.

Before curing, the clamped assembly is immersed in acetone to remove excess epoxy that may have leaked onto the SU-8 microfeatures, then immediately blow-dried with dry air after removal from the bath. The assembly is then cured at room temperature for 48 h. We avoid elevated-temperature curing to minimize thermally induced stresses under clamping that can compromise the insert–wafer seal.

We use EPO-TEK 301-2 epoxy and follow the manufacturer’s minimum alternative cure schedule (room temperature cure) to minimize thermal stress at the bonded interface. After clamping and alignment, the assembly is submerged in an acetone bath for 1 min, followed by a second 1 min acetone wash, then dried using a dry air gun prior to curing. After the 48 h cure, the bonded insert-wafer assembly is sonicated in acetone for 10 min to remove any residual uncured epoxy that was not eliminated during the initial blow-dry step.

During insert bonding, the principal failure modes were incomplete seating of pins due to z-height variation across the printed array, nonuniform clamping at the insert-wafer interface, epoxy leakage onto the SU-8 microfeatures, and stress-induced loss of seal during cure. These were mitigated by using the lock-and-key geometry for repeatable alignment, an EPDM compliant layer to equalize pressure across inserts with up to 116 µm peak-to-peak height variation, excess low-viscosity epoxy followed by two short acetone washes before cure, and a 48 h room-temperature cure to minimize thermally induced stress. The detachable magnetic build plate also simplified post-cure release of the bonded insert array from the transfer fixture without disturbing insert alignment.

![Figure 3: Array-wise insert bonding workflow. Left: inserts printed in wafer-matched positions on the transfer plate and coated on the pin side with slow-setting epoxy. Middle: aligned and clamped insert-wafer assembly used to seat all pins simultaneously and spread epoxy at the bonded interface. Right: acetone immersion after clamping, which removes excess epoxy from the wafer surface before the 48 h room-temperature cure.](figures/rendered/bonding_fixture.pdf)

### Parylene insulation coating
After insert bonding, the assembled hybrid mold is coated with 1 µm parylene C to insulate the 3D-printed resin (and adhesive) from downstream PDMS casting and cell culture. Parylene deposition was performed using the Specialty Coating Systems (SCS) 200 parylene coater available at the McGill Nanotools Micro, Nanofabrication Facility.

[TODO: how thickness is verified (e.g., witness sample + profilometry/ellipsometry); impact on demolding lifetime]

### PDMS casting and device assembly
PDMS (Sylgard 184) is mixed at a 10:1 base:curing-agent ratio, degassed for 20 min at −15 inHg, and cured for 30 min at 100°C. PDMS is cast onto the hybrid mold such that the tall insert features define the wells during curing. Casting can be parallelized by pouring, degassing, and curing multiple molds in parallel. No silanization is used; the parylene-coated mold improves PDMS release and provides insulation. After curing and demolding, the device is bonded to a substrate (e.g., glass) following standard plasma bonding protocols.

To improve demolding reliability, macro-scale mold features should avoid vertical 90° walls; draft angles and tapered walls facilitate demolding, consistent with prior insert-assisted mold designs. During demolding, the wafer should be supported on a flat surface while applying force to reduce the risk of snapping. We typically initiate demolding from corners and progress toward the center, pulling not only upward but also backward to stretch the PDMS and reduce local peel stress.

Because PDMS shrinks at elevated curing temperatures, device geometry can be uniformly scaled to compensate; OpenMFD includes built-in support for applying a shrinkage-compensation scale factor during export.

![Figure 4: Hybrid mold use and plate-format device assembly. Top: wafer tower and rack used for parallel PDMS casting, including the mold in the curing oven. Bottom: close-up of a PDMS cast on the hybrid mold, a cut-out view of the device footprint in the mold, and final framed assembly using 3D-printed components and adhesive.](figures/rendered/mold_casts_package.pdf)

### Device trimming, framing, and final assembly (plate-format package)
To facilitate rapid, repeatable device packaging, the mold includes a rectangular cutting guide surrounding the array. After demolding, devices are trimmed to a standardized rectangular footprint using an industrial paper guillotine aligned to this guide.

The trimmed PDMS device is bonded to a 110 × 74 mm coverslip-glass sheet. The PDMS-on-glass assembly is autoclaved in sterilization pouches using a dry 121°C cycle and then mounted into a 3D-printed plastic frame. Before assembly, the frame is sterilized with 70% ethanol. Loctite 5140 is dispensed into the frame grooves (typically 0.5-1 mL per frame), and the bonded device is aligned and seated onto the adhesive interface. The adhesive is then cured at room temperature for 3 days before use, after which excess cured adhesive is trimmed away with a razor blade.

3D models for the frame are provided by OpenMFD. Among the materials evaluated for frame printing, high-impact polystyrene (HIPS; polystyrene modified with rubber) was selected because it combines low hygroscopicity with lower thermal contraction than polypropylene, the only other low-hygroscopicity filament we evaluated. HIPS is also chemically similar to the polystyrene used in standard cell-culture plasticware.

Frames are printed using a Creality K1C printer with HIPS filament (e.g., Filamentum or eSUN). To reduce frame warping during fabrication, printing is performed in an enclosure with part-cooling fans turned off and reduced print speed.

### Pre-use plasma cleaning
After Loctite curing, assembled devices are plasma-cleaned using a Harrick PDC-001 benchtop plasma system (high power; 30 W, 10 min, 400 mTorr) to further sterilize the device and render surfaces hydrophilic before coating and neuronal culture. Dry ambient air is used as the process gas to control for humidity.

### Dye-based fluidic isolation validation
To assess multi-day compartmental isolation prior to biological experiments, assembled devices were loaded with 50 µL of Alexa Fluor 488 solution in one compartment and 25 µL of Alexa Fluor 568 solution in the opposing compartment. Devices were imaged immediately after loading and again after 3 days to assess dye crossover between compartments under this imposed volume asymmetry.

### Demonstration assay: plate-format neuronal culture and axon tracing
For the main platform demonstration, assembled devices were used for compartmentalized culture of E18 Sprague Dawley rat cortical neurons followed by endpoint retrograde tracing rather than axotomy. Wells were coated with 30 µL of 10 µg/mL dPGA for 10 min and washed once with water. E18 Sprague Dawley rat cortical neurons were seeded into the soma compartment in 50 µL DMEM + 10% FBS at 5,000-10,000 cells per well, allowed to attach for at least 30 min, and then switched to supplemented Neurobasal Plus medium (1% N2, 2% B27, 1% glutamine). A 50 µL volume was maintained in the soma compartment and 25 µL in the axon compartment to preserve compartmentalization by passive fluidic isolation.

Cultures were maintained for 11 days in vitro (DIV11). To label neurons whose axons extended into the distal compartment, Alexa Fluor-conjugated cholera toxin subunit B (CTB) was applied to the axon compartment at 1 µg/mL 24 h before imaging, enabling retrograde labeling of the corresponding cell bodies. A more detailed chemical-axotomy workflow used during platform development is retained outside the main manuscript in Supplementary Protocol S1.

## Results
### Hybrid mold fabrication and well formation without punching
The hybrid mold integrates millimeter-to-centimeter-tall well structures with SU-8-defined microfeatures on a single silicon wafer mold. During PDMS casting, the wells are formed in-place by the insert macros, eliminating manual punching and associated variability.

Protocol development required identification of the main failure modes. Early attempts yielded >50 failed molds, with insert delamination, SUEX surface non-flatness that prevented epoxy sealing, or SU-8 microchannel delamination. In practice, omitting any one of the key mitigations led to nonfunctional molds, whereas applying the full protocol yielded functional devices with all wells usable.

Key mitigations identified through iterative development include: (i) LP360 long-pass filtration during SUEX exposure to eliminate ridge artifacts that compromise insert–wafer sealing (Supplementary Note S1), (ii) flood-exposed SU-8 base layer to prevent microchannel delamination during development (Supplementary Note S2), (iii) slow thermal ramping (1–3°C/min) during SUEX post-exposure bake and hard bake to prevent stress-induced delamination, (iv) compliant rubber layer in the bonding fixture to accommodate insert height variation and ensure uniform pressure distribution across the array (Supplementary Table S1), (v) detachable magnetic build plate that enables post-cure disassembly by flexing the thin magnetic sheet to release bonded inserts from the transfer fixture, and (vi) room-temperature epoxy cure to minimize thermally induced stress at the bonded interface.

Using the full protocol, three consecutive molds fabricated back-to-back all produced defect-free PDMS devices. Across these three molds, we generated >50 usable PDMS casts with no protocol-related failures. One additional mold was physically broken during demolding due to improper handling, indicating that the limiting failure mode at that stage was user technique rather than insert delamination or loss of casting fidelity. The most recent mold fabrication occurred >8 months prior to writing, and the molds remain in active use with no observable degradation.

### Throughput and automation compatibility
By integrating wells during PDMS casting rather than post-processing, the workflow removes the manual punching step. The resulting devices adopt standard microtiter plate pitch and are directly compatible with multichannel pipettes, liquid-handling robots, and plate-format imaging systems without adaptation. In practice, this shifts fabrication from serial manual post-processing to batch production of full plate-format arrays.

We verified full microplate compatibility in high-content screening workflows by imaging devices on Opera Phenix and ImageXpress HCS microscopes, where plate-reader autofocus operated reliably across all wells without modification or calibration.

We also evaluated compartmental isolation using a 3-day dye-retention test in which Alexa Fluor 488 (50 µL) and Alexa Fluor 568 (25 µL) were loaded into opposing compartments. Under these asymmetric loading conditions, Alexa 488 showed gradual one-way crossover over the 3-day interval, whereas little or no reverse transfer of Alexa 568 was observed. This behavior is consistent with a sustained directional hydrostatic bias rather than rapid bidirectional mixing and supports the use of controlled volume differences to maintain predictable compartmental isolation in the device.

### Demonstration of compartmentalized neuronal culture and retrograde axon tracing in a 96-well-format device
To demonstrate biological compatibility of the plate-format device without relying on a secondary perturbation assay, we maintained compartmentalized E18 Sprague Dawley rat cortical neuron cultures in the assembled platform for 11 days and performed endpoint retrograde tracing from the distal compartment using Alexa Fluor-conjugated CTB. Neurons remained viable over this standard culture interval and extended axons through the microchannel barrier into the distal compartment, showing that the cast-in-place wells, glass-bonded packaging, and framed plate-format assembly preserved the core function of the underlying compartmentalized device geometry.

Retrogradely labeled cell bodies were readily detected after CTB addition to the distal compartment, confirming that axons crossed compartments and remained accessible to standard tracing reagents in the packaged device. Together with the high-content screening compatibility described above, these data show that the platform can support long-term neuronal culture and endpoint imaging in a plate-format device. Detailed chemical-axotomy procedures developed on this platform are retained in Supplementary Protocol S1 but are not required for the core fabrication demonstration presented here.

The primary packaging-related failure mode was not at the mold or PDMS-device level, but at the level of the 3D-printed frame: unlike injection-molded parts, filament-printed frames were not fully airtight along the perimeter of the assembled plate. As a result, the outermost devices were not reliably insulated and showed reduced culture survival relative to interior devices during long-term culture. For this reason, we sacrificed the outer devices in biological experiments and focused analysis on the internally located culture positions.

Taken together, these engineering and biological readouts show plate-format compatibility, predictable directional fluidic isolation, long-term neuronal culture support, and compatibility with endpoint retrograde axon tracing in the packaged device (Figure 5).

![Figure 5: Combined platform validation. Top: 3-day dye-retention test under asymmetric loading (Hour 0 and Hour 72) showing gradual one-way Alexa 488 crossover with little or no reverse transfer of Alexa 568. Middle: representative brightfield, DAPI, CTB-647, and Calcein-AM imaging from the packaged device. Bottom: plate-level summary plots reporting pre-assay cell counts and total cells seeded across replicate plates.](figures/rendered/validation.pdf)

### Platform generalizability: adaptation of published microfluidic designs

To demonstrate that the hybrid mold approach extends beyond the validated compartmentalized neuronal culture platform, we used OpenMFD to adapt two additional published microfluidic architectures into 96-well-format layouts. Figure 6 shows representative plate-format layouts and assay schematics for (i) an oligodendrocyte myelination platform based on Wang et al. (2018) and (ii) an axon guidance chamber with orthogonal gradients adapted from Taylor et al. (2015). Together, these examples indicate that the method can be extended beyond the simple two-compartment device fabricated and biologically validated in this work.

For each design, OpenMFD generates the full fabrication specification, including multi-layer photomask files, 3D-printable well insert arrays with lock-and-key registration features, and optional plate-frame CAD for final assembly. The design-to-fabrication workflow requires only geometric input parameters (channel widths, chamber dimensions, well pitch); OpenMFD encodes the plate-format constraints, tolerance clearances, and hybrid mold integration features automatically.

While we focus fabrication and biological validation on a compartmentalized neuronal culture platform derived from an axon injury design, the ability to render diverse published geometries as plate-compatible layouts indicates that the approach is not device-specific. The hybrid mold fabrication protocol (SU-8 microfeatures + bonded inserts + parylene coating) is constrained primarily by the design rules outlined in the Discussion rather than by a single device geometry.

![Figure 6: Platform generalizability beyond the validated compartmentalized neuron device. Representative plate-format layouts and assay schematics for two additional literature-derived architectures: (A) oligodendrocyte myelination (Wang et al., 2018) and (B) axon guidance with orthogonal gradients (Taylor et al., 2015).](figures/rendered/generalizability.pdf)

## Discussion
The presented method addresses a key multiscale fabrication challenge in PDMS microfluidics by decoupling fine microfeature definition (SU-8) from tall macrofeature creation (3D-printed inserts). The lock-and-key alignment and array-wise transfer reduce the manual burden typically associated with modular insert approaches, and adhesive bonding enables use with low-cost, widely available resin printers.

Hybrid mold fabrication was sensitive to several specific process variables. Omitting the LP360 filter, the SU-8 base layer, slow thermal ramping, compliant rubber support, detachable magnetic fixturing, or room-temperature epoxy cure reproducibly led to failure modes such as poor SUEX flatness, microchannel delamination, incomplete insert seating, or bond loss. Once these variables were controlled, the protocol produced repeatable molds and devices. Quality control was also simplified: molds were either fully usable or failed with readily visible defects, rather than producing marginal intermediate cases.

A design goal of this platform is to support plate-format adaptations of established microfluidic assays rather than requiring de novo device development. Many proven PDMS microfluidic geometries—compartmented chambers (Taylor et al., 2005; Wang et al., 2018), gradient generators (Taylor et al., 2015), and co-culture platforms (Coquinco et al., 2014)—remain limited to low-throughput formats (1-4 independent units per device) because fabrication methods that scale to plate formats often sacrifice microfeature resolution or require expensive tooling. By decoupling fabrication scale from geometric complexity, our approach allows these literature-validated architectures to be adapted into 96-well layouts without modification to the core microfluidic geometry. OpenMFD automates this translation: published device dimensions can be provided as parameters, and the software generates both the photomask layouts and the matching well insert arrays. This allows researchers to use established device geometries while gaining throughput, automation compatibility, and additional replicate capacity.

In addition to adapting existing designs, the same workflow can also be used to modify or prototype new device layouts. Because OpenMFD translates geometric parameters into fabrication-ready files (photomasks, 3D-printable inserts, and assembly fixtures), changes to channel geometry, chamber dimensions, or array layout do not require manual redrawing of each fabrication layer. The mold fabrication workflow still requires cleanroom access for photolithography, but the downstream steps (resin printing, insert bonding, PDMS casting, plasma bonding, and device assembly) use benchtop laboratory equipment.

Although we demonstrate the platform using a neuronal compartmentalization assay, the fabrication strategy is not specific to that application. The same combination of SU-8-defined microfeatures and cast-in-place wells should also suit other compartmented or gradient-based PDMS devices, provided their layouts respect the alignment, demolding, and plate-format rules described above.

Key limitations and considerations include: (i) dimensional tolerances and resin shrinkage that affect alignment and sealing, (ii) long-term mechanical stability of the adhesive bond over repeated PDMS casting cycles, (iii) solvent compatibility and handling safety (e.g., acetone cleanup), (iv) potential constraints on channel proximity to the insert-wafer interface, and (v) incomplete airtightness of filament-printed plate frames. In the current implementation, this frame limitation reduces edge insulation during long-term culture, so outer devices are sacrificed in biological experiments. This is a limitation of the current frame-fabrication method rather than the hybrid mold-fabrication strategy itself; future work could improve edge performance by testing full-infill prints or alternative frame-manufacturing approaches.

### Design rules encoded in OpenMFD
The fabrication method imposes practical multiscale constraints that we encode in OpenMFD to reduce design ambiguity and improve reproducibility:

- **Plate-format layout and keep-outs:** Arrays are generated by tiling a unit device into microtiter-compatible footprints while respecting well pitch and edge clearances needed for handling and imaging.
- **Multi-layer alignment marks:** OpenMFD can place full and hollow alignment marks in user-selected locations to support multi-layer photolithography registration.
- **Lock-and-key insert registration:** Insert pins and matching wafer holes are defined together in CAD; the reference geometry uses 1.85 × 1.85 mm pins and 2.0 × 2.0 mm square holes (150 µm total clearance).
- **Macrofeature demolding:** Tall macro features should avoid vertical 90° walls; draft angles/tapers reduce demolding forces and reduce risk of handling failures.
- **Shrinkage compensation:** Designs can be uniformly scaled to compensate PDMS shrinkage for specific curing conditions.

[TODO: add the specific plate standard targeted (e.g., ANSI/SLAS); document the minimum tested feature sizes and any quantitative tolerance budgets used in design]

## Conclusion
This work shows that tall plate-format wells can be added to SU-8-defined PDMS devices by bonding printed inserts directly to the wafer mold, so the wells are cast in place rather than punched afterward. In the current implementation, the method produced reusable molds, supported repeated PDMS casting, and yielded framed devices that could be imaged on standard high-content plate microscopes and used for compartmentalized E18 rat cortical neuron culture with retrograde CTB tracing. OpenMFD packages the layout rules needed for this workflow so that established low-throughput geometries can be adapted to plate-format molds without redrawing each fabrication layer by hand. For labs that already work with SU-8 and PDMS, this offers a practical way to move toward plate-format devices without relying on industrial hard-plastic fabrication; the main remaining packaging limitation lies in the printed frame rather than in the mold itself.

## Code and data availability
OpenMFD (design automation, example designs, and layout-generation code): `https://github.com/trissim/OpenMFD`.

OpenMFD includes the CAD used for this platform (photomask DXFs, 3D-printed insert models, and the HIPS frame models used for plate-format assembly).

OpenMFD commit used for this manuscript: `49a0eadba19baa42d610e0c387d8f1149cd2fbfc`.

Supplementary Table S1 (pin height / z variability): `supplementary/Supplementary_Table_S1_pin_z_variability.md` (derived from raw measurements in `pin_z_variability.xlsx`).

Supplementary Protocol S1 (detailed device assembly and chemical-axotomy workflow retained outside the main manuscript): `supplementary/Protocol_S1_device_assembly_and_axotomy.md` (source: `papers/MFD_assembly_and_axotomy_assay copy.odt`).

Supplementary Note S1 (LP360 filter and SUEX flatness): `supplementary/Supplementary_Note_S1_LP360_filter.md`.

Supplementary Note S2 (base layer adhesion and microchannel delamination): `supplementary/Supplementary_Note_S2_base_layer_adhesion.md`.

[TODO: add a tagged release/commit hash used for this paper; add repository location for fabrication protocols, mask files, and analysis scripts; add Video S1 reference/link if you plan to release it]

## Acknowledgements
[TODO]

## References (working list)
- Taylor, A. M., et al. *A microfluidic culture platform for CNS axonal injury, regeneration and transport.* Nat. Methods (2005). https://doi.org/10.1038/nmeth777
- Taylor, A. M., Menon, S., Gupton, S. L. *Passive microfluidic chamber for long-term imaging of axon guidance in response to soluble gradients.* Lab Chip (2015). https://doi.org/10.1039/c5lc00503e
- Wang, Z. Z., Wood, M. D., Mackinnon, S. E., Sakiyama-Elbert, S. E. *A microfluidic platform to study the effects of GDNF on neuronal axon entrapment.* J. Neurosci. Methods (2018). https://doi.org/10.1016/j.jneumeth.2018.08.002
- Coquinco, A., et al. *A microfluidic based in vitro model of synaptic competition.* Mol. Cell. Neurosci. (2014). https://doi.org/10.1016/j.mcn.2014.03.001
- Holle, A. W., et al. *Characterization of Program Controlled CO2 Laser-Cut PDMS Channels for Lab-on-a-chip Applications.* Proc. IEEE Conf. on Automation Science and Engineering (CASE) (2007).
- Park, J., Li, J., Han, A. *Micro-macro hybrid soft-lithography master (MMHSM) fabrication for lab-on-a-chip applications.* Biomed. Microdevices (2010). https://doi.org/10.1007/s10544-009-9390-9
- Tamura, T., Suzuki, T. *Seamless fabrication technique for micro to millimeter structures by combining 3D printing and photolithography.* Jpn. J. Appl. Phys. (2019). https://doi.org/10.7567/1347-4065/ab09d0
- Kajtez, J., et al. *3D-Printed Soft Lithography for Complex Compartmentalized Microfluidic Neural Devices.* Adv. Sci. (2020). https://doi.org/10.1002/advs.202001150
- Pan, J. Y., et al. *Hybrid microfabrication of 3D pyrolytic carbon electrodes by photolithography and additive manufacturing.* Micro Nano Eng. (2022). https://doi.org/10.1016/j.mne.2022.100124
- Ristola, M., et al. *A compartmentalized neuron-oligodendrocyte coculture device for myelin research: design, fabrication and functionality testing.* J. Micromech. Microeng. (2019). https://doi.org/10.1088/1361-6439/ab16a7
- Moll, L., et al. *A Microfluidic High-Capacity Screening Platform for Neurological Disorders.* ACS Chem. Neurosci. (2024). https://doi.org/10.1021/acschemneuro.3c00409
- Spijkers, X. M., et al. *A directional 3D neurite outgrowth model for studying motor axon biology and disease.* Sci. Rep. (2021). https://doi.org/10.1038/s41598-021-81335-z
