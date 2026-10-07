"""
plans.py - floor plans (existing + proposed), roof plan and block plan.

Drawings are produced as svgkit `Sheet` objects at A3, ready to import into
SmartDraw (via the SVG/PDF export) or to print for a UK householder planning
application.
"""

from __future__ import annotations

import config as C
import svgkit as sk
from geometry import View

K100 = 1 / 100.0        # 1:100
K50 = 1 / 50.0          # 1:50
K200 = 1 / 200.0        # 1:200
K500 = 1 / 500.0        # 1:500


def _sheet(title, number, scale, notes=None, legend=None):
    s = sk.Sheet(title, number, scale, C.PROJECT, C.ADDRESS, C.CLIENT, C.DATE,
                 C.DRAWN, C.CHECKED, C.REV)
    s.notes = notes or []
    s.legend = legend or []
    return s


# ---------------------------------------------------------------------------
# Floor plans
# ---------------------------------------------------------------------------
def _plan_geometry(v, existing: bool, level: str, show_ext: bool):
    """Draw the walls, partitions and rooms for one floor plan."""
    t = C.WALL_EXT
    wi = C.WALL_INT

    # ---- external walls of the existing house ----
    if existing:
        rear_ops = C.REAR_OPENINGS
    else:
        # proposed: the rear wall is opened up where the extension meets it
        rear_ops = [(C.EXT_X0 + t / 2, C.EXT_X0 + C.EXT_W - t / 2, "removed", {})]
    front_ops = C.FRONT_OPENINGS
    right_ops = C.RIGHT_OPENINGS

    v.wall(0, 0, C.HOUSE_W, 0, t, openings=rear_ops)            # rear wall
    v.wall(0, C.HOUSE_D, C.HOUSE_W, C.HOUSE_D, t, openings=front_ops)  # front
    v.wall(0, 0, 0, C.HOUSE_D, t, openings=C.LEFT_OPENINGS)     # party wall
    v.wall(C.HOUSE_W, 0, C.HOUSE_W, C.HOUSE_D, t, openings=right_ops)  # flank

    # ---- proposed extension ----
    if show_ext:
        ex0, ew, ed = C.EXT_X0, C.EXT_W, C.EXT_D
        v.wall(ex0, -ed, ex0 + ew, -ed, t, openings=C.EXT_REAR_OPENINGS)
        v.wall(ex0, -ed, ex0, 0, t, openings=C.EXT_LEFT_OPENINGS)
        v.wall(ex0 + ew, -ed, ex0 + ew, 0, t, openings=C.EXT_RIGHT_OPENINGS)
        # dwarf stub walls against the house are implied by the removed opening

    # ---- partitions ----
    if level == "GF":
        parts = C.PARTITIONS_GF
        pops = {(round(a[0]), round(a[1])): a for a in C.PART_OPENINGS_GF}
    else:
        parts = C.PARTITIONS_FF
        pops = {(round(a[0]), round(a[1])): a for a in C.PART_OPENINGS_FF}
    for (x1, y1, x2, y2) in parts:
        key = (round(x1), round(y1))
        op = pops.get(key)
        openings = None
        if op:
            openings = [(op[4], op[5], op[6], {})]
        v.wall(x1, y1, x2, y2, wi, fill=sk.EXIST_FILL, sw=sk.LW_MED,
               openings=openings)

    # ---- room labels ----
    rooms = C.ROOMS_GF if level == "GF" else C.ROOMS_FF
    for (x, y, w, d, name) in rooms:
        cx, cy = x + w / 2, y + d / 2
        v.room(cx, cy, name, C.area_of(w, d))
    if show_ext:
        ix = C.EXT_X0 + C.EXT_WALL / 2
        iy = -C.EXT_D + C.EXT_WALL / 2
        iw = C.EXT_W - C.EXT_WALL
        idp = C.EXT_D - C.EXT_WALL
        v.room(ix + iw / 2, iy + idp / 2, "GARDEN ROOM", C.area_of(iw, idp),
               sub="(new)")


def _plan_dimensions(v, existing: bool, show_ext: bool):
    t = C.WALL_EXT
    # overall width chain (below the plan, south side)
    ybot = -C.EXT_D - 1500 if show_ext else -1500
    v.dim_h(ybot, 0, C.HOUSE_W, f"{int(C.HOUSE_W)}")
    if show_ext:
        v.dim_h(-C.EXT_D - 1500, C.EXT_X0, C.EXT_X0 + C.EXT_W,
                f"{int(C.EXT_W)}", offset=-1500)
    # left side depth chain
    xleft = -1500
    v.dim_v(xleft, 0, C.HOUSE_D, f"{int(C.HOUSE_D)}", side=1)
    if show_ext:
        v.dim_v(xleft, -C.EXT_D, 0, f"{int(C.EXT_D)}", side=1, offset=-1500)


def floor_plan_sheet(existing: bool, level: str, show_ext: bool, number: str,
                     notes=None, legend=None):
    tag = "EXISTING" if existing else "PROPOSED"
    lv = "GROUND FLOOR" if level == "GF" else "FIRST FLOOR"
    scale_txt = "1:100 @ A3"
    s = _sheet(f"{tag} {lv} PLAN", number, scale_txt, notes, legend)

    k = K100
    # centre the view: plan spans roughly x -1.5..7.5 m, y -5.5..10 m
    xmin, xmax = -1800.0, C.HOUSE_W + 1800.0
    ymin = (-C.EXT_D - 2200.0) if show_ext else -2200.0
    ymax = C.HOUSE_D + 1200.0
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    v = View(s, k, 200.0 - cx * k, 150.0 + cy * k)

    _plan_geometry(v, existing, level, show_ext)
    _plan_dimensions(v, existing, show_ext)

    # title / north
    s.north(388, 60, 6)
    s.scale_bar(120, 280, K100, 5000, divisions=5)
    s.text(200, 40, f"{tag} {lv} PLAN", size=3.0, anchor="middle",
           weight="bold")
    return s


# ---------------------------------------------------------------------------
# Roof plan
# ---------------------------------------------------------------------------
def roof_plan_sheet(number: str):
    s = _sheet("PROPOSED ROOF PLAN", number, "1:100 @ A3")
    k = K100
    v = View(s, k, 95.0, 240.0)
    t = C.WALL_EXT

    # house outline
    v.rect(0, 0, C.HOUSE_W, C.HOUSE_D, fill="#f4f4f4", stroke=sk.INK,
           sw=sk.LW_THICK)
    # roof slopes: two pitches meeting at the ridge
    v.line(0, C.HOUSE_D / 2, C.HOUSE_W, C.HOUSE_D / 2, w=sk.LW_MED,
           dash="4,2")
    # pitch arrows
    v.line(C.HOUSE_W / 2, C.HOUSE_D / 2, C.HOUSE_W / 2, C.HOUSE_D, w=sk.LW_THIN)
    v.line(C.HOUSE_W / 2, C.HOUSE_D / 2, C.HOUSE_W / 2, 0, w=sk.LW_THIN)
    v.text(C.HOUSE_W / 2 + 150, C.HOUSE_D * 0.75, "ROOF PITCH 40°",
           size=2.2, cls="t-area")
    v.text(C.HOUSE_W / 2 + 150, C.HOUSE_D * 0.25, "ROOF PITCH 40°",
           size=2.2, cls="t-area")
    # chimney
    v.rect(0, C.HOUSE_D / 2 - 250, 900, 500, fill="url(#hatch-existing)",
           stroke=sk.INK, sw=sk.LW_THIN)
    v.text(450, C.HOUSE_D / 2 - 550, "CHIMNEY", size=1.9, anchor="middle",
           cls="t-small")
    # extension roof: lean-to falling away from the house
    ex0, ew, ed = C.EXT_X0, C.EXT_W, C.EXT_D
    v.rect(ex0, -ed, ew, ed, fill="url(#hatch-roof)", stroke=sk.INK,
           sw=sk.LW_THICK)
    v.line(ex0, 0, ex0 + ew, 0, w=sk.LW_THIN)
    # fall arrow
    ax = ex0 + ew / 2
    v.line(ax, -250, ax, -ed + 250, w=sk.LW_THIN)
    v.poly([(ax, -ed + 150), (ax - 120, -ed + 450), (ax + 120, -ed + 450)],
           fill=sk.INK, stroke=sk.INK, sw=sk.LW_THIN)
    v.text(ax + 250, -ed / 2, "FALL 1:40", size=2.1, cls="t-area")
    v.text(ex0 + ew / 2, -ed / 2 - 500, "NEW SINGLE PLY",
           size=2.1, anchor="middle", cls="t-area")
    v.text(ex0 + ew / 2, -ed / 2 - 900, "MEMBRANE ROOF",
           size=2.1, anchor="middle", cls="t-area")
    # gutter / fascia note
    v.line(ex0, -ed, ex0 + ew, -ed, w=sk.LW_MED)
    v.text(ex0 + ew / 2, -ed - 500, "GUTTER & FASCIA", size=1.9,
           anchor="middle", cls="t-small")

    # dimensions
    v.dim_h(-ed - 1500, ex0, ex0 + ew, f"{int(ew)}", offset=-1500)
    v.dim_v(-1500, -ed, 0, f"{int(ed)}", offset=-1500)

    s.north(388, 60, 6)
    s.scale_bar(120, 280, K100, 5000, divisions=5)
    s.text(210, 30, "PROPOSED ROOF PLAN", size=3.0, anchor="middle",
           weight="bold")
    return s


# ---------------------------------------------------------------------------
# Block plan (site plan) at 1:200
# ---------------------------------------------------------------------------
def block_plan_sheet(number: str):
    s = _sheet("PROPOSED SITE / BLOCK PLAN", number, "1:200 @ A3")
    s.legend = [
        ("new", "Proposed extension (new build)"),
        ("exist", "Existing dwelling"),
        ("dashed", "Red line application boundary"),
    ]
    k = K200
    # plot origin (0,0) = rear-left corner of plot. Road at y = PLOT_D.
    v = View(s, k, 60.0, 285.0)

    # boundary (red line)
    v.rect(0, 0, C.PLOT_W, C.PLOT_D, fill="none", stroke="#d11", sw=0.7)
    # garden / hardstanding tints
    v.rect(0, C.HOUSE_SETBACK + C.HOUSE_D, C.PLOT_W, C.REAR_GARDEN,
           fill="#f7f7f7", stroke="none", sw=0)
    # road
    v.rect(0, C.PLOT_D, C.PLOT_W, 3200, fill="#e9e9e9", stroke=sk.LW_THIN)
    v.text(C.PLOT_W / 2, C.PLOT_D + 1900, "EXAMPLE ROAD", size=2.4,
           anchor="middle", cls="t-area")

    # existing house (grey), neighbour to the left shown dashed
    v.rect(0, C.HOUSE_SETBACK, C.HOUSE_W, C.HOUSE_D,
           fill="url(#hatch-existing)", stroke=sk.INK, sw=sk.LW_MED)
    v.rect(-C.PLOT_W, C.HOUSE_SETBACK, C.PLOT_W, C.HOUSE_D,
           fill="none", stroke=sk.MID, sw=sk.LW_THIN, dash="3,2")
    v.text(-C.PLOT_W / 2, C.HOUSE_SETBACK + C.HOUSE_D + 400,
           "ADJOINING DWELLING (No. 12)", size=2.0, anchor="middle",
           cls="t-small")

    # proposed extension
    ey = C.HOUSE_SETBACK - C.EXT_D
    v.rect(C.EXT_X0, ey, C.EXT_W, C.EXT_D, fill=sk.NEW_FILL, stroke=sk.INK,
           sw=sk.LW_MED)

    # driveway
    v.rect(0, C.HOUSE_SETBACK - C.EXT_D - 1200, C.HOUSE_W, 1200,
           fill="url(#hatch-earth)", stroke="none", sw=0)

    # annotations
    v.text(C.EXT_X0 + C.EXT_W / 2, ey + C.EXT_D / 2 - 200, "EXTENSION",
           size=2.3, anchor="middle", fill="#ffffff", weight="bold")
    v.text(C.HOUSE_W / 2, C.HOUSE_SETBACK + C.HOUSE_D / 2, "DWELLING",
           size=2.3, anchor="middle", weight="bold")
    # garden depth
    v.dim_v(C.PLOT_W + 900, 0, C.HOUSE_SETBACK - C.EXT_D,
            f"{C.m(C.REAR_GARDEN + C.EXT_D, 1)} m", offset=900, side=-1)
    # extension projection
    v.dim_v(C.PLOT_W + 300, ey, C.HOUSE_SETBACK, f"{C.m(C.EXT_D, 2)} m",
            offset=300, side=-1)
    # separation to neighbour boundary
    v.dim_h(ey - 900, 0, C.EXT_X0, f"{int(C.EXT_X0)}", offset=-900)

    s.north(388, 60, 6)
    s.scale_bar(120, 280, K200, 10000, divisions=5)
    s.text(60, 20, "PROPOSED SITE / BLOCK PLAN", size=3.0, weight="bold")
    return s


# ---------------------------------------------------------------------------
# Location plan (schematic) at 1:1250
# ---------------------------------------------------------------------------
def location_plan_sheet(number: str):
    s = _sheet("LOCATION PLAN (SCHEMATIC)", number, "1:1250 @ A3")
    s.notes = [
        "SCHEMATIC ONLY - not to be submitted as the statutory location plan.",
        "A licensed OS location plan (1:1250) must be purchased, with the",
        "application site edged red and any other land owned edged blue.",
    ]
    k = 1 / 1250.0
    v = View(s, k, 210.0, 210.0)

    # surrounding streets grid (schematic)
    for i in range(-2, 4):
        y = i * 40000.0
        v.rect(-90000, y - 3000, 180000, 6000, fill="#e9e9e9", stroke=sk.LW_THIN)
        v.text(70000, y + 900, f"STREET", size=2.0, cls="t-small")
    for j in range(-1, 2):
        x = j * 55000.0
        v.rect(x - 3000, -90000, 6000, 180000, fill="#e9e9e9", stroke=sk.LW_THIN)

    # surrounding terraces (schematic blocks)
    for bx in range(-2, 3):
        for by in range(-2, 3):
            if bx == 0 and by == 0:
                continue
            v.rect(bx * 40000 - 12000, by * 30000 - 5000, 24000, 10000,
                   fill="#dedede", stroke=sk.MID, sw=sk.LW_HAIR)

    # the application plot, edged red
    v.rect(-C.PLOT_W / 2, -C.PLOT_D / 2, C.PLOT_W, C.PLOT_D, fill="none",
           stroke="#d11", sw=0.6)
    v.rect(-C.HOUSE_W / 2, C.HOUSE_SETBACK + C.HOUSE_D - C.PLOT_D / 2,
           C.HOUSE_W, C.HOUSE_D, fill=sk.NEW_FILL, stroke=sk.INK, sw=sk.LW_THIN)
    v.text(0, -C.PLOT_D / 2 - 4000, "APPLICATION SITE (RED LINE)",
           size=2.2, anchor="middle", fill="#d11", weight="bold")
    v.text(0, 0, "No. 14", size=2.0, anchor="middle", cls="t-small")

    s.north(388, 60, 6)
    s.scale_bar(120, 280, 1/1250.0, 50000, divisions=5)
    s.text(210, 30, "LOCATION PLAN", size=3.0, anchor="middle", weight="bold")
    return s


# ---------------------------------------------------------------------------
# Drawing register / cover sheet
# ---------------------------------------------------------------------------
def register_sheet(number: str, rows):
    s = _sheet("DRAWING REGISTER", number, "NTS")
    s.notes = [
        "All drawings A3; do not scale - use figured dimensions only.",
        "Read in conjunction with the planning application form and",
        "the design & access statement.",
    ]
    # PD compliance block
    pd = C.pd_status()

    def tick(ok):
        return "PASS" if ok else "CHECK"

    x, y = 30.0, 34.0
    s.text(x, y, "UK PERMITTED DEVELOPMENT CHECK (Class A, Part 1, GPDO)",
           size=3.0, weight="bold")
    y += 8
    checks = [
        ("Single storey rear extension - max depth (semi/terrace)",
         f"3.00 m", f"{C.m(pd['depth_actual'])} m", tick(pd["depth_ok"])),
        ("Maximum overall height", "4.00 m", f"{C.m(pd['height_actual'])} m",
         tick(pd["height_ok"])),
        ("Maximum eaves height", "3.00 m", f"{C.m(pd['eaves_actual'])} m",
         tick(pd["eaves_ok"])),
        ("Roof materials to match / harmonise", "-", "Match existing", "PASS"),
        ("No verandas/balconies/raised platforms", "-", "None proposed", "PASS"),
        ("Not within a conservation area / AONB / listed", "-", "Assumed",
         "VERIFY"),
    ]
    s.rect(x, y, 360, 6 + len(checks) * 7, fill=sk.PAPER, stroke=sk.INK, sw=sk.LW_THIN)
    hdr = ["Requirement", "PD limit", "Proposed", "Status"]
    cols = [x + 3, x + 175, x + 245, x + 320]
    for i, h in enumerate(hdr):
        s.text(cols[i], y + 5, h, size=2.3, weight="bold")
    s.line(x, y + 7, x + 360, y + 7, sk.LW_THIN, sk.INK)
    yy = y + 7
    for (req, lim, prop, stat) in checks:
        yy += 7
        s.text(cols[0], yy - 1, req, size=2.15, cls="t-note")
        s.text(cols[1], yy - 1, lim, size=2.15, cls="t-note")
        s.text(cols[2], yy - 1, prop, size=2.15, cls="t-note")
        s.text(cols[3], yy - 1, stat, size=2.15, weight="bold",
               fill=("#1a7f37" if stat == "PASS" else "#b26a00"))
        s.line(x, yy + 1, x + 360, yy + 1, sk.LW_HAIR, sk.LIGHT)

    # drawing list
    ly = yy + 12
    s.text(x, ly, "DRAWINGS ISSUED", size=3.0, weight="bold")
    ly += 6
    s.rect(x, ly, 360, 6 + len(rows) * 6.5, fill=sk.PAPER, stroke=sk.INK,
           sw=sk.LW_THIN)
    s.text(x + 3, ly + 5, "No.", size=2.3, weight="bold")
    s.text(x + 30, ly + 5, "Drawing title", size=2.3, weight="bold")
    s.text(x + 210, ly + 5, "Scale", size=2.3, weight="bold")
    s.text(x + 300, ly + 5, "Rev", size=2.3, weight="bold")
    s.line(x, ly + 7, x + 360, ly + 7, sk.LW_THIN, sk.INK)
    ry = ly + 7
    for (no, title, scale) in rows:
        ry += 6.5
        s.text(x + 3, ry - 1, no, size=2.15, cls="t-note")
        s.text(x + 30, ry - 1, title, size=2.15, cls="t-note")
        s.text(x + 210, ry - 1, scale, size=2.15, cls="t-note")
        s.text(x + 300, ry - 1, C.REV, size=2.15, cls="t-note")
        s.line(x, ry + 1.5, x + 360, ry + 1.5, sk.LW_HAIR, sk.LIGHT)
    return s
