# PDFs

A document and presentation workspace with editable sources, artwork, exports, and PDF tooling notes.

## Projects

- [Is Anyone Home?](output/ai-consciousness/output/) — AI consciousness and sentience presentation, available as PowerPoint, PDF, and an offline HTML presentation, with a presenter guide.
- [Tomorrow Has Questions](output/pdf/tomorrow-has-questions.pdf) — presentation PDF, with [sources and artwork](output/moonshots-tomorrow/).
- [Windows PDF tools verification](output/pdf/windows-tools-2026-10-27/) — synthetic fixtures and results for Inkscape, NAPS2, veraPDF, and multilingual OCR.

## Working here

See [AGENTS.md](AGENTS.md) for the Windows/WSL tool inventory, commands, and verification requirements. Its paths describe the original workstation; adjust them for another machine.

New documents and presentations belong under `output/<project-name>/`, with each project's editable sources, assets, and final exports kept together. Existing projects retain their current export layout.

Environment files, build intermediates, Python caches, and OS metadata are excluded by `.gitignore`. Keep credentials out of sources, exports, and archives as well as out of Git.
