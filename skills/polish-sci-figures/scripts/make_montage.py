"""Build a contact-sheet montage from figure images for cross-figure QA.

A single montage makes inconsistent fonts, panel sizes, color drift, and
label styles jump out at a glance -- far faster than opening each PNG alone.

Usage
-----
    python make_montage.py qa/final_montage.png final_figures/*.png
    python make_montage.py -c 3 --label out.png fig1.png fig2.png fig3.png

Requires: Pillow.
"""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")


LABEL_FONT_CANDIDATES = (
    ("Sarasa Gothic SC", "C:/Windows/Fonts/SarasaGothicSC-Regular.ttf", 0),
    ("Sarasa Gothic SC", "/Library/Fonts/SarasaGothicSC-Regular.ttf", 0),
    ("Sarasa Gothic SC", "/usr/share/fonts/truetype/sarasa-gothic/SarasaGothicSC-Regular.ttf", 0),
    ("Sarasa Gothic SC", "/usr/local/share/fonts/SarasaGothicSC-Regular.ttf", 0),
    ("Noto Sans CJK SC", "C:/Windows/Fonts/NotoSansCJKsc-Regular.otf", 0),
    ("Noto Sans CJK SC", "/Library/Fonts/NotoSansCJKsc-Regular.otf", 0),
    ("Noto Sans CJK SC", "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf", 0),
    ("Noto Sans CJK SC", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2),
    ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttc", 0),
    ("PingFang SC", "/System/Library/Fonts/PingFang.ttc", 0),
    ("DejaVu Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
    ("DejaVu Sans", "DejaVuSans.ttf", 0),
)


def _glyph_signature(font, character: str) -> tuple:
    mask = font.getmask(character, mode="L")
    return mask.size, mask.getbbox(), bytes(mask)


def _missing_codepoints(font, text: str) -> tuple[int, ...]:
    missing_signature = _glyph_signature(font, "\U0010ffff")
    return tuple(sorted({
        ord(character)
        for character in text
        if not character.isspace()
        and _glyph_signature(font, character) == missing_signature
    }))


def load_label_font(size: int, required_text: str = ""):
    incomplete = []
    for family, candidate, index in LABEL_FONT_CANDIDATES:
        try:
            font = ImageFont.truetype(candidate, size, index=index)
        except OSError:
            continue
        missing = _missing_codepoints(font, required_text) if required_text else ()
        if missing:
            incomplete.append((family, missing))
            continue
        return font
    if incomplete:
        family, missing = incomplete[0]
        codepoints = ", ".join(f"U+{value:04X}" for value in missing[:12])
        sys.exit(
            "No declared montage label font covers every required glyph. "
            f"The first installed candidate, {family!r}, lacks {codepoints}."
        )
    sys.exit(
        "No declared montage label font is available. Install Sarasa Gothic "
        "SC or another family from the documented fallback stack."
    )


def build_montage(paths, out, cols=0, pad=16, bg=(255, 255, 255), label=False):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    if not imgs:
        sys.exit("no input images")
    n = len(imgs)
    cols = cols or math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    cell_w = max(im.width for im in imgs)
    cell_h = max(im.height for im in imgs)
    lab_h = 22 if label else 0

    W = cols * cell_w + (cols + 1) * pad
    H = rows * (cell_h + lab_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(sheet)
    label_text = "\n".join(os.path.basename(path) for path in paths)
    font = load_label_font(14, label_text) if label else None

    for i, (im, p) in enumerate(zip(imgs, paths)):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad) + (cell_w - im.width) // 2
        y = pad + r * (cell_h + lab_h + pad)
        if label:
            draw.text((x, y), os.path.basename(p), fill=(0, 0, 0), font=font)
        sheet.paste(im, (x, y + lab_h))

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out)
    print(f"wrote {out}  ({cols}x{rows} grid, {n} figures)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", help="output PNG path")
    ap.add_argument("inputs", nargs="+", help="input figure images")
    ap.add_argument("-c", "--cols", type=int, default=0, help="columns (default: sqrt)")
    ap.add_argument("--pad", type=int, default=16, help="padding px")
    ap.add_argument("--label", action="store_true", help="print filename over each cell")
    a = ap.parse_args(argv)
    build_montage(a.inputs, a.output, cols=a.cols, pad=a.pad, label=a.label)


if __name__ == "__main__":
    main()
