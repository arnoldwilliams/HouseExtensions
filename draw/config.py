"""
config.py - project parameters for the example UK house extension.

All real-world dimensions are in millimetres. Change the numbers here and every
drawing regenerates (plans, elevations, section, roof plan, block plan).

The worked example is a typical post-war SEMI-DETACHED house in England with a
single-storey rear extension. The extension is deliberately set out so that the
drawing set doubles as a worked demonstration of the UK permitted development
(PD) limits - see `pd_status()`.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Metadata shown in the title block
# ---------------------------------------------------------------------------
PROJECT = "PROPOSED SINGLE STOREY REAR EXTENSION"
ADDRESS = "14 Example Road, Anytown, AB1 2CD"
CLIENT = "Mr & Mrs Sample"
DATE = "October 2026"
DRAWN = "AI"
CHECKED = "—"
REV = "P1"

# ---------------------------------------------------------------------------
# Existing house (semi-detached). Origin (0,0) is the rear-left corner of the
# ORIGINAL dwelling at finished ground floor level. +x runs east (right) to the
# flank wall; +y runs north (towards the front/principal elevation). The party
# wall is the LEFT (x = 0) wall. Roof ridge runs left-right at y = HOUSE_D/2.
# ---------------------------------------------------------------------------
HOUSE_W = 6000.0          # width, party wall to flank wall
HOUSE_D = 8500.0          # depth, rear wall to front (principal) elevation
WALL_EXT = 300.0          # external wall thickness
WALL_INT = 100.0          # internal partition thickness
EAVES = 2700.0            # eaves height
RIDGE = 6200.0            # ridge height above ground

# ---------------------------------------------------------------------------
# PROPOSED single storey rear extension (lean-to roof falling away from house)
# ---------------------------------------------------------------------------
EXT_D = 4000.0            # projection beyond the rear wall of the ORIGINAL house
EXT_W = 5000.0            # overall width of the extension
EXT_WALL = 300.0          # new external cavity wall thickness
EXT_X0 = 500.0            # extension left wall from the party wall
EXT_HOUSE_H = 2700.0      # height of extension roof against the house
EXT_REAR_H = 2450.0       # height of extension roof at the rear (garden) wall

# ---------------------------------------------------------------------------
# Site / garden (for the block plan). Road at the front (high y).
# ---------------------------------------------------------------------------
PLOT_W = 6900.0
PLOT_D = 25000.0
HOUSE_SETBACK = 6000.0    # front wall of house to the highway
REAR_GARDEN = PLOT_D - HOUSE_SETBACK - HOUSE_D

# ---------------------------------------------------------------------------
# Existing ground-floor room layout, rear -> front. Tuples are
# (x, y, width, depth, name) in millimetres.
# ---------------------------------------------------------------------------
ROOMS_GF = [
    (0.0,    0.0,    3000.0, 3000.0, "DINING ROOM"),
    (3000.0, 0.0,    3000.0, 3000.0, "KITCHEN"),
    (0.0,    3000.0, 3600.0, 5500.0, "LIVING / DINING"),
    (3600.0, 3000.0, 2400.0, 2200.0, "STAIRS / WC"),
    (3600.0, 5200.0, 2400.0, 3300.0, "HALL"),
]

ROOMS_FF = [
    (0.0,    0.0,    3600.0, 3000.0, "BEDROOM 3"),
    (3600.0, 0.0,    2400.0, 3000.0, "BEDROOM 4"),
    (0.0,    3000.0, 3600.0, 2200.0, "LANDING"),
    (3600.0, 3000.0, 2400.0, 2200.0, "BATHROOM"),
    (0.0,    5200.0, 3600.0, 3300.0, "BEDROOM 1"),
    (3600.0, 5200.0, 2400.0, 3300.0, "BEDROOM 2"),
]

# Internal partitions: (x1, y1, x2, y2) centrelines.
PARTITIONS_GF = [
    (3000.0, 0.0,    3000.0, 3000.0),
    (0.0,    3000.0, 6000.0, 3000.0),
    (3600.0, 3000.0, 3600.0, 8500.0),
    (3600.0, 5200.0, 6000.0, 5200.0),
]
PARTITIONS_FF = [
    (3600.0, 0.0,    3600.0, 3000.0),
    (0.0,    3000.0, 6000.0, 3000.0),
    (3600.0, 3000.0, 3600.0, 8500.0),
    (3600.0, 5200.0, 6000.0, 5200.0),
]

# Openings in partitions: (x1, y1, x2, y2, a, b, kind)
PART_OPENINGS_GF = [
    (3000.0, 0.0, 3000.0, 3000.0, 2000.0, 2900.0, "door"),
    (0.0, 3000.0, 6000.0, 3000.0, 600.0, 2400.0, "opening"),
    (0.0, 3000.0, 6000.0, 3000.0, 4300.0, 5300.0, "door"),
    (3600.0, 3000.0, 3600.0, 8500.0, 3200.0, 4100.0, "door"),
]
PART_OPENINGS_FF = [
    (3600.0, 0.0, 3600.0, 3000.0, 1900.0, 2800.0, "door"),
    (0.0, 3000.0, 6000.0, 3000.0, 600.0, 1700.0, "door"),
    (0.0, 3000.0, 6000.0, 3000.0, 3800.0, 4900.0, "door"),
    (3600.0, 3000.0, 3600.0, 8500.0, 3200.0, 4100.0, "door"),
]

# External openings: (a, b, kind, opts) measured along the wall run, which
# starts at the inner face of the corner (t/2) and runs with the wall.
FRONT_OPENINGS = [
    (550.0, 2650.0, "win", {}),
    (4450.0, 5450.0, "door", {"swing": 1}),
]
REAR_OPENINGS = [
    (650.0, 2050.0, "win", {}),
    (3250.0, 4450.0, "win", {}),
    (4850.0, 5650.0, "door", {"swing": -1}),
]
LEFT_OPENINGS = []
RIGHT_OPENINGS = [
    (650.0, 1850.0, "win", {}),
]

# Extension openings (measured from the extension's inner corner).
EXT_REAR_OPENINGS = [(850.0, 3850.0, "slider", {})]
EXT_LEFT_OPENINGS = [(900.0, 2100.0, "win", {})]
EXT_RIGHT_OPENINGS = [(900.0, 2100.0, "win", {})]

# ---------------------------------------------------------------------------
# Derived helpers
# ---------------------------------------------------------------------------
HOUSE_AREA = HOUSE_W * HOUSE_D


def pd_status() -> dict:
    """Permitted development compliance checks (Class A, Part 1, GPDO).

    For a single-storey rear extension on a house that is NOT detached, the
    'smaller' PD allowance is a maximum depth of 3 m, maximum height 4 m and
    maximum eaves height 3 m. The width limitation (half the original house)
    applies to SIDE extensions, so it is reported but not applied here.
    """
    return {
        "depth_limit": 3000.0,
        "depth_actual": EXT_D,
        "depth_ok": EXT_D <= 3000.0,
        "height_limit": 4000.0,
        "height_actual": EXT_HOUSE_H,
        "height_ok": EXT_HOUSE_H <= 4000.0,
        "eaves_limit": 3000.0,
        "eaves_actual": EXT_REAR_H,
        "eaves_ok": EXT_REAR_H <= 3000.0,
        "width_limit": HOUSE_W / 2.0,
        "width_actual": EXT_W,
        "width_ok": EXT_W <= HOUSE_W / 2.0,
    }


def area_of(w_mm: float, d_mm: float) -> float:
    """Area in square metres."""
    return (w_mm / 1000.0) * (d_mm / 1000.0)


def m(v_mm: float, dp: int = 2) -> str:
    """Format millimetres as a metre string."""
    return f"{v_mm/1000.0:.{dp}f}"
