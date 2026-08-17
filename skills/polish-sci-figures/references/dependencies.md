# Environment & dependencies

Install once into the active Python environment:

```bash
pip install matplotlib numpy pandas Pillow
# optional but recommended for direct PDF rendering:
pip install pymupdf
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

Notes
- **Fonts.** Install the proportional `Sarasa Gothic SC` family (更纱黑体),
  including regular, bold, italic, and bold italic faces. Do not substitute the
  Mono, Term, Fixed, UI, or Slab variants. Confirm Matplotlib resolves it with
  `python -c "from matplotlib import font_manager as fm; print(fm.findfont('Sarasa Gothic SC', fallback_to_default=False))"`.
  If the verified target requires another family, declare that override once.
  Never allow a silent fallback. Keep SVG recipients informed of the required
  live-text font; verify that PDF export embeds the intended family.
- **LibreOffice** is only needed to render Word/PowerPoint pages. If it is not
  installed, export the document to PDF manually and pass the PDF instead.
- **PDF renderer.** `render_doc_pages.py` prefers PyMuPDF and automatically
  falls back to Poppler's `pdftoppm` when PyMuPDF is unavailable. Install at
  least one of them; some managed runtimes already provide `pdftoppm` on PATH.
- Pin the same backend the project already uses; only default to
  Python/matplotlib when there is no existing plotting signal.
