### **I. Title**

- Concise and descriptive, reflecting the key innovation or application of the study.

### **II. Abstract**

- A brief summary of the purpose, methods, key results, and implications of the study.

### **III. Introduction**

- **A. Background and Motivation**

  - Introduction to the significance of microfluidic devices in neuroscience research (neuronal development, regeneration, and degeneration).

  - Current challenges with low-throughput devices, including limitations in scalability, cost, and compatibility with automation.

- **B. State of the Art**

  - Overview of existing microfluidic technologies and their limitations.

  - Specific challenges in fabricating high-throughput devices.

  - <u>Casting SU-8 using the glass photomask as the wafer and using a PDMS mold aligned on the glass substrate to contained the ultra thick casted SU-8 ( Takahiro Tamura, 2018</u>)

    - This method is expensive as a new photomask must be acquired for every device mold fabricated

    - Casting SU-8 is notoriously tricky and time consuming due to the difficulty in evaporating all solvents without creating internal stress which will lead to mold

  - <u>directly 3d printing tall PDMS walls to create large empty wells using a bioprinter (Janko Kajtez 2020)</u>

    - This works but requires the use of a bioprinter every single time a device needs to be made

    - The wells are fabricated once at a time in a serial manner which significantly lowers fabrication output

  - Laser cutting large wells from the PDMS device (Andrew W. Holle 2007)

    - The use of automated CO2 laser cutters with PDMS has been been well characterized and can be used to automate the removal of PDMS to create large wells in an automated manner

    - A slow speed and low laser power is required for maximum resolution of around 200um using a 750PPI laser @ 12W

    - However, a low laser power significantly reduces the ablation depth requiring multiple passes. This cannot be compensated for by increasing the speed since this also decreases ablation depth

    - On top of requiring multiple passes, only one well is formed at a time, leading a serial fabrication process which also limits device fabrication throughput

    - High performance Laser cutters are not readily available in most clean rooms and are very expensive

  - combining hot embossing and CNC milling using PMMA plastic to interface large and small features on the same mold

    - requires hot embosser and a CNC mill for microfabrication purposes, both of which are not readily available in all clean rooms

    - An extra master is required since a pre-polymer treated PDMS master for molding the device must be first fabricated out of the PMMA master

  - resin 3d printing the mold itself

    - printing a mold with a resin 3d printer is fast, straightforward and affordable, but has limited resolutions of around 50um, making it unsuitable for cellular neuroscience applications due to the requirement of channels of 20um wide and smaller

  - Resin 3D printing macro features directly onto SU-8 features (Jesper Y. Pan 2022)

    - 3D printed resin parts were interfaced with SU-8 on a silicon substrate

    - to achieve alignment between the 3D printer, the wafer is diced into individual chips, and the chips are placed in an alignment tray printed onto the build plate

    - because the first layers of resin are printed directly onto the SU-8, these layers may be printed larger at the interface resulting in a defect referred to as “elephant foot”

    - A printer with a very large build plate is required in order to perform this technique with 6” wafers which would be used for fabrication of a large high-throughput device

    - SU-8 features must be perfectly centered on wafer for proper alignment in order for this technique to work

  - Steel 3D printing well features to be glued onto the mold (Mervi Ristola 2019)

    - 3D printed well inserts align on SU-8 features using a lock and key mechanism, where a square hole made of SU8 locks in place with a protruding pin of the same dimension from under the insert

    - permanently integrates the well features on the mold for seamless creation of large wells in the casted PDMS devices

    - requires manual placing of indiviual well inserts which is time-consuming and error prone, limits amount of wells one can have on the mold

    - Requires expensive steel 3d printer which is not readily available in all clean rooms

- **C. Study Objective**

  - Clear statement of the study’s objective to develop a cost-effective, high-throughput microfluidic device using a novel fabrication method.

    - The gap in availability of affordable high-throughput devices

    - The need for methods compatible with automated systems and high-content screening

### **IV. Materials and Methods**

- **A. Materials and Equipment**

  - Detailed list of all materials, chemicals, and equipment used, including 3D printers, SU-8 photolithography tools, and Python software.

- **B. Device Design**

  - Description of the microfluidic device layout and design considerations.

  - Overview of the open-source Python script used for device design.

- **C. Fabrication Process**

  - Step-by-step explanation of the combined 3D printing and SU-8 photolithography method.

  - Specific details on the integration of large 3D-printed features with SU-8 features.

  - Process of PDMS curing and elimination of manual punching.

- **D. Functional Testing**

  - Description of the functional testing procedures for the fabricated devices, including any assays performed.

### **V. Results and Discussion**

- **A. Device Fabrication Outcomes**

  - Integration of resin 3D printing with SU-8 photolithography

  - Use of

  - Comparison with traditional fabrication methods, highlighting improvements in throughput and cost-effectiveness.

- **B. Functional Performance of the Device**

  - Results from using the device in axonal regeneration studies.

  - Effectiveness of the chemical axotomy method in inducing axonal injury.

- **C. Advantages and Limitations**

  - Discussion of the advantages of the new fabrication method, including its scalability, cost, and ease of use.

  - Consideration of any limitations or potential improvements for future iterations.

### **VI. Conclusion**

- **A. Summary of Findings**

  - Recap of the key outcomes, including the successful development of a high-throughput microfluidic device.

- **B. Implications for Future Research**

  - Discussion on how this new fabrication platform could be applied to other areas of neuroscience research.

  - Potential for the broader adoption of the method in academic and industrial settings.
