# Supplementary Protocol S1. Post-mold device assembly, primary cortical neuron culture, and CTB uptake

## Scope

This protocol describes the submission-facing workflow used to convert a
completed parylene-coated hybrid mold into an assembled plate-format device and
to perform the minimal neuronal compatibility experiment reported in the main
manuscript. The biological endpoint is the number of CTB-positive neuronal cell
bodies after distal CTB exposure. Chemical axotomy and regeneration are not part
of the validation reported in this manuscript.

The demonstrated plate contains 48 two-compartment devices and 96
pipette-accessible wells on a 9 mm well grid. The two-well device units are
arrayed at an 18 x 9 mm unit pitch. Because the filament-printed frame did not
maintain equivalent perimeter conditions during long-term culture, only
interior device positions were eligible for the biological endpoint. Each plate
contains 24 interior and 24 perimeter device positions.

## Materials and equipment

- Completed parylene-coated hybrid mold (Supplementary Protocol S2).
- Sylgard 184 PDMS base and curing agent.
- Vacuum desiccator and 100 degrees C oven.
- Industrial paper guillotine and clean razor blades.
- Coverslip glass, 110 x 74 x 0.17 mm.
- Harrick PDC-001 plasma cleaner or equivalent.
- Dry-air supply for plasma treatment.
- Sterilization pouches and autoclave with a dry 121 degrees C cycle.
- OpenMFD-generated HIPS frame printed on an enclosed FDM printer.
- 70% ethanol.
- Loctite 5140 adhesive, 3 mL Luer-lock syringe, and 18 gauge dispensing
  needle.
- dPGA surface-coating reagent.
- DMEM with 10% fetal bovine serum.
- Neurobasal Plus medium supplemented with 1% N2, 2% B27, and 1% glutamine.
- Primary E18 Sprague Dawley rat cortical neurons.
- Alexa Fluor-conjugated cholera toxin subunit B (CTB-647).
- Opera Phenix or ImageXpress high-content imaging system, or an equivalent
  plate-format fluorescence microscope.

## A. Cast and demold the PDMS device

1. Form a leak-tight aluminum-foil reservoir around the parylene-coated wafer
   mold.
2. Mix Sylgard 184 at a 10:1 base:curing-agent ratio. Approximately 35 mL total
   mixture is sufficient for one demonstrated wafer mold.
3. Pour approximately 30 mL PDMS over the mold.
4. Degas under vacuum until visible bubbles are removed (typically 10-30 min;
   approximately -15 inHg in the demonstrated setup).
5. Cure for 1 h at 100 degrees C and allow the mold to return to room
   temperature.
6. Remove the aluminum foil and release the PDMS around the mold perimeter.
7. Support the wafer on a flat surface. Initiate demolding at the corners and
   progress toward the center while pulling the PDMS upward and backward to
   reduce local peel stress.
8. Inspect the demolded cast. Wells must be open, microchannel regions must be
   intact, and no insert or SU-8/SUEX feature may have detached from the mold.

## B. Trim and bond the device to glass

1. Place the demolded PDMS feature-side up on a clean surface.
2. Protect the feature surface with clean low-residue tape and align the molded
   cutting guide with the paper-guillotine blade.
3. Trim the device to the generated 108 x 72 mm outline and cut a small
   45-degree chamfer at each corner for frame alignment.
4. Remove particles from the bonding surface with repeated application of clean
   tape. Keep the final protective layer in place until plasma treatment.
5. Place the PDMS and a clean 110 x 74 x 0.17 mm coverslip-glass sheet in the
   plasma cleaner with the bonding surfaces exposed.
6. Treat with dry-air plasma for 1 min at 200-600 mTorr in a Harrick PDC-001, or
   use locally validated equivalent conditions.
7. Bring the activated surfaces into contact while maintaining a uniform glass
   margin around the PDMS. Apply gentle pressure from the center outward.
8. Heat the bonded assembly at 100 degrees C for at least 1 min while applying
   uniform pressure.
9. Autoclave the bonded PDMS-on-glass assembly in a sterilization pouch using a
   dry 121 degrees C cycle.

## C. Assemble the framed plate

1. Sterilize the HIPS frame with 70% ethanol and allow it to dry.
2. Dispense 0.5-1 mL Loctite 5140 into the frame groove using an 18 gauge
   dispensing needle.
3. Align the bonded PDMS-on-glass assembly with the generated frame recess and
   seat the glass on the adhesive.
4. Inspect the adhesive interface for visible gaps.
5. Cure at room temperature for 3 days and trim excess cured adhesive with a
   clean razor blade.
6. Before coating or culture, plasma-treat the assembled device with dry air at
   high power (30 W) for 10 min at approximately 400 mTorr. Begin aqueous
   coating within 15 min of plasma treatment.

## D. Coat and seed primary cortical neurons

1. Isolate cortical neurons from one E18 Sprague Dawley embryo following the
   established preparation described by Harris et al. (2007), under the
   laboratory's approved animal-use procedure.
2. Distribute the same cell preparation across three separately assembled
   plates. These plates are technical plate replicates from one biological
   donor, not independent biological replicates.
3. Add 30 uL of 10 ug/mL dPGA to each culture well, incubate for 10 min, and
   wash once with sterile water.
4. Add 50 uL supplemented Neurobasal Plus medium to the distal/axon
   compartment.
5. Seed 5,000-10,000 neurons in 50 uL DMEM with 10% fetal bovine serum in the
   soma compartment.
6. Allow cells to attach for at least 30 min, then replace the soma-compartment
   medium with 50 uL supplemented Neurobasal Plus medium.
7. Remove 25 uL from the distal compartment. Maintain 50 uL in the soma
   compartment and 25 uL in the distal compartment to impose a soma-to-distal
   hydrostatic bias.
8. Maintain cultures to DIV11 using the same medium formulation and volume bias
   across all three plates.

## E. Perform distal CTB exposure and endpoint imaging

1. At DIV10, add CTB-647 to the 25 uL distal compartment at a final
   concentration of 1 ug/mL.
2. Preserve the 50 uL soma / 25 uL distal volume relationship after CTB
   addition.
3. Incubate for 24 h.
4. At DIV11, acquire endpoint CTB-647 images of the soma compartment using the
   same objective, exposure, autofocus, and field layout for all plates.
5. Count CTB-positive neuronal cell bodies using one fixed segmentation and
   positivity rule applied uniformly across plates. Retain the analysis settings
   with the source data.

## F. Eligibility, exclusions, and reporting

- Restrict the primary biological summary to the 24 interior device positions
  per plate because the filament-printed frame did not maintain equivalent
  conditions at the 24 perimeter positions during long-term culture. Across
  three plates, this excludes 72 perimeter positions before image-level QC.
- Exclude a position only when late-stage microbial contamination is visible or
  when an observable technical failure in culture or image acquisition renders
  the CTB-positive count uninterpretable. Count magnitude alone is not an
  exclusion criterion.
- Report the donor preparation as one biological replicate. Report the three
  separately assembled plates as technical plate replicates and device
  positions as technical replicates nested within plate and donor.
- In the demonstrated experiment, three of the 72 predefined interior positions
  met the technical exclusion criteria, leaving 69 positions in the
  CTB-positive-cell summary.
- Summarize CTB-positive counts descriptively by plate as the plate mean and
  standard deviation across analyzed interior positions. Do not use comparisons
  among these three plates as evidence of biological reproducibility because all
  plates received cells from the same donor preparation.

## Reference

Harris, J., Lee, H., Tu, C. T., Cribbs, D., Cotman, C., and Jeon, N. L.
Preparing E18 cortical rat neurons for compartmentalization in a microfluidic
device. *Journal of Visualized Experiments* (8), 305 (2007).
https://doi.org/10.3791/305
