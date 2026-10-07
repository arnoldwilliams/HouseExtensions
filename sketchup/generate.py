#!/usr/bin/env python3
"""
generate.py - build the SketchUp-ready model of the house extension.

    python3 generate.py            # writes ../models/house-extension.dae

The COLLADA (.dae) file imports into every version of SketchUp
(File > Import > COLLADA). For a fully native, parametric rebuild inside
SketchUp, load sketchup/house_extension.rb from the Ruby console instead.
"""

from __future__ import annotations

import os

import collada
import geometry3d

OUT = os.path.join(os.path.dirname(__file__), "..", "models")


def build():
    os.makedirs(OUT, exist_ok=True)
    solids, materials = geometry3d.build_model()
    path = os.path.join(OUT, "house-extension.dae")
    collada.write_dae(path, solids, materials)
    return path, solids


if __name__ == "__main__":
    path, solids = build()
    print(f"wrote {os.path.relpath(path)}")
    print(f"{len(solids)} solids, "
          f"{sum(len(s.faces) for s in solids)} triangles")
