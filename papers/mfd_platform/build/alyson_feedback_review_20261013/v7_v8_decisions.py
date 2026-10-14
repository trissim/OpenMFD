"""Build the proposed decisions and exact quotes for the submitted/returned drafts."""

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
data = json.loads((HERE / 'v7_v8_comparison.json').read_text())
documents = data['documents']
decisions = []


def add(title, old, new, decision, reason, feedback=(), kind='draft'):
    decisions.append(dict(id=f'R{len(decisions) + 1:02d}', title=title,
                          v7=old, v8=new, decision=decision, reason=reason,
                          feedback=list(feedback), kind=kind))


add('Title', [1], [1], 'V7 title',
    'V7 names the PDMS devices and the hybrid mold. V8 drops PDMS and SU-8 and makes the title about neuronal culture. The method is the contribution; neurons are its test case.')
add('Authors and affiliations', [2], [2, 3, 4, 5], 'V8 layout',
    'V8 adds numbered affiliations, new department names and corresponding-author details.')
add('Abstract', [4], [8], 'V7 abstract with the analyzed-device count (R53)',
    'V8 puts the 69-device count in the abstract and adds a warning about unmeasured channel sizes. V7 already states the edge-growth limit; its geometry discussion already distinguishes designed sizes from measurements.', feedback=(82, 136))
add('Introduction: applications', [6], [11], 'V7 account of the applications',
    'V7 explains why the method matters beyond neuronal assays. V8 replaces that with a narrower neuroscience account, understating the generalizability of the platform.')
add('Introduction: prior plate systems', [], [12], 'Platform context; fabrication methods remain the main comparison',
    'V8 P12 compares finished neuronal platforms. V7 P7, V7 P8 and Table S2 compare fabrication steps and equipment. The new references can be added after checking the claims they support. Neuronal platforms provide application context; fabrication methods remain the main comparison.')
add('Introduction: access to fabrication', [7], [56], 'V7 equipment-access comparison in the Introduction',
    'V8 removes the Introduction’s comparison with acquiring molding or machining equipment, along with its Table S2 citation. V8 P56 retains a shorter shared-facility explanation in Discussion. V7 explains the equipment tradeoff more directly.', feedback=(415, 488))
add('Introduction: ways to combine small channels and large wells', [8], [13], 'V7 comparison',
    'V8 changes the literature account and removes the second Table S2 citation. V7 already supplies that citation and compares the operations each method adds.', feedback=(415, 488, 498))
add('Introduction: insert-based prior work', [8, 9, 68], [14], 'V7 explanation with an earlier prior-work comparison',
    'V8 moves the comparison with individually placed metal inserts earlier. V7 already cites that work in P8 and compares it in P68, alongside the explanation of shared coordinates and whole-array transfer.')
add('Introduction: what this study tests', [10, 16, 66], [15], 'V7 description of the study',
    'Both describe the same work. V7 is shorter and identifies the untested layouts in Methods P16 and Results P66.', feedback=(84, 327))
add('Methods: what is made once and what is repeated', [12], [], 'V7 workflow explanation',
    'V8 deletes the sentence separating routine plate production in Protocol S1 from one-time mold fabrication in Protocol S2.', feedback=(539,))
add('Methods: design and generated files', [13, 14, 15, 16], [18], 'V7’s separate design paragraphs',
    'V7 separates software, tested dimensions and untested layouts. V8 combines them in one paragraph.', feedback=(19, 62))
add('Methods: SU-8 and SUEX layers', [17, 18, 19, 20, 21], [19, 20], 'V7 layer and bake details',
    'V7 identifies the base, channel and well layers separately. It also states that the SU-8 bake used direct oven placement without controlled heating or cooling. V8 keeps the temperature but drops that detail.', feedback=(39, 96))
add('Methods: resin printing', [15, 22], [18, 21], 'V7 print-preparation setting',
    'V7 says no shrinkage or tolerance compensation was applied in the print-preparation software. V8 removes that setting. The design already uses a 2.26% correction, so the separate print-preparation setting explains whether a second correction was applied.')
add('Methods: array transfer and bonding', [23], [22], 'V7 transfer and bonding steps',
    'V7 says where the EPDM sheet sits, how the plates and clamps apply pressure, and when cleaning and release occur. V8 shortens those instructions. These procedure details were already in Methods.', feedback=(11, 39))
add('Methods: parylene coating', [24], [22], 'V7’s separate coating paragraph',
    'V7 separates coating from insert bonding, names the facility and identifies the dimensions before coating. V8 folds coating into the bonding paragraph.', feedback=(96,))
add('Methods: frame printing', [26], [24], 'V7 file and software details',
    'V8 retains temperatures and layer size but removes the link to the supplied Creality Print 6.0.4 instruction file.', feedback=(562,))
add('Methods: casting, removal and glass bonding', [25, 27, 28, 29], [23], 'V7 casting and glass-bonding steps',
    'V8 drops the rack support, flat-wafer support, peeling direction, cutting guide and named cutting tool.', feedback=(21, 96))
add('Methods: frame assembly and surface treatment', [30, 31], [24], 'V7 assembly sequence',
    'V7 explains frame orientation, glass orientation, adhesive trimming and the separate second plasma treatment. V8 retains times but removes much of that sequence.', feedback=(96,))
add('Methods: how molds and plates were assessed', [32, 33, 34, 35], [25], 'V8 inspection detail with V7’s stated limits',
    'V8 names the filter, base-layer, bake and clamping conditions inspected. Both versions supply inspection criteria and the single unframed control. V7 already states that cell toxicity was not quantified.', feedback=(46, 528))
add('Methods: pipetting and microscopy', [36], [26], 'V7 wording',
    'Both report eight fitted pipette tips and two unmodified microscopes.', feedback=(74,))
add('Methods: fluorescent tracers', [37, 38], [27], 'V7 tracer details',
    'V7 supplies the secondary-antibody description, incubation conditions and explanation of how redistribution was judged. It already states that flow rate and duration were not measured.', feedback=(78, 432))
add('Methods: neuronal culture and CTβ', [39, 40, 41], [28, 29], 'V7 wording',
    'V7 supplies the one-embryo preparation, plating conditions, CTβ timing and exclusion rule, using soma and axon compartment.', feedback=(51,))
add('Methods: imaging and counting', [42, 43, 44], [30], 'V7 imaging explanation',
    'V8 deletes the pre-axotomy baseline sentence and the reason Plate 3 needed a larger imaging grid. V7 already gives those explanations, the pixel size, exposures, stitching and common counting area.', feedback=(25, 543, 608))
add('Methods: statistics', [45, 46], [31], 'V7 statistics explanation',
    'V7 already identifies technical repeats and within-plate standard deviations. Its last sentence says the summaries describe this experiment. The extra statement about not inferring other preparations adds no missing information.', feedback=(26, 432))
add('Results: four headings become six', [48, 55, 62, 65], [34, 37, 42, 45, 47, 49], 'Discuss four versus six Results groups',
    'V7 covers fabrication, casting, neuronal validation and design changes in four groups; V8 splits those topics into six. Both already separate procedures from findings.', feedback=(58,))
add('Results: design and plate geometry', [49], [34, 35], 'V7 text under V8’s design heading',
    'V7 already explains matched pins, whole-array positioning and wells formed during casting. V8 repeats dimensions from Methods and adds another unmeasured-size warning.', feedback=(62, 136))
add('Results: alternative layouts moved to the design section', [65, 66], [36], 'V8 placement with V7 wording',
    'V8 puts these outputs beside the design description. V7 already explains which components change together and says fabrication and assay testing remain future work.', feedback=(84, 327))
add('Results: general mold-development introduction', [49, 50, 51], [37], 'Begin with the failure-and-solution observations (R29–R30)',
    'V8 adds a general paragraph saying fabrication needed bonding surfaces and intact structures. The next paragraphs already give the actual failures and solutions.')
add('Results: filter and base-layer observations', [50, 51], [38], 'Existing observations with direct Figure S1/S2 links',
    'Both versions report raised edges, detachment and the successful changes. These were already Results in V7. The missing direct Figure S1/S2 links are a separate omission in both drafts.', feedback=(33, 34, 467, 471))
add('Results: additional SU-8 bake', [51], [39], 'Separate paragraph with the existing batch observations',
    'V7 reports the eight-wafer and two-wafer observations. V8 separates them into a paragraph, calls the process optimized and adds a warning about isolating variables.')
add('Results: pin heights and clamping', [52], [40], 'V8’s height statistics with the existing clamping result',
    'V8 brings the mean and standard deviation from Table S1 into main Results. V7 already reports the 116 µm range and the EPDM solution there.', feedback=(11, 127))
add('Results: open channels and release', [53], [41], 'V7 wording',
    'Both report open channels and unmeasured cast dimensions. V8 additionally states that alignment error is unquantified. V7 P68 distinguishes design clearance from actual alignment.', feedback=(136, 149))
add('Results: repeated casting and mold use', [54, 56], [42, 43], 'V7 reuse account with V8’s Figure 3 link',
    'V7 already reports five molds, three used, more than 50 casts, two losses and eight months of use. V8 adds a direct Figure 3 callout and a warning about standardized durability testing. V7 reports observed use, not a standardized lifetime test.', feedback=(48, 138, 522))
add('Results: frame materials and adhesives', [57, 58], [44], 'V7 material and adhesive observations',
    'V7 reports the warping and culture outcomes, including cultures that did not survive with the other screened adhesives. It does not claim a general toxicity or mechanical-strength test. V8 adds warnings about those unclaimed tests.')
add('Results: multichannel loading', [55, 56], [45], 'V7 pipetting result',
    'V7 says eight wells were filled with a multichannel pipette. It does not claim robotic dispensing or a measured processing rate. V8 adds a warning that those were not evaluated.', feedback=(74,))
add('Results: microscope use', [60], [46], 'V7’s experiment-specific account',
    'Both report imaging without instrument modification. V8 removes V7’s reason for choosing Opera Phenix: it was faster for these experiments.')
add('Results: tracer movement', [61], [47, 48], 'V7 tracer result and limit',
    'V7 already limits the conclusion to observed redistribution at two times and says isolation between them was not characterized. V8 expands the same limit over two paragraphs.', feedback=(78, 432))
add('Results: neuronal labeling', [62, 63], [49, 50], 'V7 text with V8’s Figure 4B link',
    'V7 already reports labeling in the soma compartment after axon-compartment application. V8 adds the direct Figure 4B callout and a warning about uncounted axonal trajectories. V7 does not claim that measurement.', feedback=(430,))
add('Results: 72 assessed and 69 counted devices', [64], [51], 'V7 count explanation with updated counts (R53)',
    'V7 supplies 24 interior devices per plate, 72 assessed, three excluded and 69 counted, with means and SD. V8 adds another biological-reproducibility warning. R53 gives the updated DMSO counts.', feedback=(53, 551))
add('Results: unframed control', [59], [52], 'V7 control observation and limit',
    'V7 reports one control, unresolved causes and analysis of interior devices. V8 states what would be needed for routine use of all 48 positions. My preference is V7’s current-scope limit and future-work wording.', feedback=(55,))
add('Discussion: contribution and prior inserts', [68], [54, 55], 'V7 quantitative comparison',
    'V7 compares three individually placed steel inserts with 96 resin inserts positioned together and gives the 17-fold margin calculation. V8 removes that calculation and adds broad statements about what is not new.')
add('Discussion: printing, coating and cell contact', [69], [55], 'V7 wording',
    'V7 explains why printing forms the wells and SU-8 forms the fine channels. Printed resin stays in the mold; the culture device is PDMS on glass.')
add('Discussion: repeated use and later bench production', [70], [56], 'V7 reuse explanation',
    'V7 reports reuse and explains that later casts do not repeat cleanroom work. It does not claim measured superiority in time, cost or production yield. V8 adds warnings about an optimized production economy.', feedback=(260, 500))
add('Discussion: limits of biological testing', [75], [57], 'V7 biological-testing limit',
    'Both identify one preparation and further testing. V8 says further studies would be needed to assess screening robustness. My preference is V7’s future-work wording; the present study demonstrates fabrication and culture, not a validated screening assay.', feedback=(140, 432))
add('Discussion: parylene and well geometry', [72, 74], [58], 'V7 coating and working-volume explanation',
    'V7 explains why coating widens a ridge while leaving its height above the base approximately unchanged. It also explains why increasing the 50 µL safe working volume would need larger, more expensive glass. V8 shortens these explanations.')
add('Discussion: edge growth', [73], [59], 'V7 wording',
    'Both retain poorer edge growth and the single unframed comparison. V7 already says the cause is unresolved and the frame can change separately.', feedback=(55,))
add('Discussion: changes to generated layouts', [71], [60], 'V7 design explanation',
    'V7 explains how pins, holes, adhesive space, sidewall slope and shrinkage correction fit together. V8 shortens that explanation and adds another list of future tests. The untested-layout statement was already in V7.', feedback=(84, 327))
add('Conclusion', [76, 77], [61, 62], 'V7 conclusion with the cast total',
    'V7 already states the contribution and the edge-growth limit. V8 adds the more-than-50-cast result and a list of tests said to be needed for broader assay robustness.', feedback=(44, 140, 432))
add('Code, files and data statement', [78, 79, 80, 81], [63, 64], 'V7 file list',
    'V7 P79 and V7 P80 name the files and their roles; V8 P64 shortens the list. Both promise a deposit. The DMSO count table is now supplied (R53). The study release, device preset and permanent archive link still need identifying.', feedback=(551, 560, 562, 564))
add('Conflict-of-interest statement', [], [65, 66], 'V8 statement before Data availability',
    'V8 adds the conflicts statement after Data availability. The journal’s order is conflicts, data availability, then acknowledgements.', feedback=(581, 583))
add('Acknowledgements and funding', [82, 83], [67], 'V7 thanks with V8 funding details',
    'V8 adds CIHR and MS Canada funding details. V7 names the facilities and their contributions.')
add('Reference list removed', list(range(84, 109)), [], 'V7 reference list with new entries',
    'V7 P84 starts a 24-entry bibliography. V8 removes it while adding citations. Check new references against the claims they support, keeping fabrication methods as the main comparison (R05). Final submission needs the complete list and numbered superscript citations.', feedback=(436, 569, 571))

add('Updated DMSO counts and Figure 4 text', [41, 64, 81, 116, 245, 247], [29, 51, 64, 77],
    'Integrate the recent DMSO plot and match the text',
    'The DMSO package has 72 rows and five counting-artifact exclusions, giving 22, 21 and 24 devices (67 total). Both drafts report three exclusions and 69 devices. The five flags need reconciling with the rule against excluding high or low counts alone (R22). Methods, Protocol S1, Results, Figure 4 and its legend need matching reasons, counts, means and SD (R55).', feedback=(51, 291, 551, 607), kind='remaining')
add('Figure 4 scale bars', [43, 116], [30, 77],
    'Use the recent calibrated CTβ views; add tracer bars',
    'The recent supplementary-biology figure has calibrated 500 µm CTβ bars, crop dimensions and saved rendering code (Sources R54), not included in V7/V8. Those views can replace the old Figure 4 microscopy. The separate tracer panel still needs its acquisition scale and a bar.', feedback=(301,), kind='remaining')
add('Counting-method settings', [241], [202],
    'Integrate the saved supplementary-biology counting method',
    'The supplementary-biology analysis supplies software, counts and overlays. Sources R55 lists the saved counting configuration. Use the configuration matching the selected count table when updating Methods and Protocol S1; match the exclusion explanation in R53.', feedback=(51,), kind='remaining')
add('Animal approval details', [226], [187],
    'Add the approving body, guidelines and approval number',
    'V7 P226 and V8 P187 mention an approved procedure but do not name the approving body, guidelines or approval number.', feedback=(576,), kind='remaining')
add('Supplementary table layout', [129, 131], [90, 92],
    'Widen the S2/S3 columns',
    'The checked render shows split words in Table S2 and dense columns in Table S3. Table S1 numbers fit on one line.', feedback=(494, 507, 606), kind='remaining')
add('Separate supplement and height CSV', [119, 121], [80, 82],
    'Use the supplied separate supplement and height CSV',
    'The Pin-height CSV matches all 96 Table S1 heights. The Separate supplement (DOCX/PDF) has the same 212 nonempty paragraphs and ten tables as V7. File details are in Sources R58.', feedback=(511, 513, 609), kind='supplied')
add('Later channel-width measurements', [53], [41, 58],
    'Report the width estimates with their measurement method',
    'Nine brightfield ruler estimates from three devices span 10.7–13.1 µm. Blurred wall-band placement gives up to 2.37 µm span sensitivity when each endpoint shifts one pixel. The pixel scale, method and overlays accompany the estimates; channel depth remains unmeasured (R61).', feedback=(136,), kind='remaining')
add('Individual mold-production records', [54], [43],
    'Keep the reuse observations; include per-mold records if available',
    'V7 P54 reports more than 50 casts, more than eight months of use and both mold losses. Existing per-mold records could add detail; no new durability study is proposed. Sources R33 compares Ristola’s reported reuse observations.', feedback=(138, 522), kind='optional')
add('Channel depth and between-cast comparisons', [53, 72], [41, 58],
    'No new depth or cast-to-cast study proposed',
    'ChatGPT proposes depth and between-cast measurements. Integrate the width estimates in R59; no depth or cast-to-cast panels are proposed here.', feedback=(136, 346), kind='optional')
add('Figure layout and additional plots', [110, 112, 114, 116, 118], [71, 73, 75, 77, 79],
    'Revisit image sizes and Figure 3/5 layout; no added durability study',
    'The recent supplementary-biology figure supplies larger views and device dots to integrate. Existing device/alignment views, Figure 3 length, Figure 5 outputs and in-figure untested labels should be revisited. Height and aggregate mold-outcome plots are ChatGPT suggestions, not proposed additions here. The existing reuse observations remain; a durability study is not part of this revision.', feedback=(214, 238, 239, 262, 291, 313, 327, 398), kind='optional')
add('Small supplement edits and extra failure comparisons', [152, 153, 155, 157, 158, 159, 161, 332], [113, 114, 116, 118, 119, 120, 122, 293],
    'Add note citations and make the protocol instruction clearer',
    'Figure S1 can be cited after Note S1’s filtered-exposure observation; Figure S2 after Note S2’s bare-silicon delamination observation. Table S3 already separates tested and files-only designs. The protocol’s open-channel result can become an inspection instruction. No raised-edge measurements are proposed: the filter addresses the observed bonding problem, and Figure S1 documents the comparison.', feedback=(450, 451, 475, 477, 541), kind='optional')

# Each former check belongs to a table row. Only additional source details are printed.
row_checks = {
    'R07': ('E13 E14 E17', 'E14'),
    'R10': ('E23 E27', ''),
    'R12': ('A15', ''),
    'R14': ('A01 A03', ''),
    'R16': ('E20', ''),
    'R17': ('A20', ''),
    'R19': ('A02', ''),
    'R23': ('E25', ''),
    'R24': ('D22', ''),
    'R25': ('A05 A06 A07 A21 A22', ''),
    'R27': ('A13 D27', ''),
    'R29': ('A14 E03 E06 E07', ''),
    'R31': ('A04 B03 B04 B06', 'B03 B04'),
    'R33': ('A08 A16 B05 E22', 'B05 E22'),
    'R35': ('A09', ''),
    'R37': ('A10 E02', ''),
    'R38': ('A11', ''),
    'R49': ('F05 F06 F07 F13', 'F06 F13'),
    'R50': ('F11', 'F11'),
    'R52': ('D28 E16 F08 F09', 'D28 F09'),
    'R53': ('A12 A19 D21 D24 F01 F02 F04', 'F01 F02 F04'),
    'R54': ('D23', 'D23'),
    'R55': ('A18 F03', 'F03'),
    'R56': ('F10', 'F10'),
    'R57': ('E11 E15 E19', ''),
    'R58': ('E10 E12 E26 F12', 'E12 E26 F12'),
    'R59': ('B07 B12 C10 F14', ''),
    'R60': ('A17 B08 B09 E21', ''),
    'R61': ('B10 B13', ''),
    'R62': ('B01 B02 B11 B14 B15 C01 C02 C03 C04 C05 C06 C07 C08 C09 C11 C12 D01 D02 D03 D04 D05 D06 D07 D08 D09 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D25 D26 E01', 'C06 C07 D08'),
    'R63': ('E04 E05 E08 E09 E18 E24 E28', 'E18'),
}
check_rows = {check: row for row, (checks, _) in row_checks.items() for check in checks.split()}
assert len(check_rows) == 119
for row in decisions:
    checks, sources = row_checks.get(row['id'], ('', ''))
    row['checks'] = checks.split()
    row['source_checks'] = sources.split()
    assert set(row['source_checks']) <= set(row['checks'])


def table_handles(text):
    pattern = r'\b([A-F]\d{2})(?:[-–](?:([A-F])?(\d{2})))?\b'
    def replace(match):
        first = match[1]
        last = int(match[3]) if match[3] else int(first[1:])
        group = match[2] or first[0]
        if group != first[0]:
            raise ValueError('Check range crosses groups: ' + match[0])
        rows = dict.fromkeys(check_rows[f'{group}{i:02d}'] for i in range(int(first[1:]), last + 1))
        return ' / '.join(rows)
    return re.sub(pattern, replace, text)

for row in decisions:
    row['reason'] = table_handles(row['reason'])
    row['decision'] = table_handles(row['decision'])

paragraphs = {name: document['paragraphs'] for name, document in documents.items()}
covered = {name: {p for row in decisions for p in row[name]} for name in ('v7', 'v8')}
unchanged = {name: {i for i, p in enumerate(paragraphs[name], 1)
                    if p and p in paragraphs['v8' if name == 'v7' else 'v7']}
             for name in paragraphs}
for name in paragraphs:
    end = paragraphs[name].index('Supplementary Information')
    missing = [i for i, p in enumerate(paragraphs[name][:end], 1)
               if p and i not in covered[name] and i not in unchanged[name]]
    if missing:
        raise ValueError(f'Changed {name} paragraphs without a decision: {missing}')


def locations(name, numbers):
    if not numbers:
        return 'No corresponding passage'
    return ', '.join(f'[{name.upper()} P{p}](../build/alyson_feedback_review_20261013/{name}_body_paragraphs.txt:{p})' for p in numbers)


feedback_lines = (ROOT / 'reviews/alyson_feedback.md').read_text().splitlines()
for row in decisions:
    for line in row['feedback']:
        if not 1 <= line <= len(feedback_lines) or not feedback_lines[line - 1].strip():
            raise ValueError('Missing feedback passage for ' + row['id'])
baseline_sentence = 'These were baseline images collected before axotomy; Supplementary Protocol S1 describes the dataset.'
table_claim = 'Supplementary Table S2 is not cited anywhere in the main manuscript.'
baseline_request = 'I would clarify that these are baseline measurements from an experiment conducted before axotomy'
assert baseline_sentence in paragraphs['v7'][43]
assert baseline_sentence not in paragraphs['v8'][29]
assert table_claim in feedback_lines[414]
assert baseline_request in feedback_lines[542]
assert sum('Supplementary Table S2' in p for p in paragraphs['v7'][:83]) == 2
assert not any('Supplementary Table S2' in p for p in paragraphs['v8'][:70])
assert paragraphs['v7'][242] == paragraphs['v8'][203]
assert not any('Figure 4B' in p or 'Fig. 4B' in p for p in paragraphs['v7'][:83])
assert sum('Figure 4B' in p or 'Fig. 4B' in p for p in paragraphs['v8'][:70]) == 1
assert not any('Figure 3' in p or 'Fig. 3' in p for p in paragraphs['v7'][:83])
assert sum('Figure 3' in p or 'Fig. 3' in p for p in paragraphs['v8'][:70]) == 1
assert not any('Conflict of Interest Statement' in p for p in paragraphs['v7'])
assert paragraphs['v8'][64] == 'Conflict of Interest Statement'
assert paragraphs['v8'][62] == 'Data availability'
assert paragraphs['v8'][66].startswith('Acknowledgements')
assert not re.findall(r'PMIDs?:', '\n'.join(paragraphs['v7'][:118]))
assert len(re.findall(r'PMIDs?:', '\n'.join(paragraphs['v8'][:79]))) == 19

opening = []


def note(text, refs=(), style=None, inline_refs=True, finding=None, links=(), underline=()):
    item = {'text': text}
    if refs:
        item['refs'] = list(refs)
    if style:
        item['style'] = style
    if inline_refs:
        item['inline_refs'] = True
    if finding is not None:
        item['finding'] = finding
    if links:
        item['links'] = [{'text': label, 'anchor': anchor} for label, anchor in links]
    if underline:
        item['underline'] = list(underline)
    opening.append(item)


def feedback_quote(number, excerpt):
    # Pasted tables contain stray tabs inside words; no words are changed.
    assert excerpt in feedback_lines[number - 1].replace('\t', ''), (number, excerpt)
    opening.append({'quote': True, 'text': excerpt, 'refs': [('feedback', number)]})


def manuscript_quote(name, number, excerpt):
    assert excerpt in paragraphs[name][number - 1], (name, number, excerpt)
    opening.append({'quote': True, 'text': excerpt, 'refs': [(name, number)]})


def attach_changes(*titles):
    heading = next(item for item in reversed(opening) if item.get('style') in ('Heading2', 'Heading3'))
    for title in titles:
        matches = [row['id'] for row in decisions if row['title'] == title]
        if len(matches) != 1:
            raise ValueError('Change title is missing or ambiguous: ' + title)
        heading.setdefault('refs', []).append(('change', matches[0]))


note('How I put this comparison together', style='Heading1')
note('While reading the ChatGPT transcript, I noticed that the later comments described V8, the returned rewrite, rather than just V7, the draft I sent. Several points referred to wording and changes I did not remember having in my draft.')
note('I checked V8 against V7 and found that those changes were in the returned version, not the one I had sent. I used ChatGPT to help map the differences, then checked every changed, added or removed main-text paragraph against both files and compiled them here.')
note('Several complaints turned out to be about changes introduced in V8. Some asked for information that V7 already had and V8 removed. Other suggestions were already covered in V7. I have separated those from the things that were actually missing from my draft. The examples come first below, with the exact wording and locations; the full list of changes follows.')
note('Repeated mentions of the same issue are grouped together. They are not extra problems.')
note('In Word for Mac, right-click a handle and choose Open Hyperlink. Use the R links to return to the table, or Contents in the footer.', underline=('right-click', 'Open Hyperlink'))

note('1. V8 removed both Table S2 citations. ChatGPT asks to add a citation V7 already had.',
     [('feedback', 415), ('feedback', 488)], style='Heading2', inline_refs=True)
note('V7 cites Table S2 twice in its Introduction. V8 removes both citations. The feedback then calls the table uncited and suggests adding an Introduction citation. That suggestion fixes a change in V8, not a gap in the draft I sent.',
     [('v7', 7), ('v7', 8), ('v8', 13)], inline_refs=True)
note('Here is one of the two citations in V7:')
manuscript_quote('v7', 8, 'Laser removal of material (ablation), direct printing, hot embossing, hard-plastic fabrication, and modular inserts combine these scales using different equipment and added operations (Supplementary Table S2).')
note('Here is what ChatGPT says is missing:')
feedback_quote(415, table_claim)
note('Here is the change ChatGPT suggests:')
feedback_quote(488, 'First, Table S2 is not cited in the Introduction or Discussion. I would add a reference to it in the Introduction, where previous fabrication strategies are described.')
note('The requested citation was already in V7 in two places. It became missing only in V8.',
     [('v7', 7), ('v7', 8), ('feedback', 488)], inline_refs=True)
note('The same Table S2 point comes up elsewhere in the feedback:')
note('The table’s S2 row marks its citation as “No” and says:')
feedback_quote(445, 'Cite in the Introduction, simplify the comparison, and standardize references.')
note('It also supplies this proposed Introduction sentence:')
feedback_quote(492, 'Existing approaches for integrating micrometer-scale channels with millimeter-scale culture compartments differ in their requirements for specialized equipment, mold preparation, component alignment, and repeated device production (Supplementary Table S2).')
note('The closing list repeats the request:')
feedback_quote(605, 'Correct the missing citations to Supplementary Figures S1–S2 and Table S2.')
note('Only the Table S2 part came from removing citations in V8. The Figure S1/S2 links really are missing in both drafts; those are separate edits.')

note('2. V8 removed the baseline-image explanation. ChatGPT asks for that explanation.',
     [('v7', 44), ('v8', 30), ('feedback', 543)], style='Heading2', inline_refs=True)
note('V7’s imaging paragraph already says:')
manuscript_quote('v7', 44, baseline_sentence)
note('V8 drops that sentence. Both drafts still mention the pre-axotomy experiment in Protocol S1; V7 also explains it plainly in the main imaging paragraph.', [('v8', 30)])
note('ChatGPT asks for this clarification:')
feedback_quote(543, baseline_request)
feedback_quote(608, 'Standardize the references and clarify the baseline neuronal imaging experiment.')
note('The feedback asks for a distinction that V7 already makes. V8 removes the sentence that makes it clear.',
     [('v7', 44), ('v8', 30), ('feedback', 543)], inline_refs=True)

note('3. V8 changes the main-text citation style. ChatGPT flags the mismatch with the unchanged captions and supplement.',
     [('v8', 11), ('v8', 79), ('feedback', 569)], style='Heading2', inline_refs=True)
note('ChatGPT’s comments describe the new style and the unchanged text:')
feedback_quote(436, 'It still identifies the source papers using author–year citations, whereas you have established a preference for PMIDs throughout this manuscript.')
feedback_quote(498, 'Third, the representative references are currently given largely in author–year format. These should be converted to your established PMID convention, using DOIs only when a verified PMID is unavailable.')
feedback_quote(567, 'Several supplementary items still use author–year references, including Table S2, the Figure 5 legend, and portions of the protocols.')
feedback_quote(569, 'These should be reconciled with the PMID-based citations used in the manuscript.')
feedback_quote(571, 'The PMIDs can remain in your working draft and be converted during final reference formatting.')
note('V7 uses author–year citations (V7 P6; V7 P8; V7 P118) and has no PMID labels. V8 adds 19 PMID labels, including V8 P11 and V8 P36, but keeps the author–year legends and supplement (V8 P79).', [('v7', 6), ('v7', 8), ('v7', 118), ('v8', 11), ('v8', 36), ('v8', 79)])
note('V8 also removes the 24-entry reference list that V7 supplied. The transcript requests reference formatting; it does not explicitly report the missing list.', [('v7', 84), ('v7', 85), ('v7', 108), ('v8', 64), ('v8', 67)])

note('4. V8 adds Figure 3 and 4B links. ChatGPT reports those links as present.',
     [('v8', 42), ('v8', 50), ('feedback', 426), ('feedback', 430)], style='Heading2', inline_refs=True)
note('ChatGPT’s figure audit says:')
feedback_quote(413, 'All five main figures are cited in the manuscript, and their content generally corresponds to the Results.')
note('The Figure 3 row marks its citation as:')
feedback_quote(426, 'Yes — Results')
feedback_quote(430, 'The manuscript appropriately cites Figure 4A for fluorescent tracer redistribution, Figure 4B for CTβ retrograde labeling, and Figure 4C for neuronal cell counts.')
note('V7 has no direct Figure 3 or Figure 4B callout. V8 adds “(Fig. 3)” in P42 and “(Fig. 4B)” in P50. The audit describes the links added in V8, not the links present in V7.', [('v7', 54), ('v7', 56), ('v7', 63), ('v8', 42), ('v8', 50)])

note('The transcript itself refers to different drafts', style='Heading2')
feedback_quote(174, 'I reviewed the five figures in your original manuscript against the revised Results and Discussion.')
feedback_quote(409, 'I reviewed the latest expanded manuscript, including the five main figures, two supplementary figures, six supplementary tables, two supplementary notes, and two detailed fabrication and experimental protocols.')
note('Together with the five changed details above, this shows that the later audit describes the rewrite. It is not just a review of the sent V7. It does not tell us which files ChatGPT received or the order of every edit.')
note('The earlier Methods table uses V7’s headings: “OpenMFD design and fabrication-file generation”, “Hybrid mold fabrication”, “Imaging and cell counting”, and the other V7 section names. V8 changes those headings. So the record does not support saying ChatGPT never saw V7.', [('feedback', 19), ('feedback', 20), ('feedback', 25), ('v7', 13), ('v7', 17), ('v7', 42), ('v8', 18), ('v8', 19), ('v8', 30)])
note('The listed figure page numbers are not enough to identify the file: page breaks depend on the rendering. Most figure comments cannot separate V7 from V8 anyway; both files retain the same images and legends.', [('feedback', 200), ('feedback', 225), ('feedback', 250), ('feedback', 273), ('feedback', 304)])

note('Several suggested explanations were already in V7', style='Heading2')
feedback_quote(14, 'Your existing draft already has a reasonable Methods structure.')
feedback_quote(31, 'Your current Results appropriately report several technical problems encountered during development:')
note('The feedback itself acknowledges these parts. V7 puts the rubber/clamps/adhesive procedure in Methods P23 and the 116 µm height spread and clamping result in Results P52. Reorganizing headings is a choice, not proof that these results were in the wrong section.', [('feedback', 11), ('v7', 23), ('v7', 52)])
manuscript_quote('v7', 54, 'The most recent molds remained in active use for more than 8 months without visible degradation.')
note('The same paragraph reports more than 50 usable casts and the two lost molds. Cast output and time in use were already stated separately. Exact per-mold counts would add detail.', [('feedback', 48), ('v7', 54)])
manuscript_quote('v7', 46, 'The plates and the devices within them are therefore technical replicates.')
manuscript_quote('v7', 61, 'Flow duration and compartmental isolation between the two imaging time points remain uncharacterized.')
manuscript_quote('v7', 66, 'Physical fabrication and assay testing of these layouts remain future work.')
note('The one-embryo limit, the tracer-test limit and the untested layouts were already stated in V7. V8 repeats them across the abstract, Results, Discussion and conclusion without adding data.', [('v7', 40), ('v7', 64), ('v8', 8), ('v8', 48), ('v8', 51), ('v8', 57), ('v8', 60), ('v8', 62)])
note('One example of an added warning:')
manuscript_quote('v7', 56, 'Eight wells were filled together with a multichannel pipette.')
manuscript_quote('v8', 45, 'although automated liquid dispensing and processing rates were not evaluated.')
note('V7 reports pipetting eight wells together. It does not claim a tested robot or a measured dispensing rate. The added warning answers a claim the original sentence did not make. R35 below keeps the result without that extra warning.')

note('Valid requests', style='Heading1')
note('5. The conflict-of-interest section belongs before Data availability.',
     [('v8', 63), ('v8', 65), ('feedback', 583)], style='Heading2', inline_refs=True)
note('This is a valid ordering correction. V8 adds a conflict-of-interest section after Data availability; V7 had no conflict-of-interest section. The request concerns the order in the returned draft, rather than missing scientific content in V7.',
     [('v7', 78), ('v7', 82), ('v8', 63), ('v8', 65), ('v8', 67)], inline_refs=True)
note('ChatGPT identifies the order in V8:')
feedback_quote(581, 'The latest manuscript places Data availability before Conflict of Interest Statement.')
note('It then states the journal’s order:')
feedback_quote(583, 'the Data Availability statement should follow the conflicts-of-interest statement and precede the Acknowledgements.')
note('The difference here is straightforward: the section order really does need attention in V8. That is separate from asking for explanations or citations that V7 already supplied.')
note('Other specific gaps', style='Heading2')
note('The specific text/layout gaps are missing direct Figure S1/S2 links, missing calibrated image bars and visibly cramped table columns. The claim that Table S1 numbers wrap was not reproduced in the checked render. The table links to the source crops.', [('feedback', 414), ('feedback', 301), ('feedback', 494), ('feedback', 505)])
note('The other jobs are to recover the actual animal approval details, counting software/settings, per-device count table and excluded IDs, and finish the study-file archive. These are specific reporting tasks. The work depends on finding the records; none calls for rewriting the whole paper.', [('feedback', 51), ('feedback', 547), ('feedback', 551), ('feedback', 560), ('feedback', 576)])
note('Finished channel widths and per-mold cast records would add data. The transcript shows no failed channel and gives no reason to require a new depth measurement.', [('feedback', 136), ('feedback', 138), ('feedback', 526), ('v7', 53)])
note('The remaining figure layouts and heading changes are choices to review. The next table covers every main-text change. It is 52 decisions about a rewrite, not 52 faults in V7.')

# Reuse the checked source quotations; organize the discussion by what remains
# to do, rather than mixing omissions, useful edits and new warnings together.
checked_opening = opening
def checked_section(title):
    start = next(i for i, item in enumerate(checked_opening) if item['text'] == title)
    stop = next((i for i in range(start + 1, len(checked_opening))
                 if checked_opening[i].get('style') in ('Heading1', 'Heading2')), len(checked_opening))
    return [dict(item) for item in checked_opening[start:stop]]

def reuse_section(title, new_title, finding):
    items = checked_section(title)
    items[0]['text'] = new_title
    items[0]['finding'] = {'feedback': finding}
    opening.extend(items)

def wording_finding(name, number, excerpt):
    assert excerpt in paragraphs[name][number - 1], (name, number, excerpt)
    return {'wording': excerpt, 'source': [name, number]}

opening = []
note('How I put this comparison together', style='Heading1')
note('As requested, I went through V8 and the accompanying 23 pages of ChatGPT discussion with a fine-toothed comb, organizing the claims and suggested revisions and checking accuracy. I noticed requests for information already in V7, the draft I sent. I also used ChatGPT to map the differences, then checked the passages against both files.')
note('When I checked the request to cite Table S2 in the Introduction, I found that V7 already cited it twice. Both citations were absent from V8.')
note('I found the same pattern with the explanation that the counting images were collected before axotomy: it was in V7, removed in V8, and requested in the discussion. For references, V7 used author–year citations throughout. V8 added main-text PMIDs but kept the author–year legends and supplement; the discussion then flagged those mixed styles.')
note('V8 also adds warnings about things the paper does not claim, such as automated dispensing and measured production costs. I had noticed similar additions from ChatGPT in earlier drafts and removed them to keep the text focused on what we tested and reported. I included these additions in the comparison below.')
note('I continued through the rest of the discussion and collected the sources here. Most annotated points concern material already present in V7: 114 of 169, counting repeated points. I separated those from useful V8 edits and the remaining fixes. I also checked whether the rewrite kept the fabrication method central, with neurons as one tested use.')
note('Useful V8 edits include direct Figure 3/4B links and pin-height statistics in Results. Remaining fixes include Figure S1/S2 links, supplementary-table layout, animal-approval details and archiving the study files. The newer counts, calibrated CTβ images and saved counting settings can also be integrated.')
note('I added the links to save you time, so you can compare the passages and move between the table, drafts and discussion without searching through the files.')
note('In Word for Mac, right-click a handle and choose Open Hyperlink. Use the R links to return to the table, or Contents in the footer.', underline=('right-click', 'Open Hyperlink'))
note('The main part to review is the table. You can provide your feedback by leaving comments in its rows.', links=[('the table', 'change_R01')])
note('The remaining {remaining_pages} pages are supporting material: copied V7/V8 passages, your ChatGPT discussion, and extra sources and explanations. The links let you check individual points without having to read all those pages.')
note('Reading guide', style='Heading1')
note('The comparison section before the table gives more detail on the rows: what V7 already had, useful V8 edits, remaining work, and removed text and added warnings.', links=[('what V7 already had', 'nav_covered'), ('useful V8 edits', 'nav_useful'), ('remaining work', 'nav_remaining'), ('removed text and added warnings', 'nav_losses')])
note('Sources: the commented ChatGPT discussion, cited V7/V8 passages, additional sources and images, and published-paper comparisons.', links=[('commented ChatGPT discussion', 'nav_transcript'), ('cited V7/V8 passages', 'nav_passages'), ('additional sources and images', 'detailed_evidence'), ('published-paper comparisons', 'published_comparisons')])
note('V7 P8 = version 7, paragraph 8. R = table row; R01-R52 compare the drafts, and R53-R63 cover remaining work. L = line in the ChatGPT discussion.')

note('1. Points already covered in V7', style='Heading1')
note('Leave comments in the revision table; the examples below explain selected rows.', links=[('revision table', 'change_R01')])
note('Table S2 was cited twice before V8 removed the links', [('feedback', 415)], style='Heading2', finding={'feedback': 415})
attach_changes('Introduction: access to fabrication', 'Introduction: ways to combine small channels and large wells')
manuscript_quote('v7', 8, 'Laser removal of material (ablation), direct printing, hot embossing, hard-plastic fabrication, and modular inserts combine these scales using different equipment and added operations (Supplementary Table S2).')
feedback_quote(415, table_claim)
note('V7 P7 and V7 P8 both cite the table. V8 P13 removes the second link and the other paragraph is deleted. Feedback L488 asks for an Introduction citation; Feedback L445, Feedback L492 and Feedback L605 repeat it.', [('v7', 7), ('v7', 8), ('v8', 13), ('feedback', 445), ('feedback', 488), ('feedback', 492), ('feedback', 605)])
note('The baseline-image explanation was in V7 before V8 removed it', [('feedback', 543)], style='Heading2', finding={'feedback': 543})
attach_changes('Methods: imaging and counting')
manuscript_quote('v7', 44, baseline_sentence)
feedback_quote(543, baseline_request)
note('V8 P30 drops that sentence. Feedback L608 repeats the request. Protocol S1 still identifies the pre-axotomy dataset at V7 P243 / V8 P204.', [('v8', 30), ('v7', 243), ('v8', 204), ('feedback', 608)])
note('The mixed citation styles start in V8', [('feedback', 569)], style='Heading2', finding={'feedback': 569})
attach_changes('Reference list removed')
note('V7 uses author–year citations (V7 P6; V7 P8; V7 P118) and has no PMID labels. V8 adds 19 PMID labels, including V8 P11 and V8 P36, but keeps the author–year legends and supplement (V8 P79).', [('v7', 6), ('v7', 8), ('v7', 118), ('v8', 11), ('v8', 36), ('v8', 79)])
feedback_quote(569, 'These should be reconciled with the PMID-based citations used in the manuscript.')
note('Feedback L436, Feedback L498 and Feedback L608 repeat the style request. V7 P84 starts the 24-entry bibliography, from V7 P85 through V7 P108. V8 ends the main text at V8 P67 without that list.', [('feedback', 436), ('feedback', 498), ('feedback', 608), ('v7', 84), ('v7', 85), ('v7', 108), ('v8', 67)])
note('F09 gives the journal’s required format: numbered superscript citations and a numbered reference list, not PMID labels. Neither draft has the final format.', [('evidence', 'F09')])

note('The procedure/result separation was already present', [('feedback', 11)], style='Heading2', finding={'feedback': 11})
attach_changes('Methods: array transfer and bonding', 'Results: four headings become six', 'Results: pin heights and clamping')
feedback_quote(11, 'The procedural details—rubber thickness, clamping arrangement, adhesive and curing conditions—belong in Materials and Methods.')
note('V7 P23 gives backing, clamps, adhesive and curing in Methods; V7 P52 gives the height spread and clamping result in Results. V8 P22 and V8 P40 keep that separation.', [('v7', 23), ('v7', 52), ('v8', 22), ('v8', 40)])
note('V7 P33 describes cast inspection; V7 P54 reports cast totals, losses and elapsed use. V7 P37 and V7 P38 describe the tracer assay; V7 P61 reports redistribution and its limits.', [('v7', 33), ('v7', 54), ('v7', 37), ('v7', 38), ('v7', 61)])
note('V7’s four Results headings cover mold fabrication (V7 P48), casting/assembly (V7 P55), neurons (V7 P62) and design changes (V7 P65). The published examples below also separate procedures from findings.', [('v7', 48), ('v7', 55), ('v7', 62), ('v7', 65)])
note('R25 covers whether four or six Results groups read better.', [('change', 'R25')])
note('Lin et al. (2017): “Mold fabrication” is in Experimental (PDF p. 2); “Mold reproducibility for multiple embossing cycles” is in Results (p. 5).', [('published', 1)])
note('Compera et al. (2021): Experimental separates “Master mold fabrication”, “Chip fabrication”, “Surface measurements” and “Microscopy and image analysis”. Results reports valve development and cell-culture outcomes.', [('published', 4)])
note('Taylor et al. (2015): Experimental has “Device fabrication”, “Device assembly and preparation”, “Neuronal culture” and “Imaging and analysis” (accepted manuscript pp. 7–9). Results begins with device design, then gradient and neuronal responses (p. 4).', [('published', 3)])
note('Carnero et al. (2024): Methods has “Manufacturing”, “Micromixer testing” and “Data collection” (PDF pp. 2–4). Results reports process optimization under “Laser parameters for manufacturing” (p. 4).', [('published', 5)])
note('Broeren et al. (2023) shows fabrication steps in main Figure 1 and gives detailed instructions in the supplement. V7 has main process Figures 2 and 3 (V7 P112; V7 P114), with detailed Protocols S1 and S2 (V7 P162; V7 P249).', [('published', 7), ('v7', 112), ('v7', 114), ('v7', 162), ('v7', 249)])

note('Cast output and elapsed use were already separate', [('feedback', 48)], style='Heading2', finding={'feedback': 48})
attach_changes('Results: repeated casting and mold use')
feedback_quote(48, 'I would strengthen this section by distinguishing the number of successful casts from mold survival over time.')
manuscript_quote('v7', 54, 'Three entered routine use and together produced more than 50 usable casts.')
manuscript_quote('v7', 54, 'The most recent molds remained in active use for more than 8 months without visible degradation.')
note('V7 P54 and V8 P43 explain both lost molds. E22 quotes Table S5’s inspection-based usable-cast definition. Per-mold counts would add detail.', [('v7', 54), ('v8', 43), ('evidence', 'E22')])

note('Untested status is already stated in the text and legend', [('feedback', 327)], style='Heading2', finding={'feedback': 327})
attach_changes('Results: alternative layouts moved to the design section')
attach_changes('Figure layout and additional plots')
feedback_quote(327, 'I would make it clear within the figure itself that these are computational designs, not experimentally validated devices.')
manuscript_quote('v7', 66, 'Physical fabrication and assay testing of these layouts remain future work.')
note('V7 Methods (V7 P16) and the Figure 5 legend (V7 P118 / V8 P79) also say these designs were not tested. V8 P36 keeps that limit in Results. An image label would make it visible without reading the legend.', [('v7', 16), ('v7', 118), ('v8', 36), ('v8', 79)])

note('Figure 1 already shows the two-well geometry; R62 covers image size and labels.', [('change', 'R62')])
note('Figure 2 already shows the alignment pin and EPDM backing; R62 covers their size and emphasis.', [('change', 'R62')])
note('All five legends already have titles, and Figure 5 has three application rows; R62 covers the proposed presentation changes.', [('change', 'R62')])
note('The supporting material already explains its observations', [('feedback', 535)], style='Heading2', finding={'feedback': 535})
note('Protocol S2 makes the mold (V7 P249); Protocol S1 uses it for casting, assembly and assays (V7 P162; E23). Notes S1/S2 explain the neighboring failure images (V7 P155; V7 P161). Table S3 distinguishes the fabricated device from files-only layouts (E18). V8 keeps these descriptions.', [('v7', 155), ('v7', 161), ('v7', 162), ('v7', 249), ('evidence', 'E18'), ('evidence', 'E23')])
note('The claimed broken numbers in Table S1 were not reproduced', [('feedback', 505)], style='Heading2', finding={'feedback': 505})
feedback_quote(505, 'Some numerical values wrap across lines because the columns are too narrow.')
note('Table S1 is unchanged. Its numbers 5.567, 5.599 and 5.483 stay on one line in the checked render (Sources R57). Table S2 does split long words. R58 identifies the 96-height CSV.', [('source', 'R57'), ('change', 'R58')])

note('2. Useful V8 edits', style='Heading1')
reuse_section('4. V8 adds Figure 3 and 4B links. ChatGPT reports those links as present.',
              'The audit recognizes two direct figure links added in V8', 426)
attach_changes('Results: repeated casting and mold use', 'Results: neuronal labeling')
note('The Figure 3 link at V8 P42 and Figure 4B link at V8 P50 are useful additions.', [('v8', 42), ('v8', 50)])
note('Existing height statistics become visible in main Results', [('v8', 40)], style='Heading2',
     finding=wording_finding('v8', 40, 'a mean height of 5.551 mm, a standard deviation of 26.7 µm'))
attach_changes('Results: pin heights and clamping')
manuscript_quote('v8', 40, 'Measurements of all 96 alignment pins in one array gave a mean height of 5.551 mm, a standard deviation of 26.7 µm, and a 116 µm range between the shortest and tallest pins (Supplementary Table S1).')
note('V7 P52 reports the 116 µm range. Table S1A and the height CSV in Sources R58 supply the 96 measurements. V8 P40 brings their mean and SD into main Results. Feedback L127 suggests plotting them.', [('v7', 52), ('source', 'R58'), ('v8', 40), ('feedback', 127)])
note('The abstract adds the analyzed-device count', [('v8', 8)], style='Heading2',
     finding=wording_finding('v8', 8, 'was quantified in 69 interior devices across three technical-replicate plates.'))
attach_changes('Abstract')
manuscript_quote('v8', 8, 'Retrograde cholera toxin subunit B labeling was quantified in 69 interior devices across three technical-replicate plates.')
note('V7 P64 reports 69 devices in Results; V7 P4 does not include that number in the abstract. V8 P8 adds it there. The updated DMSO plot now needs its own matching count (R53).', [('v7', 4), ('v7', 64), ('v8', 8), ('change', 'R53')])
note('Feedback L82 lists the 69-device result. Feedback L136 asks for measured channel sizes. R03 also covers the channel-size warning added to the abstract.', [('feedback', 82), ('feedback', 136), ('change', 'R03')])
note('V8 names the inspected development conditions in Methods', [('v8', 25)], style='Heading2',
     finding=wording_finding('v8', 25, 'rigid versus compressible clamping were assessed by visual inspection'))
attach_changes('Methods: how molds and plates were assessed')
manuscript_quote('v8', 25, 'SUEX patterning with and without LP360 filtering, SU-8 processing with and without a base layer or additional bake, and rigid versus compressible clamping were assessed by visual inspection for surface ridges, photoresist detachment, and insert seating')
note('V7 P33 describes inspection in Methods; V7 P50, V7 P51 and V7 P52 report the compared conditions in Results. V8 P25 also names those conditions in Methods.', [('v7', 33), ('v7', 50), ('v7', 51), ('v7', 52), ('v8', 25)])
note('Six Results groups and earlier alternative-design placement should be revisited', [('v8', 34), ('v8', 36)], style='Heading2', finding={'feedback': 58})
attach_changes('Results: four headings become six', 'Results: alternative layouts moved to the design section')
feedback_quote(100, 'Once that is complete, we can rewrite the Results around the six sections above.')
note('V8 starts six groups at V8 P34 and places alternative layouts beside design at V8 P36, as suggested at Feedback L84. V7 covers those topics under V7 P48, V7 P55, V7 P62 and V7 P65.', [('v7', 48), ('v7', 55), ('v7', 62), ('v7', 65), ('v8', 34), ('v8', 36), ('feedback', 84)])
note('The added conflicts declaration belongs before Data availability', [('v8', 65)], style='Heading2', finding={'feedback': 583})
attach_changes('Conflict-of-interest statement')
note('V7 goes from data availability (V7 P78) to acknowledgements (V7 P82), without a conflicts section. V8 puts conflicts (V8 P65) after data availability (V8 P63). Feedback L583 requests the journal’s order: conflicts, data availability, acknowledgements (F11).', [('v7', 78), ('v7', 82), ('v8', 63), ('v8', 65), ('feedback', 583), ('evidence', 'F11')])
note('The added neuronal-platform comparison provides context', style='Heading2')
attach_changes('Introduction: prior plate systems')
note('V8 P12 adds neuronal-platform references to check for accuracy and relevance. They can provide application context. V7 P7, V7 P8 and Table S2 compare fabrication steps and equipment, which remain the main comparison for the method.', [('v8', 12), ('v7', 7), ('v7', 8)])

note('3. Work still needed after combining V7 with useful V8 edits', style='Heading1')
note('The supporting observations are there; direct image links are not', [('feedback', 414)], style='Heading2', finding={'feedback': 11})
attach_changes('Results: filter and base-layer observations')
note('V7 P50, V7 P51 and V8 P38 report the filter and adhesion observations. The supplementary captions identify the filter comparison (V7 P155) and delamination image (V7 P161). R29 records the missing direct Figure S1/S2 citations in main Results.', [('v7', 50), ('v7', 51), ('v8', 38), ('v7', 155), ('v7', 161), ('change', 'R29')])
note('The DMSO package already supplies counts, exclusions and calibrated views', [('feedback', 301), ('feedback', 551)], style='Heading2',
     finding=wording_finding('v7', 116, '69 interior devices analyzed in total.'))
attach_changes('Updated DMSO counts and Figure 4 text', 'Figure 4 scale bars')
feedback_quote(551, 'I recommend supplying a CSV file containing the per-device counts, together with plate and device identifiers and an explicit record of the three excluded devices.')
note('Sources R53 identifies the 72-row DMSO dataset, five excluded IDs and reasons, and recalculated means/SD. Sources R54 gives the calibrated 500 µm bars and image scale.', [('source', 'R53'), ('source', 'R54')])
note('The updated CTβ plot includes 22, 21 and 24 devices (67 total; F01). V7 P64 and V8 P51 say 69 after three exclusions. The updated figure and matching count/exclusion text need integrating. The old tracer panel still needs its own bar (D23).', [('evidence', 'F01'), ('v7', 64), ('v8', 51), ('evidence', 'D23')])
note('The five new exclusions are labeled counting artifacts. V7 P41 rules out exclusion for high or low counts alone; Protocol S1 repeats that rule at V7 P245 and the old three-exclusion explanation at V7 P247. R53 covers reconciling those rules and reasons, along with the per-plate counts, means and SD.', [('v7', 41), ('v7', 245), ('v7', 247), ('change', 'R53')])
note('The recent supplementary-biology analysis supplies the counting method to integrate', [('feedback', 51)], style='Heading2',
     finding=wording_finding('v7', 241, 'using the same cell segmentation settings and criteria for CTβ labeling in every cropped image.'))
attach_changes('Counting-method settings')
feedback_quote(51, 'imaging procedure and analysis criteria.')
manuscript_quote('v7', 241, 'using the same cell segmentation settings and criteria for CTβ labeling in every cropped image.')
note('V8 P202 keeps that instruction. The recent supplementary-biology analysis supplies the software, counts, overlays and saved settings. R55 covers carrying its counting method into Methods and Protocol S1; R53 covers the updated exclusions and totals.', [('v8', 202), ('change', 'R55'), ('change', 'R53')])
note('Approval is mentioned; the specific approval details are not', [('feedback', 576)], style='Heading2',
     finding=wording_finding('v7', 226, 'under the laboratory’s approved animal-use procedure.'))
attach_changes('Animal approval details')
feedback_quote(576, 'However, the main Materials and Methods does not identify the approving institution or protocol number.')
manuscript_quote('v7', 226, 'under the laboratory’s approved animal-use procedure.')
note('V8 P187 keeps that sentence. The approving body, guidelines and approval number where available are still missing (F10).', [('v8', 187), ('evidence', 'F10')])
note('The study-file deposit is promised, not identified', [('feedback', 560)], style='Heading2', finding={'feedback': 560})
feedback_quote(560, 'I recommend ensuring that the downloadable package contains the actual photomask DXF files, insert STL files, frame designs, and the version of OpenMFD used to generate the reported devices.')
manuscript_quote('v7', 79, 'A versioned archive of the reported files will be deposited with the submission.')
manuscript_quote('v8', 64, 'A versioned archive and per-device neuronal counts will be deposited with the submission.')
attach_changes('Code, files and data statement')
note('V7 P79 names the design files; V7 P80 names the frame G-code and microscope XML (F05-F06). F07 identifies the remaining study release and permanent archive link. F01 supplies the DMSO count table to include in that archive.', [('v7', 79), ('v7', 80), ('evidence', 'F05'), ('evidence', 'F06'), ('evidence', 'F07'), ('evidence', 'F01')])
note('Table layout, supplied files and references', [('feedback', 494)], style='Heading2', finding={'feedback': 494})
attach_changes('Supplementary table layout', 'Separate supplement and height CSV', 'Reference list removed')
note('E15 shows Table S2 needs wider columns or shorter entries. E26 identifies the existing separate supplement; E12 identifies the existing 96-height CSV. F09 gives the final numbered-reference format. V7 P84 supplies the starting bibliography; V8 P12 adds references to check.', [('evidence', 'E15'), ('evidence', 'E26'), ('evidence', 'E12'), ('evidence', 'F09'), ('v7', 84), ('v8', 12)])
note('A later width check is now available', [('measurement', 0)], style='Heading2')
attach_changes('Later channel-width measurements', 'Individual mold-production records', 'Channel depth and between-cast comparisons')
feedback_quote(136, 'Measure the width and height of several representative microchannels in finished PDMS devices.')
note('Width data gives nine brightfield ruler estimates from three devices spanning 10.7–13.1 µm. Moving each endpoint one pixel changes a span by up to 2.37 µm. Channel depths remain unmeasured (R61). V7 P54 reports combined mold use; exact per-mold records requested at Feedback L138 and Feedback L526 would add detail if recorded.', [('measurement', 0), ('change', 'R61'), ('v7', 54), ('feedback', 138), ('feedback', 526)])
note('Other figure and supplement changes should be revisited', style='Heading2')
attach_changes('Figure layout and additional plots', 'Small supplement edits and extra failure comparisons')
note('Sources R53 identifies the supplied device-dot plot and counts. R62 covers image sizes and figure layout, without adding height plots or a durability study. R63 covers note links and protocol wording, without a raised-edge measurement experiment.', [('source', 'R53'), ('change', 'R62'), ('change', 'R63')])

note('4. V8 changes the feedback did not identify as losses or unnecessary additions', style='Heading1')
note('Added warnings', style='Heading2')

def added_warning(title, old_p, old_excerpt, new_p, new_excerpt, explanation):
    note(title, [('v8', new_p)], style='Heading3', finding=wording_finding('v8', new_p, new_excerpt))
    note('V7 reports:')
    manuscript_quote('v7', old_p, old_excerpt)
    note('V8 adds:')
    manuscript_quote('v8', new_p, new_excerpt)
    note(explanation.replace('V7 ', f'V7 P{old_p} ', 1).replace('V8 ', f'V8 P{new_p} ', 1), [('v7', old_p), ('v8', new_p)])

added_warning('V8 adds an automated-dispensing warning', 56,
    'Eight wells were filled together with a multichannel pipette.', 45,
    'although automated liquid dispensing and processing rates were not evaluated.',
    'V7 reports eight-well loading with a manual multichannel pipette. V8 adds a warning about robotic dispensing and processing rates.')
attach_changes('Results: multichannel loading')
added_warning('V8 adds a standardized-durability warning', 54,
    'The most recent molds remained in active use for more than 8 months without visible degradation.', 43,
    'standardized quantitative durability testing was not performed.',
    'V7 reports more than eight months of use without visible degradation. V8 adds a warning about standardized lifetime testing. Per-mold records would add detail to the reported use.')
attach_changes('Results: repeated casting and mold use')
added_warning('V8 adds a joint-strength warning', 58,
    'SI 5140 also formed a flexible, visibly leak-tight glass-to-HIPS joint that remained intact during repeated incubator transfers.', 44,
    'Adhesive toxicity and mechanical strength were not measured quantitatively',
    'V7 reports culture survival and a visibly intact joint during incubator transfers. Its Methods already state that toxicity was not quantified. V8 adds a mechanical-strength qualification to that operating observation.',)
attach_changes('Results: frame materials and adhesives')
note('V7 P34 explicitly states the existing toxicity limit in Methods.', [('v7', 34)])
added_warning('V8 adds an axonal-path-counting warning', 63,
    'consistent with tracer uptake by axons extending into the axon well and retrograde transport.', 50,
    'axonal trajectories were not independently quantified.',
    'V7 reports labeled cell bodies after axon-well treatment. V8 retains that inference, adds Figure 4B and introduces a warning about counting axonal paths.')
attach_changes('Results: neuronal labeling')
added_warning('V8 adds a cost and yield warning', 70,
    'Once the mold is complete, laboratories can cast and assemble further devices without repeating cleanroom processing.', 56,
    'not yet an optimized production economy.',
    'V7 explains that later casts avoid repeating cleanroom work. V8 adds a warning about production costs and yield, which V7 did not compare.')
attach_changes('Discussion: repeated use and later bench production')
added_warning('V8 adds future screening-validation wording', 75,
    'Further testing across independent neuronal preparations would assess biological reproducibility.', 57,
    'will be required to assess screening robustness.',
    'V7 identifies one preparation and proposes independent repeats. V8 says further studies would be needed to assess screening robustness. That condition concerns a future screening assessment, not the present fabrication demonstration.')
attach_changes('Discussion: limits of biological testing')

note('The same unmeasured-size limit appears in four V8 locations', [('v8', 8), ('v8', 35), ('v8', 41), ('v8', 58)], style='Heading3',
     finding=wording_finding('v8', 35, 'final cast dimensions were not measured.'))
attach_changes('Abstract', 'Results: design and plate geometry', 'Results: open channels and release', 'Discussion: parylene and well geometry')
manuscript_quote('v8', 8, 'final microchannel dimensions remain unmeasured.')
manuscript_quote('v8', 35, 'final cast dimensions were not measured.')
manuscript_quote('v8', 41, 'alignment error and dimensional fidelity of the final channels have not yet been quantified.')
manuscript_quote('v8', 58, 'the finished cast microchannels were not measured.')
note('V7 P53 states the unmeasured-size limit beside the open-channel result; V7 P72 explains the coating effects. V8 repeats the size limit in its abstract (V8 P8), design Results (V8 P35), fabrication Results (V8 P41) and Discussion (V8 P58).', [('v7', 53), ('v7', 72), ('v8', 8), ('v8', 35), ('v8', 41), ('v8', 58)])
note('The one-preparation limit is repeated in five paragraphs', [('v8', 31), ('v8', 49), ('v8', 51), ('v8', 57), ('v8', 64)], style='Heading3',
     finding=wording_finding('v8', 51, 'does not establish biological reproducibility across preparations.'))
attach_changes('Methods: statistics', 'Results: neuronal labeling', 'Results: 72 assessed and 69 counted devices', 'Discussion: limits of biological testing', 'Conclusion', 'Code, files and data statement')
manuscript_quote('v7', 46, 'These summaries describe variation within this experiment.')
manuscript_quote('v8', 51, 'does not establish biological reproducibility across preparations.')
manuscript_quote('v8', 62, 'will be needed to establish broader assay robustness.')
note('V7 identifies one embryo (V7 P40), technical replicates (V7 P46) and future independent repeats (V7 P75). V8 repeats the limit in statistics (V8 P31), neuronal Results (V8 P49; V8 P51), Discussion (V8 P57) and data availability (V8 P64). Its conclusion (V8 P62) separately lists biological reproducibility among future tests for broader assay robustness.', [('v7', 40), ('v7', 46), ('v7', 75), ('v8', 31), ('v8', 49), ('v8', 51), ('v8', 57), ('v8', 62), ('v8', 64)])

note('Removed explanations', style='Heading2')

def removed_explanation(title, old_p, excerpt, new_p, explanation):
    note(title, [('v7', old_p), ('v8', new_p)], style='Heading3', finding=wording_finding('v7', old_p, excerpt))
    manuscript_quote('v7', old_p, excerpt)
    note(explanation.replace('V7 ', f'V7 P{old_p} ', 1).replace('V8 ', f'V8 P{new_p} ', 1), [('v7', old_p), ('v8', new_p)])

removed_explanation('V8 removes the 17-fold design-margin ratio', 68,
    'This margin is 17 times the per-side clearance;', 55,
    'V8 keeps the 75 µm clearance and 1.275 mm margin but removes their ratio: 1.275 / 0.075 = 17. V7 uses that calculation to explain the design allowance.')
attach_changes('Discussion: contribution and prior inserts')
removed_explanation('V8 removes the coating-height explanation', 72,
    'The ridge height relative to the surrounding surface would remain approximately unchanged because the coating raises both the ridge top and the flood-exposed base.', 58,
    'V8 retains the predicted width enlargement but drops the height explanation. V7 explains that coating raises both the ridge top and surrounding base, leaving their height difference approximately unchanged.')
attach_changes('Discussion: parylene and well geometry')
removed_explanation('The adhesive-survival wording changes', 58,
    'cultures did not survive with any of the other screened adhesives.', 44,
    'V8 says SI 5140 alone supported cultures through the endpoint. V7 states directly that cultures did not survive with the other tested adhesives.')
attach_changes('Results: frame materials and adhesives')
removed_explanation('V8 drops the reason for choosing Opera Phenix', 60,
    'which was faster for these experiments.', 46,
    'V7 says Opera Phenix was faster for these experiments. V8 reports its use but drops that reason for choosing it.')
attach_changes('Results: microscope use')
note('V8 narrows the introduction to neuroscience', style='Heading3')
attach_changes('Introduction: applications')
manuscript_quote('v7', 6, 'Established designs support applications across neuroscience, stem cell biology, cancer research, immunology, and developmental biology')
manuscript_quote('v8', 11, 'enabling localized treatments and studies of axonal transport, injury, and regeneration')
note('V7 P6 explains why the method matters beyond neuronal assays. V8 P11 replaces that with a narrower neuroscience account, understating the generalizability of the platform.', [('v7', 6), ('v8', 11)])
manuscript_quote('v7', 68, 'For an array that fits on one wafer and print platform, the same alignment operation is used regardless of the number or arrangement of inserts.')
note('V7 P68 describes an operation shared across array layouts; V7 P10 identifies neuronal culture as the device used to evaluate it. V8 P54 also names coordinated design, whole-array alignment and repeated casting as the principal contribution.', [('v7', 68), ('v7', 10), ('v8', 54)])
note('The reusable-mold workflow in V7', style='Heading3', finding={'feedback': 62})
manuscript_quote('v7', 49, 'Matching pins and alignment holes allowed all 96 inserts to be positioned together on the patterned wafer.')
manuscript_quote('v7', 49, 'During PDMS casting, the inserts formed all 96 wells at once, eliminating individual well punching.')
manuscript_quote('v7', 70, 'Once the mold is complete, laboratories can cast and assemble further devices without repeating cleanroom processing.')
note('The matched files position the full array (V7 P9; V7 P49). Bonded inserts form every well in each cast (V7 P49). The mold is reused without repeating its fabrication (V7 P70). Neuronal culture tests a device made by that process (V7 P75; V7 P77).', [('v7', 9), ('v7', 49), ('v7', 70), ('v7', 75), ('v7', 77)])
removed_explanation('V8 removes the Introduction’s equipment-access comparison', 7,
    'For many academic biology groups, having a shared cleanroom fabricate a reusable mold is more accessible than acquiring precision molding or machining equipment.', 13,
    'V8 removes this Introduction comparison. V7 explains the tradeoff with buying molding or machining equipment.')
attach_changes('Introduction: access to fabrication')
note('V8 P56 retains a shorter shared-facility explanation in Discussion and says later casts avoid repeating cleanroom photolithography.', [('v8', 56)])
removed_explanation('V8 removes the print-preparation compensation setting', 22,
    'no shrinkage or tolerance compensation in the print-preparation software.', 21,
    'V7 says print preparation adds no compensation. V8 drops that setting.',)
attach_changes('Methods: resin printing')
note('V7 P15 specifies the 2.26% design enlargement; V7 P22 specifies no additional print-preparation compensation. V8 P18 retains the design enlargement, but V8 P21 omits the separate printer-software setting.', [('v7', 15), ('v7', 22), ('v8', 18), ('v8', 21)])
note('The later audit calls its source the latest expanded manuscript (Feedback L409); the figure review distinguishes original figures from revised Results (Feedback L174). The earlier Methods table uses V7’s headings (Feedback L19; Feedback L20; Feedback L25). The transcript does not list the files supplied to each prompt.', [('feedback', 19), ('feedback', 20), ('feedback', 25), ('feedback', 174), ('feedback', 409)])
note('Tim offered to read the draft. I think his input could be valuable given that he has published in Lab on a Chip twice. I would value his feedback on V7, with your revised version alongside it if you would like.', refs=[('published', 9), ('published', 10)])
for item in opening:
    if not item.get('quote'):
        item['text'] = table_handles(item['text'])
    item['refs'] = list(dict.fromkeys(('change', check_rows[number]) if name == 'evidence' else (name, number)
                                    for name, number in item.get('refs', [])))
heading = None
for item in opening:
    if item.get('style') == 'Heading1':
        heading = None
    elif item.get('style') in ('Heading2', 'Heading3'):
        heading = item
    elif heading is not None:
        rows = [ref for ref in item.get('refs', []) if ref[0] == 'change']
        heading['refs'] = list(dict.fromkeys(heading.get('refs', []) + rows))

# Keep a suggestion, its source and related comments together before the draft text.
ordered = []
position = 0
rows_by_id = {row['id']: row for row in decisions}
while position < len(opening):
    item = opening[position]
    if item.get('style') not in ('Heading2', 'Heading3'):
        ordered.append(item)
        position += 1
        continue
    end = next((i for i in range(position + 1, len(opening))
                if opening[i].get('style') in ('Heading1', 'Heading2', 'Heading3')), len(opening))
    children = opening[position + 1:end]
    quoted = next((child for child in children if child.get('quote')
                   and any(name == 'feedback' for name, _ in child.get('refs', []))), None)
    related = list(dict.fromkeys(
        [number for name, number in item.get('refs', []) if name == 'feedback']
        + [number for child in children for name, number in child.get('refs', [])
           if name == 'feedback']))
    if not related:
        related = list(dict.fromkeys(
            line for name, row_id in item.get('refs', []) if name == 'change'
            for line in rows_by_id[row_id]['feedback']))
    ordered.append(item)
    if quoted is not None:
        children.remove(quoted)
        primary = {number for name, number in quoted.get('refs', []) if name == 'feedback'}
        item['refs'] = [ref for ref in item.get('refs', []) if ref[0] != 'feedback']
        quoted['related_feedback'] = [line for line in related if line not in primary]
        ordered.append(quoted)
        if children and children[0]['text'] in ('ChatGPT suggestion:', 'ChatGPT recommends:',
                                                'ChatGPT’s figure audit says:'):
            children.pop(0)
    else:
        item['related_feedback'] = [line for line in related
                                    if ('feedback', line) not in item.get('refs', [])]
    ordered.extend(children)
    position = end
opening = ordered
(HERE / 'v7_v8_opening.json').write_text(json.dumps(opening, indent=2, ensure_ascii=False) + '\n')

front = []
summary_changes = set()
for item in opening:
    if item.get('style'):
        for name, row_id in item.get('refs', []):
            if name == 'change' and row_id not in summary_changes:
                front.extend([f'<a id="summary-change-{row_id.lower()}"></a>', ''])
                summary_changes.add(row_id)
    if item.get('style'):
        prefix = '#' * int(item['style'].removeprefix('Heading')) + ' '
    else:
        prefix = '> ' if item.get('quote') else ''
    line = prefix + item['text']
    if item.get('refs'):
        refs = []
        for name, p in item['refs']:
            if name == 'feedback':
                refs.append(f'[Feedback L{p}](alyson_feedback.md:{p})')
            elif name == 'evidence':
                refs.append(p)
            elif name == 'published':
                label = f'Paper {p}' if p else 'Published comparisons'
                refs.append(f'[{label}](#published-lab-on-a-chip-structures-comparable-to-ours)')
            elif name == 'measurement':
                refs.append('[Width data](#channel-measurements)')
            elif name == 'change':
                refs.append(f'[{p}](#change-{p.lower()})')
            elif name == 'source':
                refs.append(f'[Sources {p}](#sources-{p.lower()})')
            else:
                refs.append(locations(name, [p]))
        if item.get('inline_refs'):
            line += ' ' + '; '.join(refs) + '.'
        else:
            front.extend([line, '', '; '.join(refs) + '.', ''])
            continue
    front.extend([line, ''])
front += [
    '# Changes and remaining work',
    '',
    'V7 is the manuscript Tristan sent. V8 is the returned rewrite. This list covers every changed, added or removed main-text paragraph.',
    '',
    'R01-R52 compare the rewrite. R53 onward list remaining work, supplied files and optional additions.',
    '',
    'The table separates manuscript changes from figure suggestions that were not carried out.',
    '',
    '## My suggestions',
    '',
    '| ID | Change or work | My suggestion | What the sources show | Exact passages |',
    '| --- | --- | --- | --- | --- |',
]
for row in decisions:
    label = f"[{row['id']}](#summary-change-{row['id'].lower()})" if row['id'] in summary_changes else row['id']
    related = '<br>Related feedback: ' + '; '.join(f'[Feedback L{line}](alyson_feedback.md:{line})' for line in row['feedback']) if row['feedback'] else ''
    category = {'draft': '', 'remaining': 'Remaining: ', 'supplied': 'Supplied: ', 'optional': 'Optional: '}[row['kind']]
    front.append(f"| <a id=\"change-{row['id'].lower()}\"></a>{label} | {category}{row['title']} | {row['decision']} | {row['reason']}{related} | {locations('v7', row['v7'])}; {locations('v8', row['v8'])} |")
front += [
    '',
    '## Exact wording for each decision',
    '',
    'The quotes retain the original terminology. The explanations above use plain language. A paragraph can appear under more than one decision because V8 combines material that V7 kept separate.',
    '',
]
for row in decisions:
    front.extend([f"### {row['id']}. {row['title']}", ''])
    for name in ('v7', 'v8'):
        if not row[name]:
            front.extend([f'**{name.upper()}:** No corresponding passage.', ''])
        for p in row[name]:
            front.extend([f'**{name.upper()} P{p}:**', '', '> ' + paragraphs[name][p - 1], ''])

section = '\n'.join(front) + '\n'
report_path = ROOT / 'reviews/ALYSON_FEEDBACK_CHECK_20261013.md'
report = report_path.read_text()
old_start = report.find('# Alyson feedback: what matters for the reader')
if old_start < 0:
    raise ValueError('Original feedback check not found')
report_path.write_text(section + '\n---\n\n' + report[old_start:])
(HERE / 'v7_v8_decisions.json').write_text(json.dumps(decisions, indent=2, ensure_ascii=False) + '\n')
print(f'{len(decisions)} proposed decisions; every changed main-text paragraph covered.')
