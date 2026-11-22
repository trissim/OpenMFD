"""Restore retained artwork into PI prose; use shared native Word comparison."""
from __future__ import annotations

import argparse
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RestoredDocument(V14Document):
    """Retain the previous approved local corrections, compare against returned PI source."""
    def change(self, anchor: str, old: str, new: str) -> None:
        paragraph = self.paragraph(anchor)
        text = self.paragraph_text(paragraph)
        if old not in text:
            raise ValueError((anchor, old))
        self.replace(text, text.replace(old, new), 'Match restored figure/table content')

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
        self.change('The principal device comprised a 6 × 8 array',
                    'Design dimensions are provided in Table S1 within Supplementary Protocol 1',
                    'Design dimensions are provided in Supplementary Data File 1, sheet S6')
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

        source = (self.root / 'manuscript.md').read_text()
        figures = re.findall(r'^!\[(Figure (\d+):.*?)\]\((figures/rendered/[^)]+)\)\{width=6.5in\}', source, re.M)
        if len(figures) != 5:
            raise ValueError('Expected five original authored figures and legends')
        for caption, number, relative in figures:
            number = int(number)
            caption = re.sub(r'^Figure \d+:', f'Fig. {number}.', caption).replace('**', '')
            if number == 2:
                for old, new in (('Kerman et al. (2015)', '(PMID: 26015546)'),
                                 ('Taylor et al. (2015)', '(PMID: 26000554)'),
                                 ('Coquinco et al. (2014)', '(PMID: 24662423)')):
                    caption = caption.replace(old, new)
            if number == 4:
                caption = caption.replace('(Protocol S1; mold fabrication in Protocol S2).',
                                          '(Supplementary Protocol 2; mold fabrication in Supplementary Protocol 1).')
            if number == 5:
                caption = caption.replace('Scale bars: 5 mm, based on', 'Scale bars: approximately 5 mm, estimated from')
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
                properties = self.document.createElementNS(W, 'w:rPr')
                size = self.document.createElementNS(W, 'w:sz'); size.setAttributeNS(W, 'w:val', '18'); properties.appendChild(size)
                run.insertBefore(properties, run.firstChild)
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
        # Previously approved step renumbering is already in the clean input.
        pass


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
    with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
        for entry, payload in entries.values():
            archive.writestr(entry, payload)
    with ZipFile(original) as old, ZipFile(output) as new:
        for name in old.namelist():
            if name.startswith(('xl/worksheets/', 'xl/sharedStrings', 'xl/styles')):
                assert old.read(name) == new.read(name), name


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
        notes = json.loads((previous / (previous_stem + '_comments.json')).read_text())
        if kind is Manuscript:
            notes = [n for n in notes if not n['anchor'].startswith(('Representative CTB', 'Wafer-scale photomask'))]
            notes.append({'anchor': 'Representative DIV11 cortical neurons (Plate 1, device R03C04)',
                          'text': 'Original full Figure 5 restored, including the single P1/R03C04 example and saved orange outlines. Native historical image/ROI/scale provenance questions remain unresolved; this edit does not rerun segmentation or redraw microscopy.'})
        note_path = output / (document.stem + '_comments.json')
        note_path.write_text(json.dumps(notes, indent=2) + '\n')
        original = previous / (previous_stem + '_original.docx')
        assert references(original) == references(revised), document.source_name
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
