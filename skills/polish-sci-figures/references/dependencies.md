# Environment & dependencies

Install once into the active Python environment:

```bash
pip install matplotlib numpy pandas Pillow pymupdf
# optional, when the source workflow is R-native: use R + ggplot2 instead
# optional, for DOCX/PPTX authoring:
pip install python-docx python-pptx
```

| Capability | Package | Used by |
|---|---|---|
| Plotting (default backend) | `matplotlib`, `numpy` | figure generation, `assets/sci_style.mplstyle`, `scripts/panel_labels.py` |
| Data handling | `pandas` | reading source data |
| Contact-sheet montage | `Pillow` | `scripts/make_montage.py` |
| Render DOCX/PPTX/PDF pages to PNG | `pymupdf` (`import fitz`) **or** Poppler `pdftoppm` | `scripts/render_doc_pages.py` |
| DOCX/PPTX -> PDF conversion | **LibreOffice** (`soffice` on PATH) | `scripts/render_doc_pages.py` (only for .docx/.pptx input) |
| SVG editability audit | stdlib only | `scripts/check_svg_editability.py` |
| SVG physical-canvas audit | stdlib only | `scripts/check_svg_canvas.py` |
| PDF rendered-text size audit | `pymupdf` | `scripts/audit_pdf_text.py` |

Notes
- **Fonts.** Prefer the proportional `Sarasa Gothic SC` family (更纱黑体),
  including regular, bold, italic, and bold italic faces. Keep it first so the
  default Chinese glyph forms are SC; do not substitute the Mono, Term, Fixed,
  UI, or Slab variants. Keep the complete declared text stack to five levels:
  `Sarasa Gothic SC`, `Noto Sans CJK SC`, `Microsoft YaHei`, `PingFang SC`,
  `DejaVu Sans`. Confirm the primary
  with `python -c "from matplotlib import font_manager as fm; print(fm.findfont('Sarasa Gothic SC', fallback_to_default=False))"`.
  A family or glyph fallback is allowed only within the declared stack and
  must be recorded; if the verified target requires one exact family, any
  fallback remains a release failure. Keep SVG recipients informed of the
  ordered live-text stack (with generic `sans-serif` only as the final CSS
  tail in hand-written SVG) and verify the fonts actually embedded in PDF.
  When Poppler is available, run `pdffonts figure.pdf` and require `emb=yes`
  and `sub=yes` for every declared text or explicit math-fallback face.
- **LibreOffice** is only needed to render Word/PowerPoint pages. If it is not
  installed, export the document to PDF manually and pass the PDF instead.
- **PDF renderer.** `render_doc_pages.py` prefers PyMuPDF and automatically
  falls back to Poppler's `pdftoppm` when PyMuPDF is unavailable. Install at
  least one of them; some managed runtimes already provide `pdftoppm` on PATH.
- **PDF text-size audit.** `audit_pdf_text.py` uses the publicly available
  PyMuPDF package to inspect effective text-span sizes, including reduced
  MathText scripts. With `--min-pt 5`, ordinary runs below the floor fail and
  reduced script-like runs warn; add `--strict-glyph-floor` only when a
  verified target applies the floor to every rendered glyph.
- Pin the same backend the project already uses; only default to
  Python/matplotlib when there is no existing plotting signal.
