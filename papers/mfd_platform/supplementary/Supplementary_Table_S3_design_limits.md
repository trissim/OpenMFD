# Supplementary Table S3. Design parameters and validation checks

The tested design used two-well device units spaced 18 × 9 mm apart and a
200 µm SUEX well layer. These values provide starting points for new layouts.
Local testing can establish suitable operating ranges for smaller gaps,
margins, taper allowances, and adhesive contact areas.

| Design feature | Value used here | Allowance included in the design | Adaptations for local validation |
|---|---:|---|---|
| Device and well spacing | 6 × 8 two-well units (48 devices, 96 wells); device units spaced 18 × 9 mm apart; wells at ±4.5 mm from the unit center | Well centers remain on a 9 mm grid, so each two-well unit occupies two plate columns by one plate row | Any non-9 mm well spacing, nonstandard device spacing, or layout intended for a different liquid handler or imager |
| Device and frame dimensions | 108 × 72 mm device array on a 110 × 74 mm glass outline; 150 mm wafer with a 57.5 mm flat | The glass provides a 1 mm designed margin on each side of the device array; wafer, cutting, and frame outlines are generated from the same dimensions | Smaller glass margins, larger arrays, a different wafer diameter, or manually edited cutting or frame outlines |
| Alignment of wells, chambers, and channels | 2.5 mm well radius; 5.0 mm chamber width; 62 channels with 10 µm width and 30 µm spacing | The channel array is 2.45 mm wide, leaving a 1.275 mm chamber margin on each side; chamber and insert dimensions are derived from the same channel measurements | Narrower channel gaps, wider channel arrays, smaller chambers, or channels placed closer to insert or adhesive-contact regions |
| Separation of fabrication layers | 5 µm SU-8 microchannel layer plus 200 µm SUEX well and alignment-hole layer | The microchannels and taller well features are fabricated as separate aligned layers using matching solid and hollow alignment marks | Combining layers, changing SUEX thickness, or moving alignment holes into the microchannel layer |
| Insert alignment | 1.85 × 1.85 mm printed pins seated in 2.0 × 2.0 mm SUEX holes | 150 µm total side-to-side clearance, or 75 µm per side, between the printed pins and wafer holes | Smaller gaps between pins and holes, different resin or printer settings, or smaller alignment features |
| Insert seating across the array | Measured pin-height variation of 116 µm between the lowest and highest pins; compressible EPDM used during clamping | The clamping layers must accommodate at least the measured height variation so all pins can seat before the epoxy cures | Larger height variation across a print, stiffer clamping layers, or omission or replacement of the compressible layer |
| Insert taper and demolding | 3.8 mm insert height; 16° outer taper; 0.300 mm extra taper allowance | The taper reduces each side by 1.39 mm from bottom to top; this preserves wall thickness while avoiding vertical outer walls | Steeper walls, smaller wells or chambers after applying the taper, or less taper |
| Skirt and adhesive contact area | Two-step skirt: 0.75 × 0.66 mm plus 0.80 × 0.04 mm | Provides an approximately 0.75–0.80 mm-wide recessed contact and sealing area around the insert while keeping adhesive away from microchannels | Smaller contact areas, different epoxy viscosity, or layouts with channels closer to the insert edge |
| PDMS shrinkage compensation | 1.0226 horizontal scale factor for the 100°C cure used here | The same 2.26% enlargement is applied to matching masks and inserts, keeping them aligned after thermal curing | A different cure temperature, PDMS formulation, or independent scaling of only one output file |

## S3B. Fabrication checks for the Figure 5 layouts

For each literature-inspired layout in Figure 5, OpenMFD generated the same
mask, insert, wafer, and frame files used for the neuronal device. These matched
file sets can be fabricated with the workflow described here; their dimensions
determine the local checks listed below.

| Layout | Device spacing and array | Well radius | Microchannel summary | Current evidence | First-fabrication checks |
|---|---|---:|---|---|---|
| Demonstrated compartmentalized-neuron device | 18 × 9 mm; 6 × 8 two-well units | 2.5 mm | 62 channels with 10 µm width and 30 µm spacing | Fabricated, cast, assembled, imaged, and used for neuronal culture in analyzed interior devices | Baseline demonstrated workflow |
| Myelination-inspired layout | 18 × 18 mm; 6 × 4 units | 2.5 mm | 125 channels at 10 µm plus an oligodendrocyte branch | Complete matched fabrication files generated | Confirm the different device spacing, crossing layout, higher channel count, and assay-specific operation |
| Axon-guidance layout | 18 × 18 mm; 6 × 4 units | 2.5 mm | 83 channels at 10 µm per arm | Complete matched fabrication files generated | Confirm the different device spacing, orthogonal-gradient layout, and assay-specific operation |
| Three-compartment layout | 27 × 9 mm; 4 × 8 units | 2.5 mm | Two successive channel arrays with 125 channels at 10 µm per array | Complete matched fabrication files generated | Confirm the three-well unit, different device spacing, successive channel arrays, and assay-specific operation |
