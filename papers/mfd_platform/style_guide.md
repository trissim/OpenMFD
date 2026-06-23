# MFD Platform Manuscript Style Guide

## Voice

- Write as a biology-facing platform paper, not as an internal engineering report.
- Lead with the experimental or fabrication consequence, then explain the implementation detail.
- Keep OpenMFD as the coordination layer; keep the hybrid mold/no-punch plate-format workflow as the main story.

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

- Instead of `The barrier is not conceptual but practical`, write `Although many useful device geometries have already been described, translating them into plate-format PDMS devices remains difficult in practice.`
- Instead of `The central test of this approach is therefore not whether one plate-format device can be made once`, write `We demonstrate the full workflow with a compartmentalized neuronal culture device, spanning file generation, hybrid mold fabrication, repeated PDMS casting, plate-format handling, imaging, fluidic isolation, and long-term culture.`
- Instead of `The purpose of this analysis was not to validate additional fabricated devices`, write `These examples are design-generation examples rather than fabricated devices.`
- Instead of `The claim is therefore limited to design-generation compatibility`, write `Compatible published layouts can be translated into the mask, insert, and frame files required by the approach; layouts outside these constraints require redesign or new process development.`

## Generalizability Claims

- Separate fabricated validation from design-generation examples.
- Use the demonstrated neuronal device for end-to-end physical and biological validation.
- Use additional literature-derived layouts only to show that published geometries can be represented as OpenMFD-compatible fabrication file sets.
- Do not imply that additional geometries were fabricated, cultured, or biologically validated unless data exist.

## Preferred Framing

- `This workflow moves well formation into the reusable mold...`
- `The demonstrated device validates one complete fabrication-to-culture run...`
- `Published layouts that fit the stated constraints can be represented as OpenMFD-compatible mask, insert, and frame files...`
- `Layouts outside those constraints require redesign or new process development...`
