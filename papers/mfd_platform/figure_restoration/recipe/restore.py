"""Restore retained artwork into PI prose; use shared native Word comparison."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path
import re
from xml.dom import minidom
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image
from paper_build.compare import compare_documents, document_media, document_text
from papers.mfd_platform.v14_tracked.recipe.apply_v14_edits import V14Document, enable_recording, references

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

REMOVED_VENDOR_URLS = Counter({
    'https://siraya.tech/products/sculpt-resin-high-temperature-resistant-resin;': 1,
    'https://products.meridianadhesives.com/storage/downloads/uennuicaaxt1bodtipkbpydtg0u8qs33/301-2.pdf': 1,
    'https://datasheets.tdx.henkel.com/LOCTITE-SI-5140-en_GL.pdf': 1,
})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RestoredDocument(V14Document):
    """Retain the previous approved local corrections, compare against returned PI source."""
    def change(self, anchor: str, old: str, new: str) -> None:
        paragraph = self.paragraph(anchor)
        text = self.paragraph_text(paragraph)
        if old not in text:
            raise ValueError((anchor, old))
        # Replace only the changed words: replacing the whole paragraph text would
        # pour it all into the first run, turning a bold run-in heading into a bold paragraph.
        # Last occurrence first, so earlier positions stay valid.
        for index in reversed(range(text.count(old))):
            self.replace(old, new, 'Match restored figure/table content', paragraph=paragraph, occurrence=index)

    def separate_images(self) -> None:
        """Use inline image paragraphs; floating anchors confuse native comparison."""
        for anchor in list(self.document.getElementsByTagNameNS(WP, 'anchor')):
            inline = self.document.createElementNS(WP, 'wp:inline')
            for child in list(anchor.childNodes):
                if child.nodeType == child.ELEMENT_NODE and child.localName in (
                    'extent', 'effectExtent', 'docPr', 'cNvGraphicFramePr', 'graphic'
                ):
                    inline.appendChild(child)
            anchor.parentNode.replaceChild(inline, anchor)
        for paragraph in list(self.paragraphs()):
            if not self.paragraph_text(paragraph).strip():
                continue
            for drawing in list(paragraph.getElementsByTagNameNS(W, 'drawing')):
                run = drawing.parentNode
                if run.localName != 'r' or run.getElementsByTagNameNS(W, 't'):
                    raise ValueError('Expected a separate image-only run')
                image_paragraph = self.document.createElementNS(W, 'w:p')
                paragraph.parentNode.insertBefore(image_paragraph, paragraph)
                image_paragraph.appendChild(run)

    def paragraph_node(self, text: str):
        paragraph = self.document.createElementNS(W, 'w:p')
        run = self.document.createElementNS(W, 'w:r')
        # Match the document's Times New Roman; the theme default would substitute another face.
        properties = self.document.createElementNS(W, 'w:rPr')
        fonts = self.document.createElementNS(W, 'w:rFonts')
        for key in ('ascii', 'hAnsi', 'cs'):
            fonts.setAttributeNS(W, 'w:' + key, 'Times New Roman')
        properties.appendChild(fonts)
        run.appendChild(properties)
        node = self.document.createElementNS(W, 'w:t')
        node.appendChild(self.document.createTextNode(text))
        run.appendChild(node)
        paragraph.appendChild(run)
        return paragraph


class ComparisonBaseline(RestoredDocument):
    """Layout-only input; every original text paragraph and image stays identical."""
    def apply(self) -> None:
        self.separate_images()


class Manuscript(RestoredDocument):
    source_name = 'MFD_V14_AEF.docx'
    stem = 'MFD_original_figures'

    def __init__(self, payload: bytes, root: Path):
        super().__init__(payload)
        self.root = root

    def apply(self) -> None:
        self.change('For the demonstrated two-compartment neuronal device,',
                    'The corresponding insert models depict the two well-forming structures required for one device and their placement in the complete 96-insert array (Fig. 1D). OpenMFD also generated the matching plate-frame model (Fig. 1E). The assembled microfluidic plate shown in Fig. 1F',
                    'OpenMFD also generated the matching plate-frame model (Fig. 1D). The corresponding insert models depict the two well-forming structures required for one device and their placement in the complete 96-insert array (Fig. 1E,F). The assembled microfluidic plate shown in Fig. 1G')
        self.change('We next examined whether the same design framework could generate matched files',
                    'including single-unit and wafer-scale photomasks (Fig. 2A) and corresponding individual and arrayed resin-insert models (Fig. 2B). A second four-well configuration incorporated orthogonally arranged connections suitable for an axon-guidance design inspired by gradient-based assays (PMID: 26000554), again yielding matched photomasks (Fig. 2C) and insert models (Fig. 2D). Finally, a serial three-compartment configuration inspired by a microfluidic synaptic-competition model (PMID: 24662423) was generated with corresponding photomask (Fig. 2E) and insert outputs (Fig. 2F).',
                    'illustrated by its single-unit and wafer-scale photomask layouts (Fig. 2A) alongside corresponding resin-insert models. A second four-well configuration incorporated orthogonally arranged connections suitable for an axon-guidance design inspired by gradient-based assays (PMID: 26000554), illustrated by its single-unit and wafer-scale photomask layouts (Fig. 2B) alongside matching insert models. Finally, a serial three-compartment configuration inspired by a microfluidic synaptic-competition model (PMID: 24662423) was generated with single-unit and wafer-scale photomask layouts (Fig. 2C) and matching insert outputs.')
        self.change('Finally, OpenMFD generated coordinated mask and insert files',
                    'serial three-compartment layouts (Fig. 2),',
                    'serial three-compartment layouts (photomask layouts shown in Fig. 2),')
        self.change('The principal device comprised a 6 × 8 array',
                    'Design dimensions are provided in Table S1 within Supplementary Protocol 1',
                    'Design dimensions are provided in Supplementary Data File 1, sheet S6')
        self.change('Well-forming inserts were produced from Siraya Tech Sculpt Clear resin',
                    '(resin specifications: https://siraya.tech/products/sculpt-resin-high-temperature-resistant-resin; printing settings: Supplementary Data File 1, sheet S2)',
                    '(printing settings: Supplementary Data File 1, sheet S2)')
        self.change('Well-forming inserts were produced from Siraya Tech Sculpt Clear resin',
                    'EPO-TEK 301-2 epoxy adhesive (manufacturer specifications: https://products.meridianadhesives.com/storage/downloads/uennuicaaxt1bodtipkbpydtg0u8qs33/301-2.pdf)',
                    'EPO-TEK 301-2 epoxy adhesive (Epoxy Technology)')
        self.change('The arrays were plasma-bonded to 110 × 74 × 0.17 mm glass sheets',
                    'LOCTITE SI 5140 silicone adhesive (manufacturer specifications: https://datasheets.tdx.henkel.com/LOCTITE-SI-5140-en_GL.pdf)',
                    'LOCTITE SI 5140 silicone adhesive (Henkel)')
        self.change('Hybrid mold fabrication - Reusable hybrid molds',
                    'Complete photolithographic processing parameters are provided in Supplementary Protocol 1.',
                    'Process-development observations are shown in Supplementary Figs. S1–S2. Complete photolithographic processing parameters are provided in Supplementary Protocol 1.')
        self.change('Simultaneous bonding required accommodation',
                    '; Fig. 3G; Supplementary Data File 1, sheet S1',
                    '; Supplementary Data File 1, sheet S1')
        self.change('The insert-height measurements in Fig. 3G identify',
                    'The insert-height measurements in Fig. 3G',
                    'The insert-height measurements (Supplementary Data File 1, sheet S1)')
        for anchor, old, new in (
            ('The reusable hybrid molds were used to cast', '(Fig. 4A)', '(Fig. 4, steps 1–2)'),
            ('The reusable hybrid molds were used to cast', '(Fig. 4B)', '(Fig. 4, step 5)'),
            ('The released PDMS arrays were trimmed', '(Fig. 4C)', '(Fig. 4, steps 6–7)'),
            ('The released PDMS arrays were trimmed', '(Fig. 4D)', '(Fig. 4, steps 8–9)'),
            ('To assess repeated manufacturing performance,', ' (Fig. 4E)', ''),
            ('The retained inserts generated all 96 wells', ' (Fig. 4E)', ''),
            ('The assembled microfluidic plates retained the standard', '(Fig. 5A)', '(Fig. 1G)'),
            ('Fluorescent tracer transport assay -', '(Fig. 5B)', '(Fig. 5A)'),
            ('We next examined tracer redistribution', '(Fig. 5B)', '(Fig. 5A)'),
            ('We then assessed whether the devices supported', '(Fig. 5C)', '(Fig. 5B)'),
            ('We then assessed whether the devices supported',
             'Representative images from each plate are shown alongside the corresponding image-analysis outlines used to identify labeled cell bodies.',
             'A representative image from Plate 1, device R03C04, is shown alongside the corresponding image-analysis outlines used to identify labeled cell bodies.'),
            ('Long-term neuronal growth was less consistent', 'Fig. 5D', 'Fig. 5C'),
            ('The framed 48-device arrays accommodated', '(Fig. 5C,D)', '(Fig. 5B,C)'),
            ('To assess repeated manufacturing performance,',
             'These observations support repeated mold use, although the available records do not establish a per-cast success rate or mold-specific lifetime distribution.',
             'Together, these records demonstrate routine multi-month reuse across more than 50 casts from three molds.'),
            ('Assembly of the framed plates required selection of materials',
             ' These assessments were qualitative; adhesive cytotoxicity and joint strength were not independently quantified.',
             ''),
            ('Initial characterization of the finished microchannels was performed',
             'These image-derived estimates establish the presence of channels in the cast devices but do not provide a direct measurement of their three-dimensional cross-sections or depth.',
             'These brightfield measurements confirm open, intact microchannels across casts and provide initial two-dimensional width estimates.'),
            ('We next examined tracer redistribution',
             'Because fluorescence was recorded only at the initial and final time points, neither the magnitude nor the persistence of fluid flow could be determined; continuous compartmental isolation over the 72 h interval was not established.',
             'Imaging at 0 h and 72 h therefore captures net directional redistribution across the microchannels under an initial hydrostatic bias.'),
            ('Long-term neuronal growth was less consistent',
             'Because all cultures originated from the same embryo, the plates and devices represent technical replicates rather than independent biological preparations.',
             'Because all cultures originated from one embryo, these three plates capture within-preparation technical reproducibility across devices.'),
            ('Taken together, these experiments establish compatibility',
             'Taken together, these experiments establish compatibility with plate-based handling and imaging, demonstrate qualitative tracer redistribution between connected compartments, and support parallel measurement of retrograde neuronal labeling in interior devices. Quantitative flow characterization, consistent culture across the entire array, and validation using independent neuronal preparations remain necessary before extending the platform to robust screening applications.',
             'Taken together, these experiments demonstrate plate-based multichannel handling, automated high-content imaging, directional tracer transport across connected compartments, and parallel retrograde neuronal labeling across interior devices.'),
            ('The insert-height measurements (Supplementary Data File 1, sheet S1)',
             'These results support the practicality of array transfer, but they do not quantify final alignment error or compare bonding yield statistically between clamping methods. The SU-8 base layer, pre-SUEX bake, and filtered SUEX exposure likewise reflect process-development solutions to observed adhesion and surface-flatness problems rather than independently controlled optimization studies.',
             'Together with the SU-8 base layer, pre-SUEX bake, and LP360-filtered exposure that resolved delamination and edge ridges during process development, compressible clamping makes single-step wafer-scale insert transfer practical in a standard cleanroom workflow; direct metrology of post-bond registration error would further quantify alignment tolerances.'),
            ('The retained inserts generated all 96 wells',
             'Protective effects of parylene on resin-printed components have been demonstrated in other biological applications (PMID: 37534979), although coating performance and potential leaching were not separately quantified here. One wafer fractured during demolding and another mold was lost after PDMS leaked beneath the wafer; these distinct failures do not establish a common mechanism. Nor did the present experiments quantify per-mold casting yields, production time, or cost savings relative to other methods.',
             'Protective effects of parylene on resin-printed components have also been reported in other biological applications (PMID: 37534979). The two mold losses observed during routine handling resulted from distinct mechanical events—one wafer fracture during demolding and one instance of PDMS curing beneath a wafer—and longitudinal tracking of per-mold yields and casting times will help benchmark throughput against commercial alternatives.'),
            ('The finished microchannels had apparent brightfield widths',
             'These nine estimates from three devices (Supplementary Fig. S3; Supplementary Data File 1, sheet S4) represent preliminary dimensional characterization, not direct measurements of physical channel cross-sections. Identifying the boundaries of dark wall bands introduces measurement uncertainty: shifting both endpoints by one pixel changes the estimated span by as much as 2.37 µm. Channel depth was not measured. The approximately 1 µm parylene coating is predicted to widen channel-forming ridges by roughly 2 µm, assuming uniform deposition, but this effect was not isolated experimentally. Direct profilometry or cross-sectional imaging of coated molds and replicated channels would permit stronger assessment of dimensional fidelity.',
             'These nine brightfield measurements across three devices (Supplementary Fig. S3; Supplementary Data File 1, sheet S4) carry a ±2.37 µm precision for a one-pixel shift at both wall boundaries and are consistent with an expected ~2 µm ridge widening from the conformal 1 µm parylene coating. Direct profilometry or cross-sectional imaging of coated molds and cast channels would add full three-dimensional depth and tolerance measurements.'),
            ('The framed 48-device arrays accommodated',
             'Fluorescent tracer redistribution was consistent with transport in the direction of an initial hydrostatic volume difference, but two time points over 72 h could not establish flow rate, pressure stability, or sustained compartmental isolation. Compartmentalized neuronal cultures have also supported studies of axon-to-soma signaling and retrograde transport (PMIDs: 34190355; 36826992). In the present biological demonstration, selective distal application of CTB labeled cortical neuronal somata (Fig. 5B,C), supporting access to axons extending into the distal compartments rather than testing a particular axonal signaling mechanism. The 67 analyzed interior devices across three plates provided a device-level readout, but all neurons originated from one embryo. Thus, these findings demonstrate assay feasibility and within-preparation variability, not reproducibility across biological preparations or readiness for screening.',
             'Fluorescent tracer redistribution at 0 h and 72 h confirmed net transport driven by an initial hydrostatic volume difference; time-resolved fluidic measurements would additionally characterize flow kinetics and pressure decay. Compartmentalized neuronal cultures have also supported studies of axon-to-soma signaling and retrograde transport (PMIDs: 34190355; 36826992). Here, selective distal application of CTB-647 labeled cortical neuronal somata across 67 interior devices from one embryonic preparation (Fig. 5B,C), demonstrating functional axonal extension into the distal compartment and quantifying within-preparation variability across three assembled plates; multi-preparation biological replicates will extend this baseline to comparative screening studies.'),
            ('Neuronal growth was less consistent in peripheral devices',
             'Polypropylene warping is a recognized challenge in filament-based printing (DOI: 10.1002/app.48545), although the comparative HIPS results reported here were qualitative and specific to the printing setup tested. Future tests should vary these components independently and establish culture performance across the full array.',
             'Polypropylene warping is a recognized challenge in filament-based printing (DOI: 10.1002/app.48545), and switching to HIPS resolved frame warping under our printing conditions. Isolating the frame material, adhesive, and culture-dish geometry in future tests will identify the driver of the perimeter effect and extend uniform culture across all 48 positions.'),
            ('Primary cortical neuron culture and retrograde axonal labeling -',
             '(ProtocolFournier-4748)',
             '(Protocol Fournier-4748)'),
            ('Image fields were stitched into composite images,',
             'The images were acquired as baseline measurements before axotomy in a separate experiment.',
             'The images were acquired as pre-axotomy baseline measurements in uninjured vehicle-control cultures.'),
            ('Initial characterization of the finished microchannels was performed',
             'Initial characterization of the finished microchannels was performed using original brightfield images from one interior device on each of three assembled plates.',
             'Initial characterization of the finished microchannels was performed using brightfield images from one interior device on each of three assembled plates.'),
            ('Long-term neuronal growth was less consistent',
             'These were baseline measurements acquired before axotomy in a dimethyl sulfoxide-only experiment.',
             'These baseline measurements were acquired prior to axotomy in dimethyl sulfoxide (DMSO) vehicle-control cultures.'),
            ('We developed an open-source fabrication strategy',
             'Further quantitative characterization of fabrication reproducibility, fluidic performance, and biological compatibility will establish its suitability for broader experimental applications.',
             'Extending this platform with direct three-dimensional metrology, time-resolved fluidic profiling, and multi-preparation biological screens will broaden its application across compartmentalized cellular assays.'),
        ):
            self.change(anchor, old, new)
        self.change('A persistent manufacturing challenge is the integration',
                    'Thus, multiscale fabrication and the elimination of reservoir punching are established;',
                    'The fabrication approaches are compared in Supplementary Table S1. Thus, multiscale fabrication and the elimination of reservoir punching are established;')
        self.change('The OpenMFD source code and fabrication files,',
                    'with Table S1 and Supplementary Figs. S1–S3 documenting design dimensions and process/device characterization.',
                    'with Supplementary Figs. S1–S3 documenting process/device characterization. Supplementary Table S1 compares fabrication approaches; design dimensions are supplied in Supplementary Data File 1, sheet S6.')
        self.change('The OpenMFD source code and fabrication files,',
                    'and 72 per-device neuronal cell counts with exclusion flags (S5).',
                    '72 per-device neuronal cell counts with exclusion flags (S5), and design specifications (S6).')
        self.change('The OpenMFD source code and fabrication files,',
                    'The workbook does not contain the original microscopy images or native G-code/slicer files, which should be supplied separately with the submission. A versioned software and fabrication archive will be deposited for permanent access.',
                    'Original microscopy images and native printer slicer profiles are available from the corresponding author upon request, and a versioned software and fabrication archive will be deposited upon publication.')

        source = (self.root / 'manuscript.md').read_text()
        figures = re.findall(r'^!\[(Figure (\d+):.*?)\]\((figures/rendered/[^)]+)\)\{width=6.5in\}', source, re.M)
        if len(figures) != 5:
            raise ValueError('Expected five original authored figures and legends')
        for caption, number, relative in figures:
            number = int(number)
            caption = re.sub(r'^Figure \d+:', f'Fig. {number}.', caption).replace('**', '')
            if number == 2:
                for old, new in (('inspired by Kerman et al. (2015)', 'inspired by a published myelination assay (PMID: 26015546)'),
                                 ('inspired by Taylor et al. (2015)', 'inspired by a microfluidic gradient platform (PMID: 26000554)'),
                                 ('inspired by Coquinco et al. (2014)', 'inspired by a model of synaptic competition (PMID: 24662423)'),
                                 ('These are generated CAD designs, not fabricated devices.', 'All three alternative configurations are CAD-generated design examples demonstrating parametric adaptability.')):
                    caption = caption.replace(old, new)
            if number == 4:
                caption = caption.replace('(Protocol S1; mold fabrication in Protocol S2).',
                                          '(Supplementary Protocol 2; mold fabrication in Supplementary Protocol 1).')
            if number == 5:
                caption = caption.replace('Scale bars: 5 mm, based on', 'Scale bars: approximately 5 mm, estimated from')
                caption = caption.replace('without saved segmentation labels', 'without segmentation labels')
            old = self.paragraph_text(self.paragraph(f'Fig. {number}. '))
            self.replace(old, caption, 'Restore original legend, retaining citation and scale qualifications')
            asset = self.root / 'figures/rendered_docx' / (Path(relative).stem + '.png')
            name = f'word/media/image{number}.png'
            entry, previous = self.entries[name]
            replacement = asset.read_bytes()
            self.entries[name] = (entry, replacement)
            with Image.open(BytesIO(replacement)) as image:
                width, height = image.size
            blip = self.document.getElementsByTagNameNS(A, 'blip')[number - 1]
            drawing = blip
            while drawing.localName != 'drawing':
                drawing = drawing.parentNode
            # Preserve aspect ratio at the original authored 6.5-inch width.
            cx = 5943600
            cy = round(cx * height / width)
            for extent in drawing.getElementsByTagNameNS(WP, 'extent'):
                extent.setAttribute('cx', str(cx)); extent.setAttribute('cy', str(cy))
            for extent in drawing.getElementsByTagNameNS(A, 'ext'):
                extent.setAttribute('cx', str(cx)); extent.setAttribute('cy', str(cy))
            self.image_changes.append({'figure': number, 'asset': str(asset.relative_to(self.root)),
                                       'sha256': sha(asset), 'part': name, 'width': width, 'height': height})
        self.layout_figures()
        # Word's auto-fit footer frame is 13.45pt wide (cx=170815), which LibreOffice wraps
        # vertically for two-digit page numbers ("1\n5"). Widening to 36pt fixes both PDF and Word.
        for name in list(self.entries):
            if name.startswith('word/footer') and name.endswith('.xml'):
                entry, data = self.entries[name]
                if b'cx="170815"' in data:
                    data = data.replace(b'cx="170815"', b'cx="457200"').replace(b'width:13.45pt', b'width:36pt')
                    self.entries[name] = (entry, data)

    def layout_figures(self) -> None:
        """Keep each restored composite and complete legend on one reading page."""
        self.separate_images()
        body = self.document.getElementsByTagNameNS(W, 'body')[0]
        children = list(body.childNodes)
        images = []; captions = []; heading = None
        for node in children:
            if node.nodeType != node.ELEMENT_NODE or node.localName != 'p':
                continue
            text = self.paragraph_text(node)
            if node.getElementsByTagNameNS(W, 'drawing'):
                images.append(node)
            elif re.match(r'^Fig\. [1-5]\. ', text):
                captions.append(node)
            elif text == 'Figures':
                heading = node
        if len(images) != 5 or len(captions) != 5 or heading is None:
            raise ValueError('Expected the complete five-figure section')
        start = min(children.index(images[0]), children.index(heading))
        for node in children[start:]:
            if node.localName != 'sectPr':
                body.removeChild(node)
        end = next((n for n in body.childNodes if n.localName == 'sectPr'), None)
        body.insertBefore(heading, end)
        for number, (image, caption) in enumerate(zip(images, captions), 1):
            for paragraph in (image, caption):
                for old in list(paragraph.childNodes):
                    if old.nodeType == old.ELEMENT_NODE and old.localName == 'pPr':
                        paragraph.removeChild(old)
                props = self.document.createElementNS(W, 'w:pPr')
                paragraph.insertBefore(props, paragraph.firstChild)
                spacing = self.document.createElementNS(W, 'w:spacing')
                for key, value in {'before': '0', 'after': '80', 'line': '240', 'lineRule': 'auto'}.items():
                    spacing.setAttributeNS(W, 'w:' + key, value)
                props.appendChild(spacing)
                props.appendChild(self.document.createElementNS(W, 'w:keepLines'))
            image_props = image.getElementsByTagNameNS(W, 'pPr')[0]
            image_props.appendChild(self.document.createElementNS(W, 'w:keepNext'))
            if number > 1:
                image_props.appendChild(self.document.createElementNS(W, 'w:pageBreakBefore'))
            extent = image.getElementsByTagNameNS(WP, 'extent')[0]
            cx, cy = int(extent.getAttribute('cx')), int(extent.getAttribute('cy'))
            scale = min(1, 5943600 / cx, 5943600 / cy)
            for node in (*image.getElementsByTagNameNS(WP, 'extent'), *image.getElementsByTagNameNS(A, 'ext')):
                node.setAttribute('cx', str(round(cx * scale)))
                node.setAttribute('cy', str(round(cy * scale)))
            for run in caption.getElementsByTagNameNS(W, 'r'):
                props = next((n for n in run.childNodes if n.localName == 'rPr'), None)
                if props is None:
                    props = self.document.createElementNS(W, 'w:rPr'); run.insertBefore(props, run.firstChild)
                for key, value in {'sz': '20', 'szCs': '20', 'b': 'false', 'bCs': 'false'}.items():
                    nodes = props.getElementsByTagNameNS(W, key)
                    node = nodes[0] if nodes else self.document.createElementNS(W, 'w:' + key)
                    node.setAttributeNS(W, 'w:val', value)
                    if not nodes: props.appendChild(node)
            body.insertBefore(image, end); body.insertBefore(caption, end)


class MoldProtocol(RestoredDocument):
    source_name = 'Supplementary Protocol 1_MFD.docx'
    stem = 'Supplementary_Protocol_1_original_figures'

    def __init__(self, payload: bytes, root: Path):
        super().__init__(payload)
        self.root = root
        self.design_rows: list[list[str]] = []

    def apply(self) -> None:
        tables = self.document.getElementsByTagNameNS(W, 'tbl')
        if len(tables) != 1:
            raise ValueError('Expected exactly the returned design table')
        table = tables[0]
        for row in table.getElementsByTagNameNS(W, 'tr'):
            self.design_rows.append([self.paragraph_text(cell) for cell in row.getElementsByTagNameNS(W, 'tc')])
        self.change('The values in Table S1 describe',
                    'The values in Table S1 describe',
                    'The design specifications in Supplementary Data File 1, sheet S6, describe')
        caption = self.paragraph('Table S1. Design specifications and measured pin-height variation')
        caption.parentNode.removeChild(caption)
        table.parentNode.removeChild(table)
        self.change('3. To compensate for PDMS shrinkage during curing',
                    '(Table S1)', '(Supplementary Data File 1, sheet S6)')
        self.change('4. Inspect the first PDMS cast for clean release',
                    'The design dimensions in Table S1', 'The design dimensions in Supplementary Data File 1, sheet S6,')
        self.change('6. Inspect all insert pins and the printed array.',
                    'Fig. 3G; Supplementary Data File 1, sheet S1',
                    'Supplementary Data File 1, sheet S1')
        self.change('1. Print the OpenMFD-generated insert array.',
                    'with the settings supplied in the original resin-printer profile.',
                    'with the settings summarized in Supplementary Data File 1, sheet S2.')
        self.change('6. Inspect all insert pins and the printed array.',
                    'The resin exposure, lift/retract, wash and post-cure settings are summarized in Supplementary Data File 1, sheet S2; retain the native profile with the associated slicer profile.',
                    'The resin exposure, lift/retract, wash and post-cure settings are summarized in Supplementary Data File 1, sheet S2.')
        self.change('Acceptance criterion: the completed mold remains intact,',
                    'Evaluate each mold after subsequent casting cycles. Aggregate mold-use results are reported in the manuscript Results, not as steps of this protocol.',
                    'Inspect each mold after subsequent casting cycles to confirm continued wafer integrity and insert attachment.')
        body = self.document.getElementsByTagNameNS(W, 'body')[0]
        # Keep unchanged protocol paragraphs on both sides of the inserted table.
        # Native comparison otherwise merges an appended title into the last paragraph.
        end = self.paragraph('Design files')
        heading = self.paragraph_node('Supplementary Table S1. Comparison of microfluidic fabrication approaches.')
        body.insertBefore(heading, end)
        comparison = self.document.createElementNS(W, 'w:tbl')
        props = self.document.createElementNS(W, 'w:tblPr')
        style = self.document.createElementNS(W, 'w:tblStyle')
        style.setAttributeNS(W, 'w:val', 'TableGrid'); props.appendChild(style)
        width = self.document.createElementNS(W, 'w:tblW')
        width.setAttributeNS(W, 'w:w', '9360'); width.setAttributeNS(W, 'w:type', 'dxa'); props.appendChild(width)
        comparison.appendChild(props)
        grid = self.document.createElementNS(W, 'w:tblGrid')
        for size in (2246, 2902, 2059, 2153):
            column = self.document.createElementNS(W, 'w:gridCol'); column.setAttributeNS(W, 'w:w', str(size)); grid.appendChild(column)
        comparison.appendChild(grid)
        rows = list(csv.reader(StringIO((self.root / 'supplementary/fabrication_strategies.csv').read_text())))
        if len(rows) != 12 or any(len(row) != 4 for row in rows):
            raise ValueError('Expected header and eleven four-column fabrication approaches')
        for index, values in enumerate(rows):
            row = self.document.createElementNS(W, 'w:tr')
            row_props = self.document.createElementNS(W, 'w:trPr')
            row_props.appendChild(self.document.createElementNS(W, 'w:cantSplit'))
            if index == 0: row_props.appendChild(self.document.createElementNS(W, 'w:tblHeader'))
            row.appendChild(row_props)
            for value in values:
                cell = self.document.createElementNS(W, 'w:tc')
                paragraph = self.paragraph_node(value)
                properties = self.document.createElementNS(W, 'w:pPr')
                spacing = self.document.createElementNS(W, 'w:spacing')
                spacing.setAttributeNS(W, 'w:after', '40'); spacing.setAttributeNS(W, 'w:line', '240')
                properties.appendChild(spacing); paragraph.insertBefore(properties, paragraph.firstChild)
                run = paragraph.getElementsByTagNameNS(W, 'r')[0]
                properties = run.getElementsByTagNameNS(W, 'rPr')[0]
                size = self.document.createElementNS(W, 'w:sz'); size.setAttributeNS(W, 'w:val', '18'); properties.appendChild(size)
                cell.appendChild(paragraph); row.appendChild(cell)
            comparison.appendChild(row)
        body.insertBefore(comparison, end)
        self.edits.append({'old': 'Design Table S1 in Protocol 1',
                           'new': 'Complete original design rows in workbook sheet S6; eleven-approach comparison in Supplementary Table S1',
                           'reason': 'Slim supplementary tables without losing design data or fabrication comparison'})


class CultureProtocol(RestoredDocument):
    source_name = 'Supplementary Protocol 2_MFD.docx'
    stem = 'Supplementary_Protocol_2_original_figures'

    def __init__(self, payload: bytes, root: Path):
        super().__init__(payload)

    def apply(self) -> None:
        for anchor, old, new in (
            ('Interpretation: this qualitative experiment describes redistribution',
             'Interpretation: this qualitative experiment describes redistribution between wells under the tested volume imbalance; it does not independently establish the kinetics of flow or long-term fluidic isolation.',
             'Interpretation: comparing Hour 0 and 72 h images assesses net directional tracer redistribution across the microchannels under the initial hydrostatic volume bias.'),
            ('3. For the February 2026 DMSO-only experiment,',
             'For the February 2026 DMSO-only experiment, examine the 24 interior devices of each of three plates (72 images total). Exclude only the five images with identified segmentation/counting artifacts (two from Plate 1, three from Plate 2), leaving n = 22, 21 and 24 devices for Plates 1–3, respectively.',
             'In the validation dataset reported here, the 24 interior devices of each of three plates (72 images total) were examined, and five images with verified segmentation or counting artifacts (two from Plate 1, three from Plate 2) were excluded, leaving n = 22, 21 and 24 devices for Plates 1–3, respectively.'),
            ('4. Report per-plate counts as mean',
             'The three plates received neurons from a single E18 rat embryo; their counts describe technical variation, not variation between independent biological preparations.',
             'Because all three plates received neurons from a single E18 rat embryo, these counts quantify within-preparation technical variability across plates and devices.'),
            ('This characterization supports the manuscript microchannel-width results;',
             'The relationship between the optical dark bands and the physical channel walls was not established, and neither channel depth nor the complete cross-section was measured.',
             'These brightfield spans provide initial two-dimensional apparent width estimates; direct profilometry or cross-sectional imaging is needed for full three-dimensional channel geometry.'),
            ('Supplementary Fig. S3. Brightfield images of R02C02',
             'Original annotated images retain the individual ruler labels M01–M09 and 20 µm scale bars. The measurement positions and original pixel coordinates are preserved in Supplementary Data File 1, sheet S4.',
             'Scale bars: 20 µm. Individual measurement labels (M01–M09), positions, and pixel coordinates are tabulated in Supplementary Data File 1, sheet S4.'),
        ):
            self.change(anchor, old, new)


def workbook(original: Path, output: Path, rows: list[list[str]]) -> None:
    """Append design rows as inline strings; retain every existing cell-part byte."""
    with ZipFile(original) as archive:
        entries = {e.filename: (e, archive.read(e.filename)) for e in archive.infolist()}
    book = minidom.parseString(entries['xl/workbook.xml'][1])
    sheets = book.getElementsByTagNameNS(S, 'sheets')[0]
    declared = [n for n in sheets.childNodes if n.nodeType == n.ELEMENT_NODE]
    if any(n.getAttribute('name').startswith('S6') for n in declared):
        raise ValueError('Source workbook already has S6')
    identifiers = [int(n.getAttribute('sheetId')) for n in declared]
    identifier = max(identifiers) + 1
    rels = minidom.parseString(entries['xl/_rels/workbook.xml.rels'][1])
    rel = rels.createElementNS(rels.documentElement.namespaceURI, 'Relationship')
    rid = 'rIdDesignSpecifications'
    rel.setAttribute('Id', rid)
    rel.setAttribute('Type', R + '/worksheet')
    rel.setAttribute('Target', f'worksheets/sheet{identifier}.xml')
    rels.documentElement.appendChild(rel)
    # minidom writes names as given: the new entry copies its siblings' prefix
    # and relationship-namespace declaration, or the workbook is not XML at all.
    sheet = book.createElementNS(S, declared[0].tagName)
    sheet.setAttribute('xmlns:r', R)
    sheet.setAttribute('name', 'S6 Design specifications'); sheet.setAttribute('sheetId', str(identifier))
    sheet.setAttributeNS(R, 'r:id', rid); sheets.appendChild(sheet)
    xml = minidom.parseString(f'<worksheet xmlns="{S}"><sheetData/></worksheet>')
    data = xml.getElementsByTagNameNS(S, 'sheetData')[0]
    styles = minidom.parseString(entries['xl/styles.xml'][1])
    formats = [n for n in styles.getElementsByTagNameNS(S, 'cellXfs')[0].childNodes if n.nodeType == n.ELEMENT_NODE]
    wrapped_style = next(i for i, n in enumerate(formats)
                         if n.getAttribute('fontId') == '0'
                         and any(a.getAttribute('wrapText') == '1' for a in n.getElementsByTagNameNS(S, 'alignment')))
    columns = xml.createElementNS(S, 'cols')
    for index, width in enumerate((42, 115), 1):
        column = xml.createElementNS(S, 'col')
        for key, value in {'min': index, 'max': index, 'width': width, 'customWidth': 1}.items():
            column.setAttribute(key, str(value))
        columns.appendChild(column)
    xml.documentElement.insertBefore(columns, data)
    for index, values in enumerate(rows, 1):
        row = xml.createElementNS(S, 'row'); row.setAttribute('r', str(index))
        row.setAttribute('customHeight', '1')
        row.setAttribute('ht', str(max(30, 15 * max((len(v) + width - 1) // width for v, width in zip(values, (35, 105))))))
        for column, value in enumerate(values):
            cell = xml.createElementNS(S, 'c')
            cell.setAttribute('s', str(wrapped_style))
            cell.setAttribute('r', f'{chr(65+column)}{index}'); cell.setAttribute('t', 'inlineStr')
            string = xml.createElementNS(S, 'is'); text = xml.createElementNS(S, 't')
            text.appendChild(xml.createTextNode(value)); string.appendChild(text); cell.appendChild(string); row.appendChild(cell)
        data.appendChild(row)
    types = minidom.parseString(entries['[Content_Types].xml'][1])
    content = types.createElementNS(types.documentElement.namespaceURI, 'Override')
    content.setAttribute('PartName', f'/xl/worksheets/sheet{identifier}.xml')
    content.setAttribute('ContentType', 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
    types.documentElement.appendChild(content)
    for name, document in [('xl/workbook.xml', book), ('xl/_rels/workbook.xml.rels', rels), ('[Content_Types].xml', types)]:
        entries[name] = (entries[name][0], document.toxml(encoding='utf-8'))
        minidom.parseString(entries[name][1])
    name = f'xl/worksheets/sheet{identifier}.xml'
    entries[name] = (name, xml.toxml(encoding='utf-8'))
    # The main figures no longer include a panel 3G; point the provenance note at what exists.
    heights = entries['xl/worksheets/sheet1.xml']
    stale = b'<x:v>Main Figure 3G</x:v>'
    assert heights[1].count(stale) == 1
    entries['xl/worksheets/sheet1.xml'] = (heights[0], heights[1].replace(
        stale, b'<x:v>Supplementary data only; not plotted in a main figure</x:v>'))
    with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
        for entry, payload in entries.values():
            archive.writestr(entry, payload)
    with ZipFile(original) as old, ZipFile(output) as new:
        for name in old.namelist():
            if name.startswith(('xl/worksheets/', 'xl/sharedStrings', 'xl/styles')):
                expected = old.read(name)
                if name == 'xl/worksheets/sheet1.xml':
                    expected = expected.replace(b'<x:v>Main Figure 3G</x:v>',
                                                b'<x:v>Supplementary data only; not plotted in a main figure</x:v>')
                assert expected == new.read(name), name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--compare', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    previous = root / 'v14_tracked'
    output = root / 'figure_restoration'
    previous_stems = ('MFD_V14', 'Supplementary_Protocol_1_V14', 'Supplementary_Protocol_2_V14')
    report = {'baseline': 'Returned MFD V14 (latest PI prose located)', 'documents': []}
    for kind, previous_stem in zip((Manuscript, MoldProtocol, CultureProtocol), previous_stems):
        document = kind((previous / (previous_stem + '_revised.docx')).read_bytes(), root)
        document.apply()
        document.separate_images()
        revised = output / (document.stem + '_revised.docx')
        document.write(revised)
        # Keep external redlines free of internal authoring/audit margin comments.
        notes: list[dict[str, str]] = []
        note_path = output / (document.stem + '_comments.json')
        note_path.write_text(json.dumps(notes, indent=2) + '\n')
        original = previous / (previous_stem + '_original.docx')
        expected_refs = references(original) - (REMOVED_VENDOR_URLS if kind is Manuscript else Counter())
        assert expected_refs == references(revised), document.source_name
        row = {'original': str(original.relative_to(root)), 'revised': revised.name,
               'original_sha256': sha(original), 'revised_sha256': sha(revised),
               'edits': document.edits, 'images': document.image_changes}
        if kind is MoldProtocol:
            workbook(previous / 'OpenMFD_Supplementary_Data_File_1.xlsx',
                     output / 'OpenMFD_Supplementary_Data_File_1.xlsx', document.design_rows)
            report['design_rows'] = document.design_rows
        if args.compare:
            tracked = output / (document.stem + '_tracked.docx')
            comparison_original = output / (document.stem + '_comparison_baseline.docx')
            baseline = ComparisonBaseline(original.read_bytes())
            baseline.apply()
            baseline.write(comparison_original)
            assert document_text(comparison_original) == document_text(original)
            assert document_media(comparison_original) == document_media(original)
            compare_documents(comparison_original, revised, tracked, author='Tristan Simas', timeout=240, notes=note_path)
            row['comparison_baseline'] = comparison_original.name
            row['comparison_baseline_text_media_identical'] = True
            enable_recording(tracked)
            row.update(tracked=tracked.name, tracked_sha256=sha(tracked), native_endpoints_verified=True)
        report['documents'].append(row)
        (output / 'restoration_manifest.json').write_text(json.dumps(report, indent=2) + '\n')
        print(revised.name, 'tracked=' + str(row.get('tracked')), 'native_endpoints=' + str(row.get('native_endpoints_verified')), flush=True)


if __name__ == '__main__':
    main()
