# Supplementary Protocol S1. Post-mold device assembly, primary cortical neuron culture, and CTB retrograde axon tracing

## Scope

This protocol describes how the parylene-coated hybrid mold was used to cast
and assemble the plate-format device and perform the neuronal compatibility
experiment. It includes the two-compartment directional fluid movement assay and
CTB retrograde axon tracing. The biological endpoint is the number of
CTB-positive neuronal cell bodies per device.

The plate contains 48 two-compartment devices and 96 pipette-accessible wells
on a 9 mm well grid. The two-well device units are
spaced 18 × 9 mm apart. The biological endpoint was evaluated in the 24
interior devices on each plate because the filament-printed frame did not
maintain equivalent perimeter conditions during long-term culture. Each plate
also contains 24 perimeter devices.

## Materials and equipment

- Completed parylene-coated hybrid mold (Supplementary Protocol S2).
- Sylgard 184 PDMS base and curing agent.
- Vacuum desiccator and 100°C oven.
- Industrial paper guillotine and clean razor blades.
- Coverslip glass, 110 × 74 × 0.17 mm.
- Harrick PDC-001 plasma cleaner or equivalent.
- Dry-air supply for plasma treatment.
- Sterilization pouches and autoclave with a dry 121°C cycle.
- OpenMFD-generated HIPS frame printed on an enclosed FDM printer.
- 12-channel pipette fitted with eight tips.
- 70% ethanol.
- Henkel LOCTITE SI 5140 one-part alkoxy-cure RTV silicone sealant (3 oz tube,
  IDH 135264), 3 mL Luer-lock syringe, and 18 gauge dispensing needle.
- Dendritic polyglycerol amine (dPGA; DendroTEK Biosciences) surface-coating
  reagent.
- DMEM with 10% fetal bovine serum.
- Neurobasal Plus medium supplemented with 1% N2, 2% B27, and 1% glutamine.
- Primary E18 Sprague Dawley rat cortical neurons.
- Alexa Fluor-conjugated cholera toxin subunit B (CTB-647).
- Alexa Fluor 488- and Alexa Fluor 568-conjugated secondary antibodies.
- PerkinElmer Opera Phenix Plus high-content imaging system with a 10×/0.30 NA
  objective.

## Adhesive selection and substitution

Primary cortical-neuron cultures in devices assembled with LOCTITE SI 5140 were
visually indistinguishable from adhesive-free controls, with no observable cytotoxicity.
It was the only tested adhesive that also formed a flexible, leak-tight
glass-to-HIPS bond that remained intact through repeated incubator cycling.
Acetic-acid-cure and ketoxime-cure RTV silicones and
cyanoacrylate adhesives caused visible toxicity. Norland Optical Adhesive 81
(NOA81) appeared compatible with HEK293T cells in our tests, consistent with a
published HEK293T culture study, but primary cortical neurons exposed to the
cured adhesive died within a few days despite extended UV curing. Other tested
UV-curable adhesives also failed the primary-neuron screen. EPO-TEK 301-2 was
sufficiently rigid that the glass-to-HIPS bond fractured during incubator
cycling. Validate alternative adhesives with the intended primary cells and
with mechanical and leak testing in the complete framed device.

## Unframed packaging control

One PDMS device was bonded to glass without adding a HIPS frame or frame
adhesive and was placed in a 14.5 cm-diameter polystyrene culture dish. This
control removed both the frame and adhesive seal. Cells at the outer device
positions showed visually comparable growth to cells elsewhere in the device,
showing that these positions support culture independently of the frame
assembly. The frame provides the routine plate-handling format and can be
optimized as a separate component.

## A. Cast and demold the PDMS device

1. Form a leak-tight aluminum-foil reservoir around the parylene-coated wafer
   mold.
2. Mix Sylgard 184 at a 10:1 base:curing-agent ratio. Approximately 35 mL total
   mixture is sufficient for one wafer mold.
3. Pour approximately 30 mL PDMS over the mold.
4. Load the filled molds into the six-shelf metal wafer rack and place the rack
   in the cylindrical vacuum chamber. Degas until visible bubbles are removed
   (typically 10–30 min; approximately −15 inHg in this setup).
5. Transfer the loaded rack to the oven. Cure for 1 h at 100°C and allow the
   mold to return to room temperature.
6. Remove the aluminum foil and release the PDMS around the mold perimeter.
7. Support the wafer on a flat surface. Initiate demolding at the corners and
   progress toward the center while pulling the PDMS upward and backward to
   reduce local peel stress.
8. Inspect the demolded cast. Wells must be open, microchannel regions must be
   intact, and no insert or SU-8/SUEX feature may have detached from the mold.

## B. Trim and bond the device to glass

1. Place the demolded PDMS feature-side up on a clean sheet of paper on the
   industrial paper-guillotine bed.
2. Apply clean low-residue tape along the inner edge of each molded cutting
   wall. Overlap the wall and extend each strip beyond the circular cast onto
   the paper so that the cast is held flat. Align the molded cutting guide with
   the guillotine blade.
3. Trim the device to the generated 108 × 72 mm outline and cut a small
   45° chamfer at each corner for frame alignment.
4. Remove particles from the bonding surface with repeated application of clean
   tape. Keep the final protective layer in place until plasma treatment.
5. Place the PDMS and a clean 110 × 74 × 0.17 mm coverslip-glass sheet in the
   plasma cleaner with the bonding surfaces exposed.
6. Treat with dry-air plasma for 1 min at 200–600 mTorr in a Harrick PDC-001, or
   use locally validated equivalent conditions, to activate both surfaces for
   PDMS-glass bonding.
7. Bring the activated surfaces into contact while maintaining a uniform glass
   margin around the PDMS. Apply gentle pressure from the center outward.
8. Heat the bonded assembly at 100°C for at least 1 min while applying
   uniform pressure.
9. Autoclave the bonded PDMS-on-glass assembly in a sterilization pouch using a
   dry 121°C cycle.

## C. Assemble the framed plate

1. Decontaminate the HIPS frame with 70% ethanol, allow it to dry, and invert it
   so that the adhesive groove surrounding the device opening faces upward.
2. Dispense 0.5–1 mL LOCTITE SI 5140 into the upward-facing frame groove using
   an 18 gauge dispensing needle.
3. Invert the bonded PDMS-on-glass assembly so that the glass faces upward.
   Align the PDMS with the frame recess and lower the assembly into the frame.
4. Inspect the adhesive interface for visible gaps.
5. Cure at room temperature for 3 days, turn the framed device upright, and
   trim excess cured adhesive with a clean razor blade.
6. Before coating or culture, plasma-treat the assembled device with dry air at
   high power (30 W) for 10 min at approximately 400 mTorr to decontaminate the
   surface and make it hydrophilic. Begin aqueous coating within 15 min of
   plasma treatment.

## D. Perform the qualitative two-compartment directional fluid movement assay

1. Reserve 24 assembled two-compartment devices for the directional fluid movement
   assay.
2. Prepare Alexa Fluor 488- and Alexa Fluor 568-conjugated secondary antibodies,
   each at a 1:1000 dilution.
3. Add 25 µL Alexa Fluor 568 solution to the left compartment of each device.
4. Add 50 µL Alexa Fluor 488 solution to the right compartment.
5. Image the complete device set immediately after loading (Hour 0).
6. Leave the devices for 72 h without replenishing either compartment or
   adjusting the volumes, then image the same devices.
7. Acquire images in widefield mode using the same 10×/0.30 NA objective,
   2 × 2 camera binning, and 100 ms fluorescence exposure used for the CTB
   acquisition, with fluorophore-appropriate green and red channels.
8. Report the result as a qualitative visualization of green-signal crossover
   from the higher-volume right compartment toward the lower-volume left
   compartment.

## E. Coat and seed primary cortical neurons

1. Isolate cortical neurons from one E18 Sprague Dawley embryo following the
   established preparation described by Harris et al. (2007), under the
   laboratory's approved animal-use procedure.
2. Distribute the same cell preparation across three separately assembled
   plates. These plates are technical plate replicates from one biological
   donor, not independent biological replicates.
3. Add 30 µL of 10 µg/mL dPGA to each culture well, incubate for 10 min, and
   wash once with sterile water. dPGA was selected as the neuronal culture
   substrate based on Clément et al. (2022).
4. Add 50 µL supplemented Neurobasal Plus medium to the distal
   compartment.
5. Seed 5,000–10,000 neurons in 50 µL DMEM with 10% fetal bovine serum in the
   soma compartment.
6. Allow cells to attach for at least 30 min, then replace the soma-compartment
   medium with 50 µL supplemented Neurobasal Plus medium.
7. Remove 25 µL from the distal compartment. Maintain 50 µL in the soma
   compartment and 25 µL in the distal compartment to create a small pressure
   difference that directs fluid from the soma compartment toward the distal
   compartment.
8. Maintain cultures to DIV11 using the same medium formulation and compartment
   volumes across all three plates.

## F. Perform CTB retrograde axon tracing and endpoint imaging

1. At DIV10, add CTB-647 to the 25 µL distal compartment at a final
   concentration of 1 µg/mL.
2. Preserve the 50 µL soma / 25 µL distal volume relationship after CTB
   addition.
3. Incubate for 24 h.
4. At DIV11, acquire endpoint images in widefield mode on a PerkinElmer Opera
   Phenix Plus using a 10×/0.30 NA objective, 2 × 2 camera binning, and the
   built-in laser autofocus. Acquire brightfield images with a 10 ms exposure
   and Alexa 647 fluorescence with 640 nm excitation, 706 nm emission, and a
   100 ms exposure. The effective pixel size is 1.187 µm. Use the same
   acquisition settings for all plates.
5. Acquire 35 sites per device in a 7 × 5 grid with approximately 10% overlap
   and stitch the sites into one oversized image that fully covers the device.
6. Align each stitched brightfield image to the reference brightfield image and
   crop it to the same device area.
7. Count CTB-positive neuronal cell bodies using one fixed segmentation and
   positivity rule applied uniformly to the cropped device images. Record one
   CTB-positive soma count for each cropped device.

## G. Analysis set and reporting

- Define the primary biological summary as the 24 interior devices per plate
  because culture conditions differed at the plate perimeter. Across three
  plates, image-level QC began with 72 interior devices.
- Apply image-level exclusion only when late-stage microbial contamination or
  an observable technical failure in culture or image acquisition renders the
  CTB-positive count uninterpretable. Include every interpretable count
  regardless of magnitude.
- Report the donor preparation as one biological replicate. The three
  separately assembled plates are technical plate replicates, and the devices
  are technical replicates within each plate.
- In this experiment, 69 of the 72 predefined interior devices met the
  image-level eligibility criteria. Three devices had late-stage contamination
  or a technical failure that made the endpoint image uninterpretable.
- Summarize CTB-positive counts descriptively by plate as the plate mean and
  standard deviation across analyzed interior devices. The three plates report
  technical variation within one donor preparation.
