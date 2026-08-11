# Supplementary Table S3. Practical Design Limits for the Demonstrated Workflow

The demonstrated 18 x 9 mm unit pitch and SUEX-200 design provide recommended starting values for new layouts rather than hard process limits. Reducing clearances, margins, taper allowances, or contact lands below the demonstrated values should be treated as new process development and verified locally.

| Design feature | Demonstrated nominal value | Built-in tolerance or allowance | When local validation is recommended |
|---|---:|---|---|
| Plate-format pitch | 6 x 8 two-well units (48 devices, 96 wells); 18 x 9 mm device-unit pitch; wells at +/-4.5 mm from unit center | Well centers remain on a 9 mm grid, so each two-well unit occupies two plate columns by one plate row | Any non-9 mm well pitch, nonstandard device-unit pitch, or layout intended for a different liquid handler or imager |
| Array/package envelope | 108 x 72 mm device array on a 110 x 74 mm glass outline; 150 mm wafer with 57.5 mm flat | Glass outline provides 1 mm nominal margin per side around the generated device array; wafer, cut, and frame outlines are generated from the same coordinate system | Smaller glass margins, larger arrays, different wafer diameter, or manually edited cutting/frame outlines |
| Well, chamber, and channel coupling | 2.5 mm well radius; 5.0 mm chamber width; 62 channels at 10 um width and 30 um gap | Channel block is 2.45 mm wide, leaving 1.275 mm lateral chamber margin per side; chamber and insert footprints are derived from the same channel measurements | Narrower channel gaps, wider channel arrays, smaller chambers, or channel placement closer to insert/skirt contact regions |
| Layer separation | 5 um SU-8 microchannel layer plus 200 um SUEX well/chamber/lock layer | Fine features and tall lock/chamber features are fabricated as separate registered layers with paired full/hollow alignment marks | Collapsing layers, changing SUEX thickness, or moving lock features into the microchannel layer |
| Insert lock registration | 1.85 x 1.85 mm printed pins seated in 2.0 x 2.0 mm SUEX holes | 150 um total lateral clearance, or 75 um per side, between printed pins and wafer locks | Smaller pin-hole clearance, different resin/printer settings, or smaller lock features |
| Array-wise z seating | Measured insert pin-height variation up to 116 um peak-to-peak; EPDM compliant layer used during clamping | Clamping stack must accommodate at least the measured z variation so all pins can seat before epoxy cure | Larger print-area z variation, stiffer clamping stack, or omission/change of the compliant layer |
| Insert taper and demolding | 3.8 mm insert height; 16 degree outer taper; 0.300 mm extra taper allowance | 1.39 mm lateral taper allowance is subtracted from the insert footprint; remaining insert features stay positive while avoiding vertical macro walls | Steeper walls, smaller wells/chambers after taper subtraction, or reduced draft angle |
| Skirt and adhesive contact land | Two-step skirt: 0.75 mm x 0.66 mm plus 0.80 mm x 0.04 mm | Provides an approximately 0.75-0.80 mm inset contact/seal land around the insert footprint while keeping adhesive away from microchannels | Smaller contact lands, different epoxy viscosity, or layouts with channels closer to the insert perimeter |
| PDMS shrinkage compensation | 1.0226 x-y scale factor for the 100 degrees C cure used here | The same 2.26% overscale is applied to matched masks and inserts, preserving registration after thermal cure | Different cure temperature, PDMS formulation, or independent/manual scaling of only one output file |

## S3B. Constraint checks for Figure 5 design-generation examples

The Figure 5 layouts were generated with the same OpenMFD output classes as the
validated neuronal-culture device, but they were not fabricated or biologically
validated in this study. They should therefore be read as design-file examples,
not as completed device validations.

| Layout | Unit pitch / array | Well radius | Microchannel summary | Fabrication status | Local validation trigger |
|---|---|---:|---|---|---|
| Demonstrated compartmentalized-neuron device | 18 x 9 mm; 6 x 8 two-well units | 2.5 mm | 62 channels at 10 um width and 30 um gap | Fabricated, cast, packaged, imaged, and used for neuronal culture in analyzed interior positions | Baseline demonstrated workflow |
| Myelination design-generation example | 18 x 18 mm; 6 x 4 units | 2.5 mm | 125 channels at 10 um plus oligo branch | Generated mask, insert, and frame files only | Different unit pitch, crossing layout, higher channel count, and unfabricated layout |
| Axon-guidance design-generation example | 18 x 18 mm; 6 x 4 units | 2.5 mm | 83 channels at 10 um per arm | Generated mask, insert, and frame files only | Different unit pitch, orthogonal-gradient geometry, and unfabricated layout |
| Three-compartment design-generation example | 27 x 9 mm; 4 x 8 units | 2.5 mm | Two serial channel arrays with 125 channels at 10 um per array | Generated mask, insert, and frame files only | Three-well unit, different unit pitch, serial channel architecture, and unfabricated layout |
