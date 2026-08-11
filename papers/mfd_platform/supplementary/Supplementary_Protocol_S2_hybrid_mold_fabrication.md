# Supplementary Protocol S2. One-time hybrid SU-8/SUEX/resin mold fabrication

This protocol expands the facility-based mold fabrication steps that precede
the post-mold device replication and culture workflow in Supplementary Protocol
S1. It starts from OpenMFD-generated masks and insert models and ends with a
parylene-coated hybrid mold ready for PDMS casting.

The protocol is written for the demonstrated compartmentalized-neuron device.
Changing the array, pitch, well radius, pin clearance, SUEX thickness, channel
layout, resin, printer, or parylene thickness should be treated as local process
development and checked against Supplementary Table S3.

## Inputs

- OpenMFD-generated channel-layer photomask.
- OpenMFD-generated SUEX/well/lock-layer photomask.
- OpenMFD-generated resin insert STL array.
- OpenMFD-generated wafer, cutting, and frame/package outlines.

## Materials and equipment

- 6 inch silicon wafer (UniversityWafer ID857 in the demonstrated workflow).
- SU-8 2005 negative photoresist.
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

1. Generate matched photomask, insert, wafer, and package files from the same
   OpenMFD preset.
2. Confirm that the channel layer, SUEX/lock layer, insert pins, insert skirts,
   taper allowances, and cutting/frame outlines share the same coordinate
   system.
3. Confirm the PDMS shrinkage compensation factor used for the demonstrated
   100 degrees C cure is applied consistently to the relevant mask and insert
   outputs.
4. Before fabrication, inspect the single-device and wafer-scale DXF outputs and
   the single and arrayed insert STL outputs.

## B. Pattern the SU-8/SUEX wafer

1. Start with a clean 6 inch silicon wafer.
2. Spin coat SU-8 2005 for a 5 um target thickness.
3. Flood expose the first SU-8 2005 layer without a mask. Do not develop this
   layer. This layer functions as an adhesion base for the microchannel layer.
4. Spin coat a second SU-8 2005 layer for a 5 um target thickness.
5. Align and expose the second SU-8 layer through the microchannel photomask.
6. Bake and develop the patterned SU-8 layer according to the local SU-8 2005
   process for a 5 um target thickness.
7. Laminate SUEX K200 dry film onto the wafer.
8. Expose the SUEX layer through the SUEX/well/lock photomask using an LP360
   long-pass filter at 2800 mJ/cm2.
9. Post-exposure bake by ramping from room temperature to 50 degrees C at
   1 degree C/min, holding at 50 degrees C, and ramping down by powering off the
   oven.
10. Develop the SUEX layer in PGMEA for 20 min with mixing, exchanging developer
    at 15 min.
11. Hard bake by ramping from room temperature to 180 degrees C at
    3 degrees C/min, holding for 30 min, and ramping down by powering off the
    oven.

QC before insert bonding:

- Confirm that 5 um SU-8 microchannel features remain attached.
- Confirm that SUEX lock and chamber features are visibly intact.
- Confirm that SUEX top surfaces do not show ridge-like artifacts that would
  prevent a continuous insert-wafer epoxy seal.

## C. Print and prepare resin inserts

1. Print the OpenMFD-generated insert array using the validated resin-printer
   profile for the selected resin. The demonstrated workflow used Siraya Tech
   Sculpt Clear resin on an Elegoo Mars 3 Pro printer with the print profile in
   Supplementary Table S4.
2. Record resin, layer height, exposure, lift/retract, washing, and post-cure
   settings with the local printer profile. These settings are printer- and
   resin-specific process parameters rather than OpenMFD design parameters.
3. Clean the printed inserts by spraying with acetone and blow drying with
   compressed nitrogen. Repeat until pin features are free of residual resin;
   the demonstrated workflow used 6-8 acetone/nitrogen cycles.
4. Remove the flexible metal plate from the printer build plate and post-cure
   the print in an Elegoo Mercury X rotating UV cure station for 15 min.
5. Keep the inserts in their printed relative positions on a detachable magnetic
   build plate or equivalent transfer fixture.
6. Measure printed pin heights across the insert array before bonding. The
   demonstrated workflow measured 116 um peak-to-peak z-height variation across
   one 8 x 12 array (Supplementary Table S1).

QC before bonding:

- Confirm that inserts remain in their intended array positions.
- Confirm that pins are intact and free of resin debris.
- Confirm that measured z-height variation can be accommodated by the bonding
  fixture compliance.

## D. Bond inserts to the SU-8/SUEX wafer

1. Transfer the insert array from the resin-printer build plate to a bonding
   plate suitable for clamping against the full wafer.
2. Place a 0.03125 inch, 60A EPDM rubber sheet between the fixed magnet on the
   clamping build plate and the removable magnetic build plate carrying the
   inserts.
3. Apply EPO-TEK 301-2 epoxy in excess to the underside cavity on the pin side
   of each insert.
4. Place the wafer with SU-8/SUEX features facing the insert pins.
5. Align the wafer until all insert pins seat into their corresponding SUEX lock
   holes.
6. Place a second flat plate above the wafer and clamp the stack to spread epoxy
   at the insert-wafer interface.
7. Submerge the clamped assembly in acetone for 1 min.
8. Transfer to a fresh acetone bath for a second 1 min wash.
9. Dry the assembly using a dry air gun.
10. Cure the clamped assembly at room temperature for 48 h.
11. After cure, sonicate the bonded insert-wafer assembly in acetone for 10 min
    to remove residual uncured epoxy.
12. Release the bonded insert array from the transfer fixture by flexing the
    detachable magnetic sheet, taking care not to disturb the insert-wafer bond.

QC after bonding:

- Confirm that all inserts remain bonded.
- Confirm that the pin/lock seating is visually complete across the array.
- Confirm that visible epoxy contamination is absent from microchannel regions.
- Confirm that the wafer has not cracked during release from the bonding stack.

## E. Parylene coat the hybrid mold

1. Coat the bonded hybrid mold with 1 um parylene C.
2. Use a local parylene coater or send the completed hybrid mold to an external
   university core or commercial coating service.
3. After coating, store and handle the mold as a reusable wafer-scale mold for
   PDMS casting.

QC before routine PDMS casting:

- Confirm that the parylene-coated mold releases PDMS in a test cast.
- Confirm that cast wells are open after demolding.
- Confirm that no insert delamination, SU-8 delamination, or well-fidelity loss
  is visible after the first casts.

Nominal microchannel dimensions in the manuscript and design tables are
pre-parylene CAD dimensions. Post-parylene channel dimensions were not measured
in this study.
