from pathlib import Path
import json,re,unicodedata,hashlib,zipfile
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'source/deck-data.json').read_text())
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t)).replace('\u00ad','')
report={}
for filename,label,expected in [('Is Anyone Home.pdf','slides',26),('Presenter Guide.pdf','guide',27)]:
    doc=fitz.open(ROOT/'output'/filename);dest=ROOT/'.build'/f'{label}-pdf';dest.mkdir(exist_ok=True)
    issues=[]
    for i,p in enumerate(doc):
        text=p.get_text()
        if label=='slides':
            for box in data['slides'][i]['items']:
                if norm(box['text']) not in norm(text):issues.append({'page':i+1,'missing':box['text']})
        elif i>0:
            if norm(data['slides'][i-1]['notes']) not in norm(text):issues.append({'page':i+1,'missing':'Presenter note text'})
        for b in p.get_text('blocks'):
            if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:issues.append({'page':i+1,'outside_page':b[:4]})
        zoom=1.2 if label=='slides' else 1.1
        p.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False).save(dest/f'{i+1:02}.png')
    thumbs=[]
    for i in range(len(doc)):
        im=Image.open(dest/f'{i+1:02}.png').convert('RGB');im.thumbnail((390,550 if label=='guide' else 220))
        cell=Image.new('RGB',(410,580 if label=='guide' else 255),'#d9d9d9');cell.paste(im,((410-im.width)//2,10));ImageDraw.Draw(cell).text((12,cell.height-22),f'{i+1:02}',fill='black');thumbs.append(cell)
    for start in range(0,len(thumbs),9 if label=='guide' else 12):
        chosen=thumbs[start:start+(9 if label=='guide' else 12)];cols=3;rows=(len(chosen)+cols-1)//cols
        sheet=Image.new('RGB',(cols*410,rows*chosen[0].height),'#d9d9d9')
        for j,im in enumerate(chosen):sheet.paste(im,((j%cols)*410,(j//cols)*im.height))
        sheet.save(ROOT/'.build'/f'{label}-contact-{start+1:02}.jpg',quality=90)
    report[label]={'pages':len(doc),'expected_pages':expected,'size_points':list(doc[0].rect),'text_and_bounds_issues':issues,'metadata':doc.metadata,'links':sum(len(p.get_links()) for p in doc)}
    assert len(doc)==expected,(filename,len(doc))
report['pptx_sha256']=hashlib.sha256((ROOT/'output/Is Anyone Home.pptx').read_bytes()).hexdigest()
with zipfile.ZipFile(ROOT/'output/Is Anyone Home.pptx') as z:
    report['pptx_notes']=len([n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)])
    report['pptx_editable_textboxes']=sum(z.read(n).count(b'<a:t>') for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
(ROOT/'.build/output-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
