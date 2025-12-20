# High-throughput microfluidic fabrication via hybrid SU-8 lithography + resin-printed well inserts (working title)

## One-sentence pitch
Combine fine-feature SU-8 photolithography (∼1–20 µm channels) with millimeter–centimeter-tall resin-printed well “macros” that are adhesively bonded to the wafer mold, eliminating manual PDMS punching and enabling microtiter-plate-format PDMS microfluidics compatible with multichannel pipettes and automation.

## Target contributions (claims to support)
1. **Fabrication method:** A reproducible hybrid mold-making workflow that integrates tall well structures with fine SU-8 microfeatures on the same mold.
2. **Throughput improvement:** Mold generates devices with wells formed during casting (no punching), enabling 48/96-well (or higher) formats.
3. **Design automation:** An open-source Python layout generator that outputs mask files and enforces plate-format constraints (spacing, well geometry, alignment features).
4. **Demonstration assay:** A 96-well-format axon isolation / injury / regeneration workflow using “chemical axotomy” via liquid handling (automation-friendly).

## Figure plan (write as if figures exist)
- **Figure 1 — Workflow overview.** End-to-end pipeline: Python CAD → photomask → SU-8 mold → printed well inserts → bonding + cleanup → PDMS casting → assembled plate-format device.
- **Figure 2 — Design of the well insert + lock-and-key alignment.** CAD render + dimensions + pin/hole alignment concept; tolerance callouts.
- **Figure 3 — Bonding fixture and glue interface.** Exploded view of build plates, clamps, wafer, insert array; epoxy fill path and squeeze-out region.
- **Figure 4 — Mold results.** Photos of finished hybrid mold (macro wells + SU-8 channels) and representative PDMS cast.
- **Figure 5 — Plate-format device layout.** 96-well mapping, channel routing, compartment structure, compatibility with multichannel pipette.
- **Figure 6 — Validation/benchmarking.** Yield metrics, well-to-well variability, leakage rate, burst pressure, alignment error histogram, time/cost comparison vs punching.
- **Figure 7 — Application: automation-friendly axotomy + regeneration readouts.** Schematic + representative images/plots (neurite length, survival, regrowth curves).

## Proposed paper structure
1. **Abstract**
2. **Introduction**
   - Why microfluidics in neuroscience; need for higher throughput + automation compatibility
   - Bottleneck: creating tall wells on SU-8 molds and manual punching
   - Prior approaches: thick SU-8, modular inserts, direct printing, CNC/embossing, commercial plates (brief, with citations)
   - Our approach: hybrid mold using resin-printed inserts + adhesive bonding; plus open-source CAD tooling
3. **Materials and Methods**
   - **Device design + CAD automation**
     - Python library scope, primitives, export formats, plate-format tiling
   - **SU-8 microfeature fabrication**
     - Wafer, SU-8 type/thickness, exposure, bake, develop (parameters as placeholders if needed)
   - **Resin-printed insert fabrication**
     - Printer model, resin type, post-cure, dimensional compensation
   - **Alignment + bonding**
     - Lock-and-key pin/hole, build plate transfer, epoxy application, clamping, acetone wash, heat cure
   - **PDMS casting + device assembly**
     - PDMS mix/degassing/cure, demold, bonding to glass, sterilization
   - **Assay demonstration (axon injury/regeneration)**
     - Cell type, plating, injury reagent, endpoints, imaging/analysis
4. **Results**
   - Hybrid mold fabrication success + common failure modes
   - Throughput and time-to-device vs punching
   - Compatibility with automation/multichannel pipettes
   - Demo assay results (chemical axotomy)
5. **Discussion**
   - What this enables; limitations (solvent compatibility, resin aging, glue creep, reuse count)
   - Generalizability beyond neuroscience; scaling to 384/1536 formats (if plausible)
6. **Conclusion**
7. **Data/Code availability**
8. **Acknowledgements**
9. **References**

## “Known unknowns” to fill in later (placeholders)
- Printer + resin used (brand, heat deflection temperature, shrinkage)
- Epoxy/glue (product, viscosity, cure schedule, acetone compatibility)
- Dimensional tolerances (pin/hole fit, alignment error)
- SU-8 stack (target thicknesses for well rim + channels)
- Plate footprint and spacing constraints (SBS standard compliance?)
- Device performance metrics and assay details

