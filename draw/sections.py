"""
sections.py - proposed long section through the extension and dwelling.

Cut line runs front-to-back (looking east). The horizontal axis is real depth
(y, with the extension in negative y) and the vertical axis is real height (z),
drawn through a flipped `View`.
"""

from __future__ import annotations

import config as C
import svgkit as sk
from geometry import View

K50 = 1 / 50.0
BRICK = "url(#hatch-brick)"
SLATE = "url(#hatch-slate)"
CONCRETE = "url(#hatch-concrete)"
INSUL = "url(#hatch-insulation)"
FFL_1 = 2500.0          # first floor level
GROUND = 0.0


def _sheet(title, number, notes=None):
    s = sk.Sheet(title, number, "1:50 @ A3", C.PROJECT, C.ADDRESS, C.CLIENT,
                 C.DATE, C.DRAWN, C.CHECKED, C.REV)
    s.notes = notes or []
    return s


def _earth(v, x0, x1):
    v.rect(x0, -900, x1 - x0, 900, fill="url(#hatch-earth)", stroke="none", sw=0)
    v.line(x0, 0, x1, 0, w=sk.LW_MED, stroke=sk.INK)


def section_sheet(number: str):
    s = _sheet("PROPOSED LONG SECTION A-A", number, notes=[
        "Section A-A cut through the extension and rear rooms; see plan.",
        "Extension roof: single ply membrane on 18 mm ply, warm deck.",
        "New walls: 100 mm brick / 150 mm insulated cavity / 100 mm block.",
        "Existing dwelling retained; roof and floors as existing.",
        "All dimensions in mm; levels relative to finished ground floor (0).",
    ])
    k = K50
    # horizontal: depth coordinate; start so the rear of the extension sits left
    x_left = -C.EXT_D - 1500.0
    v = View(s, k, 205.0, 250.0)

    # ---- ground / earth ----
    _earth(v, x_left, C.HOUSE_D + 1500.0)

    # ---- existing house (in section) ----
    t = C.WALL_EXT
    # rear wall of house (cut), front wall (cut)
    v.rect(-t / 2, 0, t, C.EAVES, fill=BRICK, stroke=sk.INK, sw=sk.LW_MED)
    v.rect(C.HOUSE_D - t / 2, 0, t, C.EAVES, fill=BRICK, stroke=sk.INK,
           sw=sk.LW_MED)
    # ground + first floors
    v.rect(0, -150, C.HOUSE_D, 150, fill=CONCRETE, stroke=sk.INK, sw=sk.LW_THIN)
    v.rect(0, FFL_1 - 100, C.HOUSE_D, 100, fill="#e8e8e8", stroke=sk.INK,
           sw=sk.LW_THIN)
    # roof (two pitches in section)
    v.poly([(0, C.EAVES), (C.HOUSE_D / 2, C.RIDGE), (C.HOUSE_D, C.EAVES),
            (C.HOUSE_D, C.EAVES - 180), (C.HOUSE_D / 2, C.RIDGE - 180),
            (0, C.EAVES - 180)], fill=SLATE, stroke=sk.INK, sw=sk.LW_MED)
    # ceiling / joists
    v.line(0, FFL_1, C.HOUSE_D, FFL_1, w=sk.LW_THIN)
    # internal rear room + first floor room labels
    v.text(C.HOUSE_D * 0.35, 1300, "REAR ROOM", size=2.2, anchor="middle",
           cls="t-area")
    v.text(C.HOUSE_D * 0.62, 3600, "BEDROOM", size=2.2, anchor="middle",
           cls="t-area")

    # ---- extension (in section) ----
    ex0, ew, ed = C.EXT_X0, C.EXT_W, C.EXT_D
    # floor slab
    v.rect(-ed, -150, ed, 150, fill=CONCRETE, stroke=sk.INK, sw=sk.LW_THIN)
    # rear (garden) wall, cut
    v.rect(-ed - t / 2, 0, t, C.EXT_REAR_H, fill=BRICK, stroke=sk.INK,
           sw=sk.LW_MED)
    # insulation line in rear wall
    v.rect(-ed - t / 2 + 60, 0, 150, C.EXT_REAR_H, fill=INSUL, stroke="none",
           sw=0)
    # roof: lean-to slab from house (z=EXT_HOUSE_H) down to rear (z=EXT_REAR_H)
    v.poly([(-ed - t / 2, C.EXT_REAR_H), (0, C.EXT_HOUSE_H),
            (0, C.EXT_HOUSE_H - 150), (-ed - t / 2, C.EXT_REAR_H - 150)],
           fill=SLATE, stroke=sk.INK, sw=sk.LW_MED)
    # head of the opening in the existing rear wall (removed wall line)
    v.line(-t / 2, 0, t / 2, 0, w=sk.LW_THIN)
    # sliding door in rear wall of extension
    v.rect(-ed - t / 2 + 40, 0, 60, 2200, fill="#eef4f8", stroke=sk.INK,
           sw=sk.LW_THIN)

    # ---- levels ----
    for z, lab in ((0, "GF  0.00"), (FFL_1, "FF  +2.50"),
                   (C.EXT_REAR_H, "EXT EAVES  +2.45"),
                   (C.EXT_HOUSE_H, "EXT ROOF  +2.70"),
                   (C.EAVES, "HOUSE EAVES  +2.70"),
                   (C.RIDGE, "RIDGE  +6.20")):
        v.line(-ed - 1500, z, C.HOUSE_D + 400, z, w=sk.LW_HAIR, stroke=sk.MID,
               dash="1.5,1.5")
        v.text(-ed - 1450, z + 120, lab, size=1.9, cls="t-small")

    # ---- vertical dimensions ----
    v.dim_v(-ed - 1200, 0, C.EXT_REAR_H, f"{C.m(C.EXT_REAR_H, 2)}",
            offset=-1200, side=-1)
    v.dim_v(-ed - 2000, 0, C.RIDGE, f"{C.m(C.RIDGE, 2)}", offset=-2000,
            side=-1)
    v.dim_h(FFL_1 + 400, -ed, 0, f"{int(ed)}", offset=400, side=1)
    v.dim_h(FFL_1 + 400, 0, C.HOUSE_D, f"{int(C.HOUSE_D)}", offset=400, side=1)

    s.text(40, 24, "PROPOSED LONG SECTION A-A", size=3.0, weight="bold")
    s.scale_bar(120, 280, K50, 5000, divisions=5)
    s.north(388, 60, 6)
    return s
