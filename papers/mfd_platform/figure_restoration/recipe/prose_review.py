"""Make a prose redline with the final figures fixed on both comparison sides.

The full earlier comparison remains untouched. Reject All in this review copy
restores Alyson's prose, not her artwork; Accept All restores the reading copy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from paper_build.compare import compare_documents, document_media, document_text
from papers.mfd_platform.figure_restoration.recipe.restore import A, ComparisonBaseline, Manuscript, R, REMOVED_VENDOR_URLS, W, sha
from papers.mfd_platform.v14_tracked.recipe.apply_v14_edits import enable_recording, references


class ProseReviewBaseline(ComparisonBaseline):
    """Keep every original paragraph, using the final figure payloads and sizes."""
    source_name = Manuscript.source_name

    def __init__(self, payload: bytes, revised: ComparisonBaseline):
        super().__init__(payload)
        self.revised = revised

    def apply(self) -> None:
        super().apply()
        original_media = {name for name in self.entries if name.startswith('word/media/')}
        revised_media = {name for name in self.revised.entries if name.startswith('word/media/')}
        if original_media != revised_media:
            raise ValueError('Prose comparison needs corresponding original/final media parts')
        for old, new in zip(self.document.getElementsByTagNameNS(W, 'drawing'),
                            self.revised.document.getElementsByTagNameNS(W, 'drawing'), strict=True):
            old_ids = [n.getAttributeNS(R, 'embed') for n in old.getElementsByTagNameNS(A, 'blip')]
            new_ids = [n.getAttributeNS(R, 'embed') for n in new.getElementsByTagNameNS(A, 'blip')]
            if old_ids != new_ids:
                raise ValueError('Prose comparison needs matching image relationships')
            old.parentNode.replaceChild(self.document.importNode(new, True), old)
        for name in original_media:
            self.entries[name] = (self.entries[name][0], self.revised.entries[name][1])
        if self.entries['word/_rels/document.xml.rels'][1] != self.revised.entries['word/_rels/document.xml.rels'][1]:
            raise ValueError('Original/final relationship maps differ')


def text_revisions(path: Path) -> dict[str, list[str]]:
    """Read non-picture Word revisions, including unchanged paragraph marks."""
    w = '{' + W + '}'
    with ZipFile(path) as archive:
        xml = ET.fromstring(archive.read('word/document.xml'))
    return {tag: [''.join(text.text or '' for text in node.iter()
                         if text.tag in (w + 't', w + 'delText'))
                  for node in xml.iter(w + tag) if not list(node.iter(w + 'drawing'))]
            for tag in ('ins', 'del')}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / 'figure_restoration'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / 'comparison_inputs'
    inputs.mkdir()
    manifest = json.loads((source / 'restoration_manifest.json').read_text())
    manuscript = manifest['documents'][0]
    original = root / manuscript['original']
    revised = source / manuscript['revised']
    full_comparison = source / manuscript['tracked']
    immutable = {str(path): sha(path) for path in (original, revised, full_comparison,
                 source / 'MFD_original_figures_revised.pdf')}
    baseline = inputs / 'Alyson_prose_with_final_figures.docx'
    document = ProseReviewBaseline(original.read_bytes(), ComparisonBaseline(revised.read_bytes()))
    document.apply()
    document.write(baseline)
    assert document_text(baseline) == document_text(original)
    assert references(baseline) == references(original)
    assert references(original) - REMOVED_VENDOR_URLS == references(revised)
    assert document_media(baseline) == document_media(revised)
    reading = output / 'MFD_for_Alyson_reading.docx'
    shutil.copyfile(revised, reading)
    pdf = output / 'MFD_for_Alyson_reading.pdf'
    shutil.copyfile(source / 'MFD_original_figures_revised.pdf', pdf)
    tracked = output / 'MFD_for_Alyson_prose_redline.docx'
    compare_documents(baseline, reading, tracked, author='Tristan Simas', timeout=240,
                      notes=source / (Manuscript.stem + '_comments.json'))
    enable_recording(tracked)
    w = '{' + W + '}'
    with ZipFile(tracked) as archive:
        xml = ET.fromstring(archive.read('word/document.xml'))
        insertions, deletions = (list(xml.iter(w + tag)) for tag in ('ins', 'del'))
        assert len(list(xml.iter(w + 'drawing'))) == len(manuscript['images']) == 5
        assert not any(list(node.iter(w + 'drawing')) for node in (*insertions, *deletions))
        assert insertions and deletions
        comments = ET.fromstring(archive.read('word/comments.xml'))
        assert len(comments) >= len(json.loads((source / (Manuscript.stem + '_comments.json')).read_text()))
    assert document_media(tracked) == document_media(reading)
    assert text_revisions(tracked) == text_revisions(full_comparison)
    for path, value in immutable.items():
        assert sha(Path(path)) == value, path
    report = {
        'scope': 'Prose-only redline. Tristan original figures are fixed in both views. Full earlier comparison preserved.',
        'original_text_unchanged_in_comparison_baseline': True,
        'references_preserved': True,
        'non_picture_revisions_identical_to_full_comparison': True,
        'native_accept_all': 'Final reading text and five final figures',
        'native_reject_all': 'Original Alyson prose and the SAME five final figures; artwork is intentionally not redlined',
        'drawings': 5,
        'image_revisions': 0,
        'insertions': len(insertions),
        'deletions': len(deletions),
        'retained_inputs': immutable,
        'files': [{'name': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path)}
                  for path in (reading, pdf, tracked)],
    }
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
