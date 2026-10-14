# Chemical axotomy assay in two-compartment OpenMFD devices

## Materials

- Primary E18 Sprague Dawley rat cortical neurons.
- Dendritic polyglycerol amine (dPGA; DendroTEK Biosciences).
- DMEM containing 10% fetal bovine serum (DMEM+).
- Neurobasal Plus containing 1% N2, 2% B27, and 1% glutamine (NB+).
- CTβ-647 and CTβ-568.
- Trypsin, Triton X-100, calcein-AM, and Hoechst 33342.
- Assembled, sterilized two-compartment OpenMFD plates.

## Neuronal culture

1. Plasma-treat assembled devices with dry air at 30 W for 10 min at
   approximately 400 mTorr. Begin coating within 15 min.
2. Add 30 µL of 10 µg/mL dPGA to each well for 10 min and wash once with
   sterile water.
3. Isolate E18 Sprague Dawley rat cortical neurons as described by Harris et
   al. [1].
4. Add 50 µL NB+ to the axon compartment. Seed 15,000 neurons in
   50 µL DMEM+ in the soma compartment.
5. After at least 30 min, replace the soma medium with 50 µL NB+ and reduce the
   axon-compartment volume to 25 µL.
6. Maintain cultures with 50 µL in the soma compartment and 25 µL in the
   axon compartment. This volume difference directs fluid toward the axon
   compartment during compartment-restricted additions.

## Axotomy and endpoint labeling

1. On DIV10, add CTβ-647 to the axon compartment at 1 µg/mL while preserving
   the 50 µL soma / 25 µL axon-compartment volumes. Incubate for 24 h.
2. On DIV11, acquire pre-axotomy brightfield and CTβ-647 images.
3. Replace the axon-compartment medium with 25 µL axotomy solution containing
   0.25% trypsin and 0.0125% Triton X-100. Keep 50 µL NB+ in the soma compartment.
4. Incubate for 10 min, remove the axotomy solution, and wash the axon
   compartment three times with NB+.
5. After washing, restore the axon compartment to 25 µL NB+ or treatment
   medium. Image the axon-compartment microchannel exits during the same
   acquisition as the CTβ-647-labeled cell bodies. Axotomy was considered complete when no
   intact axons remained continuous from the microchannel exits into the axon
   compartment.
6. At 48 h after axotomy, add CTβ-568 to the axon compartment at 1 µg/mL.
7. At 72 h after axotomy, add calcein-AM at 1:1000 dilution (1 µM final) and
   stain nuclei with Hoechst 33342. Acquire brightfield, CTβ, calcein-AM, and
   Hoechst images of both compartments.

## Imaging and analysis

Images were acquired in widefield mode on an Opera Phenix Plus using a
10×/0.30 NA objective, 2 × 2 camera binning, laser autofocus, and an effective
pixel size of 1.187 µm. Brightfield images used a 10 ms exposure. Fluorescence
images used 100 ms exposures with fluorophore-appropriate channels; CTβ-647 was
acquired using 640 nm excitation and 706 nm emission.

The pre-axotomy acquisition used 35 sites per device in a 7 × 5 grid. The
post-axotomy endpoint used 65 sites with approximately 10% overlap to cover the
soma compartment, microchannels, and axon compartment for calcein-AM
analysis. OpenHCS [2] was used to stitch the sites, align each device to a
reference brightfield image, crop a consistent device area, and perform
device-level analysis. CTβ-positive somata measured the number of neurons whose
axons reached the axon compartment, calcein-AM signal measured live axonal
regrowth, and Hoechst-positive nuclei provided a cellular-loading measure.
Total axon skeleton length was converted from image pixels to micrometers using
the effective pixel size of 1.187 µm/pixel.

## Reference

1. Harris J, Lee H, Tu CT, Cribbs D, Cotman C, Jeon NL. Preparing E18 cortical
   rat neurons for compartmentalization in a microfluidic device. *Journal of
   Visualized Experiments*. 2007;(8):305. <https://doi.org/10.3791/305>.
2. OpenHCSDev. *OpenHCS* [computer software], version 0.5.15.
   <https://github.com/OpenHCSDev/OpenHCS>.
