"""Generate synthetic, non-private fixtures for the Windows PDF tool checks."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
SAMPLES = {
    "eng": {
        "font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "lines": ["English document test", "The quick brown fox jumps over the lazy dog.",
                  "PDF tools are ready for document processing."],
        "tokens": ["English", "document", "processing"],
    },
    "heb": {
        "font": "/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf",
        "lines": ["שלום עולם", "זהו מסמך בדיקה בעברית", "בדיקת זיהוי טקסט במסמך"],
        "tokens": ["שלום", "עולם", "מסמך", "בדיקה", "בעברית"],
    },
    "ara": {
        "font": "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "lines": ["مرحبا بالعالم", "هذا مستند اختبار باللغة العربية", "اختبار التعرف على النصوص"],
        "tokens": ["مرحبا", "بالعالم", "مستند", "اختبار", "العربية"],
    },
}

for language, spec in SAMPLES.items():
    image = Image.new("RGB", (2480, 3508), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(spec["font"], 82)
    for index, line in enumerate(spec["lines"]):
        rtl = language != "eng"
        draw.text((2280 if rtl else 180, 350 + index * 240), line, font=font,
                  fill="black", anchor="ra" if rtl else "la",
                  direction="rtl" if rtl else "ltr", language=language)
    image.save(ROOT / f"scan-{language}.png", dpi=(300, 300))

pdf = canvas.Canvas(str(ROOT / "scanned-three-languages.pdf"), pagesize=A4)
pdf.setTitle("Synthetic multilingual OCR fixture")
for language in SAMPLES:
    pdf.drawImage(str(ROOT / f"scan-{language}.png"), 0, 0, width=A4[0], height=A4[1])
    pdf.showPage()
pdf.save()

(ROOT / "vector-sample.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
<rect width="210" height="297" fill="white"/>
<rect x="20" y="20" width="170" height="12" fill="#164e63"/>
<text x="20" y="55" font-family="Arial" font-size="9">Vector PDF export test</text>
<text x="20" y="70" font-family="Arial" font-size="5">Searchable text and scalable artwork</text>
<circle cx="65" cy="118" r="28" fill="#0e7490"/>
<path d="M115 90 L175 145 L115 145 Z" fill="#e7a53d"/>
<text x="20" y="180" font-family="Arial" font-size="5">Windows Inkscape verification</text>
</svg>''', encoding="utf-8")
(ROOT / "expected-ocr.json").write_text(json.dumps(SAMPLES, ensure_ascii=False, indent=2), encoding="utf-8")
print("Created three raster fixtures, one image-only PDF, one editable SVG, and expected OCR text.")
