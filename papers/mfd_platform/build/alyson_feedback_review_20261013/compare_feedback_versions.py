from difflib import unified_diff
from collections import Counter
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
PATHS = {
    'v7': ROOT / 'pi_review_20261002/mfd_draft_v7.docx',
    'v8': ROOT / 'build/mfd_draft_v8_alyson_feedback.docx',
}


def read_document(path):
    with ZipFile(path) as archive:
        document = E.fromstring(archive.read('word/document.xml'))
        paragraphs = [''.join(p.xpath('.//w:t/text()', namespaces=NS))
                      for p in document.xpath('/w:document/w:body/w:p', namespaces=NS)]
        tables = [[[''.join(cell.xpath('.//w:t/text()', namespaces=NS))
                    for cell in row.xpath('./w:tc', namespaces=NS)]
                   for row in table.xpath('./w:tr', namespaces=NS)]
                  for table in document.xpath('/w:document/w:body/w:tbl', namespaces=NS)]
        media = {name: hashlib.sha256(archive.read(name)).hexdigest()
                 for name in archive.namelist() if name.startswith('word/media/')}
        comments = E.fromstring(archive.read('word/comments.xml')) if 'word/comments.xml' in archive.namelist() else None
        return {
            'path': str(path),
            'paragraphs': paragraphs,
            'tables': tables,
            'media_sha256': media,
            'tracked_changes': len(document.xpath('//w:ins|//w:del', namespaces=NS)),
            'comments': len(comments) if comments is not None else 0,
        }


def main():
    documents = {name: read_document(path) for name, path in PATHS.items()}
    summary = {}
    for name, data in documents.items():
        paragraphs = data['paragraphs']
        start = paragraphs.index('Materials and Methods')
        end = paragraphs.index('Results')
        si = paragraphs.index('Supplementary Information')
        summary[name] = {
            'methods_words_including_subheadings': sum(len(p.split()) for p in paragraphs[start + 1:end]),
            'supplementary_start_paragraph': si + 1,
            'supplementary_nonempty_paragraphs': sum(bool(p) for p in paragraphs[si:]),
            'reference_heading_paragraphs': [i + 1 for i, p in enumerate(paragraphs) if p == 'References'],
        }
        (OUTPUT / f'{name}_body_paragraphs.txt').write_text(
            '\n'.join(f'P{i:03d}\t{p}' for i, p in enumerate(paragraphs, 1)) + '\n')
    a, b = documents['v7'], documents['v8']
    supplementary = lambda data: [p for p in data['paragraphs'][data['paragraphs'].index('Supplementary Information'):] if p]
    summary['comparison'] = {
        'tables_text_identical': a['tables'] == b['tables'],
        'table_count': len(a['tables']),
        'media_bytes_identical': Counter(a['media_sha256'].values()) == Counter(b['media_sha256'].values()),
        'media_count': len(a['media_sha256']),
        'supplementary_nonempty_paragraphs_identical': supplementary(a) == supplementary(b),
        'five_figure_legends_identical': [a['paragraphs'][i - 1] for i in (110, 112, 114, 116, 118)] == [b['paragraphs'][i - 1] for i in (71, 73, 75, 77, 79)],
    }
    payload = {'documents': documents, 'summary': summary}
    (OUTPUT / 'v7_v8_comparison.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    main_text = lambda name: [f'P{i:03d}\t{p}\n' for i, p in enumerate(documents[name]['paragraphs'], 1)
                            if i < summary[name]['supplementary_start_paragraph']]
    (OUTPUT / 'v7_v8_main_text.diff').write_text(''.join(unified_diff(main_text('v7'), main_text('v8'), fromfile=str(PATHS['v7']), tofile=str(PATHS['v8']))))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
