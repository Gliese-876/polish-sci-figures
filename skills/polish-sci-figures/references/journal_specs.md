# Journal-specific figure requirements

Do not treat a static table as an authority. Journal figure rules change and
may differ by article type. For a submission, retrieve the current official
author instructions and manuscript template before setting width, height,
font, resolution, file format, color mode, or panel-label convention.

Record the official source URL and retrieval date with the submission files.
Where the journal is unknown, retain a vector master and high-resolution PNG,
use readable typography, and defer final dimensions until a target is chosen.

## Verify from the official source

- single- and double-column width, maximum height, and composite-figure rules
- minimum text size at final print width and required font family
- raster resolution, color profile, and TIFF/EPS/PDF/SVG policy
- panel-label convention, figure-legend placement, and supplementary rules
- source-data, image-integrity, and accessibility requirements

The published width and height are the canvas contract. Apply them before
drawing and follow `canvas_profiles.md`; never create a tightly cropped SVG and
resize it later to imitate the required width.

Use the stricter of the verified journal minimum and the plugin floor:
ordinary and parent text must be at least 5 pt at the declared final size.
Reduced mathematical scripts below 5 pt are warnings for final-size review
unless the official rule explicitly covers every rendered glyph; in that case
run `scripts/audit_pdf_text.py figure.pdf --min-pt 5 --strict-glyph-floor`.
Repeat the audit if a downstream document scales the figure.

For a public showcase, use the `showcase` rules in `SKILL.md`, not journal
submission rules.
