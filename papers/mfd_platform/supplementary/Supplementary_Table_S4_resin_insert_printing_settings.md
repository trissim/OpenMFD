# Supplementary Table S4. Resin insert 3D-printing and post-processing settings

These settings were used to print the wafer-bonded resin inserts. Validate
alternative printers, resins, and slicer profiles for local print quality and
fit.

## Printer and resin

| Parameter | Setting |
|---|---|
| Resin | Siraya Tech Sculpt Clear high-temperature resin |
| Printer | Elegoo Mars 3 Pro |
| Build plate / transfer fixture | Magnetic removable build plate |
| Slicer/profile name in source screenshots | Siraya High Temp |

## Print profile

| Parameter | Setting |
|---|---:|
| Layer height | 0.020 mm |
| Bottom layer count | 7 |
| Exposure time | 5.500 s |
| Bottom exposure time | 50.000 s |
| Transition layer count | 0 |
| Transition type | Linear |
| Waiting mode during printing | Resting time |
| Rest time before lift | 0.300 s |
| Rest time after lift | 1.000 s |
| Rest time after retract | 3.000 s |
| Bottom lift distance | 3.000 + 0.000 mm |
| Lifting distance | 4.000 + 0.000 mm |
| Bottom retract distance | 3.000 + 0.000 mm |
| Retract distance | 4.000 + 0.000 mm |
| Bottom lift speed | 5.000 + 0.000 mm/min |
| Lifting speed | 30.000 + 0.000 mm/min |
| Bottom retract speed | 5.000 + 0.000 mm/min |
| Retract speed | 30.000 + 0.000 mm/min |

## Advanced slicer settings

| Parameter | Setting |
|---|---|
| Bottom light PWM | 255 |
| Light PWM | 255 |
| Anti-aliasing | Enabled |
| Grey level | 2 |
| Image blur | Disabled |
| Shrinkage compensation | Disabled |
| Tolerance compensation (beta) | Disabled |
| Bottom tolerance compensation | Disabled |
| Print time compensation | Disabled |

## Post-processing

1. Spray the printed inserts with acetone.
2. Blow dry with compressed high-pressure nitrogen.
3. Repeat the acetone spray and nitrogen drying cycle until the pin features are
   completely clean of residual resin. In the demonstrated workflow this
   required 6–8 cycles.
4. Remove the flexible metal plate from the printer build plate.
5. Place the print inside an Elegoo Mercury X rotating UV cure station.
6. UV cure for 15 min.
