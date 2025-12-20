Neuronal development encompasses a complex series of processes including cellular migration, directed axon growth, synapse formation, programmed cell death and myelination. In-vitro studies on neuronal cell cultures have been instrumental in elucidating the molecular and cellular mechanisms supporting these processes. Commercially available cell culture devices that have supported these studies include Dunn chambers for the study of axon guidance, compartmented culture chambers to study axonal and cell body phenotypes and microfluidic chambers for selective drug delivery to the axonal and cell body compartment (ADD REFERENCES). Despite their commercial availability, these devices are low-throughput, prohibitively expensive for use in screens and limited in design. Creation of affordable and customizable devices that could be tailored to specific biological questions would be a major advance for the neuronal development field. We propose to develop and validate an open science platform for the design and creation of microfluidic devices that can be used to study axon guidance, synapse formation, programmed cell death and myelination in a high throughput and affordable manner. We will design and publish an open-source python library designed to create microfluidic device layouts. The software will facilitate device design by abstracting the tedious combinations of low-level operations required to create and modify device layouts. This includes the creation of wells, chambers, channels, mask alignment features as well as tiling the layout to create high-throughput versions of the device. The output file of the design can then directly be sent to film photomask printing services to be used during fabrication. The second part of the platform will consist of a protocol for creating the mold for each provided example device to teach the principles of SU-8 mold lithography for the creation of microfluidic devices. While fabrication recipes are available in most papers showcasing custom microfluidic devices, they are specific to the presented design and fail to provide sufficient instructions for reproduction. We will describe key fabrication parameters and potential fabrication artifacts to enable researchers to reliably follow the fabrication process to generate their own devices. This open-science initiative will enable any researcher with access to a clean room and basic python knowledge to produce microfluidic devices with designs from a published python software package as well as create their own designs from scratch using the tools provided.

- Note that the 48/96 well plate format on glass bottom substrate would permit for high content live imaging or fixed imaging to capture phenotypes with multiple replicates.

- Device to punch out the individual holes

Microfluidic devices are an incredibly valuable tool for in-vitro cellular neuroscience research. From neuronal development, to regeneration and degeneration, a wide variety of devices have been designed to perform specific assays to study the cellular and molecular mechanisms of these processes. Fabrication of these devices using polydimethylsiloxane (PDMS) soft lithography with SU-8 based molds have been reported and are standard since 2005. However, to this day, most published and commercially available devices are low-throughput, only allowing a few replicates per device, and are not compatible with multichannel pipettes, automated liquid handling robots and high-content screening microscopes. Unfortunately, the very few commercially available high-throughput devices are prohibitively expensive for most academic research. The main difficulty in fabricating high-throughput microfluidic devices containing arrays of large and cleanly formed wells is the necessity to manually punch out PDMS to form the wells. This is due to the difficulty in creating structures thicker than 1mm using SU-8. To resolve this issue, we present a method combining the use of affordable commercially available resin 3D printers and SU-8 photolithography using standard clean room equipment. By interfacing 3D printed well features onto the wafer with heat-curing glue, large features up to multiple millimetres to centimeters tall can be interfaced with SU-8 features as fine as 1um. Integration of these large well features on the mold allow for the formation of wells during PDMS curing, entirely skipping the need for punching wells out. Furthermore, we present an open-source python script designed to create microfluidic device layouts. The software will facilitate the device design and fabrication by abstracting the tedious combinations of low-level operations required to create and modify device layouts. This includes the creation of microchannels, wells, mask alignment features, 3D printed features as well as tiling the layout to create high-throughput versions of the device. Using our microfluidic fabrication platform, we made a high-throughput device in the format of a 96-well plate to study axonal regeneration. Using this device, we selectively injured cortical neuron axons through chemical axotomy, a new reliable axotomy method that is performed by simple automatable liquid handling. This platform will enable any researcher with access to a clean room and basic python knowledge to produce their own or published microfluidic devices designs in a high-throughput format in a rapid and cost-effective manner.

Aim 1 – Development of a high throughput microfluidic platform for the study of axon guidance.

96 well format.

Same cue in both to look at repulsion/attraction

? of how the dual gradients could be harnessed to understand the biology.

Optimized for different types of neurons.

Cortical –attractive NT-3 and repulsive ?

Retinal – attractive ephrin and a repulsive slit

<img src="media/image1.png" style="width:2.64792in;height:2.81528in" alt="A picture containing graphical user interface Description automatically generated" /><img src="media/image2.png" style="width:3.18472in;height:1.92014in" alt="Diagram Description automatically generated" />

Aim 2 – Development of a platform for synapse formation

State of the art. COS cell assays and dissociated neuronal cultures.

3 compartment device

Neuron to neuron synapse formation or neuron to COS cell synapse formation

Genetic manipulation of pre and post synaptic neurons concurrently.

96 well plate high throughput and high likelihood of synaptic contacts to improve throughput.

Potential to apply drugs to pre or post synaptic neurons. DREADDS in the pre-synaptic neuron compartment or post synaptic with genetically modified neurons to affect the activity of the pre-synaptic neuron or post synaptic neuron. Different treatments on the two populations of pre-synaptic neurons could provide for internal controls to assess synapse outcomes.

Cortical neurons and retinal neurons with neurexin and neuroligin as proof of principal both in neuronal culture and on COS cells.

DREADDS and activity and synapse formation?

<img src="media/image3.png" style="width:6.5in;height:3.74236in" alt="Chart Description automatically generated with medium confidence" />

Aim 3 – Development of a platform for programmed cell death

Neurotrophin withdrawal. Compartmentalized culture will allow for assessements of degeneration in axon and cell body compartment.

eNeuro. 2021 Jan 21;8(1):ENEURO.0277-20.2020.

[Neuronally Enriched RUFY3 Is Required for Caspase-Mediated Axon **Degeneration**.](https://pubmed.ncbi.nlm.nih.gov/31221560/)

Hertz NT, et al. Among authors: **tessier lavigne m**. Neuron. 2019. PMID: 31221560

Improve accessibility for current devices.

Add a microfluidic component to assess axons vs cell body treatments. BUT much of this may have already been done.

[Structural plasticity of actin-spectrin membrane skeleton and functional role of actin and spectrin in axon **degeneration**.](https://pubmed.ncbi.nlm.nih.gov/31042147/)

Wang G, et al. Among authors: **tessier lavigne m**. Elife. 2019. PMID: 31042147

[An anterograde pathway for sensory axon **degeneration** gated by a cytoplasmic action of the transcriptional regulator P53.](https://pubmed.ncbi.nlm.nih.gov/33823136/)

Simon DJ, et al. Among authors: **tessier lavigne m**. Dev Cell. 2021. PMID: 33823136

Aim 4 – Development of a platform for myelination

Straight axon growth into the second chamber by regulating flow prior to seeding OLs.

Cite paper showing straight growth through central compartment

Cortical neurons + OLs.

<img src="media/image4.png" style="width:6.5in;height:3.65486in" alt="Diagram Description automatically generated" />
