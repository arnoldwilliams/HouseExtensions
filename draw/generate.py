#!/usr/bin/env python3
"""
generate.py - build the full UK house-extension planning drawing set as SVG.

Run from the draw/ directory:

    python3 generate.py            # writes ../drawings/*.svg

The SVGs are A3 landscape, true to the stated metric scales, and can be imported
into SmartDraw (SmartDraw > Import, or drag-and-drop the SVG/PDF) where they
remain editable, or printed directly for a UK householder planning application.
"""

from __future__ import annotations

import os

import config as C
import plans
import elevations
import sections
import svgkit as sk

OUT = os.path.join(os.path.dirname(__file__), "..", "drawings")

# (filename, drawing number, title, scale)
REGISTER = [
    ("00-drawing-register", "00", "Drawing register & PD check", "NTS"),
    ("01-location-plan", "01", "Location plan (schematic)", "1:1250"),
    ("02-block-plan", "02", "Proposed site / block plan", "1:200"),
    ("03-existing-ground-floor-plan", "03", "Existing ground floor plan", "1:100"),
    ("04-existing-first-floor-plan", "04", "Existing first floor plan", "1:100"),
    ("05-existing-elevations", "05", "Existing elevations", "1:100"),
    ("06-proposed-ground-floor-plan", "06", "Proposed ground floor plan", "1:100"),
    ("07-proposed-first-floor-plan", "07", "Proposed first floor plan", "1:100"),
    ("08-proposed-elevations", "08", "Proposed elevations", "1:100"),
    ("09-proposed-roof-plan", "09", "Proposed roof plan", "1:100"),
    ("10-proposed-section", "10", "Proposed long section A-A", "1:50"),
]


def build():
    os.makedirs(OUT, exist_ok=True)
    made = []

    def emit(name, sheet):
        path = os.path.join(OUT, name + ".svg")
        sk.write(path, sheet.render())
        made.append(path)

    emit("00-drawing-register",
         plans.register_sheet("00", [(no, t, s) for (_, no, t, s) in REGISTER]))
    emit("01-location-plan", plans.location_plan_sheet("01"))
    emit("02-block-plan", plans.block_plan_sheet("02"))
    emit("03-existing-ground-floor-plan",
         plans.floor_plan_sheet(True, "GF", False, "03"))
    emit("04-existing-first-floor-plan",
         plans.floor_plan_sheet(True, "FF", False, "04"))
    emit("05-existing-elevations", elevations.elevations_sheet(True, "05"))
    emit("06-proposed-ground-floor-plan",
         plans.floor_plan_sheet(False, "GF", True, "06"))
    emit("07-proposed-first-floor-plan",
         plans.floor_plan_sheet(False, "FF", False, "07"))
    emit("08-proposed-elevations", elevations.elevations_sheet(False, "08"))
    emit("09-proposed-roof-plan", plans.roof_plan_sheet("09"))
    emit("10-proposed-section", sections.section_sheet("10"))

    return made


if __name__ == "__main__":
    files = build()
    for f in files:
        print("wrote", os.path.relpath(f))
    print(f"\n{len(files)} sheets written to {os.path.normpath(OUT)}")
