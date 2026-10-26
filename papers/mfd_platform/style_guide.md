# MFD Platform Manuscript Style Guide

## Voice

- Write as a biology-facing platform paper, not as an internal engineering report. Describe physical relationships plainly: `75 µm of space on each side`, not `nominal clearance`. Say when a value comes from the design rather than a measurement without burying that distinction in engineering jargon.
- Avoid rhetorical `Here, we...` openings. Use `We...` directly; the author prefers this voice.
- Lead with the experimental or fabrication consequence, then explain the implementation detail. Use Alyson Fournier's actual publications to calibrate those explanations while keeping other Lab on a Chip readers in view: explain unfamiliar fabrication to a neuronal researcher and the biological purpose to a fabrication researcher. Do not invent a stereotyped reader persona.
- Keep explaining why: connect each result to the practical problem it addresses, the reason for the observation, and what it enables or changes. Make that connection understandable without specialist knowledge where possible; do not replace an explanation with a verdict or a list of steps.
- Explain OpenMFD through the coordination problem it solves; keep the reusable hybrid mold and cast-in-place wells as the main story. Briefly explain that separate channel and well patterns and printed inserts must line up, so changing dimensions requires corresponding changes in several files. Then explain how shared inputs produce matching outputs (Figure 1). Give enough context to make the software's purpose intuitive without a programming tutorial or repeated file inventories; name implementation libraries afterward in Methods.
- Keep the biological question distinct from the mechanism of a probe. Neuronal culture and separately accessible axons provide the basis for downstream assays; CTB labeling helps demonstrate that axonal access. Do not turn use of CTB into a separate transport-mechanism study, or claim every neuronal assay requires it. Cite actual primary examples for its use.
- Explain observations, their purpose and their real limits in ordinary language. Delete sentences that merely classify a readout or repeat a scope label: `The readout is qualitative tracer redistribution` adds nothing after saying which fluorescence was compared. Keep useful limits, such as what two imaging time points cannot establish; do not replace explanation with formal-sounding assay commentary.
- Describe each inspection at the right physical object and stage. The PDMS–glass seal was checked before autoclaving; printed frames were checked for flatness and warping. Do not turn either into an unperformed quantitative test or infer frame-joint leak testing from adhesive use.
- Write positively from demonstrated results. State limits that change interpretation where they belong, rather than repeating defensive qualifications in the abstract, Results, Discussion, and conclusion. Judge each passage by what it explains, not by a blacklist of supposedly AI-like words.
- Describe what worked and why that choice worked, not a chronological account of every failed attempt. Mention a failure briefly when it explains a necessary step or supports a result; put slightly fuller, useful troubleshooting after the supplementary protocols. Neither the main paper nor the supplement should become a lab-notebook exposition.

## Paragraph and sentence flow

- Read the first sentence of every paragraph in order. Those sentences alone should carry the paper's argument, with each paragraph developing the expectation its opening creates.
- Put familiar information before new information. Explain a new term when it appears, keep pronoun references local, and avoid making the reader retain unexplained objects across clauses or paragraphs. Keep a layer or component's name, physical role and reason for its treatment together; do not interrupt that relationship with another layer or step. Introduce the mold's patterned wafer, printed inserts and alignment/bonding/coating sequence before detailing the first layer. Describe connected compartment geometry before comparing configurations or counts. Make the progression between examples explicit, and ground comparative advantages and limitations in the actual source—not assumptions about how a platform must work.
- In Methods, explain the concrete reason for the action: `To keep the wells open, we poured PDMS below the insert tops.` A purpose clause must explain an experimental or fabrication consequence, not rename the action (`To seed the compartment, we added cells`). Use natural sentence structure; repeating `To...` does not itself supply a reason.
- Reference every figure panel meaningfully in the body, not only in its caption. A range is appropriate when the sentence explains the contents represented by every panel in that range; a blanket panel list is not an explanation.

## Anti-Pattern: Meta-Paper Framing

Avoid sentences that describe the paper's logic, the authors' reasoning, or the scope of a claim instead of describing the work itself. These phrases often sound self-referential and make the prose feel dry.

Avoid constructions like:

- `The barrier is not conceptual but practical...`
- `The central test of this approach is not whether...`
- `We treated the workflow as successful only if...`
- `The purpose of this analysis was not to...`
- `The claim is therefore limited to...`
- `This design-generation claim applies to...`

Prefer direct statements about what exists, what was done, what was measured, and what remains bounded.

Examples:

- Instead of `The barrier is not conceptual but practical`, write `Micrometer-scale channels and pipette-accessible wells call for fabrication methods that span both scales.`
- Instead of `The central test of this approach is therefore not whether one plate-format device can be made once`, write `We demonstrate the full workflow with a compartmentalized neuronal culture device, spanning file generation, hybrid mold fabrication, repeated casting, plate-format handling, imaging, tracer redistribution, and neuronal culture in interior devices.`
- Instead of `The purpose of this analysis was not to validate additional fabricated devices`, write `These examples are design-generation examples rather than fabricated devices.`
- Instead of `The claim is therefore limited to design-generation compatibility`, write `Compatible published layouts can be translated into the mask, insert, and frame files required by the approach; layouts outside these constraints require redesign or new process development.`

## Generalizability Claims

- Separate fabricated validation from design-generation examples.
- Use the demonstrated neuronal device for end-to-end physical and biological validation.
- Use additional literature-derived layouts only to show that published geometries can be represented as OpenMFD-compatible fabrication file sets.
- Do not imply that additional geometries were fabricated, cultured, or biologically validated unless data exist.

## Supplementary information and data

- Keep the final reproducible protocols, concise design comparisons, and useful figures in the typeset supplement.
- Supply individual measurements and detailed printer or instrument profiles as supplementary data files. Preserve every value and unit, explain the file contents, and update all references when tables move.
- Keep supplementary references compact and attached to the relevant action, explanation or observation, usually in parentheses. No standalone narrative sentences announcing what a supplementary note, protocol, table, figure or data file supplies. Explain why the step matters; the reference is there for details, not as a separate event. Do not send readers to unrelated material or use cross-references as substitutes for an explanation. Resource indexes retain their actual indexing function.
- A supplement is not a complete development log. Retain observations that support a process choice without retelling every failed attempt. Put the protocols first and the relevant troubleshooting immediately afterward; keep measurements and long comparisons in reader-accessible data files.

## Figures and legends

- Legends should explain the figure independently: panel contents, relevant conditions, colours, symbols, scale bars and, for plots, the observation unit, sample counts and error summary. Fuller legends are useful when they add this information, not when they pad a panel inventory.
- Compare actual Fournier-coauthored figures and legends across papers; do not invent a universal house style from one example. Preserve the distinction between design files, fabricated devices and measured observations.
- Enlarge useful content and text rather than filling space with bigger margins. Group Figure 3's steps clearly, leave visible arrow shafts, and keep labels clear of equipment and neighbouring text.

## Working conversation

- Talk to Tristan and other contributors in ordinary English. Say what changed in the paper and what needs attention; do not replace a conversation with build bookkeeping or private administrative terms.

## Preferred Framing

- `This workflow moves well formation into the reusable mold...`
- `Each PDMS cast forms all 96 wells at once...`
- `Published layouts that fit the stated constraints can be represented as OpenMFD-compatible mask, insert, and frame files...`
- `Layouts outside those constraints require redesign or new process development...`
