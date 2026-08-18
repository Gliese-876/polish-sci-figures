#!/usr/bin/env python3
"""Audit effective text sizes in a final PDF with public PyMuPDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SIZE_EPSILON_PT = 1e-4


def _span_text(chars: list[tuple]) -> tuple[str, bool]:
    text: list[str] = []
    has_visible_character = False
    for item in chars:
        codepoint = item[0]
        if isinstance(codepoint, int) and 0 <= codepoint <= 0x10FFFF:
            character = chr(codepoint)
            text.append(character)
            has_visible_character |= not character.isspace()
        else:
            text.append("�")
            has_visible_character = True
    return "".join(text), has_visible_character


def audit_pdf(data: bytes, minimum_pt: float = 5.0) -> dict[str, object]:
    """Return the rendered-text size audit for a PDF byte string."""
    if minimum_pt <= 0:
        raise ValueError("minimum_pt must be positive")
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF is required; install the public package with "
            "`pip install pymupdf`."
        ) from exc

    runs: list[dict[str, object]] = []
    warnings: list[str] = []
    with pymupdf.open(stream=data, filetype="pdf") as document:
        for page_number, page in enumerate(document, 1):
            try:
                spans = page.get_texttrace()
            except Exception as exc:
                warnings.append(f"page {page_number} text extraction failed: {exc}")
                continue
            for span in spans:
                if (span.get("type") in {3, 7}
                        or float(span.get("opacity", 1.0)) <= 0):
                    continue
                chars = list(span.get("chars", []))
                text, has_visible_character = _span_text(chars)
                size = float(span.get("size", 0.0))
                if chars and has_visible_character and size > 0:
                    runs.append({
                        "page": page_number,
                        "font": str(span.get("font", "<unknown>")),
                        "size_pt": size,
                        "text": text[:80],
                    })

    below = [
        run for run in runs
        if float(run["size_pt"]) < minimum_pt - SIZE_EPSILON_PT
    ]
    auditable = bool(runs) and not warnings
    verdict = (
        "NOT AUDITABLE" if not auditable
        else "FAIL" if below
        else "PASS"
    )
    return {
        "auditable": auditable,
        "verdict": verdict,
        "minimum_required_pt": minimum_pt,
        "comparison_tolerance_pt": SIZE_EPSILON_PT,
        "minimum_found_pt": min(
            (float(run["size_pt"]) for run in runs), default=None,
        ),
        "text_run_count": len(runs),
        "below_minimum_count": len(below),
        "below_minimum": below,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="final exported PDF figure")
    parser.add_argument(
        "--min-pt", type=float, default=5.0,
        help="minimum allowed effective text size in points",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.min_pt <= 0:
        print("error: --min-pt must be positive", file=sys.stderr)
        return 2
    try:
        data = args.pdf.read_bytes()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not data.startswith(b"%PDF-"):
        print(f"error: not a PDF file: {args.pdf}", file=sys.stderr)
        return 2
    try:
        result = audit_pdf(data, args.min_pt)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(
            {"pdf": str(args.pdf), **result}, indent=2, ensure_ascii=False,
        ))
    else:
        print("SCI Figure PDF Text Audit")
        print(f"pdf: {args.pdf}")
        print(f"minimum required: {args.min_pt:g} pt")
        if result["minimum_found_pt"] is not None:
            print(f"minimum found: {result['minimum_found_pt']:g} pt")
        print(f"verdict: {result['verdict']}")
        for run in result["below_minimum"]:
            print(
                f"error: page {run['page']}: {run['size_pt']:g} pt, "
                f"{run['font']}, {run['text']!r}"
            )
        for warning in result["warnings"]:
            print(f"warning: {warning}")
        print("note: re-audit after any downstream scaling at final placement")

    if not result["auditable"]:
        return 2
    return 1 if result["below_minimum_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
