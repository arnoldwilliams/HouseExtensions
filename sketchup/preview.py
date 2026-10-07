#!/usr/bin/env python3
"""
preview.py - render orthographic previews of the massing model.

A tiny software renderer (painter's algorithm, flat shading) so the model can be
checked without opening SketchUp. Writes PNGs to ../preview/.

    python3 preview.py
"""

from __future__ import annotations

import math
import os

import geometry3d

try:
    from PIL import Image, ImageDraw
except ImportError:  # previews are optional
    Image = None

OUT = os.path.join(os.path.dirname(__file__), "..", "preview")

VIEWS = {
    "rear-elevation":  {"dir": (0, 1, 0),  "up": (0, 0, 1), "ortho": True},
    "flank-elevation": {"dir": (-1, 0, 0), "up": (0, 0, 1), "ortho": True},
    "plan":            {"dir": (0, 0, -1), "up": (0, 1, 0), "ortho": True},
    "3d":              {"dir": (0.55, 0.6, -0.6), "up": (0, 0, 1), "ortho": False},
}

LIGHT = (-0.35, -0.55, 0.75)


def _norm(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return (v[0] / m, v[1] / m, v[2] / m)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def render(solids, materials, view, size=(1000, 750), bg=(255, 255, 255)):
    d = _norm(view["dir"])                 # camera -> scene
    up = _norm(view["up"])
    right = _norm(_cross(up, d))
    tup = _norm(_cross(d, right))

    tris = []
    for s in solids:
        base = materials[s.material]["rgb"]
        for (i, j, k) in s.faces:
            p0, p1, p2 = s.verts[i], s.verts[j], s.verts[k]
            n = _norm(_cross(_sub(p1, p0), _sub(p2, p0)))
            # face towards camera?  (view dir points into scene)
            facing = _dot(n, d) < 0
            if not facing:
                n = (-n[0], -n[1], -n[2])
            inten = 0.35 + 0.65 * max(0.0, _dot(n, _norm(LIGHT)))
            col = tuple(min(255, int(c * 255 * inten)) for c in base)
            pts2d = []
            depth = 0.0
            for p in (p0, p1, p2):
                u = _dot(p, right)
                v = _dot(p, tup)
                pts2d.append((u, v))
                depth += _dot(p, d)
            tris.append((depth / 3.0, pts2d, col))

    tris.sort(key=lambda t: -t[0])         # far first

    xs = [p[0] for t in tris for p in t[1]]
    ys = [p[1] for t in tris for p in t[1]]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = 0.06 * max(maxx - minx, maxy - miny)
    minx -= pad; maxx += pad; miny -= pad; maxy += pad
    W, H = size
    scale = min(W / (maxx - minx), H / (maxy - miny))

    img = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(img)
    for _, pts, col in tris:
        pp = [((x - minx) * scale, H - (y - miny) * scale) for (x, y) in pts]
        dr.polygon(pp, fill=col, outline=(70, 70, 70))
    return img


def main():
    if Image is None:
        print("Pillow not installed; skipping previews")
        return 1
    os.makedirs(OUT, exist_ok=True)
    solids, materials = geometry3d.build_model()
    for name, view in VIEWS.items():
        img = render(solids, materials, view)
        path = os.path.join(OUT, name + ".png")
        img.save(path)
        print("preview", os.path.relpath(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
