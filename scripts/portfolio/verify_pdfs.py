"""Render every PDF page and verify metadata, Korean text and page geometry."""
from pathlib import Path
import json
import sys
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'work/portfolio/pdf-qa';out.mkdir(parents=True,exist_ok=True)
results=[]
requested=set(sys.argv[1:])
files=sorted((ROOT/'project_template').glob('*.pdf'))
if requested:
    assert requested <= {p.name for p in files}, 'Unknown PDF filename'
    files=[p for p in files if p.name in requested]
for p in files:
    doc=pdfium.PdfDocument(str(p));r=PdfReader(p);tiles=[]
    for i,page in enumerate(r.pages):
        text=page.extract_text() or ''
        assert len(text)>100,(p.name,i,'empty page')
        assert '\ufffd' not in text,(p.name,i,'bad glyph')
        assert int(page.mediabox.width)==960 and int(page.mediabox.height)==600
        im=doc[i].render(scale=1.3).to_pil().convert('RGB')
        im.save(out/f'{p.stem}-{i+1:02d}.png')
        im.thumbnail((640,400));tile=Image.new('RGB',(660,430),'#dce3df');tile.paste(im,(10,25));ImageDraw.Draw(tile).text((10,6),f'PAGE {i+1}',fill='black');tiles.append(tile)
    sheet=Image.new('RGB',(1320,430*((len(tiles)+1)//2)),'#dce3df')
    for j,t in enumerate(tiles):sheet.paste(t,((j%2)*660,(j//2)*430))
    sheet.save(out/f'{p.stem}-contact.jpg')
    results.append(dict(file=p.name,pages=len(doc),bytes=p.stat().st_size,text_characters=sum(len(q.extract_text() or '') for q in r.pages),bookmarks=len(r.outline)))
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
