"""Check the delivered documents, moved data and final page layout."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pymupdf
from paper_build.compare import document_text
from papers.mfd_platform.figure_restoration.recipe.restore import REMOVED_VENDOR_URLS
from papers.mfd_platform.v14_tracked.recipe.apply_v14_edits import references

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def text(node):
    return ''.join(t.text or '' for t in node.iter(W + 't'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    root = parser.parse_args().root.resolve()
    out = root / 'figure_restoration'
    manifest = json.loads((out / 'restoration_manifest.json').read_text())
    report = {'documents': [], 'baseline': manifest['baseline']}
    for record in manifest['documents']:
        original = root / record['original']
        revised = out / record['revised']
        tracked = out / record['tracked']
        assert record['native_endpoints_verified']
        assert hashlib.sha256(tracked.read_bytes()).hexdigest() == record['tracked_sha256']
        expected_refs = references(original) - (REMOVED_VENDOR_URLS if record['revised'].startswith('MFD_') else Counter())
        assert expected_refs == references(revised)
        with ZipFile(tracked) as archive:
            assert archive.testzip() is None
            document = ET.fromstring(archive.read('word/document.xml'))
            insertions, deletions = (len(list(document.iter(W + tag))) for tag in ('ins', 'del'))
            assert insertions > 0 and deletions > 0
            setting = ET.fromstring(archive.read('word/settings.xml')).find(W + 'trackRevisions')
            assert setting is not None and setting.get(W + 'val') not in ('false', '0', 'off')
            notes = json.loads((out / tracked.name.replace('_tracked.docx', '_comments.json')).read_text())
            ids = set()
            if notes:
                comments = ET.fromstring(archive.read('word/comments.xml'))
                ids = {c.get(W + 'id') for c in comments}
                assert len(ids) >= len(notes)
                for tag in ('commentRangeStart', 'commentRangeEnd', 'commentReference'):
                    assert ids <= {c.get(W + 'id') for c in document.iter(W + tag)}
        report['documents'].append({'file': tracked.name, 'insertions': insertions,
                                    'deletions': deletions, 'comments': len(ids),
                                    'references_preserved': True, 'recording_enabled': True,
                                    'native_accept_reject_text_media': True})

    main_record = manifest['documents'][0]
    with ZipFile(out / main_record['revised']) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
        relationships = {r.get('Id'): posixpath.normpath('word/' + r.get('Target'))
                         for r in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
        images = [hashlib.sha256(archive.read(relationships[b.get(R + 'embed')])).hexdigest()
                  for b in document.iter(A + 'blip')]
    assert images == [f['sha256'] for f in main_record['images']]
    paragraphs = [p for _, story in document_text(out / main_record['revised']) for p in story]
    body = '\n'.join(paragraphs[:paragraphs.index('Figures')])
    main_seen = []; supplementary_seen = []
    for first, last in re.findall(r'Figs?\.\s+(S?\d+)(?:[–-](S?\d+))?', body):
        for token in (first, last):
            if not token: continue
            seen = supplementary_seen if token.startswith('S') else main_seen
            if token not in seen: seen.append(token)
    assert main_seen == ['1', '2', '3', '4', '5'], main_seen
    assert supplementary_seen == ['S1', 'S2', 'S3'], supplementary_seen
    for invalid in ('Fig. 2D', 'Fig. 2E', 'Fig. 2F', 'Fig. 3G', 'Fig. 4A', 'Fig. 4B', 'Fig. 4C', 'Fig. 4D', 'Fig. 4E', 'Fig. 5D'):
        assert invalid not in body, invalid
    report['figure_order'] = main_seen
    report['supplementary_figure_order'] = supplementary_seen
    report['original_main_image_hashes'] = images

    with ZipFile(out / manifest['documents'][1]['revised']) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
        tables = list(document.iter(W + 'tbl'))
        assert len(tables) == 1
        actual = [[text(c) for c in row.findall(W + 'tc')] for row in tables[0].findall(W + 'tr')]
    with (root / 'supplementary/fabrication_strategies.csv').open() as stream:
        assert actual == list(csv.reader(stream))
    with ZipFile(root / 'v14_tracked/OpenMFD_Supplementary_Data_File_1.xlsx') as original, ZipFile(out / 'OpenMFD_Supplementary_Data_File_1.xlsx') as revised:
        for name in original.namelist():
            if name.startswith(('xl/worksheets/', 'xl/sharedStrings', 'xl/styles')):
                expected = original.read(name)
                if name == 'xl/worksheets/sheet1.xml':
                    expected = expected.replace(b'<x:v>Main Figure 3G</x:v>',
                                                b'<x:v>Supplementary data only; not plotted in a main figure</x:v>')
                assert expected == revised.read(name), name
        sheet = ET.fromstring(revised.read('xl/worksheets/sheet6.xml'))
        rows = [[ ''.join(c.itertext()) for c in row] for row in sheet.find(S + 'sheetData')]
        assert rows == manifest['design_rows']
    report['design_table_rows_in_S6'] = len(rows)
    report['original_workbook_cells_and_styles_byte_identical'] = True
    report['sheet1_provenance_note_updated_from_main_figure_3g'] = True
    report['fabrication_comparison_approaches'] = len(actual) - 1

    report['pdfs'] = []
    for path in sorted(out.glob('*_revised.pdf')):
        pdf = pymupdf.open(path)
        figures = []
        for number, page in enumerate(pdf, 1):
            content = page.get_text()
            pictures = page.get_image_info()
            assert re.sub(r'\d|\s', '', content) or pictures, (path.name, 'blank page', number)
            for picture in pictures:
                x0, y0, x1, y1 = picture['bbox']
                assert x0 >= -1 and y0 >= -1 and x1 <= page.rect.width + 1 and y1 <= page.rect.height + 1
            labels = re.findall(r'Fig\.\s*([1-5])\.', content)
            if path.name == 'MFD_original_figures_revised.pdf' and labels:
                assert pictures, ('legend separated from figure', number, labels)
                figures.extend(labels)
        if path.name == 'MFD_original_figures_revised.pdf':
            assert figures == ['1', '2', '3', '4', '5'], figures
        report['pdfs'].append({'file': path.name, 'pages': len(pdf),
                               'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    (out / 'delivery_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
