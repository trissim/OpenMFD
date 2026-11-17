"""Expose accepted wording and actual OOXML comment ranges for peer review."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from paper_build.compare import paragraph_text

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--directory',type=Path,required=True)
ROOT=parser.parse_args().directory.resolve()
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
report=[]
for path in sorted(ROOT.glob('*_tracked.docx')):
    with ZipFile(path) as archive:
        root=ET.fromstring(archive.read('word/document.xml'))
        comments={}
        if 'word/comments.xml' in archive.namelist():
            for comment in ET.fromstring(archive.read('word/comments.xml')):
                comments[comment.get(W+'id')]={'author':comment.get(W+'author'),'text':'\n'.join(paragraph_text(p) for p in comment.iter(W+'p')),'selected_text':'','paragraphs':[],'starts':0,'ends':0}
        # A read-only projection of the delivered redlines, not a substitute
        # for Writer's already-executed native accept/reject verification.
        for parent in root.iter():
            for child in list(parent):
                if child.tag in {W+'del',W+'moveFrom'}:
                    parent.remove(child)
        active=set()
        paragraphs=[]
        for index,p in enumerate(root.iter(W+'p'),1):
            text=paragraph_text(p)
            if text:
                paragraphs.append({'paragraph':index,'text':text})
            for node in p.iter():
                if node.tag==W+'commentRangeStart':
                    key=node.get(W+'id'); active.add(key); comments[key]['starts']+=1
                elif node.tag==W+'commentRangeEnd':
                    key=node.get(W+'id'); active.remove(key); comments[key]['ends']+=1
                elif node.tag==W+'t':
                    for key in active:
                        comments[key]['selected_text']+=node.text or ''
                        if index not in comments[key]['paragraphs']:
                            comments[key]['paragraphs'].append(index)
        assert not active
        notes_path=ROOT/path.name.replace('_tracked.docx','_comments.json')
        notes=json.loads(notes_path.read_text())
        assert len(notes)==len(comments)
        for note in notes:
            matches=[c for c in comments.values() if c['text']==note['text']]
            assert len(matches)==1
            match=matches[0]
            assert match['starts']==match['ends']==1
            assert match['selected_text']==note['anchor'],(path.name,note['anchor'],match['selected_text'])
        settings=ET.fromstring(archive.read('word/settings.xml'))
        track=settings.find(W+'trackRevisions')
        assert track is not None and track.get(W+'val','true') not in {'false','0','off'}
        report.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'accepted_text_projection':paragraphs,'actual_comment_ranges':comments,'expected_anchor_texts_match':True,'recording_enabled':True})
(ROOT/'accepted_text_and_comments.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps([{'file':r['file'],'sha256':r['sha256'],'paragraphs':len(r['accepted_text_projection']),'comments':len(r['actual_comment_ranges']),'anchors_verified':r['expected_anchor_texts_match']} for r in report],indent=2))
