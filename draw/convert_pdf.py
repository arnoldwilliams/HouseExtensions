#!/usr/bin/env python3
"""
convert_pdf.py - render each drawing SVG to an exact A3 landscape PDF.

SmartDraw imports PDF as well as SVG; the PDF is handy for printing and for
councils that prefer PDF uploads. Uses headless Chromium so no third-party
Python packages are required.
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.normpath(os.path.join(HERE, "..", "drawings"))

CHROMIUM = os.environ.get("CHROMIUM", "chromium")

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  @page {{ size: A3 landscape; margin: 0; }}
  html, body {{ margin: 0; padding: 0; }}
  svg {{ display: block; width: 420mm; height: 297mm; }}
</style></head><body>
{svg}
</body></html>
"""


def convert(svg_path: str) -> str:
    pdf_path = svg_path[:-4] + ".pdf"
    with open(svg_path, "r", encoding="utf-8") as f:
        svg = f.read()
    html = HTML.format(svg=svg)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     encoding="utf-8") as t:
        t.write(html)
        tmp = t.name
    try:
        subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu",
             "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
             "--virtual-time-budget=4000",
             f"--print-to-pdf={pdf_path}", "file://" + tmp],
            check=True, capture_output=True, text=True)
    finally:
        os.unlink(tmp)
    return pdf_path


def main():
    svgs = sorted(glob.glob(os.path.join(SVG_DIR, "*.svg")))
    if not svgs:
        print("no SVGs found; run generate.py first", file=sys.stderr)
        return 1
    for svg in svgs:
        pdf = convert(svg)
        print("pdf  ", os.path.relpath(pdf, SVG_DIR),
              f"({os.path.getsize(pdf)//1024} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
