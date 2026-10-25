# MFD Platform Manuscript Style Guide

## Voice

- Write as a biology-facing platform paper, not as an internal engineering report.
- Lead with the experimental or fabrication consequence, then explain the implementation detail.
- Keep explaining why: connect each result to the practical problem it addresses, the reason for the observation, and what it enables or changes. Make that connection understandable without specialist knowledge where possible; do not replace an explanation with a verdict or a list of steps.
- Explain OpenMFD through the matching files it generates; keep the reusable hybrid mold and cast-in-place wells as the main story.
- Write positively from demonstrated results. State limits that change interpretation where they belong, rather than repeating defensive qualifications in the abstract, Results, Discussion, and conclusion.
- Describe the final working process. Keep development failures only when they explain a necessary step or the evidence for a result.

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
- A supplement is not a complete development log. Retain observations that support a process choice without retelling every failed attempt.

## Preferred Framing

- `This workflow moves well formation into the reusable mold...`
- `Each PDMS cast forms all 96 wells at once...`
- `Published layouts that fit the stated constraints can be represented as OpenMFD-compatible mask, insert, and frame files...`
- `Layouts outside those constraints require redesign or new process development...`
