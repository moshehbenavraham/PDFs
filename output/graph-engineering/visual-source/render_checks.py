from pathlib import Path
import json
from PIL import Image, ImageOps, ImageDraw, ImageFont
import pymupdf as fitz

BASE = Path(__file__).resolve().parents[1]
TMP = BASE.parent.parent / "tmp/pdfs/graph-visual"
font = ImageFont.truetype("/usr/share/fonts/truetype/ibm-plex/IBMPlexMono-Regular.ttf", 13)
files = sorted(TMP.glob("page-[0-9][0-9].png"))
assert len(files) == 24, len(files)
for sheet in range(3):
    contact=Image.new("RGB",(1008,1340),"#d4dbd2")
    for i,f in enumerate(files[sheet*8:sheet*8+8]):
        im=Image.open(f).convert("RGB")
        im.thumbnail((480,300),Image.Resampling.LANCZOS)
        x=16+(i%2)*496
        y=20+(i//2)*330
        contact.paste(im,(x,y))
        ImageDraw.Draw(contact).text((x,y+304),f"PAGE {sheet*8+i+1:02d}",font=font,fill="#163c3d")
    contact.save(TMP/f"contact-{sheet+1}.png")

doc=fitz.open(BASE/"graph-engineering-visual-guide.pdf")
problems=[]
for number,page in enumerate(doc,1):
    blocks=page.get_text("dict")["blocks"]
    spans=[s for b in blocks if "lines" in b for l in b["lines"] for s in l["spans"]]
    for i,a in enumerate(spans):
        ar=fitz.Rect(a["bbox"])
        if not page.rect.contains(ar): problems.append((number,"out-of-bounds",a["text"]))
        for b in spans[i+1:]:
            br=fitz.Rect(b["bbox"])
            overlap=ar & br
            if overlap.width>1 and overlap.height>3:
                problems.append((number,"text-overlap",a["text"],b["text"]))
print(json.dumps({"text_geometry_issues":problems,"contact_sheets":3},indent=2))
