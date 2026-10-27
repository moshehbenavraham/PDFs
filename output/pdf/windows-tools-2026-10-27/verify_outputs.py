"""Check the saved smoke-test outputs; retain OCR limitations in the report."""
from pathlib import Path
import json
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
import numpy as np
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent
expected = json.loads((ROOT / "expected-ocr.json").read_text(encoding="utf-8"))

def normalized(text):
    return " ".join("".join(c for c in text if unicodedata.category(c) != "Cf").split())

results = {"date": "2026-10-27", "pdfs": [], "conformance": [], "ocr": []}
for path in sorted(ROOT.glob("*.pdf")):
    doc = fitz.open(path)
    qpdf = subprocess.run(["qpdf", "--check", str(path)], capture_output=True, text=True)
    fonts = subprocess.run(["pdffonts", str(path)], capture_output=True, text=True, check=True).stdout
    (ROOT / (path.stem + "-fonts.txt")).write_text(fonts, encoding="utf-8")
    (ROOT / (path.stem + "-structure.txt")).write_text(qpdf.stdout + qpdf.stderr, encoding="utf-8")
    text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
    (ROOT / (path.stem + "-text.txt")).write_text(text, encoding="utf-8")
    results["pdfs"].append({"file": path.name, "pages": len(doc),
        "page_sizes_pt": [[round(p.rect.width, 3), round(p.rect.height, 3)] for p in doc],
        "structure_exit": qpdf.returncode, "font_listing": path.stem + "-fonts.txt"})
    assert qpdf.returncode == 0, f"Structural failure: {path.name}"
    assert len(doc) == (3 if path.stem in {"scanned-three-languages", "naps2-multilingual", "naps2-multilingual-best", "wsl-ocr"} else 1)
    for page in doc:
        assert abs(page.rect.width - 595.276) < 1 and abs(page.rect.height - 841.89) < 1

for path in sorted(ROOT.glob("*-verapdf.xml")):
    root = ET.parse(path).getroot()
    report = next(e for e in root.iter() if e.tag.split("}")[-1] == "validationReport")
    compliant = report.attrib["isCompliant"] == "true"
    should_pass = not path.name.startswith("inkscape-export")
    results["conformance"].append({"report": path.name, "pdfa_2b": compliant,
                                   "expected": should_pass, "job_status": report.attrib["jobEndStatus"]})
    assert compliant == should_pass and report.attrib["jobEndStatus"] == "normal"

for name in ["naps2-eng-pdfa", "naps2-heb-pdfa", "naps2-ara-pdfa", "naps2-ara-best-pdfa", "naps2-multilingual", "naps2-multilingual-best", "wsl-ocr"]:
    if name == "wsl-ocr":
        texts = (ROOT / "wsl-ocr.txt").read_text(encoding="utf-8").split("\f")
    else:
        texts = [p.get_text() for p in fitz.open(ROOT / (name + ".pdf"))]
    languages = list(expected) if len(texts) == 3 else ["eng" if "-eng-" in name else "heb" if "-heb-" in name else "ara"]
    for lang, text in zip(languages, texts):
        missing = [line for line in expected[lang]["lines"] if normalized(line) not in normalized(text)]
        results["ocr"].append({"file": name, "language": lang, "missing_or_changed_lines": missing})
        if name in {"wsl-ocr", "naps2-eng-pdfa", "naps2-heb-pdfa"}:
            assert not missing, (name, lang, missing)

original = fitz.open(ROOT / "inkscape-export.pdf")
roundtrip = fitz.open(ROOT / "inkscape-roundtrip.pdf")
assert original[0].get_text() == roundtrip[0].get_text()
a = original[0].get_pixmap(alpha=False)
b = roundtrip[0].get_pixmap(alpha=False)
assert (a.width, a.height) == (b.width, b.height)
delta = np.abs(np.frombuffer(a.samples, dtype=np.uint8).astype(float) - np.frombuffer(b.samples, dtype=np.uint8).astype(float))
results["inkscape_roundtrip"] = {"text_preserved": True, "mean_absolute_pixel_delta_0_to_255": float(delta.mean())}
results["limits"] = ["NAPS2 omitted the middle Arabic line in both Fast and Best modes.",
    "The three-language Best-mode test also changed an English line.",
    "WSL OCRmyPDF sidecar matched all sample lines; RTL extraction order varies by PDF text extractor.",
    "Inkscape emitted a UTF16 import warning, but sample text and page geometry were preserved.",
    "WIA/TWAIN enumeration found no scanner; physical scanning and broad GUI workflows were not tested."]
(ROOT / "verification.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"structurally_valid_pdfs": len(results["pdfs"]), "validation_cases": len(results["conformance"]),
    "ocr_cases": len(results["ocr"]), "ocr_cases_with_changed_lines": sum(bool(x["missing_or_changed_lines"]) for x in results["ocr"]),
    "inkscape_roundtrip": results["inkscape_roundtrip"]}, indent=2))
