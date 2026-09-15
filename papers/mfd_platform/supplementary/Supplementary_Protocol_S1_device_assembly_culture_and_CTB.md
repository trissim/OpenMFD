# Supplementary Protocol S1. Post-mold device assembly, primary cortical neuron culture, and CTB retrograde axon tracing

## Scope

This protocol covers PDMS casting from the parylene-coated hybrid mold,
plate assembly, neuronal culture, and imaging. The assays measure tracer
movement between compartments and count CTB-positive neuronal cell bodies
in each device.

The plate contains 48 two-compartment devices and 96 pipette-accessible wells
on a 9 mm well grid. The two-well device units are
spaced 18 × 9 mm apart. CTB-positive cell bodies were counted in the 24
interior devices on each plate because culture performance was poorer at the
plate edges during long-term culture. Each plate also contains 24 perimeter
devices. The safe maximum working volume for this plate is 50 µL per well.

## Materials and equipment

- Completed parylene-coated hybrid mold (Supplementary Protocol S2).
- Sylgard 184 PDMS base and curing agent.
- Vacuum desiccator and 100°C oven.
- Industrial paper guillotine and clean razor blades.
- Coverslip glass, 110 × 74 × 0.17 mm.
- Harrick PDC-001 plasma cleaner or equivalent.
- Dry-air supply for plasma treatment.
- Sterilization pouches and autoclave operated at 121°C for 15 min.
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

Use LOCTITE SI 5140 for the frame assembly described here. Adhesives were
screened according to whether primary cortical-neuron cultures survived to the
end of the experiment; only SI 5140 passed. Cell toxicity was not quantified.
Test alternative adhesives for cell survival, joint strength, and leaks in
the complete framed device.

## Control without a frame or frame adhesive

One PDMS device was bonded to glass without adding a HIPS frame or frame
adhesive and was placed in a 14.5 cm-diameter polystyrene culture dish. This
control removed both the frame and adhesive seal and changed the surrounding
culture environment. Growth was assessed visually. The control does not
identify the separate effects of the frame, adhesive seal, or dish; observations
are reported in the main Results.

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
7. Support the wafer on a flat surface. Start peeling at the corners and
   progress toward the center while pulling the PDMS upward and backward to
   reduce stress on the wafer.
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
9. Autoclave the bonded PDMS-on-glass assembly in a sterilization pouch at
   121°C for 15 min.

## C. Assemble the framed plate

1. Decontaminate the HIPS frame with 70% ethanol, allow it to dry, and invert it
   so that the adhesive groove surrounding the device opening faces upward.
2. Dispense 0.5–1 mL LOCTITE SI 5140 into the upward-facing frame groove using
   an 18 gauge dispensing needle.
3. Invert the bonded PDMS-on-glass assembly so that the glass faces upward.
   Align the PDMS with the frame recess and lower the assembly into the frame.
4. Inspect the adhesive joint for visible gaps.
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
   each at a 1:1000 dilution in phosphate-buffered saline (PBS).
3. Add 25 µL Alexa Fluor 568 solution to the left compartment of each device.
4. Add 50 µL Alexa Fluor 488 solution to the right compartment.
5. Image the complete device set immediately after loading (Hour 0).
6. Keep the devices in a cell-culture incubator for 72 h without replenishing
   either compartment or adjusting the volumes, then image the same devices.
7. Acquire images in widefield mode using the same 10×/0.30 NA objective,
   2 × 2 camera binning, and 100 ms fluorescence exposure used for the CTB
   imaging, with green and red channels suited to the two fluorophores.
8. Compare green fluorescence in the initially lower-volume left compartment
   between Hour 0 and 72 h. The readout is qualitative tracer redistribution
   from the higher-volume right compartment.

## E. Coat and seed primary cortical neurons

1. Isolate cortical neurons from one embryonic day 18 (E18) Sprague Dawley rat
   embryo following the procedure described by Harris et al. (2007), under the
   laboratory's approved animal-use procedure.
2. Distribute neurons from that embryo across three separately assembled
   plates. Because the neurons all come from the same embryo, the plates are
   technical replicates, not independent biological samples.
3. Add 30 µL of 10 µg/mL dPGA to each culture well, incubate for 10 min, and
   wash once with sterile water. dPGA was selected as the neuronal culture
   substrate based on Clément et al. (2022).
4. Add 50 µL supplemented Neurobasal Plus medium to the distal
   compartment.
5. Seed 5,000–10,000 neurons in 50 µL DMEM with 10% fetal bovine serum in the
   cell-body (soma) compartment.
6. Allow cells to attach for at least 30 min, then replace the soma-compartment
   medium with 50 µL supplemented Neurobasal Plus medium.
7. Remove 25 µL from the distal compartment. Maintain 50 µL in the soma
   compartment and 25 µL in the distal compartment to create a small pressure
   difference that directs fluid from the soma compartment toward the distal
   compartment.
8. Maintain cultures for 11 days in vitro (DIV11) following the procedure of Harris
   et al. (2007), with the medium formulation and compartment volumes specified
   above applied across all three plates.

## F. Perform CTB retrograde axon tracing and imaging

1. At DIV10, add CTB-647 to the 25 µL distal compartment at a final
   concentration of 1 µg/mL.
2. After adding CTB, keep 50 µL in the soma compartment and 25 µL in the
   distal compartment.
3. Incubate for 24 h.
4. At DIV11, collect images in widefield mode on a PerkinElmer Opera
   Phenix Plus using a 10×/0.30 NA objective, 2 × 2 camera binning, and the
   built-in laser autofocus. Acquire brightfield images with a 10 ms exposure
   and Alexa 647 fluorescence with 640 nm excitation, 706 nm emission, and a
   100 ms exposure. The effective pixel size is 1.187 µm. Use the same
   exposure and optical settings for all plates.
5. Collect overlapping images and stitch them into one image per device. In this
   experiment, Plates 1 and 2 used 35 imaging positions per device (7 × 5 grid),
   and Plate 3 used 42 positions (7 × 6 grid), with approximately 10% overlap.
   Plate 3's PDMS array was shifted slightly rightward during gluing, so a larger
   area was imaged to capture more microchannel exits. The area covered by
   35 imaging positions was sufficient for cell counting.
6. Align each stitched brightfield image to the reference brightfield image and
   crop all plates to the same area for cell counting, regardless of whether
   images were collected at 35 or 42 positions. Imaging a larger area does not
   enlarge the area used for counting.
7. Identify and count CTB-positive neuronal cell bodies using the same cell
   segmentation settings and criteria for CTB labeling in every cropped image.
   Record one CTB-positive cell-body count for each cropped device.

## G. Analysis set and descriptive statistics

- CTB-positive cells were counted before axotomy in the February 2026
  three-plate DMSO-only experiment.
- Analysis was restricted to the 24 interior devices per plate because culture
  conditions differed at the plate perimeter. Images from 72 interior devices
  across three plates were checked for contamination and technical failures.
- Devices were excluded only when late-stage microbial contamination or an
  observable technical failure in culture or imaging prevented cell counting.
  Every usable count was included, whether high or low.
- All neurons came from one embryo. The three separately assembled plates
  and the devices within each plate are technical replicates, not samples from
  different embryos.
- In this experiment, 69 of the 72 interior devices had images suitable for
  cell counting. Three devices had late-stage contamination or a technical
  failure that prevented cell counting in the final image.
- CTB-positive counts are summarized descriptively as the mean and standard
  deviation across analyzed interior devices within each plate, representing
  variation among devices containing neurons from the same embryo.
