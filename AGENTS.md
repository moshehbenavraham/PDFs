# PDF workspace: local tools and operating guide

Ubuntu inventory verified **2026-10-13** on Ubuntu 24.04.4 LTS, x86-64, WSL2. Windows inventory refreshed **2026-10-27** below.
Project root: `/home/aiwithapex/projects/PDFs`. Git initialized on **2026-10-27**; earlier inventory checks predate repository creation.

## Working instructions

- Codex runs in the Windows desktop app with access to PowerShell, installed Windows applications/utilities, and WSL Ubuntu tools. Use either environment as appropriate; verify individual tool availability before use.
- From PowerShell, invoke Linux tools with `wsl.exe -d Ubuntu -- <command>`. The Windows path to this workspace is `\\wsl.localhost\Ubuntu\home\aiwithapex\projects\PDFs`; Windows drives are accessible in WSL under `/mnt/<drive>`.
- Use the installed tools below before introducing another dependency. This is a machine inventory, not a project dependency manifest.
- Keep original PDFs and editable sources; write modifications to a separate output file unless replacement was requested.
- Create new documents and presentations under `output/<project-name>/`, keeping each project's editable sources, assets and final exports together in that folder.
- Choose the explicit Python interpreter below. Bare `python` is a broken wrapper pointing to a deleted virtual environment in another project.
- Keep reports concise: outcome first, then verification or a concrete blocker. Do not add AI attribution or session links to artifacts.
- For repository work, resolve the Git root and absolute Git common directory, then consult `~/.codex/knowledge/index.md`; read only the note matching that confirmed root/common directory. No matching note existed when checked on 2026-10-27.
- `.env` is private, contains a credential, and is ignored by `.gitignore`. Do not print its values, copy them into documents, or include it in output bundles.
- Verify actual output: inspect page count and dimensions, extract text, check fonts, and render the changed pages. A successful command alone does not prove correct layout, reading order, accessibility, redaction, or archival conformance.

## Quick choice by task

| Task | Existing local route |
| --- | --- |
| Create precise pages, forms, invoices, tables, barcodes | ReportLab in the PDF Python environment |
| Edit pages, add text/images/annotations, redact, crop, render | PyMuPDF in the PDF environment; PDF-XChange Editor on Windows for manual editing |
| Merge, split, rotate, rearrange, stamp, fill forms, change metadata | `qpdf`, `pdftk`, `pypdf`, `pikepdf`, PyMuPDF |
| HTML/CSS to PDF | `weasyprint`; Playwright with the explicit cached Chromium path |
| Books, paged CSS, print layout | `vivliostyle`, `pagedjs-cli`, Typst, XeLaTeX/LuaLaTeX |
| Markdown to PDF | `pandoc` with `xelatex`, `lualatex`, `weasyprint`, or `typst` as appropriate to that Pandoc version |
| Word, spreadsheet, presentation to PDF | LibreOffice headless; `python-docx`, `python-pptx`, `openpyxl`, `xlsxwriter`, or JS `docx` to prepare sources |
| Raster images to PDF without unnecessary recompression | `img2pdf` |
| Searchable scanned PDFs | `ocrmypdf`, Tesseract; installed languages/data: **eng**, **heb**, **ara**, **osd**. Windows NAPS2 is also installed; see OCR qualification below. |
| Text, positions, tables, images, metadata extraction | `pdftotext`, `pdfimages`, `pdfinfo`, `pdfplumber`, `pdfminer.six`, PyMuPDF, `exiftool` |
| Layout-aware document conversion | Dedicated Docling environment; model availability must be checked separately |
| Render PDF pages and compare edits | `pdftoppm`, `pdftocairo`, `mutool draw`, PyMuPDF, PDFium; ImageMagick `compare` on rendered images |
| SVG, charts, diagrams, equations | CairoSVG, `rsvg-convert`, Matplotlib, Graphviz, Mermaid, TikZ/PGFPlots, KaTeX/MathJax |
| Font inspection/subsetting, RTL and multilingual layout | Fontconfig, FontTools, Noto/IBM Plex/Amiri fonts, HarfBuzz/FriBidi/Pango, XeLaTeX |
| PDF structure and embedded-font checks | `qpdf --check`, `pdfinfo`, `pdffonts`; these do not establish PDF/A, PDF/X, or PDF/UA compliance |

## Runtime locations and important distinctions

| Runtime/location | What is actually available |
| --- | --- |
| `/home/aiwithapex/.venvs/pdf/bin/python` | Preferred PDF interpreter: Python 3.12.3. Venv includes system site packages and sees user packages; its own packages override older system versions. |
| `/usr/bin/python3` | Python 3.12.3 with Ubuntu packages plus `~/.local/lib/python3.12/site-packages`. Does **not** have PyMuPDF, pypdf, pdfplumber, Matplotlib, CairoSVG, or svglib directly. |
| `/home/aiwithapex/.local/bin/python` | Broken wrapper to `/home/aiwithapex/projects/roaring-lion/backend/.venv/bin/python`. Do not use it. |
| `/home/aiwithapex/docling-env/.venv/bin/python` | Separate Docling/ML environment. Use its own `bin/docling` and interpreter. |
| `/home/aiwithapex/.local/share/uv/tools/nano-pdf/bin/python` | Isolated `nano-pdf` environment with additional PDF/OCR Python packages. |
| `/home/aiwithapex/.nvm/versions/node/v24.15.0/bin/node` | Active Node 24.15.0. Global packages live under the corresponding `lib/node_modules`. Other NVM versions exist; switching Node can change global package availability. |
| `/home/aiwithapex/.local/bin/pw-node` | Sets global `NODE_PATH` and runs Node; use for CommonJS scripts requiring global Playwright or `docx`. |
| `/home/aiwithapex/.local/bin/playwright-js` | JavaScript Playwright 1.59.1 wrapper. |
| `/home/aiwithapex/.local/bin/playwright` | **Python** Playwright 1.58.0 CLI, not the JavaScript installation. |
| `/usr/bin/java` | OpenJDK 21.0.12.1; supports installed PDFtk/PDFBox. `javac`, Maven, and Gradle were not on PATH. |
| Other build/runtime tools | `uv`, `uvx`, `pip3`, Poetry, `npm`, `npx`, `pnpm`, Bun, Ruby/Gem, Perl, PHP, Go, Rust/Cargo, GCC/G++, Make, CMake, `pkg-config`. These support scripts/builds, not additional PDF engines by themselves. |

Use explicit interpreter calls; activation is optional:

```bash
/home/aiwithapex/.venvs/pdf/bin/python your_pdf_script.py
/usr/bin/python3 your_office_script.py
pw-node your_browser_script.cjs
```

## PDF command-line tools

Unless otherwise shown, the following commands are in `/usr/bin`.

| Tool and installed version | Commands / capabilities |
| --- | --- |
| Poppler utilities 24.02.0 | `pdfinfo` metadata/page boxes; `pdftotext` text, layout and bounding boxes; `pdffonts` embedding/subsetting details; `pdfimages` extract/list raster images. |
| Poppler rendering/conversion | `pdftoppm` PNG/JPEG/PPM rendering; `pdftocairo` PNG/JPEG/TIFF/PDF/PS/EPS/SVG output as supported by its flags; `pdftohtml`; `pdftops`. |
| Poppler assembly/attachments/signatures | `pdfseparate`, `pdfunite`, `pdfattach`, `pdfdetach`, `pdfsig`. Signature inspection does not imply a signing certificate is configured. |
| qpdf 11.9.0 | `qpdf`: structural checks, object/JSON inspection, page assembly, rotation, linearization, stream/object rewriting, encryption/decryption. |
| MuPDF tools 1.23.10 | `mutool`: `draw`, `convert`, `clean`, `merge`, `extract`, `info`, `show`, and other subcommands listed by local help. The installed `mutool draw` reports **ICC support is not available**. |
| PDFtk Java 3.3.3 | `pdftk` (also `pdftk.pdftk-java`): concatenate/burst/rotate, background/stamp, FDF/XFDF forms, flattening, attachments, metadata, encryption. The command is `pdftk`, not `pdftk-java`. |
| Ghostscript 10.02.1 | `gs`, `ghostscript`: PDF/PostScript interpretation, rasterization, `pdfwrite` rewriting, downsampling and color/output-device processing. Rewriting may change interactive features and content. |
| Ghostscript wrappers | `ps2pdf`, `ps2pdf12`, `ps2pdf13`, `ps2pdf14`, `ps2pdfwr`, `pdf2ps`, `pdf2dsc`, `eps2eps`, `ps2epsi`, `dvipdf`. |
| ExifTool 12.76 | `exiftool`: inspect/write supported document and image metadata, including XMP. PDF metadata updates can retain previous revisions; do not use this as a redaction method. |
| PDFMiner CLI, system release 20221105 | `pdf2txt`, `dumppdf`; PDF environment also has newer `pdf2txt.py`, `dumppdf.py` from pdfminer.six 20260107. |
| img2pdf 0.5.1 | `img2pdf`: place compatible raster image streams into PDFs, set page size/layout and DPI. |
| OCRmyPDF 15.2.0+dfsg1 | `ocrmypdf`: searchable text layer, deskew/orientation options, OCR sidecar text, optimization and PDF/A output options. Basic OCR to ordinary PDF was tested. |
| Tesseract 5.3.4 / Leptonica 1.82.0 | `tesseract`: OCR to text, searchable PDF, hOCR, TSV and other supported configurations. Tessdata: `/usr/share/tesseract-ocr/5/tessdata/`; **eng**, **heb**, **ara**, **osd** installed (Hebrew/Arabic added 2026-10-27). |
| unpaper 7.0.0 | `unpaper`: scanned-page cleanup, deskewing and border/layout processing. |
| JBIG2 decoder 0.20 | `jbig2dec` decodes JBIG2; the `jbig2` encoder is **not installed**. |
| PDFium Python CLI | `~/.local/bin/pypdfium2` uses 5.5.0; `~/.venvs/pdf/bin/pypdfium2` uses 5.13.0. Run `--help` for render/extract/inspection operations. |
| PDF environment CLIs | `~/.venvs/pdf/bin/{pymupdf,pdfplumber,cairosvg,svg2pdf,markdown_py,pdf2txt.py,dumppdf.py}`. Not on the default PATH. |
| Apache PDFBox / FontBox 1.8.16 | `/usr/share/java/pdfbox.jar`, `/usr/share/java/fontbox.jar` (versioned jars also present). Legacy Java PDF operations; text extraction tested with the classpath shown below. |
| nano-pdf 0.2.1 | `~/.local/bin/nano-pdf`: natural-language page editing/addition through Gemini. CLI starts; uses `GEMINI_API_KEY` and a remote image model. API access was not exercised. It is not an offline structural editor. |

```bash
java -cp '/usr/share/java/*' org.apache.pdfbox.PDFBox ExtractText input.pdf output.txt
```

## Authoring, publishing, and office conversion

| Tool | Local version, route, and notes |
| --- | --- |
| Pandoc | `/usr/bin/pandoc` 3.1.3. Converts Markdown, HTML, DOCX, LaTeX and other supported source formats; PDF output needs an engine. `pandoc --list-input-formats`, `--list-output-formats`, and local help are authoritative for this installed release. |
| Typst | `~/.cargo/bin/typst` 0.15.0. `compile`, `watch`, `fonts`, structured typesetting, tables/math, PDF and supported image export. Basic PDF compilation tested. Remote package imports still require a cached package or network access. |
| Tectonic | `~/.cargo/bin/tectonic` 0.16.9. Self-contained TeX driver; executable/version verified. Its bundle was not found in the usual cache locations, so offline document compilation is not established. |
| TeX Live | Ubuntu TeX Live 2023. `pdflatex`, `xelatex`, `lualatex` each generated a PDF. Full inventory below. |
| WeasyPrint | `/usr/bin/weasyprint` 61.1. HTML/CSS paged documents, CSS print layout, links/bookmarks and supported font embedding. PDF creation tested. |
| wkhtmltopdf | `/usr/bin/wkhtmltopdf` and `wkhtmltoimage` 0.12.6. Older Qt WebKit renderer. Basic PDF conversion tested with `QT_QPA_PLATFORM=offscreen`; do not assume modern Chromium CSS/JS behavior or patched-Qt-only flags. |
| Vivliostyle CLI | Global `@vivliostyle/cli` 11.0.4; CLI reports viewer core 2.43.2, with `@vivliostyle/core` package 2.45.2 also present. CSS paged media, books, Markdown through VFM, crop marks/bleed, PDF output. Tested with `--executable-browser` below. |
| Paged.js | Global `pagedjs-cli` 0.4.3 with `pagedjs` 0.4.3. HTML/CSS pagination and PDF export. No `--version` option in this CLI; version comes from package metadata. Tested with `PUPPETEER_EXECUTABLE_PATH`. |
| Chromium/Playwright/Puppeteer | Modern HTML/CSS/JS rendering and browser PDF export. See the required executable override below. |
| LibreOffice 24.2.7.2 | `libreoffice`, `soffice`, `lowriter`, `localc`, `loimpress`; Writer, Calc, Impress, Draw, Math and Base installed. DOCX-to-PDF conversion tested. Draw can import PDFs for visual edits, with possible reconstruction/layout changes. |
| LibreOffice automation | `python3-uno`, Python/Java/JavaScript/BeanShell providers, UNO runtime and Java jars installed. `/usr/bin/python3` and the PDF interpreter both import `uno`. |
| LibreOffice report/import support | Report Builder; Firebird, HSQLDB, MySQL and PostgreSQL drivers; import libraries for AbiWord, CorelDRAW, FreeHand, Keynote, Publisher, PageMaker, Visio, WordPerfect and graphics. See native package appendix. |
| GNU troff / PostScript | `groff`, `troff`, `grops` from `groff-base` 1.23.0; PostScript output can feed `ps2pdf`. A complete groff macro/font installation is not implied. |
| Paper sizing | `paperconf` from `libpaper-utils`, plus page geometry controls in each authoring engine. |

### Browser PDF route that works on this machine

Cached Playwright Chromium revisions are **1228, 1234, 1243**, with matching headless-shell directories and FFmpeg 1011 under `~/.cache/ms-playwright`.
The global JavaScript Playwright default expects **1217**, which is missing. Global Puppeteer 25.3.0 also points to a missing Chrome cache. Neither default path should be assumed usable.

This existing binary launched successfully and generated a PDF:

```text
/home/aiwithapex/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome
Chromium 153.0.8010.12
```

Ubuntu also has a Chromium snap, 155.0.8059.39, reachable as `/snap/bin/chromium` and `/usr/bin/chromium-browser`. Its launch was not part of the PDF smoke test. No Firefox/WebKit bundle was present in the shared Playwright cache.

Example CommonJS script; run with `pw-node print.cjs`:

```javascript
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/home/aiwithapex/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',
  });
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(path.resolve('input.html')).href);
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: 'output.pdf', format: 'A4',
      printBackground: true, preferCSSPageSize: true });
  } finally {
    await browser.close();
  }
})();
```

For pages with asynchronous images/charts, wait for their application-specific readiness before printing.

```bash
vivliostyle build input.html \
  --executable-browser /home/aiwithapex/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome \
  -o output.pdf

PUPPETEER_EXECUTABLE_PATH=/home/aiwithapex/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome \
  pagedjs-cli input.html -o output.pdf
```

## Python libraries

Versions below are the effective imports, not just duplicate distribution metadata. **PDF** means `/home/aiwithapex/.venvs/pdf/bin/python`; **system** means `/usr/bin/python3` including its user site. Both can see many supporting libraries; the PDF venv adds/overrides the specialized packages.

| Package / import | PDF version | System version | Use |
| --- | --- | --- | --- |
| PyMuPDF / `pymupdf` | 1.28.2 | absent | Page editing, rendering, text/image extraction, annotations, redactions, links, widgets, page geometry. |
| `pypdf` | 6.19.0 | absent | Pure Python assembly, forms, metadata, outlines, page transformations and encryption support. |
| `pdfplumber` | 0.11.10 | absent | Text/word/line coordinates, table extraction and debugging. |
| `pdfminer.six` / `pdfminer` | 20260107 | 20221105 | Detailed text/layout analysis. |
| `pikepdf` | 8.7.1 | 8.7.1 | qpdf-backed PDF object/page/metadata editing and stream rewriting. |
| `pypdfium2` | 5.13.0 | 5.5.0 | PDFium rendering, text access and low-level bindings. |
| `reportlab` | 5.0.1 | 4.1.0 | PDF canvas, Platypus layout, tables, graphics, forms and barcode modules. |
| Pillow / `PIL` | 12.3.0 | 10.2.0 | Raster preprocessing, drawing, compositing, image formats and contact sheets. |
| `matplotlib` | 3.11.2 | absent | Vector PDF/SVG charts, raster charts and multipage `PdfPages`. |
| CairoSVG / `cairosvg` | 2.9.1 | absent | SVG to PDF, PNG and PostScript. |
| `svglib` | 2.2.0 | absent | SVG to ReportLab drawings/PDF. |
| `cairocffi` | 1.7.1 | absent | Cairo access through CFFI. |
| Pycairo / `cairo` | 1.25.1 | 1.25.1 | Vector drawing and PDF/SVG surfaces. |
| `rlPyCairo` | 0.3.0 | 0.3.0 | ReportLab raster graphics backend. |
| `weasyprint` | 61.1 | 61.1 | Programmatic HTML/CSS-to-PDF. |
| `pydyf` | 0.9.0 | 0.9.0 | Low-level PDF writer used by this WeasyPrint version. |
| `img2pdf` | 0.5.1 | 0.5.1 | Image-to-PDF assembly. |
| `ocrmypdf` | 15.2.0+dfsg1 | 15.2.0+dfsg1 | OCR pipeline; prefer the tested system CLI for its dependency combination. |
| `opencv-python` / `cv2` | 4.13.0.92 | 4.13.0.92 | Scan/image geometry, thresholding, deskew preprocessing, computer vision. |
| `rapidocr` | 3.7.0 | 3.7.0 | OCR package imports, but default ONNX runtime is missing. See caveat below. |
| `python-docx` / `docx` | 1.2.0 | 1.2.0 | Word source creation/editing before LibreOffice export. |
| `python-pptx` / `pptx` | 1.0.2 | 1.0.2 | Slide creation/editing before PDF export. |
| `openpyxl` | 3.1.5 | 3.1.5 | Excel workbook input/editing and print settings. |
| `xlsxwriter` | 3.2.9 | 3.2.9 | Spreadsheet source creation, tables/charts/print setup. |
| `fonttools` / `fontTools` | 4.61.1 | 4.61.1 | Font inspection, conversion, subsetting and merging. |
| `playwright` | 1.58.0 | 1.58.0 | Browser automation; explicit Chromium path avoids missing default cache. |
| Python-Markdown / `markdown` | 3.10.3 | absent | Markdown to HTML for PDF renderers. |
| `numpy`, `pandas`, `scipy` | 2.4.2 / 2.3.3 / 1.17.1 | same | Data preparation, numerical work and report tables. |
| `shapely`, `networkx` | 2.1.2 / 3.6.1 | same | Geometry and graph data for figures. |
| GDAL / `osgeo.gdal` | 3.8.4 | 3.8.4 | Geospatial raster/vector conversion; installed GDAL advertises read/write geospatial PDF. |
| `uno` | LibreOffice 24.2.7 bindings | same | LibreOffice automation. |

Additional installed support libraries, available through the PDF interpreter:

- HTML/XML/templates: `Jinja2` 3.1.2, `MarkupSafe` 2.1.5, `lxml` 6.0.2, `beautifulsoup4` 4.14.3, `soupsieve` 2.8.3, `html5lib` 1.1, `defusedxml` 0.7.1, `cssselect` 1.2.0, `cssselect2` 0.7.0, `tinycss2` 1.2.1, `webencodings` 0.5.1.
- Text/math/formatting: `markdown-it-py` 3.0.0, `marko` 2.2.2, `Pygments` 2.17.2, `pyphen` 0.14.0, `Babel` 2.10.3, `latex2mathml` 3.78.1, `pylatexenc` 2.10, `sympy` 1.14.0, `tabulate` 0.9.0, `rich` 13.7.1, `unicodedata2` 15.1.0, `semchunk` 2.2.2.
- Font/plot dependencies: `freetype-py` 2.4.0, `ufoLib2` 0.16.0, `contourpy` 1.4.0, `cycler` 0.12.1, `kiwisolver` 1.5.1; `brotli` 1.2.0 for compressed font/web assets.
- Geometry/data: `rtree` 1.4.1, `pyclipper` 1.4.0, `PyYAML` 6.0.1, `et_xmlfile` 2.0.0, `olefile` 0.46, `filetype` 1.2.0, `chardet` 5.2.0, `charset-normalizer` 3.4.4.
- Native bindings: `cffi` 1.16.0 and `PyGObject` 3.48.2; `cryptography` 41.0.7 and `pyOpenSSL` 23.2.0 support cryptographic building blocks but are not complete PDF signing workflows.

### Separate Python environments

- **Docling**: `/home/aiwithapex/docling-env/.venv/bin/docling`, `docling-tools`, `docling-view`. Installed: `docling` 2.76.0, `docling-core` 2.67.1, `docling-parse` 5.5.0, `docling-ibm-models` 3.11.0, `torch` 2.10.0+cu128, `torchvision` 0.25.0+cu128, `transformers` 4.57.6, `rapidocr` 3.7.0, `pypdfium2` 5.5.0, Pillow 12.0.0. Office/data dependencies also include python-docx 1.2.0, python-pptx 1.0.2, openpyxl 3.1.5, pandas 2.3.3 and OpenCV 4.13.0.92. CLI help runs. Full model inference/GPU execution was not tested; `onnxruntime` and `easyocr` are absent here.
- **nano-pdf**: `/home/aiwithapex/.local/share/uv/tools/nano-pdf/` contains `nano-pdf` 0.2.1, `pypdf` 6.6.2, `pdf2image` 1.17.0, `pytesseract` 0.3.13 and its own Pillow. Use this interpreter to import the latter two packages; they are not installed in the default/PDF environments.
- **RapidOCR models**: three local files exist under `~/.local/lib/python3.12/site-packages/rapidocr/models/`: `ch_PP-OCRv4_det_infer.onnx`, `ch_PP-OCRv4_rec_infer.onnx`, `ch_ppocr_mobile_v2.0_cls_infer.onnx`. Model files alone do not make the missing `onnxruntime` backend usable.
- Other projects contain duplicate Office/image/data libraries and Pillow versions. They are project-owned environments, not a reason to modify those projects or add their site-packages to this workspace's interpreter.

## JavaScript packages, including useful bundled dependencies

The active global package root is:

```text
/home/aiwithapex/.nvm/versions/node/v24.15.0/lib/node_modules
```

In this section **G** abbreviates that root. A dependency bundled inside another package is present on disk but is not automatically importable from this project. Use `createRequire` from its owning package, or later declare it in a project manifest if the project needs a stable dependency.

| Package/version | Location relative to G | Use/status |
| --- | --- | --- |
| `playwright`, `@playwright/test` 1.59.1 | top level | Browser PDF export, screenshots and checks; explicit Chromium path tested. |
| `puppeteer` 25.3.0 | top level | Browser rendering/printing; default browser cache missing. |
| `agent-browser` 0.25.3 | top level | Browser automation CLI, including its `pdf` command; separate session/browser setup applies. |
| `@vivliostyle/cli` 11.0.4 | top level | Book/print layout and PDF export. |
| `pagedjs-cli` 0.4.3 | top level | CSS paginated HTML to PDF. |
| `@mermaid-js/mermaid-cli` 11.17.0 | top level | `mmdc` exports diagrams to SVG, PNG or PDF. |
| `docx` 9.7.1 | top level | JS/TS Word authoring; export through LibreOffice. |
| `pdf-lib` 1.17.1 | `pagedjs-cli/node_modules/pdf-lib` (also bundled with Vivliostyle) | Create/modify PDFs, forms and page composition. Import and PDF creation tested. Includes `@pdf-lib/standard-fonts` 1.0.0 and `@pdf-lib/upng` 1.0.1. |
| `unpdf` 1.8.1 | `@kenkaiiii/ggcoder/node_modules/unpdf` | PDF extraction/rendering helpers; import tested. |
| MuPDF JS/WASM `@u1f992/mupdf` 1.27.0-patched.1 | `@vivliostyle/cli/node_modules/mupdf` | Bundled PDF processing engine; package presence verified. |
| `press-ready` 4.0.3 | `@vivliostyle/cli/node_modules/press-ready` | Print/preflight pipeline used by Vivliostyle. Presence verified; its complete press-ready workflow was not run. |
| `sharp` 0.34.5 | `wrangler/node_modules/sharp` | Fast raster processing and SVG rasterization; import tested. Bundled native `@img/sharp-*` / libvips assets. Additional copies include 0.35.5 under ggcoder. |
| `@napi-rs/canvas` 0.1.100 | `@mermaid-js/mermaid-cli/node_modules/@napi-rs/canvas` | Canvas drawing/render support; native import tested. Vivliostyle separately has 0.1.69. |
| `fontkit` 2.0.4 | `hyperframes/node_modules/fontkit` | Font parsing/layout; import tested. Also bundled with ggcoder. |
| `mermaid` 11.17.2 | `@mermaid-js/mermaid-cli/node_modules/mermaid` | Diagram grammar/renderer; CLI also bundles ELK, tidy-tree, ZenUML and parser support. |
| `d3` 7.9.0 | `@mermaid-js/mermaid-cli/node_modules/d3` | SVG/data visualizations before browser/PDF export. |
| `katex` 0.16.47 | `pagedjs-cli/node_modules/katex` | Mathematical HTML rendering; also bundled with Mermaid. |
| `mathjax` 3.2.2 | `pagedjs-cli/node_modules/mathjax` | Mathematical typesetting before printing. |
| `@vivliostyle/vfm` 2.7.0 | `@vivliostyle/cli/node_modules/@vivliostyle/vfm` | Markdown publishing, with remark/rehype/unified processing dependencies. |
| `handlebars` 4.7.9 | `@vivliostyle/cli/node_modules/handlebars` | HTML/document templates. |
| `marked` 15.0.12 | `@kenkaiiii/ggcoder/node_modules/marked` | Markdown-to-HTML source preparation. |
| `prismjs` 1.27.0 / `highlight.js` 10.7.3 | Vivliostyle / ggcoder `node_modules`, respectively | Code syntax highlighting in documents. |
| `postcss` 8.5.28 / `css-tree` 1.1.3 | `hyperframes/node_modules/postcss` / `pagedjs-cli/node_modules/css-tree` | Print stylesheet parsing/transformation. |
| `jszip` 3.10.2 / `adm-zip` 0.5.18 | `docx/node_modules/jszip` / `hyperframes/node_modules/adm-zip` | DOCX/PPTX/XLSX and asset archive manipulation. |

Other useful packages found **inside other projects**, not global dependencies:

- `qrcode` 1.5.4: `/home/aiwithapex/projects/hermes/node_modules/qrcode`.
- `chart.js` 4.5.1: `/home/aiwithapex/projects/durisweb/frontend/node_modules/.pnpm/chart.js@4.5.1/node_modules/chart.js`.
- `fontkitten` 1.0.3: `/home/aiwithapex/projects/factionos/node_modules/fontkitten`.
- `opentype.js` 0.8.0/2.0.0 also exists in editor/server dependency trees; those private paths are fragile.
- Other projects/caches contain newer Playwright versions through 1.64.0, a prerelease, and newer Puppeteer/Mermaid copies. Their presence does not change the active global versions or supply matching browsers automatically.

Example for the existing nested `pdf-lib` installation:

```javascript
const { createRequire } = require('node:module');
const fromPaged = createRequire(
  '/home/aiwithapex/.nvm/versions/node/v24.15.0/lib/node_modules/pagedjs-cli/package.json'
);
const { PDFDocument } = fromPaged('pdf-lib');
```

## Images, diagrams, figures, and related utilities

| Tool | Installed capability |
| --- | --- |
| ImageMagick 6.9.12-98 Q16 | `convert`, `identify`, `compare`, `montage`, `mogrify`, `composite`. Version 6 uses `convert`; `magick` is absent. PDF rasterization worked under the current policy. Prefer vector-preserving PDF tools for structural edits. |
| ImageMagick delegates | Installed delegate build includes Cairo/Pango, Fontconfig/FreeType, JPEG, PNG, TIFF, WebP, HEIC, JPEG 2000, OpenEXR, DjVu, WMF and others. Delegate support is not a separate editor installation. Policy: `/etc/ImageMagick-6/policy.xml`. |
| librsvg 2.58.0 | `rsvg-convert`: SVG to PDF/PNG/PS/EPS; PDF conversion tested. |
| Graphviz | `dot` reports 2.43.0; Ubuntu package is 2.42.2-9ubuntu0.1. `dot`, `neato`, `fdp`, `sfdp`, `circo`, `twopi`; PDF/SVG diagrams. PDF output tested. |
| Mermaid CLI | `mmdc` 11.17.0; PDF export tested with a Puppeteer configuration specifying the cached Chromium executable. |
| VTracer | `~/.cargo/bin/vtracer` 0.6.5; bitmap tracing to SVG. |
| Netpbm 11.05.02 | Broad raster converters/filters: `pnmcrop`, `pnmscale`, `pnmrotate`, `pnmcut`, `pnmcat`, `pnmtopng`, `pngtopnm`, `jpegtopnm`, `pnmtojpeg`, `tifftopnm`, `pnmtotiff`, `pnmtops`, `pstopnm`, `pbmtext`, `pbmtextps`, `pamtosvg`, `svgtopam`, and package-provided related commands. |
| PNG tools | `pngquant` 2.18.0, `optipng` 0.7.8, `pngfix`, `png-fix-itxt`. PNG quantization/optimization/repair. |
| JPEG optimization | `jpegoptim` 1.4.7. `jpegtran`, `cjpeg`, and `djpeg` were not found. |
| WebP tools 1.3.2 | `cwebp`, `dwebp`, `webpmux`, `img2webp`, `webpinfo` for image assets. |
| FFmpeg 8.1.1 | `/usr/local/bin/ffmpeg`, `ffprobe`, installed under `/opt/ffmpeg-8.1.1`. Extract video frames, rescale/convert assets, create contact sheets. Ubuntu `/usr/bin/ffmpeg` is a separate 6.1.1 installation. |
| GDAL 3.8.4 | `gdalinfo`, `gdal_translate`, `ogr2ogr`; geospatial PDF input/output driver present. |
| Display helpers | `xvfb-run`, WSLg display integration, `xdg-open`, `wslpath`; useful for applications requiring a display or Windows paths. |
| Generic document pipeline tools | `rg`, `jq`, `file`, `iconv`, `uconv`, `dos2unix`, `curl`, `wget`, `zip`, `unzip`, `tar`, compression utilities, checksums and `diff`. Python's standard library covers CSV/JSON/XML/SQLite/ZIP/subprocess workflows. |

## TeX, layout packages, and helper programs

Installed TeX collections (Debian/Ubuntu package names):

```text
tex-common
texlive-base                 texlive-binaries
texlive-latex-base           texlive-latex-recommended
texlive-latex-extra          texlive-pictures
texlive-xetex                texlive-luatex
texlive-plain-generic        texlive-lang-arabic
texlive-lang-other           texlive-fonts-recommended
texlive-fonts-extra          texlive-fonts-extra-links
tex-gyre                    lmodern
cm-super                    cm-super-minimal
dvisvgm
```

These collections contain many individual `.sty`, `.cls`, font and language files. Installed files, not online TeX package catalogs, determine availability. `kpsewhich` confirmed all packages/classes in this table:

| Purpose | Installed packages/classes |
| --- | --- |
| Unicode, fonts, RTL/languages | `fontspec`, `polyglossia`, `bidi`, `babel`, `newunicodechar`, `unicode-math` |
| Page size, headers, positioned overlays | `geometry`, `fancyhdr`, `eso-pic`, `background`, `textpos`, `crop` |
| PDF inclusion, links, bookmarks | `pdfpages`, `graphicx`, `hyperref`, `bookmark` |
| Tables | `booktabs`, `longtable`, `tabularx`, `xltabular` |
| Diagrams/charts/color/boxes | `tikz`, `pgfplots`, `xcolor`, `tcolorbox` |
| Math, typography, code | `amsmath`, `microtype`, `listings`, `minted` |
| Other document features | `glossaries`, `qrcode`, `pdfx`, `tagpdf`, `environ` |
| Document classes | `article`, `beamer`, `memoir`, KOMA-Script `scrartcl` |

Additional installed commands include `tex`, `latex`, `pdftex`, `xetex`, `luatex`, `luahbtex`, `dvilualatex`, `etex`, `eptex`, `euptex`, `ptex`, `uptex`, `optex`, `bibtex`, `bibtex8`, `bibtexu`, `makeindex`, `makeglossaries`, `kpsewhich`, `texdoc`, `tlmgr`, `mktexlsr`, `dvips`, `dvipdfm`, `dvipdfmx`, `xdvipdfmx`, `dvisvgm`, `mptopdf`, `epspdf`, `epspdftk`, `pdftosrc`, `pdfannotextractor`, `pdfatfi`, `pdfopen`, `pdfclose`, `thumbpdf`, `pn2pdf`, `tpic2pdftex`, `tikztosvg`, `htlatex`, `htxelatex`, `detex`, `latex-wordcount`, `fig4latex`, `simpdftex`, and `xhlatex`. Some helpers require their own input conventions or external components; binary presence is not an end-to-end test.

Not found: `latexmk`, `biber`, `pdfcrop`, `pdfjam`, `pdfbook2`, `pdfnup`, `biblatex.sty`, `xeCJK.sty`, `luatexja.sty`. Installed CJK fonts do not supply these missing TeX language packages. `minted` is present and `pygmentize` is available; its execution requirements still depend on the document/TeX configuration.

## Fonts, shaping, and color resources

Fontconfig sees **3,249 distinct font-file paths** and **2,398 distinct family/style label lines**. These are not counts of unique font families. Default font lookup is through Fontconfig; Windows font files are separately available in `/mnt/c/Windows/Fonts` and are not automatically included in that count.

- Main font trees: `/usr/share/fonts`, `/usr/share/texmf/fonts`, `/usr/share/texlive/texmf-dist/fonts`; use `fc-match` or `kpsewhich` for a specific file.
- Common document families include Inter/Inter Display, IBM Plex, DejaVu, Liberation, Noto, Roboto, Open Sans, Lato, Carlito, Caladea, EB Garamond, Linux Libertine/Biolinum, Latin Modern, TeX Gyre, FreeFont and URW Base35.
- Hebrew/Arabic options include Noto Hebrew/Arabic families, IBM Plex Sans Hebrew/Arabic, Amiri and Amiri Quran. CJK options include Noto CJK, IPA, AR PL, Nanum and WenQuanYi. Fonts and OCR language data are separate resources.
- Mathematical/symbol choices include STIX, STIX Math, Asana Math, Latin Modern Math, TeX Gyre math families, Symbola, OpenSymbol and Font Awesome. Color emoji is present through Noto Color Emoji; test the chosen PDF renderer's output.
- Tools: `fc-list`, `fc-match`, `fc-scan`, `fc-cache`; `fonttools`, `ttx`, `pyftsubset`, `pyftmerge` in `~/.local/bin`.
- Rendering/shaping libraries: FreeType 2.13.2, Fontconfig 2.15.0, HarfBuzz 8.3.0 (including subset/Cairo/ICU support), FriBidi 1.0.13, Pango 1.52.1, Graphite2 1.3.14, ICU 74.2, Cairo 1.18.0, Pixman 0.42.2 and Little CMS 2.14.
- ICC profiles: `/usr/share/color/icc/` contains sRGB, compatibleWithAdobeRGB1998, Gray, Gray-CIE_L, LStar-RGB, ITULab and Cineon/CineLog profiles. `/usr/share/color/icc/ghostscript/` contains default RGB/CMYK/Gray, sRGB, Adobe RGB-compatible, Lab and other Ghostscript profiles.
- Hyphenation/spelling resources: `hunspell-en-us`, `hyphen-en-us`, Python Pyphen/Babel, and installed TeX language collections.

All installed `fonts-*` packages at inventory time (metapackages and alternate-format subpackages included):

```text
fonts-adf-accanthis                  fonts-adf-berenis
fonts-adf-gillius                    fonts-adf-universalis
fonts-arphic-ukai                    fonts-arphic-uming
fonts-cabin                          fonts-cantarell
fonts-clear-sans                     fonts-comfortaa
fonts-comic-neue                     fonts-croscore
fonts-crosextra-caladea              fonts-crosextra-carlito
fonts-dejavu                         fonts-dejavu-core
fonts-dejavu-extra                   fonts-dejavu-mono
fonts-droid-fallback                 fonts-ebgaramond-extra
fonts-firacode                       fonts-font-awesome
fonts-freefont-otf                   fonts-freefont-ttf
fonts-gfs-artemisia                  fonts-gfs-complutum
fonts-gfs-didot                      fonts-gfs-neohellenic
fonts-gfs-olga                       fonts-gfs-solomos
fonts-go                             fonts-hosny-amiri
fonts-ibm-plex                       fonts-inter
fonts-ipafont-gothic                 fonts-ipafont-mincho
fonts-lato                           fonts-liberation
fonts-liberation-sans-narrow         fonts-liberation2
fonts-linuxlibertine                 fonts-lmodern
fonts-lobster                        fonts-lobstertwo
fonts-nanum                          fonts-noto
fonts-noto-cjk                       fonts-noto-cjk-extra
fonts-noto-color-emoji               fonts-noto-core
fonts-noto-extra                     fonts-noto-mono
fonts-noto-ui-core                   fonts-noto-ui-extra
fonts-noto-unhinted                  fonts-oflb-asana-math
fonts-open-sans                      fonts-opensymbol
fonts-paratype                       fonts-roboto-slab
fonts-roboto-unhinted                fonts-sil-andika
fonts-sil-charis                     fonts-sil-gentium
fonts-sil-gentium-basic              fonts-sil-gentiumplus
fonts-sil-gentiumplus-compact        fonts-sil-padauk
fonts-stix                           fonts-symbola
fonts-texgyre                        fonts-texgyre-math
fonts-tlwg-garuda                    fonts-tlwg-garuda-otf
fonts-tlwg-kinnari                   fonts-tlwg-kinnari-otf
fonts-tlwg-laksaman                  fonts-tlwg-laksaman-otf
fonts-tlwg-loma                      fonts-tlwg-loma-otf
fonts-tlwg-mono                      fonts-tlwg-mono-otf
fonts-tlwg-norasi                    fonts-tlwg-norasi-otf
fonts-tlwg-purisa                    fonts-tlwg-purisa-otf
fonts-tlwg-sawasdee                  fonts-tlwg-sawasdee-otf
fonts-tlwg-typewriter                fonts-tlwg-typewriter-otf
fonts-tlwg-typist                    fonts-tlwg-typist-otf
fonts-tlwg-typo                      fonts-tlwg-typo-otf
fonts-tlwg-umpush                    fonts-tlwg-umpush-otf
fonts-tlwg-waree                     fonts-tlwg-waree-otf
fonts-ubuntu                         fonts-unifont
fonts-urw-base35                     fonts-wqy-zenhei
```

Inspect precise family/style/file support before selecting a font:

```bash
fc-match 'Inter'
fc-match 'Noto Sans Hebrew'
fc-list : family style file
kpsewhich fontspec.sty
```

## Native library and format support

These installed libraries back the command-line and Python tools; a shared library alone does not imply its corresponding standalone application is installed.

| Area | Installed package families / resources |
| --- | --- |
| PDF/PostScript | `libpoppler134`, `poppler-data`, `libqpdf29t64`, `libgs10`, `libgs10-common`, `libgs-common`, `libpdfbox-java`; MuPDF command-line tools; PDFium native library bundled with pypdfium2. |
| Graphics/layout | `libcairo2`, `libcairo-gobject2`, `libcairo-script-interpreter2`, `libpango-1.0-0`, `libpangocairo-1.0-0`, `libpangoft2-1.0-0`, `libpixman-1-0`, `librsvg2-2`, `libgd3`, ImageMagick libraries, Graphviz libraries. |
| Fonts/text/color | `libfreetype6`, `libfontconfig1`, `libharfbuzz0b`, `libharfbuzz-subset0`, `libharfbuzz-cairo0`, `libharfbuzz-icu0`, `libharfbuzz-gobject0`, `libfribidi0`, `libgraphite2-3`, `libicu74`, `liblcms2-2`, `libeot0`, `liblangtag1`. HarfBuzz and FriBidi development packages also installed. |
| Raster codecs | `libpng16-16t64`, `libjpeg-turbo8`, `libtiff6`, `libtiffxx6`, `libwebp7`, `libwebpdecoder3`, `libwebpdemux2`, `libwebpmux3`, `libopenjp2-7`, `libjbig0`, `libjbig2dec0`, `libnetpbm11t64`; PNG/JPEG/TIFF/WebP/JBIG development packages installed. |
| OCR and barcode primitives | `libtesseract5`, Leptonica (`liblept5`), `libqrencode4`, `libzbar0t64`; `qrencode` and `zbarimg` command-line programs are absent. |
| Vector tracing/metafiles | `libpotrace0`, `libwmflite-0.2-7`; no `potrace` executable was found. |
| Office import/export | `libabw-0.1-1`, `libcdr-0.1-1`, `libetonyek-0.1-1`, `libfreehand-0.1-1`, `libmspub-0.1-1`, `libpagemaker-0.0-0`, `libvisio-0.1-1`, `libwpd-0.10-10`, `libwpg-0.3-3`, `librevenge-0.0-0`, `libodfgen-0.1-1`, `libepubgen-0.1-1`. |
| UNO/report generation | `liblibreoffice-java`, `libunoloader-java`, `libuno-cppu3t64`, `libuno-cppuhelpergcc3-3t64`, `libuno-purpenvhelpergcc3-3t64`, `libuno-sal3t64`, `libuno-salhelpergcc3-3t64`, `uno-libs-private`, `ure`, `ure-java`; LibreOffice report-builder packages. |
| Printing/paper | `libcups2t64`, CUPS snap 2.4.19, `libpaper1`, `libpaper-utils`. WSL/CUPS printer configuration was not verified; Windows PDF queues are listed below. |
| Java crypto | Bouncy Castle `/usr/share/java/bcprov.jar` (1.77), alongside legacy PDFBox/FontBox. This is not a configured PDF signing service. |

## Windows tools available alongside WSL

Verified **2026-10-27** through registry/file versions, printer enumeration, Python imports and CLI version checks. GUI apps, Office exports, licensing and scanner operation were not exercised. Checks covered standard application folders, `D:\Apps`, user Programs, app registrations and the Codex runtime; arbitrary portable locations were not exhaustively searched.

- **PDF-XChange Editor 10.7.5.403**: `C:\Program Files\Tracker Software\PDF Editor\PDFXEdit.exe`; PDF editing, annotation and inspection, subject to enabled features.
- **Microsoft Office 16.0.20527.20088**: `C:\Program Files\Microsoft Office\root\Office16\{WINWORD,EXCEL,POWERPNT}.EXE`; native Office authoring/PDF export routes, with COM registrations confirmed for PowerShell automation. `MSPUB.EXE` is also present; usability untested.
- **PDF printer queues**: `Microsoft Print to PDF` and `PDF-XChange Lite` are installed; print output was not tested.
- **PDF viewers/browser printing**: Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`), Edge (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`) and Brave (`C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`).
- **Raster/capture tools**: Paint.NET 5.1.12 (`D:\Apps\paint.net\paintdotnet.exe`), Microsoft Paint and Snipping Tool.
- **Native Python 3.12.14**: `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Imports verified: ReportLab 4.4.9, pypdf 6.10.0, pdfplumber 0.11.9, pypdfium2 5.14.0, Pillow, python-docx, python-pptx, openpyxl and XlsxWriter. Bare Windows `python` resolves to a WindowsApps alias; use the explicit interpreter.
- **Native Poppler 26.07.0**: `pdfinfo` and `pdftoppm` run from the Codex runtime's `dependencies\native\poppler\Library\bin`; only these two Poppler executables are bundled here. Use WSL for `pdftotext`, `pdffonts`, qpdf, Ghostscript and Tesseract, which were not found on Windows PATH.
- **Windows automation/OCR**: PowerShell 7.6.5, Windows PowerShell, `wsl.exe` and `winget` are available. The separate Windows OCR API enumerates only `en-US`; NAPS2 and WSL Tesseract now have English, Hebrew and Arabic data.

Rediscover app-managed runtime paths with `load_workspace_dependencies` after updates. Use PowerShell's `& 'C:\path with spaces\tool.exe'` invocation syntax; from WSL, convert filenames with `wslpath -w` and access Windows drives via `/mnt/c`, `/mnt/d`, etc.

### Installed Windows PDF additions (2026-10-27)

Per-user installation root: `C:\Users\apexw\AppData\Local\Programs\PDFTools` (`$env:LOCALAPPDATA\Programs\PDFTools`). Paths below are relative to this root. Start menu shortcuts are under **PDF Tools**. NAPS2 and Inkscape use official portable distributions; veraPDF uses its official installer.

- **[veraPDF 1.30.3](https://verapdf.org/)**: `bin\verapdf.cmd` launches the CLI with private **Temurin JRE 21.0.12.1+1** from `Java\jdk-21.0.12.1+1-jre`; GUI: Start menu **veraPDF**. Validates PDF/A and machine-checkable PDF/UA requirements; human accessibility checks remain necessary. The vendor's `veraPDF\verapdf.bat` requires Java environment setup; prefer the supplied `bin\verapdf.cmd` launcher.
- **[NAPS2 8.6.0](https://www.naps2.com/)**: GUI `NAPS2\NAPS2.Portable.exe`; CLI `NAPS2\App\NAPS2.Console.exe` (also `bin\naps2-console.cmd`). English/Hebrew/Arabic **Fast and Best** models are in `NAPS2\Data\components\tesseract4\{fast,best}\{eng,heb,ara}.traineddata`. Default OCR mode remains Fast; use explicit `--ocrlang` and `-n 0` for existing files.
- **[Inkscape 1.4.4](https://inkscape.org/)**: GUI `inkscape\bin\inkscape.exe`; synchronous CLI `inkscape\bin\inkscape.com` (also `bin\inkscape.cmd`). PDF import uses `--pages=1` in this version, not the older `--pdf-page` option. Keep editable SVG sources.
- **WSL OCR data**: Ubuntu packages `tesseract-ocr-heb` and `tesseract-ocr-ara` installed alongside English; `/usr/share/tesseract-ocr/5/tessdata/{heb,ara}.traineddata`. OCRmyPDF accepts `-l eng+heb+ara`.

`PDFTools\bin` was appended to the **user PATH**; restart the shell/app to pick it up, or use the explicit paths below. Use absolute input/output filenames: CMD launchers can reset a UNC working directory. Installation sources, hashes and the verified veraPDF signing-key fingerprint are recorded in `output/pdf/windows-tools-2026-10-27/installation.json`.

```powershell
$pdfTools = Join-Path $env:LOCALAPPDATA 'Programs\PDFTools'
& "$pdfTools\bin\verapdf.cmd" --flavour 2b --format text 'C:\work\document.pdf'
& "$pdfTools\NAPS2\App\NAPS2.Console.exe" -i 'C:\work\scan.pdf' -o 'C:\work\searchable.pdf' -n 0 --ocrlang 'eng+heb+ara' --pdfcompat A2-b
& "$pdfTools\inkscape\bin\inkscape.com" 'C:\work\figure.svg' '--export-filename=C:\work\figure.pdf'
& "$pdfTools\inkscape\bin\inkscape.com" 'C:\work\document.pdf' --pages=1 '--export-filename=C:\work\page1.svg'
```

WSL multilingual alternative (run inside Ubuntu, or prefix with `wsl.exe -d Ubuntu --` and use absolute Linux paths):

```bash
ocrmypdf -l eng+heb+ara --output-type pdf --optimize 0 --sidecar recognized.txt scanned.pdf searchable.pdf
```

**Qualification:** CLI launches, SVG-to-PDF and PDF-to-SVG round trip, native Poppler rendering, page counts/A4 geometry, extracted text, embedded fonts and PDF structure were checked. veraPDF accepted five PDF/A-2b samples and rejected an ordinary PDF. Inkscape emitted a UTF16 import warning but preserved sample text and appearance. NAPS2 recognized the English/Hebrew samples but omitted an Arabic line in both modes; combined Best-mode OCR also changed English words. Prefer the WSL OCRmyPDF route for Arabic pending document-specific checks: its sidecar matched every English/Hebrew/Arabic sample line. RTL extraction order varies by reader. WIA/TWAIN enumeration returned no scanners; physical scanning and broad GUI workflows remain untested. Fixtures, renders and detailed results: `output/pdf/windows-tools-2026-10-27/verification.json`.

## Local skills and reusable assets

Read the relevant skill before applying its workflow. These resources are local; API-backed image generation still requires the service rather than being offline software.

- `/home/aiwithapex/.codex/skills/playwright-local/SKILL.md`: machine-specific JavaScript/Python Playwright routing and wrappers. Revalidate its runtime facts against the cache mismatch documented above.
- `/home/aiwithapex/.codex/skills/create-docx/SKILL.md`: Word document authoring and PDF-ready layout. `scripts/setup_docx_env.sh` is an **installer**, not an inventory checker; it can install docxtpl, mammoth, Markdown, pypandoc and docxcompose. Their appearance in that script does not mean they are currently installed.
- `/home/aiwithapex/.codex/skills/diagram-design/SKILL.md`: HTML/SVG diagrams and exports; local `assets/` contains templates and examples. `scripts/drawio_extract.py`, `mermaid_extract.py`, and `self_check.py` support source extraction/checking.
- `/home/aiwithapex/.codex/skills/imagegen/SKILL.md`: generating/editing raster assets for documents. Local helper scripts include `image_gen.py` and `remove_chroma_key.py`; generation is service-backed.
- `/home/aiwithapex/.codex/skills/agent-browser/SKILL.md`: browser automation workflow for the installed CLI.

## Useful command recipes

Run these against copies and choose output names appropriate to the task. They are templates, not commands to execute automatically when reading this file.

```bash
# Inspect structure, text, fonts and page geometry.
pdfinfo input.pdf
pdffonts input.pdf
qpdf --check input.pdf
pdftotext -layout input.pdf output.txt
pdfimages -list input.pdf

# Render the first page for inspection; omit -f/-l to render all pages.
pdftoppm -f 1 -l 1 -r 150 -png input.pdf page

# Assemble/reorder PDFs and extract a page range.
qpdf --empty --pages first.pdf second.pdf -- merged.pdf
qpdf input.pdf --pages . 2-4 -- selected.pdf
pdftk input.pdf cat 1-3 output selected-pdftk.pdf

# Images, HTML and Markdown to PDF.
img2pdf image1.jpg image2.png -o images.pdf
weasyprint input.html output.pdf
pandoc input.md --pdf-engine=xelatex -o output.pdf
typst compile input.typ output.pdf

# OCR with the installed English data; ordinary PDF output, no optimization.
ocrmypdf -l eng --output-type pdf --optimize 0 \
  --sidecar recognized.txt scanned.pdf searchable.pdf

# Office conversion with an isolated temporary LibreOffice profile.
lo_profile=$(mktemp -d /tmp/pdf-lo-profile.XXXXXX)
libreoffice "-env:UserInstallation=file://$lo_profile" \
  --headless --convert-to pdf --outdir output input.docx

# Vector figure export.
rsvg-convert -f pdf -o figure.pdf figure.svg
dot -Tpdf diagram.dot -o diagram.pdf

# Validate embedded fonts and render again after any structural edit.
qpdf --check output.pdf
pdffonts output.pdf
```

For Mermaid, supply a Puppeteer JSON file with `executablePath` set to the cached Chromium path, then use `mmdc -p puppeteer.json -i diagram.mmd -o diagram.pdf`. A test used `args: ["--no-sandbox"]` for Mermaid/Paged.js; only use that flag when the runtime requires it and inputs are trusted.

## Known gaps and boundaries

- Not found as Linux commands: `pdfcpu`, `cpdf`, `prince`, `quarto`, `pandoc-crossref`, `inkscape`, `gimp`, `krita`, `scribus`, `blender`, `drawio`, `plantuml`, `d2`, `asy`, `gnuplot`, R, Octave, `unoconv`, `unoserver`, `abiword`, `gnumeric`, `fontforge`, `hb-shape`, `hb-view`, `otfinfo`, `potrace`, `autotrace`, `qrencode`, `zbarimg`, `tiff2pdf`, `tiffinfo`, `tiffcp`, `oxipng`, `jbig2`, `jbig2enc`, `verapdf`, `jhove`, `diff-pdf`, `diffpdf`, `pdfarranger`, `pdfshuffler`, `evince`, `okular`, `atril`, `xpdf`, `zathura`.
- Windows veraPDF is installed for PDF/A and machine-checkable PDF/UA validation; see its launcher above. Engines offering archival/tagging modes still need document-specific validation. `qpdf --check` checks structure, not conformance or visual correctness.
- No installed default/PDF-environment packages were found for Camelot, tabula-py, fpdf2, borb, pdfrw, pyHanko, endesive, EasyOCR, ONNX Runtime, Plotly, Kaleido, Seaborn, python-bidi, arabic-reshaper, Python qrcode, svgwrite, drawsvg, or rst2pdf. Some needs are already covered by the alternative libraries above.
- No installed Node packages named `pdfkit`, `pdfmake`, `jspdf`, `@react-pdf/renderer`, or `html2pdf.js` were found in the scanned local package trees. `pdf-lib` and `unpdf` are available as nested dependencies.
- No Adobe Acrobat/Reader executable was found in the examined standard Adobe installation folders; an Adobe directory alone does not establish Acrobat availability.
- WSL Tesseract and Windows NAPS2 have English/Hebrew/Arabic OCR data; other languages need separate installation. Observe the NAPS2 Arabic accuracy limitation documented above. RapidOCR's ONNX files do not replace Tesseract language packs.
- Visual masking is not redaction. When removal is requested, use actual redaction/content removal and verify extraction, images, annotations, attachments and saved revisions as relevant.

## Inventory evidence and refresh

Evidence came from command resolution/version/help output, installed `dpkg` records, Python metadata **and imports**, global and nested Node manifests, 25 discovered Python environment configurations, Fontconfig, `kpsewhich`, browser cache inspection, and Windows executable paths. The accessible home tree, `/usr/local`, `/opt`, system packages and standard Windows application folders were checked. Unreadable container/database data directories were excluded; arbitrary container filesystems, deleted installations, remote services and every possible Windows portable-app location are not claimed as inventoried.

Representative runtime checks succeeded for ReportLab, PyMuPDF editing/rendering, pypdf, pikepdf, pdfplumber text extraction, PDFium rendering, CairoSVG, svglib, Matplotlib PDF export, python-docx creation, LibreOffice conversion, WeasyPrint, wkhtmltopdf, pdfLaTeX/XeLaTeX/LuaLaTeX, Typst, Graphviz, Mermaid, Paged.js, Vivliostyle, explicit-path Chromium printing, img2pdf, qpdf, PDFtk, Ghostscript, Poppler, MuPDF, rsvg-convert, PDFBox extraction, ImageMagick PDF rasterization and pdf-lib creation. OCRmyPDF produced a searchable PDF and recognized the synthetic input text. Broader specialized features are available by local package/tool evidence, not individually certified by those smoke tests.

Useful refresh commands (read-only; do not expose `.env`):

```bash
command -v qpdf mutool pdftk pandoc typst tectonic weasyprint ocrmypdf
dpkg-query -W -f='${db:Status-Abbrev}\t${binary:Package}\t${Version}\n'
/home/aiwithapex/.venvs/pdf/bin/python -m pip list
/usr/bin/python3 -m pip list
uv tool list
npm root -g
npm list -g --depth=0
fc-list : family style file
tesseract --list-langs
kpsewhich pdfpages.sty
dpkg -L texlive-latex-extra
dpkg -L netpbm
```

Use `dpkg -L PACKAGE` for every file/command in a bundled system package and `kpsewhich NAME.sty` for individual TeX packages. Recheck the active Node/Python executable and actual import path after upgrades; duplicate installed metadata can report versions that are shadowed at runtime.
