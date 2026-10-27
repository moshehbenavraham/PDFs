from pathlib import Path
import json, math, hashlib
import pymupdf as fitz
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT.parent/'pdf/tomorrow-has-questions.pdf'
QA=ROOT/'qa'
doc=fitz.open(PDF)
reader=PdfReader(PDF)
assert len(doc)==33, len(doc)
assert all(abs(p.rect.width-1280)<.01 and abs(p.rect.height-720)<.01 for p in doc)
alltext=[]
issues=[]
for p in doc:
    text=p.get_text()
    alltext.append(text)
    if '\ufffd' in text:issues.append(f'Page {p.number+1}: replacement glyph')
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                x0,y0,x1,y1=s['bbox']
                if x0 < -1 or y0 < -1 or x1>1281 or y1>721:
                    issues.append(f'Page {p.number+1}: out of bounds {s["text"]}')
    p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(QA/f'slide-{p.number+1:02}.png')
(QA/'extracted-text.txt').write_text('\n\n'.join(alltext))
fontnames=set()
embedded=[]
for p in reader.pages:
    for ref in p['/Resources'].get('/Font',{}).values():
        f=ref.get_object();name=str(f.get('/BaseFont'))
        if name in fontnames:continue
        fontnames.add(name)
        descriptor=f.get('/FontDescriptor')
        is_emb=bool(descriptor and any(k in descriptor.get_object() for k in ['/FontFile','/FontFile2','/FontFile3']))
        embedded.append({'font':name,'embedded':is_emb})
        if name!='/'+'Helvetica' and not is_emb:issues.append(f'Unembedded font: {name}')
for start in range(0,len(doc),4):
    montage=Image.new('RGB',(1920,1128),'#c6cdc9')
    d=ImageDraw.Draw(montage)
    for j in range(4):
        n=start+j+1
        if n>len(doc):break
        im=Image.open(QA/f'slide-{n:02}.png').resize((960,540),Image.Resampling.LANCZOS)
        x=(j%2)*960;y=(j//2)*564
        montage.paste(im,(x,y+24))
        d.text((x+12,y+5),f'{n:02}',fill='#102b3d')
    montage.save(QA/f'contact-{start//4+1:02}.jpg',quality=94)

report={
 'file':str(PDF),'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
 'pages':len(doc),'page_size_points':[1280,720], 'size_bytes':PDF.stat().st_size,
 'bookmarks':len(doc.get_toc()),'external_links':sum(len(p.get_links()) for p in doc),
 'fonts':embedded,'text_characters':sum(len(s) for s in alltext),'issues':issues,
 'reliability_math':{'20_steps':round(.99**20*100,1),'100_steps':round(.99**100*100,1)},
 'robot_cost_reduction':round((1-.9/1.14)*100,1)
}
(QA/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if issues:raise SystemExit(1)
