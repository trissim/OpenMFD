"""Apply the agreed V14 edits to clean copies, then use paper_build's native redlines.

The returned archive is immutable. No old Markdown manuscript is regenerated.
"""
from __future__ import annotations

import argparse
from abc import ABC, abstractmethod
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from xml.dom import minidom
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageChops, ImageDraw
from paper_build.compare import compare_documents, document_text

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
AUTHOR = 'Tristan Simas'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class V14Document(ABC):
    """One supplied document owns its clean edits and unresolved review notes."""
    source_name: str
    stem: str

    def __init__(self, payload: bytes):
        with ZipFile(BytesIO(payload)) as archive:
            self.entries = {entry.filename: (entry, archive.read(entry.filename)) for entry in archive.infolist()}
        self.original = payload
        self.document = minidom.parseString(self.entries['word/document.xml'][1])
        self.edits: list[dict[str, str]] = []
        self.notes: list[dict[str, str]] = []
        self.image_changes: list[dict] = []

    @staticmethod
    def paragraph_text(paragraph) -> str:
        return ''.join(child.data for node in paragraph.getElementsByTagNameNS(W, 't')
                       for child in node.childNodes if child.nodeType == child.TEXT_NODE)

    def paragraphs(self):
        return self.document.getElementsByTagNameNS(W, 'p')

    def paragraph(self, anchor: str):
        matches = [p for p in self.paragraphs() if anchor in self.paragraph_text(p)]
        if len(matches) != 1:
            raise ValueError(f'{self.source_name}: expected one paragraph for {anchor!r}, found {len(matches)}')
        return matches[0]

    def replace(self, old: str, new: str, reason: str, paragraph=None, occurrence=None) -> None:
        # An explicit paragraph lets a caller replace just the changed words, so the
        # surrounding runs (for example a bold run-in heading) keep their formatting.
        paragraph = paragraph if paragraph is not None else self.paragraph(old)
        text = self.paragraph_text(paragraph)
        if occurrence is None and text.count(old) != 1:
            raise ValueError(f'Nonunique edit text: {old!r}')
        start = text.index(old)
        for _ in range(occurrence or 0):
            start = text.index(old, start + 1)
        end = start + len(old)
        offset = 0
        inserted = False
        for node in paragraph.getElementsByTagNameNS(W, 't'):
            value = ''.join(c.data for c in node.childNodes if c.nodeType == c.TEXT_NODE)
            following = offset + len(value)
            if offset < end and following > start:
                left = max(0, start - offset)
                right = min(len(value), end - offset)
                replacement = value[:left] + (new if not inserted else '') + value[right:]
                inserted = True
                for child in list(node.childNodes):
                    node.removeChild(child)
                node.appendChild(self.document.createTextNode(replacement))
                node.setAttribute('xml:space', 'preserve')
            offset = following
        assert inserted
        assert self.paragraph_text(paragraph) == text[:start] + new + text[end:]
        self.edits.append({'old': old, 'new': new, 'reason': reason})

    @abstractmethod
    def apply(self) -> None: ...

    def write(self, path: Path) -> None:
        self.entries['word/document.xml'] = (self.entries['word/document.xml'][0], self.document.toxml(encoding='utf-8'))
        with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
            for entry, data in self.entries.values():
                archive.writestr(entry, data)

    def note(self, anchor: str, text: str) -> None:
        self.paragraph(anchor)
        self.notes.append({'anchor': anchor, 'text': text})


class MainManuscript(V14Document):
    source_name = 'MFD_V14_AEF.docx'
    stem = 'MFD_V14'

    def apply(self) -> None:
        self.replace('; mold fabrication and assembly performance are evaluated in the subsequent Results sections.', '.', 'E1: remove navigation, retain finding')
        self.replace(' Repeated casting performance and characterization of the finished microfluidic devices are addressed in the following section.', '', 'E1: remove navigation')
        self.replace(' Fluid transport and neuronal compatibility of the assembled plates are evaluated in the following Results section.', '', 'E1: remove navigation')
        self.replace('These examples demonstrate coordinated generation of fabrication files for different compartment numbers and channel arrangements. These are computational design outputs only and alternative configurations were not fabricated, cast, or biologically validated.', 'OpenMFD generated matched fabrication files for these different compartment numbers and channel arrangements; the alternative devices were not fabricated, cast or biologically tested.', 'E2: retain generated-only scope without repetition')
        self.replace("Schematics in panels A–D are adapted from the original manuscript's fabrication workflow.", 'Panels A–D show the casting and plate-assembly workflow.', 'E5: remove draft-history framing')
        self.replace('Black signal on white is the original display convention', 'CTB fluorescence is displayed as black signal on white', 'E6: name the display directly')
        self.replace('positions suggesting', 'positions, suggesting', 'E7: punctuation')
        anchor = 'Photographs and pin-height measurements are from the original fabrication experiments; panels B and D are schematic and are not to scale.'
        self.replace(anchor, anchor + ' In the procedure described in Supplementary Protocol 1D, the inserts remain on their flexible metal carrier during alignment and bonding; EPDM backing behind the carrier accommodates insert-height differences as the pins seat in the SUEX openings.', 'E4: describe documented procedure, not invisible schematic layers')
        self.note('Complete acquisition parameters, image positions, and analytical procedures are provided in Supplementary Protocol 2.', 'Please confirm the historical analysis software/version, stitching/registration and segmentation settings, CTB-positive classification rule, and any manual corrections. The retained handoff does not establish that the same candidate configuration generated every historical count; do not substitute current defaults or silently rerun the observations.')
        self.note('ProtocolFournier-4748', 'Retain this PI-supplied ethics information. Please confirm exact identifier typography and coverage of this preparation before submission.')
        self.note('Supporting plate frames were fabricated from high-impact polystyrene (HIPS) using a Creality K1C filament printer', 'Workbook S3 retains five top layers and a source note of 0.8 mm at 0.20 mm layer height. Please check the native slicer/G-code for the controlling parameter or override; no supplied setting has been silently changed.')
        self.note('A versioned software and fabrication archive will be deposited for permanent access.', 'Before submission, identify the actual archive/deposit and supplied microscopy, ROI/calibration/crop records, exclusion provenance, native printer profiles/G-code and fabrication files. The current ZIP/workbook does not contain all of those files. Keep prospective wording until deposit is complete; no DOI is invented here.')
        self.note('Representative CTB-647 images at DIV11, from one interior device on each plate', 'The three named examples and yellow overlays are present and their IDs match the retained source handoff. Final source-image/crop/ROI/scale preservation still requires comparison with the native records; no biological image was redrawn in this revision.')
        image_name = 'word/media/image1.png'
        entry, raw = self.entries[image_name]
        image = Image.open(BytesIO(raw)).convert('RGB')
        if image.size != (2000, 1220):
            raise ValueError('The agreed Figure 1 artwork size changed')
        original = image.copy()
        # Only the tiny second recipe line beneath the wafer layout; no masks,
        # photography, scale bars or experimental imagery are in this rectangle.
        bounds = (280, 731, 430, 744)
        ImageDraw.Draw(image).rectangle((bounds[0], bounds[1], bounds[2]-1, bounds[3]-1), fill='white')
        difference = ImageChops.difference(original, image).getbbox()
        if difference is None:
            raise ValueError('The recipe removal changed no pixels')
        assert bounds[0] <= difference[0] < difference[2] <= bounds[2]
        assert bounds[1] <= difference[1] < difference[3] <= bounds[3]
        data = BytesIO(); image.save(data, format='PNG')
        self.entries[image_name] = (entry, data.getvalue())
        self.image_changes.append({'part': image_name, 'old_sha256': digest(raw), 'new_sha256': digest(data.getvalue()), 'removed_text': 'Use 60mL of Sylgard 184 in 1:10 ratio', 'bounds_px': bounds, 'changed_bbox_px': difference, 'reason': 'C1: remove conflicting recipe instruction; retain procedure in protocol'})
        self.note('Wafer-scale photomask containing 48 two-compartment devices', 'Figure 1C artwork revision removes only the tiny conflicting recipe inscription. The unchanged protocol distinguishes about 35 mL mixed, 30 mL dispensed and a 60 mL syringe, with 10:1 base:curing agent. The entire original image is retained as the deleted image revision so rejecting the figure change restores V14.')


class MoldProtocol(V14Document):
    source_name = 'Supplementary Protocol 1_MFD.docx'
    stem = 'Supplementary_Protocol_1_V14'

    def apply(self) -> None:
        first = self.paragraph('Troubleshooting note — SU-8 adhesion and thermal stability.')
        second = self.paragraph('Troubleshooting note — SUEX surface flatness.')
        following = self.paragraph('C. Print, clean and inspect the resin-insert array')
        body = first.parentNode
        assert second.parentNode is body and following.parentNode is body
        children = list(body.childNodes)
        start, end = children.index(second), children.index(following)
        assert children.index(first) < start < end
        moved = children[start:end]
        for node in moved:
            body.insertBefore(node, first)
        self.edits.append({'old': 'SU-8/S2 block before SUEX/S1 block', 'new': 'SUEX/S1 block before SU-8/S2 block', 'reason': 'C3: move complete original paragraphs, images and captions without relabeling'})


class CultureProtocol(V14Document):
    source_name = 'Supplementary Protocol 2_MFD.docx'
    stem = 'Supplementary_Protocol_2_V14'

    def apply(self) -> None:
        for old, new in (
            ('4. Transfer approximately 30 mL', '3. Transfer approximately 30 mL'),
            ('5. Load the filled molds', '4. Load the filled molds'),
            ('6. Transfer the loaded rack', '5. Transfer the loaded rack'),
            ('7. Remove the aluminum foil', '6. Remove the aluminum foil'),
            ('8. Support the wafer on a flat surface.', '7. Support the wafer on a flat surface.'),
            ('9. Inspect the demolded cast.', '8. Inspect the demolded cast.'),
        ):
            self.replace(old, new, 'C2: consecutive numbering; all eight retained actions confirmed by mfd13911')
        self.note('Identify and count CTB-positive neuronal cell bodies using the same cell segmentation settings and criteria for CTB labeling in every cropped image.', 'This repeat-use instruction does not establish the configuration used for the historical observations. Please confirm historical segmentation/positivity settings and manual corrections from the run records, or state the remaining limitation without substituting current defaults.')


def references(path: Path) -> Counter:
    text='\n'.join(p for story, paragraphs in document_text(path) for p in paragraphs)
    return Counter(re.findall(r'\((?:PMID|PMIDs|DOI):[^)]*\)|https?://[^\s)]+', text))


def enable_recording(path: Path) -> None:
    with ZipFile(path) as archive:
        entries={e.filename:(e,archive.read(e.filename)) for e in archive.infolist()}
    entry,data=entries['word/settings.xml']
    xml=minidom.parseString(data)
    nodes=xml.getElementsByTagNameNS(W,'trackRevisions')
    if nodes:
        node=nodes[0]
    else:
        node=xml.createElementNS(W,'w:trackRevisions'); xml.documentElement.appendChild(node)
    node.setAttributeNS(W,'w:val','true')
    entries['word/settings.xml']=(entry,xml.toxml(encoding='utf-8'))
    with ZipFile(path,'w',compression=ZIP_DEFLATED) as archive:
        for item,payload in entries.values(): archive.writestr(item,payload)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--prepare-only',action='store_true')
    members = V14Document.__subclasses__()
    parser.add_argument('--document', choices=[member.stem for member in members])
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest = out/'edit_manifest.json'
    if args.document:
        report=json.loads(manifest.read_text())
        report['documents']=[row for row in report['documents'] if Path(row['original']).name != args.document+'_original.docx']
    else:
        report={'archive':str(args.archive.resolve()),'archive_sha256':digest(args.archive.read_bytes()),'documents':[]}
    with ZipFile(args.archive) as archive:
        for member in members:
            if args.document and member.stem != args.document:
                continue
            payload=archive.read(member.source_name); edit=member(payload); edit.apply()
            original=out/(edit.stem+'_original.docx'); revised=out/(edit.stem+'_revised.docx'); tracked=out/(edit.stem+'_tracked.docx')
            original.write_bytes(payload); edit.write(revised)
            assert references(original)==references(revised),edit.source_name
            notes=out/(edit.stem+'_comments.json'); notes.write_text(json.dumps(edit.notes,indent=2)+'\n')
            row={'original':str(original),'original_sha256':digest(payload),'revised':str(revised),'revised_sha256':digest(revised.read_bytes()),'references_unchanged':True,'edits':edit.edits,'comments':edit.notes}
            row['image_changes']=edit.image_changes
            if not args.prepare_only:
                compare_documents(original,revised,tracked,author=AUTHOR,timeout=180,notes=notes)
                enable_recording(tracked)
                with ZipFile(tracked) as doc:
                    xml=minidom.parseString(doc.read('word/document.xml'))
                    row['tracked_insertions']=len(xml.getElementsByTagNameNS(W,'ins'))
                    row['tracked_deletions']=len(xml.getElementsByTagNameNS(W,'del'))
                    assert row['tracked_insertions'] and row['tracked_deletions']
                row.update(tracked=str(tracked),tracked_sha256=digest(tracked.read_bytes()),native_accept_reject_text_and_media_verified=True,recording_enabled=True)
            report['documents'].append(row)
            (out/'edit_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row,indent=2),flush=True)
        workbook='OpenMFD_Supplementary_Data_File_1.xlsx'
        data=archive.read(workbook); (out/workbook).write_bytes(data)
        report['workbook']={'filename':workbook,'sha256':digest(data),'unchanged':True}
    (out/'edit_manifest.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
