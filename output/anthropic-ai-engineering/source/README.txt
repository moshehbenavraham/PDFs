HOW ANTHROPIC BUILDS WITH AI

Main presentation: how-anthropic-builds-with-ai.pdf
Format: 960 x 540 points, 16:9 landscape.
Running order: slides 1-18, paced for 20 minutes.
Slides 19-20 contain linked primary sources and evidence limits.
All presentation content is on the slides. No speaker notes are required.

EDITABLE SOURCES
build_deck.py contains the full text, layout, colors and PDF authoring code.
slide-plan.json records slide titles, source URLs and timing.
research.md preserves the supplied research without alteration.
image-prompts.json records the final prompts used with built-in imagegen.
The three project images are in ../assets/:
  workshop.png
  verification.png
  boundaries.png

REBUILD ON THIS WORKSPACE
Run from WSL Ubuntu:
/home/aiwithapex/.venvs/pdf/bin/python source/build_deck.py

The script requires ReportLab, PyMuPDF, and the IBM Plex Sans and Mono
TrueType fonts under /usr/share/fonts/truetype/ibm-plex/.
It recreates the PDF in the project directory and local review renders
under .build/. Fonts in the delivered PDF are embedded.

EVIDENCE
Quantitative claims retain their team, period and self-report scope.
The brief, task selection guide, scorecard and pilot are adaptations.
The supplied research and six primary sources informed the deck.
No claim of a universal Anthropic model or internal configuration is made.
