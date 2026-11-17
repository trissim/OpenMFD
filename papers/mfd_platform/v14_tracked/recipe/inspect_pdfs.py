"""Render every exported page to bounded contact sheets and record PDF properties."""
from pathlib import Path
import hashlib
import json
import argparse
import pymupdf
from PIL import Image, ImageDraw

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--directory',type=Path,required=True)
root=parser.parse_args().directory.resolve()
output=root/'pdf-review'; output.mkdir(exist_ok=True)
report=[]
for path in sorted(root.glob('*.pdf')):
    doc=pymupdf.open(path)
    previews=[]; pages=[]
    for number,page in enumerate(doc,1):
        scale=450/page.rect.width
        bitmap=page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False)
        image=Image.frombytes('RGB',(bitmap.width,bitmap.height),bitmap.samples)
        tile=Image.new('RGB',(470,680),'#dedede')
        image.thumbnail((450,645))
        tile.paste(image,((470-image.width)//2,25))
        ImageDraw.Draw(tile).text((8,5),f'{path.stem} | page {number}',fill='black')
        previews.append(tile)
        text=page.get_text()
        pages.append({'page':number,'size_pt':[page.rect.width,page.rect.height],'characters':len(text),'text':text})
    contacts=[]
    for start in range(0,len(previews),9):
        sheet=Image.new('RGB',(470*3,680*3),'#aaaaaa')
        for offset,image in enumerate(previews[start:start+9]):
            sheet.paste(image,((offset%3)*470,(offset//3)*680))
        target=output/f'{path.stem}_pages_{start+1:02d}-{min(start+9,len(previews)):02d}.jpg'
        sheet.save(target,quality=90)
        contacts.append(str(target))
    assert pages and sum(p['characters'] for p in pages)>0
    report.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'page_count':len(pages),'contact_sheets':contacts,'pages':pages})
    print(f'{path.name}: {len(pages)} pages; contacts: {contacts}',flush=True)
(root/'pdf_export_checks.json').write_text(json.dumps(report,indent=2)+'\n')
