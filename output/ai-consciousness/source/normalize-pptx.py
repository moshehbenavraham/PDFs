import sys, zipfile, re, os
from pathlib import Path
from xml.etree import ElementTree as E
p=Path(sys.argv[1]); out=p.with_suffix('.normalized.pptx')
with zipfile.ZipFile(p) as src, zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dst:
    slide_count=sum(bool(re.fullmatch(r'ppt/slides/slide\d+\.xml',n)) for n in src.namelist())
    for info in src.infolist():
        b=src.read(info.filename)
        if info.filename in ('docProps/core.xml','docProps/app.xml'):
            root=E.fromstring(b)
            for el in root:
                tag=el.tag.split('}')[-1]
                if tag=='title': el.text='Is Anyone Home? AI Consciousness & Sentience'
                if tag in ('creator','lastModifiedBy'): el.text=''
                if tag in ('Slides','Notes'): el.text=str(slide_count)
                if tag=='PresentationFormat': el.text='On-screen Show (16:9)'
            b=E.tostring(root,encoding='utf-8',xml_declaration=True)
        dst.writestr(info,b)
os.replace(out,p)
