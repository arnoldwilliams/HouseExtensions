"""
svgkit.py - a tiny, dependency-free SVG drawing toolkit for architectural sheets.

Everything is expressed in *paper millimetres*. A sheet is A3 landscape
(420 x 297 mm) and the SVG viewBox uses the same units, so 1 user unit == 1 mm
on paper. Views (the bits of real building that get drawn) map real-world
millimetres onto paper millimetres through a scale factor, e.g. 1:100 -> 0.01.

Only the standard library is used so the generator runs anywhere.
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# Sheet / page constants
# --------------------------------------------------------------------------
A3W, A3H = 420.0, 297.0        # A3 landscape, mm
MARGIN = 10.0                  # border margin
INNER = 6.0                    # inner rule offset from the border

# Line weights (mm) - roughly BS 1192 / ISO 128 style hierarchy
LW_THICK = 0.70                # cut walls / building outline
LW_MED = 0.35                  # secondary / new work emphasis
LW_THIN = 0.18                 # dimensions, hatching, projections
LW_HAIR = 0.13                 # grid / setting out

# Greys
INK = "#101010"
MID = "#5a5a5a"
LIGHT = "#b8b8b8"
EXIST_FILL = "#d9d9d9"         # existing walls (grey)
NEW_FILL = "#2b2b2b"           # proposed / new walls (near-black)
PAPER = "#ffffff"


def fmt(v: float) -> str:
    """Compact number formatting for SVG output."""
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


# --------------------------------------------------------------------------
# Patterns / defs
# --------------------------------------------------------------------------
DEFS = f"""
<defs>
  <pattern id="hatch-existing" width="2.2" height="2.2" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45)">
    <rect width="2.2" height="2.2" fill="{EXIST_FILL}"/>
    <line x1="0" y1="0" x2="0" y2="2.2" stroke="{MID}" stroke-width="0.22"/>
  </pattern>
  <pattern id="hatch-concrete" width="2.4" height="2.4" patternUnits="userSpaceOnUse"
           patternTransform="rotate(35)">
    <rect width="2.4" height="2.4" fill="#efefef"/>
    <line x1="0" y1="0" x2="0" y2="2.4" stroke="#8a8a8a" stroke-width="0.2"/>
    <circle cx="0.9" cy="1.7" r="0.22" fill="#8a8a8a"/>
  </pattern>
  <pattern id="hatch-earth" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="3" fill="#fafafa"/>
    <line x1="0" y1="1.5" x2="1.5" y2="0" stroke="#9a9a9a" stroke-width="0.2"/>
    <line x1="1.5" y1="3" x2="3" y2="1.5" stroke="#9a9a9a" stroke-width="0.2"/>
  </pattern>
  <pattern id="hatch-insulation" width="3" height="2" patternUnits="userSpaceOnUse">
    <rect width="3" height="2" fill="#ffffff"/>
    <path d="M0,2 Q0.75,0.4 1.5,2 T3,2" fill="none" stroke="#c07000" stroke-width="0.2"/>
  </pattern>
  <pattern id="hatch-roof" width="2.6" height="2.6" patternUnits="userSpaceOnUse"
           patternTransform="rotate(-45)">
    <rect width="2.6" height="2.6" fill="#f4f4f4"/>
    <line x1="0" y1="0" x2="0" y2="2.6" stroke="#a8a8a8" stroke-width="0.18"/>
  </pattern>
  <pattern id="hatch-tile" width="3.2" height="2" patternUnits="userSpaceOnUse">
    <rect width="3.2" height="2" fill="#ededed"/>
    <line x1="0" y1="0" x2="3.2" y2="0" stroke="#8f8f8f" stroke-width="0.16"/>
    <line x1="0" y1="1" x2="3.2" y2="1" stroke="#8f8f8f" stroke-width="0.16"/>
  </pattern>
  <pattern id="hatch-brick" width="4" height="2" patternUnits="userSpaceOnUse">
    <rect width="4" height="2" fill="#f5f0e8"/>
    <line x1="0" y1="1" x2="4" y2="1" stroke="#c3b399" stroke-width="0.18"/>
    <line x1="2" y1="0" x2="2" y2="1" stroke="#c3b399" stroke-width="0.18"/>
    <line x1="0" y1="1" x2="0" y2="2" stroke="#c3b399" stroke-width="0.18"/>
    <line x1="4" y1="1" x2="4" y2="2" stroke="#c3b399" stroke-width="0.18"/>
  </pattern>
  <pattern id="hatch-slate" width="3" height="2" patternUnits="userSpaceOnUse">
    <rect width="3" height="2" fill="#e7e7e7"/>
    <line x1="0" y1="1" x2="3" y2="1" stroke="#9a9a9a" stroke-width="0.15"/>
    <line x1="1.5" y1="0" x2="1.5" y2="1" stroke="#9a9a9a" stroke-width="0.15"/>
  </pattern>
</defs>
"""

CSS = f"""
<style>
  text {{ font-family: Helvetica, Arial, sans-serif; fill: {INK}; }}
  .t-title   {{ font-size: 4.2px; font-weight: bold; letter-spacing: 0.3px; }}
  .t-sub     {{ font-size: 2.9px; font-weight: bold; }}
  .t-label   {{ font-size: 2.5px; }}
  .t-room    {{ font-size: 2.6px; font-weight: bold; }}
  .t-area    {{ font-size: 2.1px; fill: {MID}; }}
  .t-dim     {{ font-size: 2.2px; fill: {INK}; }}
  .t-note    {{ font-size: 2.15px; }}
  .t-small   {{ font-size: 1.85px; fill: {MID}; }}
  .t-scale   {{ font-size: 2.6px; font-weight: bold; }}
</style>
"""


# --------------------------------------------------------------------------
# Sheet
# --------------------------------------------------------------------------
class Sheet:
    def __init__(self, title, number, scale, project, address, client, date,
                 drawn="AI", checked="—", rev="P1"):
        self.title = title
        self.number = number
        self.scale = scale
        self.project = project
        self.address = address
        self.client = client
        self.date = date
        self.drawn = drawn
        self.checked = checked
        self.rev = rev
        self.body = []
        self.notes = []
        self.legend = []
        self.notes_pos = None      # (x, y) paper mm, default bottom-left
        self.legend_pos = None

    # ---- low level -----------------------------------------------------
    def add(self, s):
        self.body.append(s)

    def line(self, x1, y1, x2, y2, w=LW_THIN, stroke=INK, dash=None,
             cap="butt", opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" '
                 f'y2="{fmt(y2)}" stroke="{stroke}" stroke-width="{fmt(w)}" '
                 f'stroke-linecap="{cap}"{d}{o}/>')

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=LW_THIN,
             dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" '
                 f'height="{fmt(h)}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{fmt(sw)}"{d}{o}/>')

    def poly(self, pts, fill="none", stroke=INK, sw=LW_THIN, dash=None,
             closed=True):
        p = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{fmt(sw)}"{d}/>')

    def path(self, d, fill="none", stroke=INK, sw=LW_THIN, dash=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{fmt(sw)}"{ds}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=LW_THIN):
        self.add(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{fmt(sw)}"/>')

    def text(self, x, y, s, size=2.5, anchor="start", weight="normal",
             cls=None, rotate=None, fill=None):
        c = f' class="{cls}"' if cls else f' font-size="{fmt(size)}"'
        w = f' font-weight="{weight}"' if weight != "normal" else ""
        f = f' fill="{fill}"' if fill else ""
        t = f' transform="rotate({fmt(rotate)} {fmt(x)} {fmt(y)})"' if rotate else ""
        self.add(f'<text x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}"'
                 f'{c}{w}{f}{t}>{escape(str(s))}</text>')

    # ---- dimensions ----------------------------------------------------
    def dim(self, x1, y1, x2, y2, label, offset=7.0, size=2.2,
            tick=1.6, side=1, textside=1, ext=True):
        """Linear dimension between two paper points, offset perpendicular."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        nx, ny = -uy * side, ux * side
        ax, ay = x1 + nx * offset, y1 + ny * offset
        bx, by = x2 + nx * offset, y2 + ny * offset
        if ext:
            self.line(x1 + nx * 1.5, y1 + ny * 1.5, ax + nx * 1.5, ay + ny * 1.5,
                      LW_HAIR, MID)
            self.line(x2 + nx * 1.5, y2 + ny * 1.5, bx + nx * 1.5, by + ny * 1.5,
                      LW_HAIR, MID)
        self.line(ax, ay, bx, by, LW_THIN, INK)
        for px, py in ((ax, ay), (bx, by)):
            self.line(px - (ux + nx) * tick, py - (uy + ny) * tick,
                      px + (ux + nx) * tick, py + (uy + ny) * tick, LW_THIN, INK)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        off = (size * 0.75) * textside
        self.text(mx + nx * off, my + ny * off, label, size=size, anchor="middle",
                  cls="t-dim")

    # ---- annotation helpers -------------------------------------------
    def scale_bar(self, x, y, k, total_mm_real, divisions=4, height=2.4):
        """Alternating black/white scale bar; k = drawing scale factor."""
        seg = total_mm_real / divisions * k
        for i in range(divisions):
            self.rect(x + i * seg, y, seg, height,
                      fill=INK if i % 2 == 0 else PAPER, stroke=INK, sw=LW_THIN)
        for i in range(divisions + 1):
            real = total_mm_real / divisions * i
            lab = f"{real/1000:.1f}" if real % 1000 else f"{int(real/1000)}"
            self.text(x + i * seg, y - 0.9, lab, size=1.9, anchor="middle",
                      cls="t-small")
        self.text(x + divisions * seg + 1.6, y + height - 0.2, "m", size=1.9,
                  cls="t-small")

    def north(self, cx, cy, r=6.0):
        self.circle(cx, cy, r, fill=PAPER, stroke=INK, sw=LW_THIN)
        self.poly([(cx, cy - r * 0.82), (cx - r * 0.34, cy + r * 0.5),
                   (cx, cy + r * 0.24)], fill=INK, stroke=INK, sw=LW_THIN)
        self.poly([(cx, cy - r * 0.82), (cx + r * 0.34, cy + r * 0.5),
                   (cx, cy + r * 0.24)], fill="none", stroke=INK, sw=LW_THIN)
        self.text(cx, cy - r - 1.2, "N", size=2.8, anchor="middle",
                  weight="bold")

    # ---- frame / title block ------------------------------------------
    def _frame(self):
        self.rect(MARGIN, MARGIN, A3W - 2 * MARGIN, A3H - 2 * MARGIN,
                  fill="none", stroke=INK, sw=0.9)
        self.rect(MARGIN + INNER, MARGIN + INNER,
                  A3W - 2 * (MARGIN + INNER), A3H - 2 * (MARGIN + INNER),
                  fill="none", stroke=INK, sw=LW_MED)
        # drawing area corner ticks
        for cx in (MARGIN, A3W - MARGIN):
            for cy in (MARGIN, A3H - MARGIN):
                self.circle(cx, cy, 0.9, fill=INK, stroke="none")

    def _title_block(self):
        # Bottom-right title block, 180 x 52 mm
        bw, bh = 180.0, 52.0
        bx, by = A3W - MARGIN - INNER - bw, A3H - MARGIN - INNER - bh
        self.rect(bx, by, bw, bh, fill=PAPER, stroke=INK, sw=0.9)
        # horizontal rules
        rows = [by + 16, by + 27, by + 37, by + 44]
        for r in rows:
            self.line(bx, r, bx + bw, r, LW_THIN, INK)
        # vertical splits on the lower rows
        self.line(bx + 90, by + 27, bx + 90, by + 44, LW_THIN, INK)
        self.line(bx + 135, by + 27, bx + 135, by + 44, LW_THIN, INK)

        # project banner
        self.text(bx + 3, by + 6.5, self.project, size=3.4, weight="bold")
        self.text(bx + 3, by + 12.0, self.address, size=2.3, cls="t-small")
        self.text(bx + bw - 3, by + 6.5, "PROPOSED", size=2.6, anchor="end",
                  weight="bold", fill=MID)
        self.text(bx + bw - 3, by + 11.0, "REAR / SIDE EXTENSION", size=2.2,
                  anchor="end", cls="t-small")

        # drawing title
        self.text(bx + 3, by + 22.5, self.title.upper(), size=3.6, weight="bold")

        # scale / number row
        self.text(bx + 3, by + 32.5, "SCALE", size=1.9, cls="t-small")
        self.text(bx + 3, by + 35.5, self.scale, size=2.7, weight="bold")
        self.text(bx + 93, by + 32.5, "DRAWING No.", size=1.9, cls="t-small")
        self.text(bx + 93, by + 35.5, self.number, size=2.7, weight="bold")
        self.text(bx + 138, by + 32.5, "REV", size=1.9, cls="t-small")
        self.text(bx + 138, by + 35.5, self.rev, size=2.7, weight="bold")

        # bottom row of metadata
        meta = [
            (bx + 3, "DRAWN", self.drawn),
            (bx + 48, "CHECKED", self.checked),
            (bx + 93, "DATE", self.date),
            (bx + 138, "CLIENT", self.client),
        ]
        for x, k, v in meta:
            self.text(x, by + 41.5, k, size=1.7, cls="t-small")
            self.text(x, by + 47.5, v, size=2.1)

    def _notes_panel(self, x, y, w):
        if not self.notes:
            return
        h = 4.6 + len(self.notes) * 3.3
        self.rect(x, y, w, h, fill=PAPER, stroke=INK, sw=LW_THIN)
        self.text(x + 2.5, y + 4.0, "NOTES", size=2.6, weight="bold")
        for i, n in enumerate(self.notes):
            self.text(x + 2.5, y + 8.0 + i * 3.3, f"{i+1}.  {n}", size=2.15,
                      cls="t-note")

    def _legend(self, x, y, w):
        if not self.legend:
            return
        h = 4.6 + len(self.legend) * 3.4
        self.rect(x, y, w, h, fill=PAPER, stroke=INK, sw=LW_THIN)
        self.text(x + 2.5, y + 4.0, "LEGEND", size=2.6, weight="bold")
        for i, (kind, label) in enumerate(self.legend):
            yy = y + 8.2 + i * 3.4
            if kind == "new":
                self.rect(x + 2.5, yy - 2.3, 4.2, 2.6, fill=NEW_FILL, stroke=INK,
                          sw=LW_THIN)
            elif kind == "exist":
                self.rect(x + 2.5, yy - 2.3, 4.2, 2.6, fill="url(#hatch-existing)",
                          stroke=INK, sw=LW_THIN)
            elif kind == "dashed":
                self.line(x + 2.5, yy - 1.0, x + 6.7, yy - 1.0, LW_THIN, INK,
                          dash="2,1.4")
            elif kind == "concrete":
                self.rect(x + 2.5, yy - 2.3, 4.2, 2.6, fill="url(#hatch-concrete)",
                          stroke=INK, sw=LW_THIN)
            self.text(x + 8.6, yy, label, size=2.1, cls="t-note")

    # ---- output --------------------------------------------------------
    def render(self):
        self._frame()
        self._title_block()
        base = A3H - MARGIN - INNER
        notes_h = 4.6 + len(self.notes) * 3.3 if self.notes else 0.0
        legend_h = 4.6 + len(self.legend) * 3.4 if self.legend else 0.0
        if self.notes:
            if self.notes_pos:
                self._notes_panel(self.notes_pos[0], self.notes_pos[1], 96)
            else:
                self._notes_panel(MARGIN + INNER, base - notes_h, 96)
        if self.legend:
            if self.legend_pos:
                self._legend(self.legend_pos[0], self.legend_pos[1], 60)
            else:
                self._legend(MARGIN + INNER, base - notes_h - legend_h, 60)
        body = "\n".join(self.body)
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{fmt(A3W)}mm" height="{fmt(A3H)}mm" '
                f'viewBox="0 0 {fmt(A3W)} {fmt(A3H)}">\n'
                f'{DEFS}\n{CSS}\n{body}\n'
                f'</svg>\n')


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
