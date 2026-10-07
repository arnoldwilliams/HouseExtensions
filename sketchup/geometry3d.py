"""
geometry3d.py - shared 3D massing model of the dwelling and extension.

The same configuration that drives the 2D SVG drawing set (draw/config.py)
builds a small set of solids here. Those solids feed two exporters:

* a COLLADA (.dae) file, which every version of SketchUp can import, and
* the native SketchUp Ruby script, which rebuilds the same massing in SketchUp
  using the Ruby API.

Units are millimetres, matching draw/config.py. The COLLADA writer converts to
metres (SketchUp's conventional working unit) via the <unit> element.
"""

from __future__ import annotations

import config as C


class Solid:
    """A triangle mesh with a name and a material key."""

    def __init__(self, name, material, verts, faces):
        self.name = name
        self.material = material
        self.verts = verts          # list of (x, y, z) in mm
        self.faces = faces          # list of triangles (i, j, k)


def _quad(a, b, c, d):
    return [(a, b, c), (a, c, d)]


def box(name, material, x0, y0, z0, x1, y1, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = []
    f += _quad(0, 3, 2, 1)      # base (down)
    f += _quad(4, 5, 6, 7)      # top (up)
    f += _quad(0, 1, 5, 4)      # -y
    f += _quad(1, 2, 6, 5)      # +x
    f += _quad(2, 3, 7, 6)      # +y
    f += _quad(3, 0, 4, 7)      # -x
    return Solid(name, material, v, f)


def gable(name, material, x0, y0, x1, y1, z_eaves, z_ridge):
    """Gable solid, ridge running along x at y = (y0+y1)/2."""
    ym = (y0 + y1) / 2.0
    v = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0),
         (x0, y0, z_eaves), (x1, y0, z_eaves), (x1, y1, z_eaves), (x0, y1, z_eaves),
         (x0, ym, z_ridge), (x1, ym, z_ridge)]
    f = []
    f += _quad(0, 3, 2, 1)              # base
    f += _quad(4, 5, 9, 8)              # -y roof slope
    f += _quad(6, 7, 8, 9)              # +y roof slope
    f += _quad(0, 1, 5, 4)              # -y wall
    f += _quad(1, 2, 6, 5)              # +x wall
    f += _quad(2, 3, 7, 6)              # +y wall
    f += _quad(3, 0, 4, 7)              # -x wall
    f += [(0, 3, 7), (0, 7, 8), (0, 8, 4)]   # x0 gable end (pentagon)
    f += [(1, 2, 6), (1, 6, 9), (1, 9, 5)]   # x1 gable end (pentagon)
    return Solid(name, material, v, f)


def lean_to(name, material, x0, y0, x1, y1, h_high, h_low, high_edge="y1"):
    """Shed roof volume: slopes from `high_edge` side down to the other."""
    if high_edge == "y1":
        top = [(x0, y0, h_low), (x1, y0, h_low), (x1, y1, h_high), (x0, y1, h_high)]
    else:
        top = [(x0, y0, h_high), (x1, y0, h_high), (x1, y1, h_low), (x0, y1, h_low)]
    v = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)] + top
    f = []
    f += _quad(0, 3, 2, 1)
    f += _quad(4, 5, 6, 7)
    f += _quad(0, 1, 5, 4)
    f += _quad(1, 2, 6, 5)
    f += _quad(2, 3, 7, 6)
    f += _quad(3, 0, 4, 7)
    return Solid(name, material, v, f)


# ---------------------------------------------------------------------------
# Model assembly
# ---------------------------------------------------------------------------
def build_model():
    """Return (solids, materials) for the example dwelling + extension."""
    t = C.WALL_EXT
    solids = []

    # Existing house body with a pitched roof (ridge along x at y = D/2).
    solids.append(gable("House", "brick", 0.0, 0.0, C.HOUSE_W, C.HOUSE_D,
                        C.EAVES, C.RIDGE))

    # Party-wall neighbour hint (semi-detached), mirrored to the left.
    solids.append(gable("Adjoining dwelling", "brick_existing",
                        -C.HOUSE_W, 0.0, 0.0, C.HOUSE_D, C.EAVES, C.RIDGE))

    # Chimney on the flank of the ridge.
    solids.append(box("Chimney", "brick",
                      C.HOUSE_W - 900.0, C.HOUSE_D / 2.0 - 250.0, 0.0,
                      C.HOUSE_W - 100.0, C.HOUSE_D / 2.0 + 250.0, C.RIDGE + 700.0))

    # Proposed single-storey rear extension (lean-to rising to the house).
    ex0, ew, ed = C.EXT_X0, C.EXT_W, C.EXT_D
    solids.append(lean_to("Extension", "brick", ex0, -ed, ex0 + ew, 0.0,
                          C.EXT_HOUSE_H, C.EXT_REAR_H, "y1"))
    # Thin roof slab, a distinct finish on top of the extension.
    solids.append(lean_to("Extension roof", "roof",
                          ex0 - 50.0, -ed - 50.0, ex0 + ew + 50.0, 0.0,
                          C.EXT_HOUSE_H + 120.0, C.EXT_REAR_H + 120.0, "y1"))

    # Patio slab in the garden (ground context).
    solids.append(box("Patio", "paving",
                      ex0 - 200.0, -ed - 3000.0, -150.0,
                      ex0 + ew + 200.0, -ed - 50.0, 0.0))

    materials = {
        "brick":          {"rgb": (0.78, 0.66, 0.52), "name": "Brick (existing)"},
        "brick_existing": {"rgb": (0.72, 0.72, 0.72), "name": "Adjoining dwelling"},
        "roof":           {"rgb": (0.28, 0.30, 0.33), "name": "Roof (slate/membrane)"},
        "paving":         {"rgb": (0.80, 0.80, 0.78), "name": "Paving"},
    }
    return solids, materials
