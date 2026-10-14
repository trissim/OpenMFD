"""Compare the actual V9 file with V7 and render the linked review."""

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E
from PIL import Image

from compare_feedback_versions import read_document


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = ROOT / 'build/alyson_feedback_v7_v9_review_20261014'
BUILD.mkdir(exist_ok=True)
TEMPLATE = ROOT / 'reviews/alyson_feedback_v7_v8_review_v59.docx'
OUTPUT = ROOT / 'reviews/alyson_feedback_v7_v9_review.docx'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
NS = {'w': W[1:-1]}
BLUE, GREEN, ORANGE, BLACK, GRAY = '175DA0', '246B40', '925400', '222222', '595959'
COLORS = {'both': GREEN, 'v7': BLUE, 'v9': ORANGE, 'missing': GRAY, 'mixed': BLACK}
docs = {
    'v7': read_document(ROOT / 'pi_review_20261002/mfd_draft_v7.docx'),
    'v9': read_document(ROOT / 'build/mfd_draft_v9_alyson_version.docx'),
}
old_rows = json.loads((HERE / 'v7_v8_decisions.json').read_text())
rows = []


def add(number, title, old, new, suggestion, reason, status='both'):
    prior = old_rows[number - 1]
    rows.append(dict(id=f'R{number:02d}', title=title, v7=old, v9=new,
                     suggestion=suggestion, reason=reason, status=status,
                     feedback=prior['feedback'], checks=prior['checks']))


add(1, 'Title', [1], [1], 'Keep the shared title',
    'V9 retains the V7 title, including PDMS, SU-8 and the hybrid wafer mold.')
add(2, 'Authors and affiliations', [2], [3, 6, 7, 8], 'V9 layout',
    'V9 adds numbered affiliations and corresponding-author notation; its first affiliation now includes the department and institution.', 'v9')
add(3, 'Abstract', [4], [11], 'V7 framing with a concise device count',
    'V9 begins with neuronal applications and drops V7’s measured reuse totals (>50 casts; >8 months) and edge-growth limitation. Its “precise alignment” and “compartmentalized axonal growth” wording is stronger than the nominal registration and indirect-labeling accounts in Results/Discussion; keep the fabrication workflow, reuse observations and culture limit, using the reconciled device count from R53.')
add(4, 'Introduction: applications', [6], [13], 'V7 account of the applications',
    'V7 connects the method to neuroscience, stem-cell biology, cancer, immunology and developmental biology; V9 replaces this with neuronal connectivity and perturbations, understating the generalizability of the fabrication platform.')
add(5, 'Introduction: prior plate systems', [7, 8], [14], 'Platform context; fabrication methods remain the main comparison',
    'V9 adds high-capacity, modular and fluid-walled neuronal systems; check each new reference and the claim it supports, then use them as application context alongside the comparison of fabrication operations and equipment in V7 and Table S2.', 'v9')
add(6, 'Introduction: access to fabrication', [7], [15, 87], 'V7 equipment-access comparison and Table S2 link',
    'V7 compares obtaining a mold from a shared facility with acquiring molding or machining equipment and cites Table S2; V9 omits this Introduction comparison and citation, while retaining a shorter shared-facility account in Discussion.', 'v7')
add(7, 'Introduction: combining channels and wells', [8], [15], 'V7 fabrication comparison with its Table S2 link',
    'V9 narrows the comparison to hybrid micro–macro molding and additive neuronal devices and removes the second Table S2 citation; retain the comparison of operations each fabrication route adds.', 'v7')
add(8, 'Introduction: insert-based prior work', [8, 9, 68], [16, 85], 'Earlier prior-work comparison with V7’s array-transfer explanation',
    'V9 introduces Ristola’s individually placed metal inserts earlier and retains the single-operation transfer of 96 inserts in Discussion; keep that distinction, including its applicability to other insert arrangements.')
add(9, 'Introduction: what this study tests', [10, 16, 66], [17, 27, 60], 'Concise study overview; retain the untested-layout qualification',
    'Both describe the same fabrication and neuronal demonstration; V9 retains the computational-only status in Methods and Results but expands the overview and repeats dimensions.')
add(10, 'Methods: one-time fabrication and repeated casting', [12], [24, 87], 'Restore the short Protocol S1/S2 workflow explanation',
    'V9 removes the opening Methods sentence distinguishing routine production in Protocol S1 from one-time mold fabrication in Protocol S2; the two protocols are unchanged, and Discussion retains the underlying distinction.', 'v7')
add(11, 'Methods: design and generated files', [13, 14, 15, 16], [25, 26, 27], 'Keep separate design, tested-geometry and generated-layout paragraphs',
    'V9 preserves the software/export description, shared coordinates, device dimensions and untested layouts in three paragraphs; its leading heading is incorporated into the first paragraph rather than standing separately.')
add(12, 'Methods: SU-8 and SUEX layers', [17, 18, 19, 20, 21], [28, 29, 30, 31], 'Keep the layer and bake details',
    'V9 retains the base, microchannel and well layers, developer replacement, heating/cooling conditions and direct oven placement without controlled ramps; the procedural losses identified in V8 are absent here.')
add(13, 'Methods: resin printing', [15, 22], [26, 32], 'Keep design scaling separate from print-preparation compensation',
    'V9 retains the 2.26% design enlargement and explicitly says no shrinkage or tolerance compensation was applied in the print-preparation software.')
add(14, 'Methods: array transfer and bonding', [23], [33], 'Keep the procedure in Methods',
    'V9 retains the rubber position, thickness and hardness, clamps, epoxy, washes, cure and release sequence; the corresponding height variation and seating outcome remain in Results.')
add(15, 'Methods: parylene coating', [24], [34], 'Keep the separate coating paragraph',
    'V9 preserves the coating thickness, facility, equipment and pre-coating design dimensions; its added PMID should be verified and formatted with the other references.')
add(16, 'Methods: frame printing', [26], [35], 'Keep the supplied printing-file details',
    'V9 retains HIPS printing conditions, Table S6 and the supplied Creality Print 6.0.4 G-code file.')
add(17, 'Methods: casting, demolding and glass bonding', [25, 27, 28, 29], [36, 37, 38], 'Keep the detailed casting and bonding sequence',
    'V9 retains the rack, parallel processing, wafer support, peeling direction, guillotine, glass dimensions and bonding parameters; it adds prior-work references to the tapered-sidewall paragraph.')
add(18, 'Methods: frame assembly and surface treatment', [30, 31], [39, 40], 'Keep the assembly sequence and distinct plasma steps',
    'V9 retains frame/glass orientation, adhesive volume and cure, trimming, and the separate second plasma treatment; its explanatory final sentence repeats a distinction already made by the sequence.')
add(19, 'Methods: mold and device assessment', [32, 33, 34, 35], [41, 42, 43], 'Keep the inspection criteria and unframed control',
    'V9 retains individual pin measurements, inspection criteria, usable-cast definition, adhesive culture screening and the single unframed control; it also retains the statement that toxicity was not quantified.')
add(20, 'Methods: pipetting and microscopy', [36], [44], 'Keep the experiment-specific procedure',
    'Both identify eight fitted tips and imaging on two unmodified high-content systems.')
add(21, 'Methods: fluorescent tracers', [37, 38], [45], 'Keep the tracer procedure and its stated limit',
    'V9 retains the secondary antibodies, volumes, dilution, incubation, objective, binning, exposure and visual assessment; it also retains the unmeasured flow-rate and duration limit.')
add(22, 'Methods: neuronal culture and CTβ', [39, 40, 41], [46, 48], 'Keep V7’s terminology; reconcile the exclusions in R53',
    'V9 retains the one-embryo preparation, coating, plating, medium, CTβ timing and exclusion rule; it moves the technical-replicate statement into the culture paragraph and explains soma/axon terminology.')
add(23, 'Methods: imaging and counting', [42, 43, 44], [49, 50], 'Keep the imaging and baseline explanation',
    'V9 retains the pixel scale, exposures, stitching, common counting area, reason for Plate 3’s larger grid and the pre-axotomy baseline sentence; the baseline clarification requested in the saved discussion is already present in both V7 and V9.')
add(24, 'Methods: statistics', [45, 46], [51], 'Keep the descriptive summaries; update them with R53',
    'V9 retains the within-plate SD and explicit technical-replicate explanation without V8’s extra warning about inferring other preparations.')
add(25, 'Results: four groups become six', [48, 55, 62, 65], [58, 61, 67, 71, 74, 77], 'Discuss four versus six Results groups',
    'V9 separates design, mold development, casting, compatibility, tracer transport and neuronal testing; V7 covers these topics in four groups, and both already separate procedures from findings.', 'v9')
add(26, 'Results: coordinated design and plate geometry', [49], [58, 59], 'V7’s concise account under the proposed design heading',
    'V9 explains the same coordinated components and dimensions over two paragraphs; these dimensions are already specified in Methods, so the Results can concentrate on what the coordinated design enables.')
add(27, 'Results: alternative layouts moved earlier', [65, 66], [60], 'Earlier placement with concise generated-layout wording',
    'V9 places alternative fabrication files beside the design result and retains the untested status; V7 explains the same coordinated changes in its final Results group.')
add(28, 'Results: general mold-development statements', [49, 50, 51], [61, 66], 'Begin with the failures and solutions; omit the recap',
    'V9 adds an opening requirement statement and a closing summary around the existing filter, adhesion and clamping observations; the intervening paragraphs already show how the mold was developed.', 'v9')
add(29, 'Results: filter and base-layer observations', [50, 51], [62, 63], 'Existing observations with direct Figure S1/S2 links',
    'Both report the raised edges, detachment and successful process changes in Results; V9 still cites only Notes S1/S2 rather than the figures themselves.')
add(30, 'Results: additional SU-8 bake', [51], [63], 'Keep the batch observations without calling the process optimized',
    'V9 keeps the eight-wafer and subsequent two-wafer observations; “optimization” and “optimized” also appear in its mold-development account, although the sequential batches do not isolate variables or establish an optimum.')
add(31, 'Results: pin heights and clamping', [52], [64], 'Keep the added mean and SD with the existing clamping result',
    'V9 brings the mean 5.551 mm and SD 26.7 µm from Table S1 into main Results alongside V7’s existing 116 µm range, uneven rigid clamping and successful EPDM seating.')
add(32, 'Results: open channels and mold release', [53], [65], 'Report the observation; integrate the width check in R59',
    'Both report open cast channels and unmeasured channel dimensions; V9 retains the limit beside that result, while its later Discussion repeats it.')
add(33, 'Results: repeated casting and mold use', [54, 56], [67, 68], 'Keep the reuse observations and V9’s Figure 3 link',
    'V9 retains five assembled molds, three used routinely, more than 50 casts, both losses and more than eight months of use; it adds a direct Figure 3 callout and does not retain V8’s standardized-durability warning.')
add(34, 'Results: frame materials and adhesives', [57, 58], [69, 70], 'V7’s direct observations without a new strength warning',
    'V9 retains lower visible HIPS warping and the surviving SI 5140 cultures but changes the failed-adhesive wording and adds an unperformed mechanical-strength test; Methods already states that toxicity was not quantified.')
add(35, 'Results: multichannel loading', [55, 56], [71, 73], 'Keep the eight-well loading observation',
    'V9 reports the manual eight-well operation without V8’s robotic-dispensing warning; its closing compatibility paragraph repeats the preceding loading and imaging observations.')
add(36, 'Results: microscope use', [60], [72], 'Restore the reason for choosing Opera Phenix',
    'Both report use of two unmodified systems; V9 omits V7’s explanation that Opera Phenix was faster for these experiments.', 'v7')
add(37, 'Results: tracer movement', [61], [74, 75, 76], 'V7’s concise result and limit',
    'V9 spreads loading, redistribution and the existing flow/isolation limit over three paragraphs; V7 already reports the two-time-point result and its limits in one Results paragraph.')
add(38, 'Results: neuronal labeling', [62, 63], [77, 78], 'Concise neuronal result with the Figure 4B link',
    'V9 adds the direct Figure 4B link and retains the inference of uptake by axons and retrograde transport; its abstract uses stronger “compartmentalized axonal growth” wording than this result supports directly.')
add(39, 'Results: assessed and counted devices', [64], [79, 80], 'Integrate the updated DMSO counts and plot in R53',
    'Both report 72 interior devices, three exclusions and 69 analyzed devices, with plate means and within-plate SD; the later DMSO dataset needs a reconciled exclusion account before replacing those totals.')
add(40, 'Results: unframed control and edge growth', [59, 64, 73], [81], 'Keep the control observation with its limits',
    'V9 moves the unframed control into neuronal Results and explicitly lists the unresolved frame, adhesive, sealing and culture-environment contributions; V7 already reports the control and unresolved cause.')
add(41, 'Results: repeated neuronal-summary paragraph', [75], [82, 88], 'Keep the result; state the independent-preparation limit once',
    'V9 adds a closing neuronal-validation summary and future independent-preparation sentence, then repeats the same limit in Discussion; the one-preparation design is already explicit in Methods.', 'v9')
add(42, 'Discussion: contribution and prior inserts', [67, 68], [84, 85], 'V7’s process-centered account with the earlier prior-work citation',
    'V9 retains simultaneous positioning and transfer across other array layouts but expands the contribution and adds an alignment-accuracy warning; its introductory statement remains centered on the fabrication strategy.')
add(43, 'Discussion: printer resolution and parylene', [69], [86], 'Keep printed parts confined to the mold; vet the added references',
    'V9 retains the distinction between resin in the mold and PDMS/glass in the finished device, adds printed-mold/coating references, and appends a future configuration-compatibility qualification.')
add(44, 'Discussion: repeated use and bench production', [70, 71], [87], 'Keep the one-time mold/repeated-casting explanation',
    'V9 retains the eight-month use observation and later bench production, then adds unmeasured time, labor and cost comparisons; V7 describes avoided processing steps rather than claiming measured savings.')
add(45, 'Discussion: coating and working volume', [72], [89], 'Keep the coating explanation and integrate R59',
    'Unlike V8, V9 retains the relative-height explanation: coating raises both ridge and surrounding surface; it also retains the expected width increase and 50 µL working-volume constraint, while adding dimensional-fidelity and scaling-refinement proposals.')
add(46, 'Discussion: edge growth', [73], [90], 'V7’s concise wording with the unresolved frame factors',
    'Both report the poorer peripheral growth and unframed control; V9 expands the same unresolved mechanism into a separate Discussion paragraph after describing it in Results.')
add(47, 'Discussion: adapting other layouts', [74], [91], 'Keep the coordinated-design explanation and tested/generated distinction',
    'Both explain changes to pins, holes, adhesive space and layout; V9 retains the shared-file logic but adds a list of future alignment, casting, transport and biological checks for the untested layouts.')
add(48, 'Conclusion', [76, 77], [92, 93], 'V7 conclusion with concise observed reuse and assay results',
    'V9 repeats the contribution and adds future quantitative reproducibility and peripheral-culture work; its “48 independent” devices should mean separate device units rather than independent biological replicates.')
add(49, 'Code, files and data statement', [78, 79, 80, 81], [94, 95], 'Accurate file list and dataset availability, with a completed study archive',
    'V9 compresses the file list and states that experimental data are provided in the supplement or repository; the embedded supplement is unchanged and lacks individual counts, so name the actual supplied dataset and reconcile it through R53, while completing the promised versioned archive.')
add(50, 'Conflict-of-interest statement', [78, 82], [94, 96, 97], 'Keep the declaration and put it before Data availability',
    'V9 adds the conflicts declaration after Data availability; the required order is conflicts, data availability, acknowledgements.', 'v9')
add(51, 'Acknowledgements and funding', [82, 83], [98], 'V7 acknowledgements plus accurate funding details',
    'V9 adds CIHR and MSCanada funding but removes V7’s separate thanks; verify the funding and retain the existing acknowledgements as appropriate.')
add(52, 'References and citation style', list(range(84, 109)), [13, 16, 27, 34, 108], 'V7 bibliography with vetted new entries and consistent citations',
    'V7 has a 24-entry bibliography and author–year citations; V9 omits that list and adds 20 PMID/PMIDs labels while retaining author–year text in the legends, supplement and some Methods paragraphs; include the complete references, vet the additions, and apply the final numbered journal style.')
add(53, 'Updated DMSO counts and Figure 4 text', [41, 64, 81, 116, 245, 247], [48, 79, 80, 95, 106, 235, 237], 'Integrate the recent DMSO plot and match the text',
    'The later DMSO package has 72 rows and five counting-artifact exclusions, giving 22, 21 and 24 devices (67 total); both drafts still report three exclusions and 69 devices, so reconcile the flags with the exclusion rule, then update Methods, Protocol S1, Results, Figure 4 and its legend.', 'missing')
add(54, 'Figure 4 scale bars', [43, 116], [49, 106], 'Use the recent calibrated CTβ views; add tracer bars',
    'The newer supplementary-biology views supply calibrated 500 µm CTβ bars and crop dimensions; integrate these views into Figure 4, while adding the acquisition scale and bar to the separate tracer panel.', 'missing')
add(55, 'Counting-method settings', [241], [231], 'Integrate the saved supplementary-biology counting method',
    'The newer analysis supplies software, count tables, overlays and saved settings; identify the configuration matching the chosen dataset and integrate it into Methods and Protocol S1, with the reconciled exclusions from R53.', 'missing')
add(56, 'Animal approval details', [226], [216], 'Add the approving body, guidelines and approval number',
    'Both protocols mention an approved procedure but omit the approving body, guidelines and approval number.', 'missing')
add(57, 'Supplementary table layout', [121, 129, 131], [111, 119, 121], 'Restore compact S1 numbers; widen the S2/S3 columns',
    'The data are unchanged, but V9 removes S1’s explicit 10-point cell text and inherits a 12-point default; in its rendered page 21, 5.567 splits into 5.56 and 7, and the other heights wrap similarly. The earlier V7/V8 render kept these values on one line. V9 also splits long words in S2; restore readable numerical cells and widen the comparison columns.', 'v9')
add(58, 'Separate supplement and height CSV', [119, 121], [109, 111], 'Use the existing separate supplement and height CSV',
    'The 96-height CSV matches Table S1 and the existing separate supplement matches V7’s supplementary text and ten tables; V9 retains those contents unchanged.')
add(59, 'Later channel-width measurements', [53], [65, 89], 'Report the width estimates with their measurement method',
    'The later check supplies nine brightfield ruler estimates from three devices, spanning 10.7–13.1 µm; moving each blurred-wall endpoint by one pixel changes a span by up to 2.37 µm, so report the pixel scale, endpoint rule and overlays with the estimates.', 'missing')
add(60, 'Individual mold-production records', [54], [68, 87], 'Keep the reuse observations; add per-mold records if available',
    'Both report more than 50 casts, more than eight months of use and both mold losses; existing per-mold records could add detail, but no new durability study is proposed.')
add(61, 'Channel depth and between-cast comparisons', [53, 72], [65, 89], 'No new depth or cast-to-cast study proposed',
    'The saved discussion proposes depth and between-cast measurements; integrate the available width estimates in R59 without adding those studies.', 'missing')
add(62, 'Figure layout and additional plots', [110, 112, 114, 116, 118], [100, 102, 104, 106, 108], 'Revisit image sizes and Figure 3/5 layout; integrate the supplied biology views',
    'All five legend titles, device/alignment views and Figure 5’s three application rows already exist; V9 removes the legends’ explicit 11-point size and inherits 12-point text. Revisit image sizes and layout and integrate the recent device-dot plot and calibrated views; height and aggregate mold plots are possible uses of existing data, not proposed additions here.')
add(63, 'Small supplement edits', [152, 153, 155, 157, 158, 159, 161, 332], [142, 143, 145, 147, 148, 149, 151, 322], 'Add note citations and clarify the protocol inspection instruction',
    'Add Figure S1/S2 links within the corresponding notes; Table S3 already separates tested and generated-only designs, and the protocol’s open-channel result can become an inspection instruction; no raised-edge measurement experiment is proposed.')

rows_by_id = {row['id']: row for row in rows}
for row in rows:
    for version in docs:
        for number in row[version]:
            assert 0 < number <= len(docs[version]['paragraphs']), (row['id'], version, number)
summary = {
    'tables_identical': docs['v7']['tables'] == docs['v9']['tables'],
    'media_identical': Counter(docs['v7']['media_sha256'].values()) == Counter(docs['v9']['media_sha256'].values()),
    'supplement_identical': [p for p in docs['v7']['paragraphs'][118:] if p] == [p for p in docs['v9']['paragraphs'][108:] if p],
    'legends_identical': [docs['v7']['paragraphs'][p-1] for p in (110,112,114,116,118)] == [docs['v9']['paragraphs'][p-1] for p in (100,102,104,106,108)],
    'methods_words': {name: sum(len(p.split()) for p in data['paragraphs'][data['paragraphs'].index('Materials and Methods')+1:data['paragraphs'].index('Results')]) for name, data in docs.items()},
}
assert all(summary[key] for key in ('tables_identical','media_identical','supplement_identical','legends_identical'))


def qtext(node):
    return ''.join(node.xpath('.//w:t/text()', namespaces=NS))


def elem(parent, tag, **attrs):
    child = E.SubElement(parent, W + tag)
    for key, value in attrs.items():
        child.set(W + key, str(value))
    return child


def run(parent, text, color=BLACK, bold=False, size=22, italic=False, underline=False):
    r = elem(parent, 'r')
    props = elem(r, 'rPr')
    elem(props, 'color', val=color)
    elem(props, 'sz', val=size)
    if bold:
        elem(props, 'b')
    if italic:
        elem(props, 'i')
    if underline:
        elem(props, 'u', val='single')
    t = elem(r, 't')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return r


bookmark_id = 100000


def bookmark(p, anchor):
    global bookmark_id
    bookmark_id += 1
    start = E.Element(W+'bookmarkStart', {W+'id': str(bookmark_id), W+'name': anchor})
    p.insert(1 if p.find(W+'pPr') is not None else 0, start)
    elem(p, 'bookmarkEnd', id=bookmark_id)


def wording_color(version, number):
    other = 'v9' if version == 'v7' else 'v7'
    text = docs[version]['paragraphs'][number-1]
    return GREEN if text in docs[other]['paragraphs'] else BLUE if version == 'v7' else ORANGE


def link(p, label, anchor, color=BLACK, size=18, bold=False):
    h = elem(p, 'hyperlink', anchor=anchor)
    run(h, label.replace(' ', '\u00a0') if re.fullmatch(r'V[79] P\d+|Feedback L\d+', label) else label,
        color=color, size=size, bold=bold, underline=True)
    return h


def paragraph(parent, text='', style=None, anchor=None, size=22):
    p = elem(parent, 'p')
    props = elem(p, 'pPr')
    if style:
        elem(props, 'pStyle', val=style)
    elem(props, 'spacing', after=100, line=240, lineRule='auto')
    if style and style.startswith('Heading'):
        elem(props, 'keepNext')
        size={'Heading1':30,'Heading2':26,'Heading3':22}[style]
        props.find(W+'spacing').set(W+'before','160')
    if style=='Quote':
        elem(props,'shd',val='clear',fill='F3F4F5')
        borders=elem(props,'pBdr')
        elem(borders,'left',val='single',sz=12,color='999999',space=6)
        elem(props,'ind',left=180)
    cursor = 0
    for match in re.finditer(r'\bV([79])\s+P(\d+)\b|\bFeedback L(\d+)\b|\bR(\d{2})\b|right-click|Open Hyperlink', text):
        run(p, text[cursor:match.start()], size=size)
        if match[1]:
            version, number = 'v'+match[1], int(match[2])
            link(p, match[0], f'cmp_{version}_P{number}', wording_color(version, number), size)
        elif match[3]:
            number = int(match[3])
            link(p, match[0], f'src_L{number:03d}', feedback_colors.get(number, BLACK), size)
        elif match[4]:
            link(p, match[0], f'change_R{match[4]}', size=size)
        else:
            run(p,match[0],size=size,underline=True)
        cursor = match.end()
    run(p, text[cursor:], size=size)
    if style and style.startswith('Heading'):
        for r in p.iter(W+'r'):
            elem(r.find(W+'rPr'),'b')
    if anchor:
        bookmark(p, anchor)
    return p


def field(p, anchor):
    r = elem(p, 'r')
    elem(r, 'fldChar', fldCharType='begin')
    instruction = elem(elem(p, 'r'), 'instrText')
    instruction.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    instruction.text = f' PAGEREF {anchor} \\h '
    elem(elem(p, 'r'), 'fldChar', fldCharType='separate')
    run(p, '0')
    elem(elem(p, 'r'), 'fldChar', fldCharType='end')


def page_link(parent, label, anchor, end=None, prefix=''):
    p = paragraph(parent, prefix)
    link(p, label, anchor, size=22)
    run(p, ' (pp. ' if end else ' (p. ')
    field(p, anchor)
    if end:
        run(p, '–')
        field(p, end)
    run(p, ')')
    return p


def excerpt(parent, version, number, text):
    assert text in docs[version]['paragraphs'][number-1], (version, number, text)
    p = paragraph(parent, '', 'Quote')
    run(p, text, italic=True)
    paragraph(parent, f'{version.upper()} P{number}', size=18)


def make_table(parent, headers, widths):
    table = elem(parent, 'tbl')
    props = elem(table, 'tblPr')
    elem(props, 'tblW', w=sum(widths), type='dxa')
    elem(props, 'tblLayout', type='fixed')
    borders = elem(props, 'tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        elem(borders, edge, val='single', sz=4, color='CCCCCC')
    margins = elem(props, 'tblCellMar')
    for edge in ('top','left','bottom','right'):
        elem(margins, edge, w=75, type='dxa')
    grid = elem(table, 'tblGrid')
    for width in widths:
        elem(grid, 'gridCol', w=width)
    if not headers:
        return table
    tr = elem(table, 'tr')
    elem(elem(tr,'trPr'),'tblHeader')
    for text, width in zip(headers,widths):
        tc = elem(tr,'tc')
        props=elem(tc,'tcPr')
        elem(props,'tcW',w=width,type='dxa')
        elem(props,'shd',fill='EEEEEE',val='clear')
        p=paragraph(tc)
        run(p,text,bold=True)
    return table


def quote_refs(parent, row):
    p=paragraph(parent,'',size=18)
    for version in docs:
        cited = set(int(m[1]) for m in re.finditer(version.upper()+r' P(\d+)',row['reason']))
        numbers = row[version]
        if row['id']=='R52' and version=='v7':
            numbers=[84,85,108]
        for number in numbers:
            if number not in cited:
                link(p,f'{version.upper()} P{number}',f'cmp_{version}_P{number}',wording_color(version,number))
                run(p,'    ',size=18)
    return p


def write_package(parts,path):
    with ZipFile(path,'w',ZIP_DEFLATED) as archive:
        for name,content in parts.items():
            archive.writestr(name,content)


def serialized(node):
    return E.tostring(node,xml_declaration=True,encoding='UTF-8',standalone=True)


def source_lines(p):
    return ''.join(n.text or '' if n.tag==W+'t' else '\n'
                   for n in p.iter() if n.tag in (W+'t',W+'br')).splitlines()


def restore_external_link(p, original):
    label=qtext(original)
    for r in list(p.findall(W+'r')):
        t=r.find(W+'t')
        if t is None or label not in (t.text or ''):
            continue
        before,after=t.text.split(label,1)
        index=p.index(r)
        p.remove(r)
        for offset,(text,node) in enumerate(((before,deepcopy(r)),(None,deepcopy(original)),(after,deepcopy(r)))):
            if text is not None:
                node.find(W+'t').text=text
            p.insert(index+offset,node)
        return


def feedback_metadata(parts):
    """Retain the annotated selections, reassessing their V9 coverage."""
    original=E.fromstring(parts['word/comments.xml'])
    source_lines={}
    current_line=None
    for node in E.fromstring(parts['word/document.xml']).iter():
        if node.tag==W+'bookmarkStart' and re.fullmatch(r'src_L\d+',node.get(W+'name','')):
            current_line=int(node.get(W+'name').removeprefix('src_L'))
        elif node.tag==W+'commentRangeStart':
            if current_line is None:
                raise ValueError('Comment precedes its transcript handle')
            source_lines[int(node.get(W+'id'))]=current_line
    notes=[]
    overrides={
        12:('both','V7 P51 reports SU-8 detachment on bare silicon and the base layer that prevented it; V9 P63 retains both observations. R29 covers the missing direct Figure S2 citation separately.'),
        22:('both','V7 P64 and V9 P79 report poorer edge growth and explain why analysis was restricted to interior devices. R53 covers integrating the later count dataset.'),
        27:('both','V7 P56 and V9 P71 report manual multichannel loading; V9 does not retain V8’s automated-dispensing warning. R35 covers the loading result.'),
        33:('both','Methods contains 2,226 words in V7 and 2,194 in V9; V7 P23 and V9 P33 give the bonding procedure, while V7 P52 and V9 P64 report its outcome. Both retain the detailed protocols.'),
        45:('both','Table S1 supplies one array’s measured heights and Table S5 supplies aggregate mold records; those data could be plotted, but no new characterization figure is proposed here (R62).'),
        69:('both','Table S5 supplies aggregate reuse observations, not mold-by-mold counts; R62 retains those observations without adding a durability plot.'),
        91:('mixed','V9 removes the legends’ explicit 11-point text size and inherits 12-point Times New Roman; the figure images and their labels are unchanged. R62 covers their presentation separately.'),
        104:('mixed','The saved discussion accompanied V8. Its Table S2 and mixed-citation observations also apply to V9, but V9 P50 retains the baseline explanation requested at Feedback L543. R07, R23 and R52 separate those points.'),
        105:('v9','V9 P67 adds the Figure 3 callout and V9 P78 adds Figure 4B; V7 already states the tracer limit and technical-replicate design. R33, R38 and R37 cover those distinctions.'),
        108:('v9','V9 P67 includes the direct Figure 3 link missing from V7 main text. R33 keeps that useful link with the existing reuse observations.'),
        109:('v9','V9 P78 includes the direct Figure 4B link missing from V7 main text. R38 keeps the link with the existing labeling result.'),
        144:('both','V7 P44 and V9 P50 both state that the images were collected before axotomy; their protocols also identify the baseline dataset. The clarification requested here is already present in V9 (R23).'),
        148:('both','V7 P79 and V9 P95 identify software and fabrication files and promise a versioned archive. V9 states experimental data are provided; identify the actual dataset and completed release in R49 and R53.'),
        149:('both','V7 P80 identifies frame G-code and Plate 1 microscope XML; V9 P35 retains the G-code description and V9 P50 retains the XML description. R49 covers including those files in the archived study package.'),
        152:('v7','V7 P84 starts the 24-entry bibliography; V9 has no reference-list heading or entries before its legends. R52 covers restoring the list, vetting new citations and final formatting.'),
        165:('both','This repeats Feedback L543; V7 P44 and V9 P50 both retain the pre-axotomy baseline explanation. R23 records that the V8 deletion is absent from V9.'),
        131:('both','Table S2 has the same content in V7 and V9; the new V9 render splits long words, as did the earlier render. R57 covers widening the comparison columns.'),
        134:('v9','Both drafts supply the same 96 heights, but V9 removes the explicit 10-point cell setting and its page 21 now splits 5.567 into 5.56 and 7; the earlier render kept the numbers on one line. R57 covers this V9 formatting change; R58 supplies the existing CSV.'),
        135:('both','Tables S2/S3 retain their contents and S3 already distinguishes tested from generated-only layouts; S2 still splits long words. R57 covers widening the comparison columns.'),
        161:('mixed','This repeats the table-layout requests: S2/S3 retain their contents, while V9’s S1 numbers now wrap after removal of the compact cell font. R57 covers restoring the numerical layout and widening comparison columns.'),
    }
    paragraph_map={8:11,18:26,19:28,20:31,21:32,22:33,23:36,24:35,25:41,26:44,27:45,28:46,29:48,30:49,31:51,34:58,35:59,36:60,37:61,38:62,39:63,40:64,41:65,42:67,43:68,44:70,45:71,46:72,47:75,48:76,49:78,50:78,51:80,54:84,55:85,56:87,57:88,58:89,59:90,60:91,61:93,62:93,63:94,64:95,65:96,66:97,67:98,71:100,73:102,75:104,77:106,79:108}
    def map_number(number):
        return number+29 if number>=80 else paragraph_map[number]
    def convert_answer(text):
        text=text.replace('\u00a0',' ')
        text=re.sub(r'V8 P(\d+)-P(\d+)',lambda m:'V9 P'+str(map_number(int(m[1])))+'–P'+str(map_number(int(m[2]))),text)
        text=re.sub(r'V8 P(\d+)',lambda m:'V9 P'+str(map_number(int(m[1]))),text)
        return text.replace('V8','V9')
    for comment in original:
        number=int(comment.get(W+'id'))
        label=qtext(comment[0])
        status='both' if label=='In V7 and V8.' else 'v7' if label=='In V7 only.' else 'v9' if label=='In V8 only.' else 'missing' if label=='Not supplied in V7 or V8.' else 'mixed'
        answer=convert_answer(qtext(comment[1]))
        if number in overrides:
            status,answer=overrides[number]
        targets=comment.xpath('.//w:hyperlink/@w:anchor',namespaces=NS)
        row_ids=list(dict.fromkeys(t.removeprefix('change_') for t in targets if t.startswith('change_R')))
        source_links=[t for t in targets if t.startswith('src_L')]
        if not source_links:
            raise ValueError('Comment has no transcript target: '+str(number))
        notes.append(dict(id=number,status=status,answer=answer,rows=row_ids,
                          line=source_lines[number],
                          related=list(dict.fromkeys(source_links))))
    return notes


feedback_colors={}


def build():
    with ZipFile(TEMPLATE) as archive:
        parts={name:archive.read(name) for name in archive.namelist()}
    notes=feedback_metadata(parts)
    for number in {note['line'] for note in notes}:
        statuses={note['status'] for note in notes if note['line']==number}
        feedback_colors[number]=COLORS[next(iter(statuses))] if len(statuses)==1 and 'missing' not in statuses else BLACK
    for note in notes:
        for number in note['related']:
            feedback_colors.setdefault(int(number.removeprefix('src_L')),BLACK)
    doc=E.fromstring(parts['word/document.xml'])
    body=doc.find(W+'body')
    old=list(body)
    start=next(i for i,n in enumerate(old) if qtext(n)=='Feedback suggestions and review comments')
    end=next(i for i,n in enumerate(old) if qtext(n)=='Cited V7 and V8 passages')
    transcript=[deepcopy(n) for n in old[start:end]]
    source_start=next(i for i,n in enumerate(old) if qtext(n)=='Additional sources and images')
    source_end=next(i for i,n in enumerate(old) if qtext(n)=='Published Lab on a Chip comparisons')
    supporting=[deepcopy(n) for n in old[source_start:source_end]]
    source_targets={b.get(W+'name') for n in supporting for b in n.iter(W+'bookmarkStart')}
    published=[deepcopy(n) for n in old[source_end:] if n.tag!=W+'sectPr']
    section=deepcopy(body.find(W+'sectPr'))
    for child in list(body):
        body.remove(child)
    paragraph(body,'V7 and V9 comparison','Heading1','review_intro')
    paragraph(body,'After our discussion, I compared the additional V9 file you shared with V7, the draft I sent. I also used ChatGPT to organize the comparison, then checked the passages against both files. This comparison replaces the V8-specific findings where V9 differs.')
    paragraph(body,'V9 retains the baseline-image explanation, detailed baking and assembly procedures, print-preparation setting and coating-height explanation. Its Methods contains 2,194 words versus 2,226 in V7. The title, all five legends, supplementary text, ten tables and seven image contents are unchanged.')
    paragraph(body,'The Table S2 citations and reference list are still absent, and the mixed citation styles remain. V9 adds useful Figure 3/4B links and pin-height statistics in Results. The newer count dataset, calibrated images and saved counting settings can be integrated alongside the remaining citation, layout, ethics and archive fixes.')
    paragraph(body,'I kept the fabrication method central in the suggestions, with neuronal culture as one tested use. I also marked added warnings about tests the paper does not claim, and places where the rewrite repeats existing results or limits.')
    paragraph(body,'The links let you compare the passages and return to the rows without searching through the files. In Word for Mac, right-click a handle and choose Open Hyperlink; use the R links to return to the table, or Contents in the footer.')
    p=page_link(body,'revision table','change_R01','revision_table_end','The main part to review is the ')
    run(p,'. You can leave comments in its rows.')
    p=paragraph(body,'The remaining ')
    bookmark(p,'remaining_support_pages')
    run(p,'00')
    # Keep the dynamic value in its own bookmark for the page-cache pass.
    marker=p.find(W+'bookmarkStart')
    closing=p.find(W+'bookmarkEnd')
    p.remove(closing)
    p.append(closing)
    run(p,' pages are linked supporting material: the saved ChatGPT discussion, cited passages, sources and images.')
    paragraph(body,'Reading guide','Heading2')
    paragraph(body,'V7 P8 = version 7, paragraph 8. V9 P50 = version 9, paragraph 50. R = table row; L = line in the saved ChatGPT discussion.')
    paragraph(body,'Source-handle colors compare wording; comment colors show whether the point is covered.')
    paragraph(body,'The discussion below is the one shared with V8; its comments now check the corresponding points against V7 and V9.')
    paragraph(body,'Contents','Heading2','review_contents')
    entries=[('Comparison (details)','comparison','comparison_end'),
             ('Revision table (leave comments here) ←','change_R01','revision_table_end'),
             ('ChatGPT discussion, with comments (mostly accessed via links)','nav_transcript','nav_transcript_end'),
             ('Cited V7 and V9 passages','nav_passages','nav_passages_end'),
             ('Additional sources and images','detailed_evidence','detailed_evidence_end'),
             ('Published Lab on a Chip comparisons','published_comparisons','published_comparisons_end')]
    toc=make_table(body,[],[7100,2260])
    for border in toc.find(W+'tblPr').find(W+'tblBorders'):
        border.set(W+'val','nil')
    for label,anchor,last in entries:
        tr=elem(toc,'tr')
        cells=[]
        for width in (7100,2260):
            cell=elem(tr,'tc');elem(elem(cell,'tcPr'),'tcW',w=width,type='dxa');cells.append(cell)
        left=paragraph(cells[0])
        link(left,label,anchor,size=22)
        p=paragraph(cells[1])
        elem(p.find(W+'pPr'),'jc',val='right')
        run(p,'→ pp. ' if anchor=='change_R01' else 'pp. ',size=18)
        field(p,anchor);run(p,'–',size=18);field(p,last)
        for r in p.iter(W+'r'):
            props=r.find(W+'rPr')
            if props is not None:props.find(W+'sz').set(W+'val','18')
        if anchor=='change_R01':
            for r in tr.iter(W+'r'):
                props=r.find(W+'rPr')
                if props is None:
                    props=E.Element(W+'rPr');r.insert(0,props)
                elem(props,'b')
    paragraph(body,'Comparison','Heading1','comparison')
    paragraph(body,'Already covered in V7','Heading2')
    paragraph(body,'Table S2 was cited twice before the rewrite removed its links','Heading3')
    paragraph(body,'Supplementary Table S2 is not cited anywhere in the main manuscript.','Quote')
    paragraph(body,'Feedback L415',size=18)
    excerpt(body,'v7',8,'Laser removal of material (ablation), direct printing, hot embossing, hard-plastic fabrication, and modular inserts combine these scales using different equipment and added operations (Supplementary Table S2).')
    paragraph(body,'V7 P7 and V7 P8 both cite Table S2; V9 P15 retains a narrower fabrication comparison without either citation. R06 and R07 propose keeping the comparison and its links; Feedback L488 repeats the request.')
    paragraph(body,'The baseline explanation is retained in V9','Heading3')
    paragraph(body,'I would clarify that these are baseline measurements from an experiment conducted before axotomy','Quote')
    paragraph(body,'Feedback L543',size=18)
    excerpt(body,'v9',50,'These were baseline images collected before axotomy; Supplementary Protocol S1 describes the dataset.')
    paragraph(body,'V7 P44 and V9 P50 both give this explanation; R23 keeps it with the imaging procedure.')
    paragraph(body,'Procedures and outcomes already occupy different sections','Heading3')
    paragraph(body,'V7 P23 and V9 P33 give the EPDM/clamping procedure in Methods; V7 P52 and V9 P64 report the height spread and seating result in Results. V7 P33 and V9 P41 describe cast inspection, while V7 P54 and V9 P68 report cast output and elapsed use. R14, R19, R31 and R33 cover those examples.')
    paragraph(body,'Figure 1 already shows the two-well geometry; Figure 2 shows the pin and EPDM backing; the five legends already have titles and Figure 5 has three application rows. R62 covers the presentation changes.')
    paragraph(body,'Useful V9 edits','Heading2')
    paragraph(body,'V9 P67 and V9 P78 add direct Figure 3 and Figure 4B links (R33; R38); V9 P64 brings Table S1’s mean and SD into main Results beside the existing height spread (R31). R27 covers moving generated layouts beside design, and R25 covers four versus six Results groups.')
    paragraph(body,'Work still needed','Heading2')
    paragraph(body,'The direct Figure S1/S2 links are still missing (R29); the mixed citation styles and absent bibliography remain (R52). V9 P13 contains main-text PMIDs, while V9 P108 retains author–year citations in the unchanged Figure 5 legend; some Methods references also remain author–year.')
    paragraph(body,'R53–R55 cover integrating the newer count dataset, calibrated CTβ views and saved counting configuration. R59 covers the later width estimates. R56 covers animal approval details, R49 the study archive, and R50 the conflicts/data-availability order.')
    paragraph(body,'V9’s rendered Table S1 now breaks 5.567 into 5.56 and 7, despite unchanged values; its cell text no longer has V7’s explicit 10-point size and inherits the 12-point default. R57 shows this formatting change and covers widening the comparison tables.')
    paragraph(body,'Removed explanations and added warnings','Heading2')
    paragraph(body,'Removed explanations','Heading3')
    paragraph(body,'V9 P72 omits V7 P60’s reason for choosing Opera Phenix, and V9 P85 omits V7 P68’s explicit 17-fold margin ratio while retaining the underlying dimensions. V9 P13 narrows V7 P6’s application breadth. R36, R42 and R04 propose retaining these explanations.')
    paragraph(body,'Added warnings and repetition','Heading3')
    paragraph(body,'V9 P70 adds an unperformed joint-strength test to the observed adhesive result (R34); V9 P87 adds unmeasured labor/time/cost comparisons to the one-time-mold workflow (R44). V7 reports intact joints and avoided processing steps, not measured strength or cost savings.')
    paragraph(body,'The one-preparation limit is explicit in Methods, repeated at the end of neuronal Results and repeated in Discussion (V9 P46; V9 P51; V9 P77; V9 P82; V9 P88). The tracer limit appears in Methods, Results and Discussion (V9 P45; V9 P76; V9 P88). R41 and R37 cover reducing this repetition without dropping the limits.')
    paragraph(body,'V9 P11 omits V7 P4’s measured reuse totals and edge-growth limitation. It calls alignment “precise”, while V9 P85 says actual accuracy was not directly quantified; it also describes compartmentalized axonal growth more strongly than the indirect-labeling account in V9 P78. R03 keeps the fabrication framing, reuse observations and measured culture limit.')
    p=paragraph(body,'Tim offered to read the draft. I think his input could be valuable given that he has published in Lab on a Chip twice. I would value his feedback on V7, with your revised version alongside it if you would like.')
    run(p,'    ',size=18);link(p,'Paper 9','published_paper_9');run(p,'    ',size=18);link(p,'Paper 10','published_paper_10')
    bookmark(p,'comparison_end')
    paragraph(body,'Revision table','Heading1')
    paragraph(body,'The rows cover the V7/V9 differences and the remaining reporting and presentation work; unchanged items are retained where they answer a point in the saved discussion.')
    table=make_table(body,['ID','Change or work','My suggestion','What the sources show'],[650,1600,2300,4810])
    for row in rows:
        tr=elem(table,'tr')
        cells=[]
        for width in (650,1600,2300,4810):
            tc=elem(tr,'tc');elem(elem(tc,'tcPr'),'tcW',w=width,type='dxa');cells.append(tc)
        p=paragraph(cells[0],anchor='change_'+row['id'])
        link(p,row['id'],'detail_'+row['id'],size=22)
        paragraph(cells[1],row['title'])
        paragraph(cells[2],row['suggestion'])
        paragraph(cells[3],row['reason'])
        quote_refs(cells[3],row)
        p=paragraph(cells[3],'',size=18)
        if 'sources_'+row['id'] in source_targets:
            link(p,'Sources','sources_'+row['id'])
        elif row['id']=='R59':
            link(p,'Width data','channel_measurements')
        elif row['id']=='R60':
            link(p,'Related reuse report','sources_R33')
        if row['feedback']:
            p=paragraph(cells[3],'Related feedback: ',size=18)
            for number in row['feedback']:
                link(p,f'Feedback L{number}',f'src_L{number:03d}',feedback_colors.get(number,BLACK))
                run(p,'    ',size=18)
    bookmark(list(table.iter(W+'p'))[-1],'revision_table_end')
    for node in transcript:
        if qtext(node)=='Feedback suggestions and review comments':
            node=paragraph(E.Element('holder'),'Saved ChatGPT discussion, with V7/V9 comments','Heading1','nav_transcript')
            body.append(node)
            continue
        for b in list(node.iter(W+'bookmarkStart')):
            if b.get(W+'name','').startswith('nav_'):
                bid=b.get(W+'id');b.getparent().remove(b)
                for closing in node.xpath('.//w:bookmarkEnd[@w:id="'+bid+'"]',namespaces=NS):
                    closing.getparent().remove(closing)
        body.append(node)
    bookmark(list(body.iter(W+'p'))[-1],'nav_transcript_end')
    paragraph(body,'Details and cited V7/V9 passages','Heading1','nav_passages')
    # Row details supply the return path; each complete source paragraph appears once.
    emitted=set()
    comment_refs={(m[1],int(m[2])) for note in notes for m in re.finditer(r'\bV([79]) P(\d+)',note['answer'])}
    for row in rows:
        p=paragraph(body,row['id']+'. '+row['title'],'Heading2','detail_'+row['id'])
        run(p,'    ',size=18);link(p,'Table row '+row['id'],'change_'+row['id'])
        paragraph(body,row['reason'])
        paragraph(body,'My suggestion: '+row['suggestion'])
        if row['feedback']:
            paragraph(body,'Related feedback: '+'    '.join(f'Feedback L{n}' for n in row['feedback']),size=18)
        for version in docs:
            for number in row[version]:
                key=(version,number)
                if key in emitted:
                    paragraph(body,f'{version.upper()} P{number}',size=18)
                    continue
                emitted.add(key)
                p=paragraph(body,f'{version.upper()} P{number}','Heading3',f'cmp_{version}_P{number}')
                run(p,'    ',size=18);link(p,'Table row '+row['id'],'change_'+row['id'])
                paragraph(body,docs[version]['paragraphs'][number-1],'SourceQuote')
    for version_string,number in sorted(comment_refs):
        version='v'+version_string
        if (version,number) not in emitted:
            emitted.add((version,number))
            paragraph(body,f'{version.upper()} P{number}','Heading3',f'cmp_{version}_P{number}')
            paragraph(body,docs[version]['paragraphs'][number-1],'SourceQuote')
    bookmark(list(body.iter(W+'p'))[-1],'nav_passages_end')
    for node in supporting:
        holder=E.Element('holder')
        holder.append(node)
        for p in node.iter(W+'p'):
            if p.xpath('.//w:drawing',namespaces=NS):
                continue
            text=qtext(p)
            if text=='Additional sources and images':
                continue
            if text.startswith('Table row R') or re.match(r'R\d{2}\. ',text):
                continue
            if text.startswith('DOCX Normal specifies'):
                p.getparent().remove(p)
                continue
            # Preserve later measurements/configurations, not the obsolete V8 text excerpts.
            if 'V8' in text or 'v8' in text or 'V7 P' in text or 'v7 P' in text:
                if re.search(r'\(V8 p\. \d+\)',text):
                    for t in p.iter(W+'t'):
                        t.text=re.sub(r'\(V8 p\. \d+\)','(earlier render)' if text.startswith('Table ') else '(unchanged figure)',t.text or '')
                else:
                    # A source cell can combine an obsolete V8 quote and current
                    # dataset/configuration details, separated by Word line breaks.
                    retained=[line.replace('v8 Table','V9 Table') for line in source_lines(p)
                              if not re.search(r'\bv[78]\s+P\d+|\bv8\b',line,re.I)]
                    external=p.xpath('.//w:hyperlink[@r:id]',namespaces={**NS,'r':R[1:-1]})
                    parent=p.getparent()
                    insertion=parent.index(p)
                    for line in retained:
                        fresh=paragraph(E.Element('holder'),line)
                        for h in external:
                            if qtext(h) in line:
                                restore_external_link(fresh,h)
                        parent.insert(insertion,fresh)
                        insertion+=1
                    p.getparent().remove(p)
                    continue
            for a in p.iter(W+'hyperlink'):
                target=a.get(W+'anchor','')
                if target.startswith('cmp_v8_'):
                    raise ValueError('Obsolete source handle in retained source material')
        for retained_node in list(holder):
            body.append(retained_node)
        if qtext(node).startswith('R57. '):
            paragraph(body,'V9 Table S1, rendered page 21: heights split across lines','Heading3')
            paragraph(body,'The cell value remains 5.567 in the DOCX; V9’s layout displays 5.56 above 7. The earlier-render crops below show the same values without this wrapping.')
            path=BUILD/'v9_s1_wrapping.png'
            if not path.is_file():
                raise FileNotFoundError(path)
            image_parts=E.fromstring(parts['word/_rels/document.xml.rels'])
            relationship_id='rIdV9S1Crop'
            if any(n.get('Id')==relationship_id for n in image_parts):
                raise ValueError('Duplicate source image relationship')
            E.SubElement(image_parts,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',
                         Id=relationship_id,Type=R[1:-1]+'/image',Target='media/v9_s1_wrapping.png')
            parts['word/_rels/document.xml.rels']=serialized(image_parts)
            parts['word/media/v9_s1_wrapping.png']=path.read_bytes()
            drawing=deepcopy(next(n for n in supporting if n.xpath('.//w:drawing',namespaces=NS)))
            width,height=Image.open(path).size
            cx=5669280;cy=round(cx*height/width)
            for n in drawing.iter():
                if E.QName(n).localname=='blip':n.set(R+'embed',relationship_id)
                if E.QName(n).localname in ('extent','ext') and 'cx' in n.attrib:
                    n.set('cx',str(cx));n.set('cy',str(cy))
                if E.QName(n).localname=='docPr':n.set('id','100001');n.set('name','V9 Table S1 numeric wrapping')
            body.append(drawing)
        if qtext(node).startswith('R62. '):
            paragraph(body,'Legend formatting: V7 explicitly sets 11-point text; V9 removes those size settings and inherits the 12-point default. The legend wording and image bytes are unchanged.')
    bookmark(list(body.iter(W+'p'))[-1],'detailed_evidence_end')
    for node in published:
        holder=E.Element('holder')
        holder.append(node)
        for p in list(node.iter(W+'p')):
            if qtext(p)=='Matching draft passage':
                next_node=p.getnext()
                p.getparent().remove(p)
                if next_node is not None and next_node.tag==W+'p':
                    next_node.getparent().remove(next_node)
            elif 'v8 P' in qtext(p) or 'V8 P' in qtext(p):
                p.getparent().remove(p)
        if node.getparent() is holder:
            body.append(node)
    bookmark(list(body.iter(W+'p'))[-1],'published_comparisons_end')
    old_end_ids={b.get(W+'id') for b in body.iter(W+'bookmarkStart')
                 if b.get(W+'name','').endswith('_end') and int(b.get(W+'id'))<100000}
    for b in list(body.iter()):
        if b.tag in (W+'bookmarkStart',W+'bookmarkEnd') and b.get(W+'id') in old_end_ids:
            b.getparent().remove(b)
    body.append(section)
    comments=E.Element(W+'comments',nsmap={'w':W[1:-1]})
    status_labels={'both':'In V7 and V9.','v7':'In V7 only.','v9':'In V9 only.','missing':'Not supplied in V7 or V9.','mixed':'Context or mixed points.'}
    for note in notes:
        c=elem(comments,'comment',id=note['id'],author='Review notes',initials='RN',date=datetime.now(timezone.utc).isoformat())
        p=paragraph(c)
        run(p,status_labels[note['status']],color=COLORS[note['status']],bold=True)
        paragraph(c,note['answer'])
        for r in c[-1].findall(W+'r'):
            r.find(W+'rPr').find(W+'color').set(W+'val',COLORS[note['status']])
        if note['rows']:
            paragraph(c,'Rows: '+'    '.join(note['rows']),size=18)
        if len(note['related'])>1:
            paragraph(c,'Related feedback: '+'    '.join('Feedback L'+str(int(t.removeprefix('src_L'))) for t in note['related'] if int(t.removeprefix('src_L'))!=note['line']),size=18)
    # Recolor the preserved transcript selections from the revised comment assessment.
    active=set()
    colors={note['id']:note['status'] for note in notes}
    for node in body.iter():
        if node.tag==W+'commentRangeStart':
            active.add(int(node.get(W+'id')))
        elif node.tag==W+'commentRangeEnd':
            active.discard(int(node.get(W+'id')))
        elif node.tag==W+'r' and active:
            statuses={colors[number] for number in active}
            color=COLORS[next(iter(statuses))] if len(statuses)==1 else BLACK
            props=node.find(W+'rPr')
            if props is None:
                props=E.Element(W+'rPr');node.insert(0,props)
            c=props.find(W+'color')
            if c is None:
                c=elem(props,'color')
            c.set(W+'val',color)
            shading=props.find(W+'shd')
            if shading is not None:
                shading.set(W+'fill',{'both':'EAF5ED','v7':'EAF1FA','v9':'FFF2E3','missing':'F0F0F0','mixed':'F0F0F0'}[next(iter(statuses))] if len(statuses)==1 else 'F0F0F0')
    # Source handles use exact wording; transcript/row links use the point assessment.
    for tree in (doc,comments):
        for a in tree.iter(W+'hyperlink'):
            target=a.get(W+'anchor','')
            match=re.fullmatch(r'cmp_(v[79])_P(\d+)',target)
            color=wording_color(match[1],int(match[2])) if match else feedback_colors.get(int(target.removeprefix('src_L')),BLACK) if target.startswith('src_L') else BLACK
            for r in a.iter(W+'r'):
                props=r.find(W+'rPr')
                if props is None:
                    props=E.Element(W+'rPr');r.insert(0,props)
                c=props.find(W+'color')
                if c is None:
                    c=elem(props,'color')
                c.set(W+'val',color)
    # Header/footer navigation is shared with the previous document, but the draft label changes.
    for name,content in list(parts.items()):
        if re.match(r'word/(?:header|footer)[^/]*\.xml$',name):
            tree=E.fromstring(content)
            for t in tree.iter(W+'t'):
                t.text=(t.text or '').replace('V8','V9')
            for a in tree.iter(W+'hyperlink'):
                if a.get(W+'anchor')=='review_contents':
                    continue
                if a.get(W+'anchor'):
                    a.set(W+'anchor','review_contents')
            parts[name]=serialized(tree)
    parts['word/document.xml']=serialized(doc)
    parts['word/comments.xml']=serialized(comments)
    core=E.fromstring(parts['docProps/core.xml'])
    title=core.find('{http://purl.org/dc/elements/1.1/}title')
    if title is None:
        title=E.SubElement(core,'{http://purl.org/dc/elements/1.1/}title')
    title.text='V7 and V9 manuscript comparison'
    parts['docProps/core.xml']=serialized(core)
    validate(parts,emitted)
    write_package(parts,OUTPUT)
    (BUILD/'v7_v9_comparison.json').write_text(json.dumps(dict(documents=docs,summary=summary,rows=rows,notes=notes),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    print('Created',OUTPUT,'with',len(rows),'rows and',len(notes),'reassessed comments.')


def validate(parts,emitted=None):
    doc=E.fromstring(parts['word/document.xml'])
    names=[b.get(W+'name') for b in doc.iter(W+'bookmarkStart')]
    duplicates=[name for name,count in Counter(names).items() if count>1]
    if duplicates:
        raise ValueError('Duplicate bookmarks: '+str(duplicates))
    missing=[]
    for name,content in parts.items():
        if name.startswith('word/') and name.endswith('.xml'):
            for a in E.fromstring(content).iter(W+'hyperlink'):
                if a.get(W+'anchor') and a.get(W+'anchor') not in names:
                    missing.append((name,a.get(W+'anchor')))
    if missing:
        raise ValueError('Unresolved internal links: '+str(missing))
    ids={c.get(W+'id') for c in E.fromstring(parts['word/comments.xml'])}
    if {c.get(W+'id') for c in doc.iter(W+'commentRangeStart')}!=ids:
        raise ValueError('Comment selections no longer match their notes')
    for row in rows:
        for version in docs:
            assert all(f'cmp_{version}_P{number}' in names for number in row[version])
    v9_main=docs['v9']['paragraphs'][:98]
    covered={n for row in rows[:52] for n in row['v9']}
    omitted=[i for i,p in enumerate(v9_main,1) if p and i not in covered and p not in ('Abstract','Introduction','Materials and Methods','Results','Discussion')]
    if omitted:
        raise ValueError('Main-text paragraphs not covered by rows: '+str(omitted))


def cache_pages(pdf):
    with ZipFile(OUTPUT) as archive:
        parts={name:archive.read(name) for name in archive.namelist()}
    document=E.fromstring(parts['word/document.xml'])
    rendered=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
    page_texts=[s for s in rendered.split('\f') if s.strip()]
    text=re.sub(r'\s+',' ',rendered)
    mapping={}
    for p in document.iter(W+'p'):
        instructions=[n for n in p.iter(W+'instrText') if (n.text or '').strip().startswith('PAGEREF')]
        if not instructions:
            continue
        anchors=[n.text.split()[1] for n in instructions]
        is_contents=p.getparent().tag==W+'tc'
        prefix=qtext(p.getparent().getparent()[0]) if is_contents else qtext(p).split(' (p')[0]
        pattern=r'\s*(?:→\s*)?pp\.\s*(\d+)\s*[–-]\s*(\d+)' if is_contents else r'\s*\(pp?\.\s*(\d+)(?:\s*[–-]\s*(\d+))?\)'
        matches=re.findall(re.escape(prefix)+pattern,text)
        if len(matches)!=1:
            raise ValueError('Page field not found in render: '+prefix)
        numbers=[n for n in matches[0] if n]
        if len(numbers)!=len(anchors):
            raise ValueError('Wrong page count for '+prefix)
        for anchor,value in zip(anchors,numbers):
            if anchor in mapping and mapping[anchor]!=value:
                raise ValueError('Conflicting page references')
            mapping[anchor]=value
        in_result=False;current=None
        for child in p:
            instr=child.find(W+'instrText')
            if instr is not None and instr.text.strip().startswith('PAGEREF'):
                current=instr.text.split()[1]
            marker=child.find(W+'fldChar')
            if marker is not None:
                state=marker.get(W+'fldCharType')
                if state=='separate':in_result=True
                if state=='end':in_result=False
            t=child.find(W+'t')
            if in_result and t is not None:
                t.text=mapping[current]
        if prefix in ('Comparison (details)','Revision table (leave comments here) ←','ChatGPT discussion, with comments (mostly accessed via links)','Cited V7 and V9 passages','Additional sources and images','Published Lab on a Chip comparisons'):
            run(p,' ('+str(int(numbers[-1])-int(numbers[0])+1)+' pages)',bold=prefix.startswith('Revision table'),size=18)
    marker=next(b for b in document.iter(W+'bookmarkStart') if b.get(W+'name')=='remaining_support_pages')
    p=marker.getparent()
    value=next(t for t in p.iter(W+'t') if t.text=='00')
    value.text=str(len(page_texts)-int(mapping['revision_table_end']))
    parts['word/document.xml']=serialized(document)
    validate(parts)
    write_package(parts,OUTPUT)
    print('Cached page links; revision table pp.',mapping['change_R01']+'–'+mapping['revision_table_end'],';',len(page_texts),'pages total.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache-pages',type=Path)
    args=parser.parse_args()
    if args.cache_pages:
        cache_pages(args.cache_pages)
    else:
        build()
