Prompt:  I'm confused about what is materials and methods vs what is results in this version of the manuscript

The confusion is understandable because your manuscript describes both the development of a fabrication method and the experimental validation of that method. As a result, several technical details could appear in either section.

For Lab on a Chip, I recommend a clear distinction:

Materials and Methods should explain how the molds and devices were fabricated and how their performance was evaluated. Results should explain what was achieved, which technical problems were overcome, and how well the devices performed.

For example, your draft describes the use of a compressible EPDM rubber backing to align 96 resin inserts despite differences in their printed heights.

The procedural details—rubber thickness, clamping arrangement, adhesive and curing conditions—belong in Materials and Methods. The observation that pin heights varied by 116 µm, that rigid clamping produced uneven contact, and that the compressible backing permitted simultaneous insert alignment belongs in Results.

1. How I would reorganize your manuscript
Your existing draft already has a reasonable Methods structure. I would retain most of its headings but reorganize the Results to tell a more compelling engineering story.



Materials and MethodsCorresponding Results
OpenMFD design and fabri	cation-file generationParametric design of medium-throughput microflui	dic devices
Hybrid mold fabricationDevelopment and optimization of reu	sable hybrid molds
PDMS casting and plate assemblyRepeated device fabr	ication and mold durability
Mold and device characterizationDevice int	egrity and compatibility with automated workflows
Fluorescent tracer assayDirectional fluid transport between compartments
Primary cortical neur	on culture and CTβ retrograde axon tracingNeuronal culture and compar	tment-specific axonal labeling
Imaging and cell countingIncorporated i	nto neuronal validation Results
Statistical analysisQuantitative outco	mes reported in the relevant Results sections
The important difference is that the Methods describe the experimental procedures, whereas the Results follow the engineering development and validation of the technology.

2. Specific examples from your draft
Example A: Fabrication optimization
Your current Results appropriately report several technical problems encountered during development:

Raised SUEX edges interfered with insert bonding.
SU-8 features detached when patterned directly onto silicon.
Differences in printed insert heights prevented uniform bonding with rigid clamping.
A compressible backing improved contact across the insert array.
These observations belong in Results because they demonstrate why particular design modifications were necessary.

By contrast, exposure energies, baking temperatures, solvent treatments, adhesive application and clamping procedures belong in Methods.

I would retain these optimization experiments because they provide evidence that your method solves genuine fabrication problems.

Example B: Mold durability
The statement that three molds produced more than 50 usable casts is a Result.

The procedure used to inspect molds and determine whether a cast was usable belongs in Methods.

However, I would strengthen this section by distinguishing the number of successful casts from mold survival over time. These are related but different measurements of durability.

Example C: Neuronal validation
Your Methods should specify the neuronal preparation, plating density, culture conditions, timing and concentration of CTβ treatment, imaging procedure and analysis criteria.

Your Results should report the observed axonal labeling, number of successfully analyzed devices, variability between plates and limitations in culture performance.

Importantly, the poorer neuronal growth at the plate edges is a Result, not a methodological detail to omit.

3. A recommended Results structure
I suggest six principal Results subsections:

1. Parametric design of medium-throughput microfluidic devices

Introduce OpenMFD, the coordinated generation of photomasks and insert arrays, the 48-device/96-well format, and the principal design features.

2. Development of reusable hybrid photolithographic–3D-printed molds

Describe the successful integration of SU-8/SUEX photolithography with printed inserts. This is where the optimization experiments involving SU-8 adhesion, SUEX exposure, insert alignment and compressible bonding should appear.

3. Reproducible fabrication and assembly of plate-format devices

Present the finished PDMS devices, elimination of manual well punching, repeated casting, mold durability and integration with the supporting frame.

4. Compatibility with automated liquid handling and high-content imaging

Demonstrate the 9 mm well spacing, multichannel pipetting and imaging on standard high-content microscopy systems.

5. Characterization of fluid transport between compartments

Present the fluorescent tracer experiments, including the observed directional redistribution and limitations of the measurements.

6. Validation of compartmentalized primary neuronal culture

Present neuronal survival and morphology, CTβ retrograde labeling, the 69 analyzed interior devices and the edge-related culture limitations.

The alternative device designs generated by OpenMFD could be incorporated into Section 1 or presented as a short final Results subsection demonstrating design flexibility, provided it is clear that those configurations were generated computationally but not fabricated or biologically tested.

4. One important editorial change
I would move most of the highly detailed fabrication information into the supplementary protocols while retaining the essential technical specifications in the main Materials and Methods.

Your current manuscript contains unusually detailed descriptions of printer settings, specific manufacturing steps and troubleshooting. That information is valuable for reproducibility, but presenting all of it in the main text risks obscuring the technological contribution.

For example, the main Methods should describe the SU-8/SUEX layer architecture, the resin-insert fabrication and alignment procedure, bonding conditions and parylene coating. The supplementary protocol can provide every exposure setting, printer movement parameter, washing step and detailed assembly instruction.

I would not shorten the Methods at the expense of reproducibility. Rather, I would organize the information so that readers can understand the procedure from the main manuscript and reproduce it precisely using the supplement.

5. Recommended next step
I recommend rewriting Materials and Methods first, using the existing draft as the technical source.

We should preserve the experimental details and numerical parameters, eliminate repetition, move observations and interpretations into Results, and identify any missing information needed for reproducibility.

Once that is complete, we can rewrite the Results around the six sections above. This will allow us to present the fabrication innovation much more effectively while ensuring that every experimental claim has a corresponding methodological description.

I've also opened a Work-mode session for a more detailed section-by-section review of the manuscript, where we can reorganize the actual Word document without losing the original technical content.



Figures 

One weakness is that Figures 2 and 3 primarily illustrate fabrication procedures rather than demonstrate fabrication performance.

For a stronger engineering manuscript, I would consider adding a quantitative characterization figure documenting mold yield, repeated casting performance, and microchannel geometry. This could substantially strengthen the Results without requiring an additional biological experiment.

I’ll also check the draft’s supplementary tables to see which quantitative panels can be made from measured data, and which would need additional experiments.

The supplementary tables contain enough measured data for a useful preliminary figure: all 96 insert-pin heights, mold outcomes (five assembled, three used routinely), and the reported total of more than 50 usable casts. The limitation is that the draft does not give exact cast counts per mold or measured channel dimensions, so I won’t imply those are available.



2. Sample quantitative characterization figure
Yes, you have enough data to produce a meaningful preliminary characterization figure, although additional measurements would strengthen it considerably.

I used data from Supplementary Tables S1 and S5 to generate three panels:



PanelMeasurementData available
A. Spatial variation in insert heightHeatma			p showing deviations in pin height across the 8 × 12 printed arrayAll	 96 individual measurements
B. Insert-height distributionHistogram sho	wing variability in 3D-printed insert heightsMean 5.551 mm; SD 26.7 µ	m; range 116 µm
C. Mold fabrication outcomesNumber of molds successfu	lly used versus molds lost during fabrication or handling3 routinely u	sed; 2 lost; 5 total
The first two panels are particularly useful because they quantitatively establish a technical challenge that your fabrication method addresses: substantial variation in the heights of simultaneously printed inserts.

The compressible EPDM backing is an important component of your innovation, and these measurements provide quantitative justification for its incorporation.

3. What is missing for a stronger figure?
For a fabrication-focused Lab on a Chip manuscript, I would ideally add two additional measurements.

Microchannel dimensional fidelity: Measure the width and height of several representative microchannels in finished PDMS devices. This would allow comparison with the nominal 10 µm width and demonstrate how accurately the photolithographic features are reproduced.

Repeated casting performance: Report the number of successful PDMS casts from each of the three reusable molds. If records are available, these could establish manufacturing consistency and provide a more informative measure of mold durability.

These experiments are more directly relevant to the central technological claims than additional biological assays.

4. My recommendation
I would develop the sample into a dedicated figure titled:

Figure X. Fabrication reproducibility and durability of hybrid photolithographic–3D-printed molds.

The strongest final version would include spatial variation in resin-insert heights, finished microchannel dimensions, and repeated casting performance.

Your current measurements are sufficient for an initial figure, but microchannel dimensional fidelity is the most important missing quantitative characterization.

That measurement would provide direct evidence that the hybrid mold retains the micrometer-scale precision needed for compartmentalized neuronal assays.





Sample_Quantitative_Device_Characterization.png





Editorial Assessment

One issue deserves particular attention before submission: The manuscript would benefit from direct measurements of finished microchannel dimensions. This would support the central claim that combining photolithography with 3D-printed inserts preserves the fine structures required for neuronal compartmentalization.



Figures



Recommendations for the figures in your Lab on a Chip manuscript
I reviewed the five figures in your original manuscript against the revised Results and Discussion. My main recommendation is to make the figures less like illustrations of a fabrication protocol and more like evidence supporting the technological innovation and experimental validation.

The existing figures contain most of the visual material you need, but their presentation could be substantially improved.

I would retain the five-figure structure, consider adding one quantitative fabrication-characterization figure, and standardize the legends.

1. Incorporating figure titles into legends
For Lab on a Chip, I recommend using a short, descriptive title as the first sentence of each figure legend, followed immediately by the explanation of the individual panels.

For example:

Fig. 1. Parametric design of hybrid molds for medium-throughput microfluidic devices. (A) OpenMFD generates coordinated fabrication files from shared design parameters. (B) Single-device photomask layout. (C) Wafer-scale photomask layout. (D) Three-dimensional models of individual well-forming inserts and the complete insert array. (E) Supporting plate-frame model. (F) Assembled microfluidic culture plate containing 48 two-compartment devices and 96 wells.

This is preferable to placing a large descriptive title within the figure itself and then repeating that title in the legend.

I suggest three conventions throughout the manuscript:

Within the figure: Use panel letters (A–F), concise labels, dimensions, and annotations necessary to interpret the images.
First sentence of the legend: State the principal message of the figure in bold.
Remaining legend: Explain the panels, relevant experimental conditions, sample sizes, and quantitative measurements.
The figure titles should communicate what each figure demonstrates, not simply describe its contents.

For instance, Development of reusable hybrid molds for wafer-scale microfluidic fabrication is stronger than Insert transfer and wafer bonding for the hybrid mold.

2. Figure-by-figure recommendations
Figure 1. Parametric design and device architecture
Current figure: Page 13 of the original manuscript.

This figure shows the OpenMFD design interface, photomasks, individual resin inserts, insert arrays, supporting frame, and assembled device.

The essential information is present, but the figure is visually fragmented. The software outputs and photographs are displayed at different scales, and the relationships between the components are not immediately obvious.

Suggested improvements

Make the central message that one parametric design generates every component necessary to manufacture the device.

I would retain the existing panels but reorganize them into a more continuous workflow:

OpenMFD parameters → Photomasks and resin inserts → Reusable mold → Complete microfluidic plate

I would particularly recommend adding a larger schematic of one two-compartment device showing the wells and connecting microchannels. The current figure does not sufficiently emphasize the neuronal compartmentalization geometry.

The 48-device/96-well organization and 9 mm spacing should also be clearly indicated.

Proposed title and legend

Fig. 1. Parametric design enables coordinated fabrication of medium-throughput microfluidic devices. (A) OpenMFD generates matched photolithographic masks, three-dimensional resin inserts, and supporting plate components from shared design parameters. (B) Schematic of an individual two-compartment device showing culture wells connected by parallel microchannels. (C) Wafer-scale photomask layout containing 48 two-compartment devices. (D) Models of individual resin inserts and the complete 96-insert array. (E) Three-dimensional model of the supporting plate frame. (F) Assembled PDMS microfluidic plate containing 96 wells arranged on a standard 9 mm grid.

Note: Panel B would require modifying the existing figure.

Figure 2. Hybrid mold fabrication and alignment
Current figure: Page 14.

This is potentially one of the most important figures because it illustrates your central engineering innovation.

However, the current arrangement gives similar visual emphasis to the clamping equipment, alignment geometry, and photographs of the bonded inserts.

I would make the simultaneous alignment of 96 inserts the dominant visual element.

The figure should establish how the shared coordinate system, corresponding pins and holes, and compressible backing work together.

I recommend emphasizing the following features:

Registration of the entire resin-insert array with the wafer.
Enlargement of the square alignment pin and SUEX opening.
Cross-sectional schematic showing the compressible EPDM backing.
Photograph of the successfully assembled mold.
The 1.85 mm pin, 2.00 mm opening, and 75 µm clearance per side should remain clearly labeled.

Proposed title and legend

Fig. 2. Simultaneous alignment and integration of 3D-printed inserts into reusable photolithographic molds. (A) Patterned silicon wafer and resin-insert array before assembly. (B) Schematic of the alignment interface showing the 1.85 × 1.85 mm resin pin positioned within a 2.0 × 2.0 mm SUEX opening, providing 75 µm nominal clearance per side. (C) Clamping assembly used to bond the inserts to the wafer. (D) Cross-sectional schematic illustrating the compressible EPDM backing used to accommodate variations in insert height. (E) Photograph of bonded resin inserts. (F) Micrograph of the patterned SUEX alignment openings.

I would consider incorporating the measured 116 µm variation in insert height into this figure as a quantitative panel. That would directly connect the engineering problem with the solution shown.

Figure 3. Repeated casting and plate assembly
Current figure: Page 15.

This figure illustrates PDMS pouring, degassing, curing, demolding, trimming, bonding, and frame assembly.

Although informative, it is currently closer to a supplementary fabrication protocol than a central Results figure.

I would simplify it considerably.

The central message should be:

One reusable hybrid mold produces multiple complete microfluidic plates without additional well punching.

I would retain a clear schematic of the principal stages and move some of the more detailed assembly photographs to the supplementary information.

Ideally, this figure would also include a quantitative demonstration of mold reuse.

Proposed title and legend

Fig. 3. Repeated fabrication of plate-format microfluidic devices using reusable hybrid molds. Schematic illustrating the production of complete PDMS microfluidic arrays from a reusable silicon-wafer mold. PDMS is cast over the hybrid mold, degassed, cured, and demolded to produce 48 two-compartment devices with 96 preformed culture wells. Each cast is trimmed, plasma-bonded to glass, and incorporated into a supporting plate frame. Because the resin inserts remain attached to the mold, subsequent casting cycles generate all culture wells without individual punching. Three molds collectively produced more than 50 usable casts.

For the last sentence, adding a quantitative panel would be particularly valuable.

Figure 4. Functional validation of neuronal microfluidic devices
Current figure: Page 16.

This is the most important biological validation figure and, in my opinion, the one that would benefit most from substantial revision.

The current figure combines fluorescent tracer redistribution, CTβ-labeled neurons, and quantitative neuronal labeling. These are appropriate experiments, but the small images make it difficult to assess the results.

Suggested improvements

I would reorganize Figure 4 into five panels:

A. Experimental schematic: Show a two-compartment device indicating the direction of fluid movement and the site of CTβ application.

B. Fluid transport: Retain the fluorescent tracer images at 0 and 72 hours, but enlarge representative devices so that redistribution between compartments is evident.

C. Neuronal culture: Include a high-resolution image illustrating neuronal cell bodies, microchannels, and axonal extension. A representative image spanning both compartments would be particularly informative.

D. Retrograde labeling: Include higher-magnification images showing CTβ-positive neuronal cell bodies following tracer administration to the axonal compartment.

E. Quantitative analysis: Retain the CTβ-positive cell count data, but consider displaying individual device measurements rather than only the plate means and standard deviations.

Displaying individual data points would demonstrate the range of responses across the 69 analyzed devices. It would also avoid creating the impression that the three plates represent independent biological replicates.

Proposed title and legend

Fig. 4. Functional validation of compartmentalized neuronal culture and retrograde axonal labeling. (A) Schematic illustrating the two-compartment microfluidic architecture, direction of fluid movement established by a hydrostatic volume difference, and selective application of CTβ to the axonal compartment. (B) Fluorescence images showing tracer distributions immediately after loading and following 72 h of incubation. Alexa Fluor 568-conjugated antibody (red) and Alexa Fluor 488-conjugated antibody (green) were introduced into opposite compartments at initial volumes of 25 and 50 µL, respectively (24 devices). (C) Representative image of primary cortical neurons cultured in the microfluidic devices at DIV11. (D) Representative fluorescence images showing retrogradely labeled neuronal cell bodies following application of CTβ-647 to the axonal compartment at DIV10. (E) Quantification of CTβ-positive neuronal cell bodies across three independently assembled plates. Data represent 69 analyzed interior devices derived from one embryonic neuronal preparation; devices and plates are technical replicates.

Panels A and C would require additional figure preparation. Panel E could be improved using the existing individual cell-count dataset.

I would also ensure that all fluorescence micrographs have appropriate scale bars.

Figure 5. Adaptability of the fabrication approach
Current figure: Page 17.

This figure shows OpenMFD-generated designs for three alternative applications:

Oligodendrocyte myelination.
Axon guidance.
Three-compartment neuronal culture.
The scientific purpose is appropriate, but the figure currently contains considerable redundancy because each design is represented by several very similar software outputs.

I would simplify the figure into three rows, one for each application, with three columns:



ApplicationDevice geometryCorresponding resin-insert array
MyelinationTwo 			cell populations connected by microchannelsMatched insert configuratio	n
Axon guidanceOrthogonal compartment arrangementMatched insert confi		guration
Three-compartment cultureThree interconnected compartmentsMa		tched insert configuration
The wafer-scale layout could be included as a small inset rather than a separate full-sized panel.

Proposed title and legend

Fig. 5. Parametric generation of alternative compartmentalized microfluidic device configurations. OpenMFD-generated photomasks and corresponding resin-insert arrays for three literature-inspired microfluidic architectures. (A, B) Configuration for studying oligodendrocyte myelination and neuron–glia interactions. (C, D) Configuration incorporating orthogonal compartments for axon-guidance experiments. (E, F) Three-compartment neuronal culture configuration. For each design, changes in compartment geometry, well arrangement, and microchannel organization are incorporated into matched photolithographic and three-dimensional fabrication files. These configurations were generated computationally and have not been fabricated or experimentally validated.

One important point: I would make it clear within the figure itself that these are computational designs, not experimentally validated devices.

3. Should you add a quantitative characterization figure?
Yes. I believe this would be the single most valuable improvement to the manuscript.

The strongest publications describing new microfabrication technologies generally combine an explanation of the fabrication process with quantitative evidence of manufacturing performance.

Currently, your manuscript contains excellent illustrations of how the devices are made, but less quantitative evidence demonstrating how reliably they can be manufactured.

I recommend developing a new figure with the following structure.

Proposed Figure 6. Quantitative characterization of hybrid mold fabrication


PanelC	ontentAvailability
AHeatmap of measured insert-height variation acros		s the 96-position arrayAvailable
BDistribution of individual insert h		eightsAvailable
CMold fabrication outcomes and repeated casting perfo		rmancePartially available
DMeasured microchannel widths in finished P		DMS devicesAdditional measurements required
EComparison of microchann		el dimensions between successive casts or different moldsAdditional me	asurements required
The existing measurements provide a mean pin height of 5.551 mm, standard deviation of 26.7 µm, and range of 116 µm. These results are directly relevant to the compressible alignment method.

However, I would not present the three usable molds out of five assembled molds as a general manufacturing success rate without explaining the two failures and the limited sample size.

The most important new measurement would be the dimensional accuracy of the microchannels in the finished PDMS devices.

Suggested title and legend

Fig. 6. Quantitative characterization of hybrid mold fabrication and device reproducibility. (A) Spatial distribution of measured resin-insert heights across a 96-position array, expressed as deviations from the mean. (B) Distribution of insert heights (mean, 5.551 mm; standard deviation, 26.7 µm; range, 116 µm). (C) Fabrication outcomes for five hybrid molds, three of which entered routine use and collectively produced more than 50 usable PDMS casts. (D, E) Proposed quantitative measurements of microchannel dimensional fidelity and variation between successive PDMS casts.

Panels D and E should only be included once actual measurements are available.

An alternative would be to combine this quantitative figure with the existing Figure 2, producing a stronger composite figure that links fabrication challenges, engineering solutions, and manufacturing performance. This would avoid increasing the number of main figures.

4. Additional recommendations for figure presentation
There are several changes I would apply consistently.

Remove the large titles embedded within the figures. The current figures sometimes contain descriptive headings that duplicate information in the legends. These take up space and reduce the size available for scientific images. The short bold title at the beginning of the figure legend should carry that information.

Use consistent labeling. Panel letters should be placed in the same position, using the same font and size, throughout all figures. I recommend capital letters (A, B, C) and a consistent sans-serif font for labels within figures. Your manuscript text and Word figure legends will continue to use Times New Roman, 12 pt, black, justified, and single-spaced.

Emphasize quantitative findings. Where possible, integrate measurements directly into the relevant figure rather than placing all numerical information in supplementary tables.

Make the microchannels more visible. The connecting microchannels are central to the biological application and technical demands of the platform. At least one figure should show them clearly at high magnification.

Reduce unnecessary photographs of equipment. Photographs of clamps, racks, and assembly stages can be useful for reproducibility but are often better suited to supplementary protocols. The main figures should prioritize the fabricated structures and evidence of device performance.

5. Recommended final figure organization
I would ultimately aim for five main figures rather than six:



Final figurePrincipal messageSource
Figure 1			Parametric design generates coordinated fabrication componentsRevised 	existing Fig. 1
Figure 2Hybrid fabrication enables simultaneous insert	 alignment, with quantitative validationExisting Fig. 2 + characteriza	tion data
Figure 3Reusable molds enable repeated fabrication of comple	te plate-format devicesRevised existing Fig. 3
Figure 4Devices suppor		t directional fluid movement and compartmentalized neuronal assaysExpa	nded existing Fig. 4
Figure 5The design framework accommodates alterna	tive microfluidic architecturesSimplified existing Fig. 5
If you obtai	n quantitative measurements of microchannel fidelity and between-cast reproducibility, a dedicated sixth figure may become justified.

My recommendation
I would prioritize revisions in this order:

First, improve Figure 2 by integrating the existing insert-height measurements with the alignment and bonding schematics. This would strengthen the presentation of the central engineering innovation.

Second, improve Figure 4 by adding larger representative neuronal images and displaying the individual CTβ-positive cell counts. This would make the biological validation more convincing.

Third, simplify Figures 1, 3, and 5 to remove redundant information and establish a consistent visual style.

The central principle should be that each figure demonstrates one important finding from the Results, while the figure legend provides the experimental detail necessary to interpret it.

I would also keep the legends reasonably concise—ideally approximately 60–120 words each, depending on the number and complexity of panels—rather than repeating extensive methodological descriptions already provided in Materials and Methods.

This is a conceptual layout only, not a presentation of experimental results. The microscopy images and individual data points are illustrative and must be replaced with your actual data before publication.

PastedGraphic-1.png

Prompt: are all figures including supplemental figures explained and cited in the manuscript draft. Is the supplemental material appropriate and what modifications would you suggest

Review of figures and Supplementary Information — Lab on a Chip
Overall, the supplementary material is appropriate for a methods-development manuscript, but I identified several issues that should be corrected before submission.

I reviewed the latest expanded manuscript, including the five main figures, two supplementary figures, six supplementary tables, two supplementary notes, and two detailed fabrication and experimental protocols.

The main findings are:

All five main figures are cited in the manuscript, and their content generally corresponds to the Results.
Neither Supplementary Figure S1 nor Supplementary Figure S2 is explicitly cited in the main manuscript.Both are discussed indirectly through references to Supplementary Notes S1 and S2.
Supplementary Table S2 is not cited anywhere in the main manuscript. It contains a useful comparison of existing microfluidic fabrication approaches.
The remaining supplementary tables, notes, and protocols are referenced.
Some supplementary information could be reorganized to improve readability and strengthen the evidence supporting the fabrication method.
I would retain most of the supplementary content. For a Lab on a Chip manuscript introducing a fabrication technology, detailed protocols, printing parameters, design specifications, and quantitative measurements are particularly valuable.

1. Audit of the main figures


FigureC	ontentCited in main text?Assessment
Figure 1OpenMFD design, fabricat			ion files, and assembled deviceYes — Methods and ResultsAppropriate		
Figure 2Insert alignment and hybrid mold assemblyYes — Methods and		 ResultsAppropriate
Figure 3Repeated PDMS casting and plate assembly			Yes — ResultsAppropriate
Figure 4Directional tracer movement and ne		uronal validationYes — ResultsAppropriate, with some qualifications		
Figure 5Alternative microfluidic configurations generated by OpenMFD		Yes — ResultsAppropriate
Figure 4 warrants particular attention
The 	manuscript appropriately cites Figure 4A for fluorescent tracer redistribution, Figure 4B for CTβ retrograde labeling, and Figure 4C for neuronal cell counts.

The interpretation is also appropriately cautious: the tracer experiment demonstrates redistribution but does not establish sustained fluidic isolation, and the neuronal experiments involve three technical-replicate plates derived from one embryonic preparation.

I would retain those qualifications.

One minor modification is needed in the Figure 5 legend. It still identifies the source papers using author–year citations, whereas you have established a preference for PMIDs throughout this manuscript. These should be converted to the corresponding verified PMIDs.

2. Audit of the supplementary material


Supplementary itemCited in main manuscript?Assessment an		d recommendation
Figure S1 — Effect of LP360 filtering on SUEXNo dir	ect citationRetain. Add an explicit citation in the fabrication-optimi	zation Results.
Figure S2 — SU-8 delaminationNo direct citationReta		in. Directly supports an important fabrication challenge. Add a Results citation.
Table S1 — Resin-insert height measurementsYesEssential. 		Keep the 96 individual measurements. Improve table formatting.
Table S2 — Comparison of fabrication approachesNoUseful but needs revision. Cit		e in the Introduction, simplify the comparison, and standardize references.
Table S3 — Design parameters and validation checksYesVery valuable. Reta		in, but improve readability and distinguish validated parameters from design assumptions.
Table S4 — Resin-printing parametersYesEssential for r		eproducibility. Retain.
Table S5 — Mold fabrication and casting outcomesYesImportant but insufficiently quantitative. Add individual mold-prod		uction records if available.
Table S6 — HIPS frame-printing settings	YesAppropriate. Retain.
Note S1 — LP360 exposure optimizationYesAppropriate, but explici			tly reference Figure S1 within the note.
Note S2 — SU-8 adhesion and thermal processingYesAppropriate, but explicitly reference Figure S2 within t		he note.
Protocol S1 — Device assembly and neuronal cultureYesEssen		tial. Retain the detailed protocol.
Protocol S2 — Hybrid mold fabricationYesEssential. This is one of the most valuable components of the s		upplementary material.
Supplementary Figures S1 and S2
These are scientifically relevant because they document technical problems encountered during fabrication.

Figure S1 provides a qualitative comparison of SUEX structures exposed with and without the LP360 filter. This supports your observation that the filter reduces raised-edge artifacts.

Figure S2 shows SU-8 delamination when microchannel features are patterned directly onto silicon without the continuous SU-8 base layer.

Both images provide useful evidence supporting the rationale for fabrication optimization.

I would add these references directly to the Results.

For Figure S1, the relevant Results sentence could be revised to:

Incorporating the LP360 long-pass filter substantially reduced the raised-edge artifacts observed following unfiltered SUEX exposure, producing visibly flatter surfaces suitable for resin-insert bonding (Supplementary Fig. S1).

For Figure S2:

SU-8 microchannel structures patterned directly onto silicon exhibited delamination during subsequent processing (Supplementary Fig. S2), whereas incorporating a continuous, flood-exposed SU-8 base layer prevented this observed failure.

I would also add explicit references to the figures within Supplementary Notes S1 and S2.

One potential improvement: Figure S2 currently documents the unsuccessful fabrication condition. A corresponding image showing intact SU-8 structures following incorporation of the base layer would provide a more convincing visual demonstration of the improvement.

Similarly, Figure S1 is qualitative. Quantitative measurements of the raised-edge features would strengthen the comparison, although they are not essential to retain the figure.

3. Supplementary Table S2 needs attention
This is probably the supplementary table I would revise most substantially.

It compares approximately ten fabrication approaches, including conventional soft lithography, hot embossing, 3D printing, hybrid molding, and commercial devices.

This comparison is relevant because the novelty of your manuscript depends on clearly distinguishing your fabrication strategy from earlier multiscale approaches.

However, I identified three problems.

First, Table S2 is not cited in the Introduction or Discussion. I would add a reference to it in the Introduction, where previous fabrication strategies are described.

A suitable sentence would be:

Existing approaches for integrating micrometer-scale channels with millimeter-scale culture compartments differ in their requirements for specialized equipment, mold preparation, component alignment, and repeated device production (Supplementary Table S2).

Second, the table is difficult to read. The six columns contain considerable text, and several rows extend across multiple pages.

I would shorten the entries substantially and consider using a landscape page orientation.

Third, the representative references are currently given largely in author–year format. These should be converted to your established PMID convention, using DOIs only when a verified PMID is unavailable.

I would also describe the table as a qualitative comparison of fabrication strategies, not a quantitative comparison of manufacturing efficiency. The manuscript does not contain experiments directly comparing fabrication time, costs, yields, or dimensional accuracy across the different approaches.

4. The supplementary tables need formatting improvements
I inspected the rendered supplementary pages, and this is a significant presentation issue.

Supplementary Table S1: Some numerical values wrap across lines because the columns are too narrow. For measurements reported to three decimal places, this makes the data difficult to interpret and creates a risk of transcription errors.

Supplementary Tables S2 and S3: These are particularly difficult to read. Their narrow columns produce substantial text wrapping, and individual tables extend across several pages.

Supplementary Tables S4 and S6: These are easier to follow because they largely contain two-column lists of printing parameters.

My recommendation is to prepare the Supplementary Information as a separate document, using landscape orientation for Tables S1–S3 and portrait orientation for the remaining material.

I would also provide the individual height measurements from Table S1 as a CSV file.

This is consistent with RSC guidance, which encourages accessible, machine-readable supporting data and notes that supplementary files are published without editorial reformatting. Royal Society of Chemistry

5. Supplementary Table S5 should provide more quantitative manufacturing information
Table S5 currently reports that five hybrid molds were assembled, three entered routine use, two were lost, and the three working molds collectively produced more than 50 usable casts.

These are useful findings, but the table would be substantially stronger if it contained mold-specific production data.

Ideally, each mold would have an individual record of the number of casts attempted, number meeting the acceptance criteria, reason for failure or retirement, and duration of use.

This would allow readers to distinguish initial fabrication success from mold durability and casting reproducibility.

If those records are unavailable, I would retain the existing summary but avoid implying that a precise manufacturing yield has been established.

I would also ensure that the supplementary definition of a usable cast is presented clearly as an inspection-based criterion, rather than implying that channel dimensional accuracy was measured.

6. Are the supplementary protocols appropriate?
Yes. I would retain both protocols, including their detailed experimental parameters.

In fact, they are particularly valuable for a manuscript introducing a fabrication method intended for adoption by other laboratories.

Supplementary Protocol S2 describes the novel hybrid-mold fabrication process and should remain comprehensive. Details such as photoresist processing, insert transfer, alignment, adhesive curing, parylene deposition, and demolding are central to reproducibility.

Supplementary Protocol S1 provides the corresponding procedures for casting, device assembly, neuronal culture, tracer application, and imaging.

The division between these protocols is logical: one describes the specialized fabrication of the reusable mold, while the other explains how the mold is used to produce and operate experimental devices.

I would make only modest editorial changes, primarily eliminating duplicated explanations and ensuring consistency with the main Materials and Methods.

One specific detail deserves clarification. Protocol S1 refers to neuronal images acquired before axotomy in a particular experiment. Since axotomy is not presented as an experimental endpoint in this manuscript, I would clarify that these are baseline measurements from an experiment conducted before axotomy, rather than imply that axotomy was part of the reported validation.

7. Additional items that should be addressed before submission
A. Provide the underlying neuronal count data
The manuscript reports CTβ-positive neuronal cell counts from 69 interior devices, but the individual measurements are not included in the supplementary tables.

The Data Availability statement indicates that these data will be deposited.

I recommend supplying a CSV file containing the per-device counts, together with plate and device identifiers and an explicit record of the three excluded devices.

This would allow reviewers to evaluate the variability represented in Figure 4C.

B. Provide a complete set of fabrication files
An unusual advantage of your manuscript is that the complete fabrication design can be made available.

Lab on a Chip specifically encourages authors to submit chip-design masks as electronic supplementary information. Royal Society of Chemistry

I recommend ensuring that the downloadable package contains the actual photomask DXF files, insert STL files, frame designs, and the version of OpenMFD used to generate the reported devices.

The printing G-code and microscope XML files should also be included or linked to a stable repository.

Providing a permanently archived software release with a DOI would be preferable to relying exclusively on a GitHub repository that may change.

C. Standardize references throughout the supplement
Several supplementary items still use author–year references, including Table S2, the Figure 5 legend, and portions of the protocols.

These should be reconciled with the PMID-based citations used in the manuscript.

For final submission, note that Lab on a Chip requires numbered superscript citations and a numbered reference list. The PMIDs can remain in your working draft and be converted during final reference formatting. Royal Society of Chemistry

D. Add a complete animal ethics statement
The supplementary neuronal culture protocol states that the embryonic cortical neurons were prepared under an approved animal-use procedure.

However, the main Materials and Methods does not identify the approving institution or protocol number.

I recommend adding this information to the main manuscript, using the actual approval details. RSC's author guidelines require appropriate ethical reporting for studies involving animals. Royal Society of Chemistry

E. Correct the placement of the Data Availability statement
The latest manuscript places Data availability before Conflict of Interest Statement.

RSC specifies the reverse order: the Data Availability statement should follow the conflicts-of-interest statement and precede the Acknowledgements. Royal Society of Chemistry

This is a straightforward correction.

8. Recommended final organization of the Supplementary Information
I would organize it into three components.



ComponentContents
Supplementary M	ethodsProtocol S1: PDMS casting, assembly, neuronal culture and assays	. Protocol S2: Hybrid mold fabrication.
Supplementary Characterization and DesignFigures S1–S2, Notes S1–S2, Tables S1–S3 and S5.
Supplementary Fabrication 	ParametersTables S4 and S6, with associated G-code, CAD files and micr	oscopy settings available separately.
This would create a more logical distinction between the instructions needed to reproduce the device and the experimental evidence supporting the fabrication method.

I would keep the source CAD and numerical datasets in machine-readable formats rather than relying solely on tables embedded in a Word document.

9. Overall recommendation
I would retain all five main figures, both supplementary figures, and most of the existing supplementary material.The content is scientifically relevant and broadly appropriate for Lab on a Chip.

My priorities, in order, would be:

Correct the missing citations to Supplementary Figures S1–S2 and Table S2.
Reformat Supplementary Tables S1–S3, especially the numerical measurements and wide comparison tables.
Add the underlying CTβ cell-count dataset and more detailed mold-production records, if available.
Standardize the references and clarify the baseline neuronal imaging experiment.
Prepare a separate, well-organized Supplementary Information document and an archived package of the fabrication files.
The supplementary material is already one of the stronger aspects of the manuscript because it provides unusually detailed instructions for reproducing the fabrication process.

The most significant remaining weakness is not the quantity of supporting information, but the limited quantitative characterization of mold performance and finished microchannel geometry.

Providing those measurements would strengthen both the main Results and the Supplementary Information.

I would address the citation and formatting problems now, while treating additional microchannel measurements and mold-specific production records as the highest-value experimental improvements before submission.
