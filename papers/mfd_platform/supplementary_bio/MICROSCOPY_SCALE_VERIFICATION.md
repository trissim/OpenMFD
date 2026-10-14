# Microscopy scale verification

Verified 2026-09-21 for the three-plate DMSO-only axotomy figure.

## Result

The microscopy calibration is **1.1867525298988041 µm/pixel**. A 500 µm
scale bar must therefore span **421.318 source-image pixels**. The scale bars in
Panel G are calibrated correctly.

## Independent checks

1. **Instrument metadata:** every PRE and POST Opera Phenix `Images/Index.xml`
   reports `ImageResolutionX` and `ImageResolutionY` as
   `1.1867525298988041E-06 m`, with a 10x/0.30 NA objective, 2x2 binning, and
   1080 x 1080 pixel fields. This value is consistent across all three plates.
2. **Tile geometry:** adjacent field centers are 1.153523-1.153524 mm apart,
   equivalent to approximately 972 pixels at the reported calibration. This is
   the expected spacing for 1080-pixel fields with about 10% overlap.
3. **Stitch dimensions:** the 13 x 6 field POST mosaic is 12,646 x 5,917 pixels.
   Its dimensions agree with full-resolution placement of the 1080-pixel fields
   after the small registration corrections made during stitching.
4. **Processing path:** OpenHCS assembly translates and blends the original
   tiles without changing their scale. The subsequent device operations are
   crops. Top-hat background subtraction temporarily downsamples only its
   background estimate and restores it to the original image shape before
   skeletonization.
5. **Microchannel-length cross-check:** in the original full-resolution P1
   R04C04 stitched brightfield device, the two ends of each microchannel array
   are at x = 5924 and x = 6177, or 253 pixels apart. The raw Opera calibration converts this to
   `253 x 1.1867525298988041 = 300.25 µm`, versus the 300 µm CAD channel
   length (0.08% difference). Both channel arrays give the same 253-pixel
   measurement. This is the primary device-geometry validation.
6. **Chamber-width cross-check:** the two long edges of a nominally 5.0 mm
   chamber are about 4,184 pixels apart in the same stitched brightfield image.
   The instrument calibration converts this to 4.965 mm, within about 0.7% of
   the CAD dimension. This independently excludes a 2x or 4x scale error.
7. **Measurement provenance:** for P1 R02C02, summing `branch_distance` in the
   OpenHCS branch table gives 25,283.335557 pixels, exactly matching the value
   carried into the figure's `total_axon_count` field. Multiplying those pixel
   distances by the acquisition calibration therefore yields µm.

## Display dimensions

- PRE representative crop: 2292 x 3700 pixels = 2.720 x 4.391 mm.
- POST representative crop: 1000 pixels wide = 1.187 mm.
- A 500 µm bar occupies 18.4% of the PRE crop width and 42.1% of the POST
  crop width. Its relatively large appearance in the narrow POST crop is
  expected.

The `600 dpi` TIFF tag on previously rendered comparison figures is print
resolution, not microscope calibration, and was not used.
