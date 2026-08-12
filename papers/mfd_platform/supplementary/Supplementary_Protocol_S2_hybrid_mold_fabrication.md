# Supplementary Protocol S2. One-time hybrid SU-8/SUEX/resin mold fabrication

This protocol describes the one-time mold fabrication performed in a shared
microfabrication facility before the repeated benchtop device-production and
culture workflow in Supplementary Protocol S1. It starts from OpenMFD-generated
masks and insert models and ends with a parylene-coated hybrid mold ready for
PDMS casting.

The protocol describes the compartmentalized-neuron device used here.
Supplementary Table S3 provides validation checks for adapting the array,
device spacing, well radius, pin clearance, SUEX thickness, channel layout,
resin, printer, or parylene thickness.

## Inputs

- OpenMFD-generated channel-layer photomask.
- OpenMFD-generated SUEX well-layer and insert-alignment photomask.
- OpenMFD-generated resin insert STL array.
- OpenMFD-generated wafer, cutting, and plate-frame outlines.

## Materials and equipment

- 6-inch silicon wafer (UniversityWafer ID857 was used here).
- SU-8 2005 negative photoresist (Kayaku Advanced Materials).
- SUEX K200 dry film.
- PGMEA developer.
- LP360 long-pass filter for SUEX exposure.
- Laurell WS-650-8B spin coater or equivalent.
- SK 335R6 laminator or equivalent dry-film laminator.
- EVG620 mask aligner or equivalent photolithography aligner.
- Elegoo Mars 3 Pro resin printer or locally validated equivalent.
- Siraya Tech Sculpt Clear high-temperature resin or locally validated
  equivalent.
- Detachable magnetic resin-printer build plate or equivalent transfer fixture.
- Larger bonding plate compatible with the full wafer.
- EPDM rubber sheet, 0.03125 inch thickness, 60A durometer.
- EPO-TEK 301-2 epoxy.
- Acetone baths and dry air gun.
- Specialty Coating Systems SCS 200 parylene coater or equivalent parylene C
  coating service.

## A. Generate and review fabrication files

1. Generate matched photomask, insert, wafer, and frame files from the same
   OpenMFD preset.
2. Confirm that the channel layer, SUEX well and alignment-hole layer, insert
   pins, insert skirts, taper allowances, and cutting/frame outlines share the
   same coordinate system.
3. Confirm the PDMS shrinkage compensation factor used for the demonstrated
   100°C cure is applied consistently to the relevant mask and insert
   outputs.
4. Before fabrication, inspect the single-device and wafer-scale DXF outputs and
   the single and arrayed insert STL outputs.

## B. Pattern the SU-8/SUEX wafer

1. Start with a clean 6-inch silicon wafer.
2. Spin coat SU-8 2005 for a 5 µm target thickness.
3. Flood expose the first SU-8 2005 layer without a mask. Do not develop this
   layer. This layer functions as an adhesion base for the microchannel layer.
4. Spin coat a second SU-8 2005 layer for a 5 µm target thickness.
5. Align and expose the second SU-8 layer through the microchannel photomask.
6. Bake and develop the patterned SU-8 layer according to the manufacturer's
   SU-8 2005 process for a 5 µm target thickness.
7. Hard bake the developed two-layer SU-8 stack for 10 min at 150°C
   before SUEX lamination. Place the approximately 10 µm stack directly in the
   heated oven and remove it after 10 min; no controlled heating ramp or
   cooldown is required.
8. Laminate SUEX K200 dry film onto the wafer.
9. Expose the SUEX layer through the well and insert-alignment photomask using
   an LP360 long-pass filter at 2800 mJ/cm².
10. Post-exposure bake by ramping from room temperature to 50°C at
   1°C/min, holding at 50°C for at least 12 h overnight, then
   shutting off the oven and allowing it to cool.
11. Develop the SUEX layer in PGMEA for 20 min with mixing, exchanging developer
    at 15 min.
12. Hard bake by ramping from room temperature to 120°C at
    3°C/min, holding for 30 min, and ramping down by powering off the
    oven.

Routine inspection after photolithography:

- Confirm that the 5 µm SU-8 microchannel features remain attached.
- Confirm that the SUEX well features and insert-alignment holes are visibly intact.
- Confirm that the SUEX top surfaces are sufficiently flat for a continuous
  insert-wafer epoxy seal.

## C. Print and prepare resin inserts

1. Print the OpenMFD-generated insert array using the validated resin-printer
   profile for the selected resin. This work used Siraya Tech
   Sculpt Clear resin on an Elegoo Mars 3 Pro printer with the print profile in
   Supplementary Table S4.
2. Record resin, layer height, exposure, lift/retract, washing, and post-cure
   settings with the local printer profile. These settings apply to the local
   printer and resin, independently of the device dimensions in OpenMFD.
3. Clean the printed inserts by spraying with acetone and blow drying with
   compressed nitrogen. Repeat until pin features are free of residual resin;
   this work used 6–8 acetone/nitrogen cycles.
4. Remove the flexible metal plate from the printer build plate and post-cure
   the print in an Elegoo Mercury X rotating UV cure station for 15 min.
5. Keep the inserts in their printed relative positions on a detachable magnetic
   build plate or equivalent transfer fixture.
6. Measure printed pin heights across the insert array before bonding. The
   measured array had 116 µm peak-to-peak pin-height variation across
   one 8 × 12 array (Supplementary Table S1).

Routine inspection before bonding:

- Confirm that inserts remain in their intended array positions.
- Confirm that pins are intact and free of resin debris.
- Confirm that the compliant bonding fixture can accommodate the measured
  pin-height variation.

## D. Bond inserts to the SU-8/SUEX wafer

1. Transfer the insert array from the resin-printer build plate to a bonding
   plate suitable for clamping against the full wafer.
2. Place a 0.03125-inch-thick, 60A EPDM rubber sheet between the fixed magnet
   on the clamping build plate and the removable magnetic build plate carrying
   the inserts.
3. Apply EPO-TEK 301-2 epoxy in excess to the underside cavity on the pin side
   of each insert.
4. Place the wafer with SU-8/SUEX features facing the insert pins.
5. Align the wafer until all insert pins seat into their corresponding SUEX
   alignment holes.
6. Place a second flat plate above the wafer and clamp the stack to spread epoxy
   at the insert-wafer interface.
7. Submerge the clamped assembly in acetone for 1 min.
8. Transfer to a fresh acetone bath for a second 1 min wash.
9. Blow-dry the assembly thoroughly with dry air until the bonding interfaces
   and nearby feature regions are as dry and visibly clear as possible.
10. Cure the clamped assembly at room temperature for 48 h.
11. After cure, sonicate the bonded insert-wafer assembly in acetone for 10 min
    to remove residual material.
12. Release the bonded insert array from the transfer fixture by flexing the
    detachable magnetic sheet while preserving the insert-wafer bond.

Routine inspection after bonding:

- Confirm that all inserts remain bonded.
- Confirm that all pins are visibly seated in their alignment holes across the
  array.
- Confirm that the wafer remains intact after release from the bonding stack.

## E. Parylene coat the hybrid mold

1. Coat the bonded hybrid mold with 1 µm parylene C.
2. Use a local parylene coater or send the completed hybrid mold to an external
   university core or commercial coating service.
3. After coating, store and handle the mold as a reusable wafer-scale mold for
   PDMS casting.

Routine inspection during the first casting cycle:

- Confirm that the parylene-coated mold releases PDMS.
- Confirm that the cast wells are open after demolding.
- Confirm that the cast retains the intended well features.

Microscopy confirmed open channels after coating and casting. Specified
microchannel dimensions in the manuscript and design tables refer to the
pre-parylene CAD values.
