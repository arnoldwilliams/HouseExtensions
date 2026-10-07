"""
elevations.py - existing and proposed elevations.

Convention: ridge runs parallel to the rear (and front) wall, so the rear and
front elevations show a rectangular roof band and the side (flank) elevation
shows a gable. Heights are real millimetres on the vertical axis, drawn with a
`View` whose y axis is flipped so z increases upwards.
"""

from __future__ import annotations

import config as C
import svgkit as sk
from geometry import View

K100 = 1 / 100.0

# Opening heights (mm above finished floor level)
SILL_GF, HEAD_GF = 900.0, 2100.0
SILL_FF, HEAD_FF = 1000.0, 2000.0
DOOR_H = 2100.0
SLIDER_H = 2200.0
BRICK = "url(#hatch-brick)"
SLATE = "url(#hatch-slate)"


def _sheet(title, number):
    return sk.Sheet(title, number, "1:100 @ A3", C.PROJECT, C.ADDRESS, C.CLIENT,
                    C.DATE, C.DRAWN, C.CHECKED, C.REV)


# ---------------------------------------------------------------------------
# Opening symbols (elevation)
# ---------------------------------------------------------------------------
def _window(v, x0, x1, sill, head):
    v.rect(x0, sill, x1 - x0, head - sill, fill="#ffffff", stroke=sk.INK,
           sw=sk.LW_THIN)
    xm = (x0 + x1) / 2
    v.line(xm, sill, xm, head, w=sk.LW_HAIR)
    v.line(x0 - 60, sill - 40, x1 + 60, sill - 40, w=sk.LW_THIN)  # cill


def _door(v, x0, x1, h):
    v.rect(x0, 0, x1 - x0, h, fill="#f0f0f0", stroke=sk.INK, sw=sk.LW_THIN)
    xm = (x0 + x1) / 2
    v.line(xm, 0, xm, h, w=sk.LW_HAIR)


def _glazing(v, x0, x1, z0, z1, n=3):
    v.rect(x0, z0, x1 - x0, z1 - z0, fill="#eef4f8", stroke=sk.INK,
           sw=sk.LW_THIN)
    for i in range(1, n):
        xm = x0 + (x1 - x0) * i / n
        v.line(xm, z0, xm, z1, w=sk.LW_HAIR)


# ---------------------------------------------------------------------------
# Shells
# ---------------------------------------------------------------------------
def _rear_front_shell(v, W, eaves, ridge):
    v.rect(0, 0, W, eaves, fill=BRICK, stroke=sk.INK, sw=sk.LW_THICK)
    v.rect(0, eaves, W, ridge - eaves, fill=SLATE, stroke=sk.INK, sw=sk.LW_MED)
    v.line(0, eaves, W, eaves, w=sk.LW_MED)
    v.line(0, ridge, W, ridge, w=sk.LW_MED)
    for x in (0, W):
        v.line(x, eaves, x, ridge, w=sk.LW_MED)


def _ground(v, x0, x1):
    v.line(x0, 0, x1, 0, w=sk.LW_THICK)
    # short ground hatch
    v.rect(x0, -260, x1 - x0, 260, fill="url(#hatch-earth)", stroke="none", sw=0)
    v.line(x0, -260, x1, -260, w=sk.LW_HAIR, stroke=sk.MID)


# ---------------------------------------------------------------------------
# Individual views
# ---------------------------------------------------------------------------
def _rear_view(v, existing, show_ext):
    W, eaves, ridge = C.HOUSE_W, C.EAVES, C.RIDGE
    _ground(v, -1200, W + 1200)
    _rear_front_shell(v, W, eaves, ridge)

    if existing:
        for (a, b, kind, opt) in C.REAR_OPENINGS:
            x0 = C.WALL_EXT / 2 + a
            x1 = C.WALL_EXT / 2 + b
            if kind == "win":
                _window(v, x0, x1, SILL_GF, HEAD_GF)
            elif kind == "door":
                _door(v, x0, x1, DOOR_H)

    if show_ext:
        ex0, ew = C.EXT_X0, C.EXT_W
        # rear wall of the extension (nearest the viewer)
        v.rect(ex0, 0, ew, C.EXT_REAR_H, fill=BRICK, stroke=sk.INK,
               sw=sk.LW_THICK)
        # extension roof surface, rising away to the house
        v.rect(ex0, C.EXT_REAR_H, ew, C.EXT_HOUSE_H - C.EXT_REAR_H, fill=SLATE,
               stroke=sk.INK, sw=sk.LW_MED)
        for (a, b, kind, opt) in C.EXT_REAR_OPENINGS:
            _glazing(v, ex0 + C.EXT_WALL / 2 + a, ex0 + C.EXT_WALL / 2 + b,
                     0, SLIDER_H, n=4)
        # projecting side walls shown as returns
        for x in (ex0, ex0 + ew):
            v.line(x, 0, x, C.EXT_REAR_H, w=sk.LW_MED)

    # levels + dims
    v.line(-900, C.EXT_REAR_H if show_ext else C.EAVES, -900,
           C.RIDGE, w=sk.LW_HAIR, stroke=sk.MID)
    v.dim_v(-700, 0, C.EXT_REAR_H if show_ext else C.EAVES,
            f"{C.m(C.EXT_REAR_H if show_ext else C.EAVES, 2)}", offset=-700,
            side=-1)
    v.dim_v(-700, 0, C.RIDGE, f"{C.m(C.RIDGE, 2)}", offset=-2200, side=-1)
    v.dim_h(-1400, 0, W, f"{int(W)}", offset=-1400, side=-1)
    if show_ext:
        v.dim_h(-2600, ex0, ex0 + ew, f"{int(ew)}", offset=-2600, side=-1)
    v.text(W / 2, C.RIDGE + 700, "REAR ELEVATION", size=2.6, anchor="middle",
           weight="bold")


def _front_view(v, existing):
    W, eaves, ridge = C.HOUSE_W, C.EAVES, C.RIDGE
    _ground(v, -1200, W + 1200)
    _rear_front_shell(v, W, eaves, ridge)
    for (a, b, kind, opt) in C.FRONT_OPENINGS:
        x0, x1 = W - (C.WALL_EXT / 2 + b), W - (C.WALL_EXT / 2 + a)  # mirrored
        if kind == "win":
            _window(v, x0, x1, SILL_GF, HEAD_GF)
        elif kind == "door":
            _door(v, x0, x1, DOOR_H)
    # front door canopy
    v.rect(W - (C.WALL_EXT / 2 + 5450) - 120, DOOR_H, 1000 + 240, 180,
           fill=SLATE, stroke=sk.INK, sw=sk.LW_THIN)
    v.dim_v(-700, 0, eaves, f"{C.m(eaves, 2)}", offset=-700, side=-1)
    v.dim_v(-700, 0, ridge, f"{C.m(ridge, 2)}", offset=-2200, side=-1)
    v.dim_h(-1400, 0, W, f"{int(W)}", offset=-1400, side=-1)
    v.text(W / 2, ridge + 700, "FRONT (PRINCIPAL) ELEVATION", size=2.6,
           anchor="middle", weight="bold")


def _flank_view(v, existing, show_ext):
    D, eaves, ridge = C.HOUSE_D, C.EAVES, C.RIDGE
    ed = C.EXT_D if show_ext else 0.0
    x0 = -ed - 500
    _ground(v, x0, D + 1200)
    if show_ext:
        # extension body, rear on the left, roof rising to the house
        v.poly([(-ed, 0), (0, 0), (0, C.EXT_HOUSE_H), (-ed, C.EXT_REAR_H)],
               fill=BRICK, stroke=sk.INK, sw=sk.LW_THICK)
        v.line(-ed, C.EXT_REAR_H, 0, C.EXT_HOUSE_H, w=sk.LW_MED)
    # house gable
    v.rect(0, 0, D, eaves, fill=BRICK, stroke=sk.INK, sw=sk.LW_THICK)
    v.poly([(0, eaves), (D / 2, ridge), (D, eaves)], fill=SLATE, stroke=sk.INK,
           sw=sk.LW_MED)
    v.line(0, eaves, D, eaves, w=sk.LW_MED)
    # right flank window (kitchen) - run starts at the rear wall
    for (a, b, kind, opt) in C.RIGHT_OPENINGS:
        if kind == "win":
            _window(v, C.WALL_EXT / 2 + a, C.WALL_EXT / 2 + b, SILL_GF, HEAD_GF)
    # dims
    v.dim_v(x0 + 500, 0, ridge, f"{C.m(ridge, 2)}", offset=-700, side=-1)
    if show_ext:
        v.dim_v(-ed - 400, 0, C.EXT_REAR_H, f"{C.m(C.EXT_REAR_H, 2)}",
                offset=-400, side=-1)
    v.dim_h(-1400, -ed if show_ext else 0, D,
            f"{C.m(D + ed, 1)} m", offset=-1400, side=-1)
    v.text((D - ed) / 2, ridge + 700, "SIDE (FLANK) ELEVATION", size=2.6,
           anchor="middle", weight="bold")


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------
def _place(s, kind, existing, show_ext, ox, oy):
    k = K100
    v = View(s, k, ox, oy)
    if kind == "rear":
        _rear_view(v, existing, show_ext)
    elif kind == "front":
        _front_view(v, existing)
    elif kind == "flank":
        _flank_view(v, existing, show_ext)


def elevations_sheet(existing: bool, number: str):
    tag = "EXISTING" if existing else "PROPOSED"
    s = _sheet(f"{tag} ELEVATIONS", number)
    if not existing:
        s.notes = [
            "Extension finished in materials to match the existing dwelling.",
            "New walls: 100 mm facing brick outer leaf, 150 mm insulated cavity.",
            "Extension roof: single ply membrane, min. fall 1:40, dark grey.",
            "All new windows and doors uPVC/alu, anthracite grey, min. U 1.4.",
            "Any works within 3 m of a boundary to comply with Part A / fire.",
        ]
        s.notes_pos = (250.0, 35.0)
        s.legend = [("new", "New / proposed work"),
                    ("exist", "Existing retained")]
        s.legend_pos = (250.0, 60.0)
    # rear + front side by side, flank below
    _place(s, "rear", existing, not existing, 40, 92)
    _place(s, "front", existing, False, 145, 92)
    _place(s, "flank", existing, not existing, 58, 182)
    s.scale_bar(60, 278, K100, 5000, divisions=5)
    s.north(388, 60, 6)
    return s
