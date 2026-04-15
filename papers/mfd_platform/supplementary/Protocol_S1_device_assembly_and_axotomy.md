Introduction

This protocol describes the fabrication, assembly, and operation of microfluidic devices for studying axonal injury and regeneration in neuronal cultures. These compartmentalized platforms enable the physical separation of neuronal cell bodies from their axons, allowing targeted axonal injury (axotomy) while preserving the soma. This separation is critical for investigating the cell-autonomous mechanisms of axonal regeneration and screening potential therapeutic interventions.

The protocol is divided into three main sections:

Device Fabrication and Assembly - Details the complete workflow for creating functional devices, including PDMS molding from silicon wafers, 3D printing of support frames using HIPS filament, plasma bonding to glass coverslips, and final assembly with biocompatible adhesive. The resulting devices are autoclavable and suitable for long-term cell culture.

Cell Culture and Axotomy - Covers surface preparation, neuronal seeding, and the chemical axotomy procedure using trypsin and Triton X-100. The compartmentalized design maintains fluidic isolation between chambers, enabling selective axonal injury while maintaining cell body viability.

Endpoint Analysis - Describes retrograde labeling strategies using cholera toxin B conjugates and live-cell staining with calcein-AM to quantify both total axonal regeneration and the proportion of neurons successfully regenerating axons. Optional automated analysis using OpenHCS is supported.

The complete process from device fabrication to endpoint imaging typically spans 12-14 days, with devices requiring 3 days of curing post-assembly and cultures typically maintained for 10-11 days before axotomy.

  
*Materials:*

- > Plasma cleaner: <https://harrickplasma.com/plasma-cleaners/expanded-plasma-cleaner/>

- > Paper cutter for PDMS <https://www.vevor.ca/paper-cutter-c_10879/vevor-industrial-paper-cutter-heavy-duty-paper-cutter-12-for-a4-paper-cutting-p_010539581610?adp=gmc&utm_id=17326114712&gad_source=1>

- > K1C 3D printer <https://store.creality.com/ca/products/k1c-3d-printer>

- > HIPS filament <https://www.digitmakers.ca/products/esun-hips-filament-1-75-mm-white?variant=40491850891426>

- > Device coverslip glass <https://www.uqgoptics.com/product/d263t-eco-100-off-per-pack-2/>

- > Sterilization pouches <https://www.fishersci.ca/shop/products/fisherbrand-instant-sealing-sterilization-pouches-6/p-32012#?keyword=>

- > 18GA luer-lok needle <https://www.amazon.ca/PATIKIL-Dispensing-Stainless-Plastic-Applicator/dp/B0CYFLRX3M?th=1>

- > 3mL BD Luer-lok syringe <https://www.fishersci.ca/shop/products/bd-disposable-syringes-luer-lok-tips-3/p-3239164>

- > 60mL syringe <https://www.fishersci.ca/shop/products/bulk-unsterile-syringes-6/14817177#?keyword=60ml%20syringe>

- > Loctite 5140 glue [https://www.digikey.ca/en/products/detail/loctite/135264/2486659?gclsrc=aw.ds&&utm_adgroup=General&productid=2486659](https://www.digikey.ca/en/products/detail/loctite/135264/2486659?gclsrc=aw.ds&&utm_adgroup=General&productid=2486659&utm_id=go_cmp-17855401585_adg-_ad-__dev-c_ext-_prd-2486659_sig-EAIaIQobChMI2tS_t9G3jAMVTDUIBR1AlhrXEAQYASABEgL42PD_BwE&gad_source=1&gclid=EAIaIQobChMI2tS_t9G3jAMVTDUIBR1AlhrXEAQYASABEgL42PD_BwE&gclsrc=aw.ds)

- > Calcein-am: <https://www.thermofisher.com/order/catalog/product/C3099?SID=srch-srp-C3099>

- > alexa-647/568-conjugated-choleratoxin-beta (CtB-647/568) <https://www.thermofisher.com/order/catalog/product/C34778?SID=srch-srp-C34778>

- > Neurobasal plus 1% N2, 2% B27, 1% glutamine (NB+)

- > DMEM + 10% FBS (DMEM+)

- > dPGA / dendrimer coating <https://dendrotek.ca/products/dpga?variant=43694937571575>

- > OpenHCS: https://pypi.org/project/openhcs/

Device Fabrication

*![PDMS preparation icon](media/image1.png) ![PDMS mold icon](media/image2.png) Prepare and curing PDMS in the mold*

- > Cut a round aluminum foil sheet form a dish surrounding the wafer/mold with sealed aluminum foil walls

- > For each device prepare 35mL of PDMS using a 1A:10B ratio (3.5mL part A 31.5mL part B) in a large red solo cup on a scale

- > Transfer 30mL of PDMS from the red cup into 60mL syringes

- > Transfer 30mL of PDMS from each syringe into each wafer/mold

- > Move the molds into the desiccator and leave under negative pressure until bubbles are gone (10-30 minutes)

- > Move the bubble-free PDMS casted mold into an over @100C for 1hour

*![Frame printing icon](media/image3.png) ![Frame icon](media/image4.png) 3D printing the frame*

- > While the PDMS cures, you can print the frame using the 3D model provided in the link in the materials

- > You must use an enclosed FDM 3D printer that supports HIPS filament. The Creality K1C printer is an easy-to-use all-in-one printer suitable for printing the frames. HIPS was selected because it has low hygroscopicity and lower thermal contraction than polypropylene, the only other low-hygroscopicity filament we evaluated.

- > The provided settings should be used, or the following principles should be respected to reduce frame warping:

  - > Turn off the fans, this will allow the ambient air to stay warm, allowing the plate to remain flat rather than warp due to rapid cooling

  - > Print slowly and avoid using the corners of the build plate if the calibration is not on point. This will also reduce the odds of detaching.

  - > Use the enclosure to keep the print environment warm and reduce warping during fabrication

Demolding and cutting the cured device

- > Take molds out of oven and allow to cure to room temp

- > Carefully removed all the aluminum foil from the molds/wafers

- > Start demolding the PDMS by ensuring the PDMS is unstuck all along the perimeter for the mold

- > Keep gently demolding all the wells by gently demolding each corner of the device at sequentially and progressively

- > Once demolded, lay the demolded PDMS on a white sheet of paper with the feature side facing up

- > Place masking tape along the inner rectangle marks outlining the actual cut device dimensions on the PDMS. The tape should be long enough to stick to the paper, then go over the PDMS and back onto the paper. This will be done for all 4 sides of the rectangular device

- > Use the industrial paper cutter to cut the device into its rectangular dimensions from the whole demolded piece. The blade should be aligned with the masking tape placed along the inner rectangle dimensions

- > Use a razor blade to cut a small 45 degree angle at each corner of the cut out rectangular device. This will make it easy for the device to align in the frame.

- > Clean the device by applying and removing packing tape repeatedly to remove any particles that may be dirtying feature surface. Leave the tape on and remove right before placing in plasma cleaner

Bonding to glass

- > Place a blow-dried .17mm glass coverslip 110x74mm and the prepared PDMS device with tape removed in the plasma cleaner. In a cylindrical chamber, the glass can go below the platform sample with the PDMS device.

- > Plasma clean with pure O2 or dry ambient air with varying time power and pressure. For a Harrick Plasma PDC-001, plasma clean with dry air between 200 and 600 mTorr for 1min.

- > Move the PDMS device onto a clean nearby platform and with the plasma exposed side facing up

- > Hold the glass slide using index fingers and thumbs to hold the glass with the exposed side facing down

- > Bring the glass closer to the device, intermittently verifying that the glass is properly aligned with the device by making sure there is excess glass along all sides

- > Gently let go of the glass, allowing it to drop on the device. Gently press on the middle of the glass, spreading out horizontally then again vertically.

- > Heat is applied to the assembly for 1min+ at 100C to finalize the bond. The device can be flipped around to have the glass facing down and placed on a hotplate or in an oven with a large weight placed on the PDMS device to add pressure to further strengthen the bond.

- > The devices can then be autoclaved in a dry 121C cycle in Fisher instant seal sterilization pouches.

*Assembling to frame*

- > Fill a 3mL syringe with a 18GA needle with some loctite 5140 glue.

- > Take a 3D printed frame and place it with the bottom facing up.

- > Dispense about 0.5-1mL of glue to fill the grooves along the whole or the device

- > Grab the bonded device with index fingers and thumbs withthe device facing down and glass facing up

- > Align the devices with the rectangular insert for the device in the frame then gently let the device fall into place once aligned. The glass will lay on the glue on the frame.

- > Inspect that the glue has sealed the entire perimeter of the glass slide and frame device insert.

- > Let the glue dry for 3 days at room temperature before using the device.

- > Once cured, trim away any excess glue using a razor blade

*![Cell culture icon](media/image5.png) ![Culture workflow icon](media/image6.png) Culturing Cells*

- > Plasma-clean the assembled device in frame with the same conditions as bonding but leave for at least 10 minutes. This ensures that the surfaces are sterilized and that the glass and PDMS are hydrophilic. If you do not plasma clean or if you leave the surfaces exposed to air for more than 15 mins after plasma cleaning, aqueous solutions will not pass through the microchannels ruining the experiment.

- > The wells are all coated with 30ul of 10ug/ml dPGA for 10 minutes and washed with ddH2O once

- > Add 50uL NB+ to axonal compartment

- > Seed E18 Sprague Dawley rat cortical neurons in 50uL DMEM+ (5,000-10,000 cells/well) in cellbody compartment

- > After the cells have seeded for at least 30 minutes, media swap the cell body compartment with 50uL NB+

- > Remove 25uL from axon compartment, setting up a gradient 50ul-\>25uL  

Axotomy

- > ![CTB-647 timing icon](media/image7.png) Day prior to axotomy (day10), add 1ug/mL CtB-647 to the axonal cell body compartment. Ensure the volume in the cell body compartment is 2x the axonal after addition of ctb (Cellbody 50uL, Axon 25ul)

- > On the day of the axotomy, image the cells before axotomizing, with the brightfield and Ctb-647 channel (far-red/cy5)

- > Once the imaging is done, prepare a mixture of 0.25% trypsin and 0.0125% triton x-100. Remove all the media in the axonal compartment and replace with triton-x + trypsin mix. Make sure there is less volume of triton-x + trypsin in the axonal compartment than media in the cell body compartment like with the ctb addition ).

- > Wait 10 minutes

- > Wash the axonal wells 3 times with NB+

- > Add treatment conditions if wanted

- > Wait at least 24 hours for regeneration (can wait much longer if wanted)

*End point imaging:*

- > ![CTB-568 timing icon](media/image8.png) Day prior to endpoint (day end-1), add 1ug/mL CtB-568 to the axonal cell body compartment. Ensure the volume in the cell body compartment is 2x the axonal after addition of ctb (Cellbody 50uL, Axon 25ul)

- > On endpoint day, 1uM of calcein-AM to axonal compartment and image whole device

- > You may also stain for DAPI in the cell body compartment to count total cells in cell body compartment

- > When imaging, make sure you have a channel for calcein-AM (green, or red) and CtB (color of your choice except green) and optionally DAPI

- > The total regeneration can be quantified looking at calcein-AM stained axons in the axonal compartment

- > The number of neurons having regenerating axons is quantified by counting CtB positive cells in the cell body compartment, by prior and after axotomy.

- > The total number of seeded cells is quantified by counting DAPI positive cells in the cell body compartment

- > OpenHCS may be used for automated analysis
