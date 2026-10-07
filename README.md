# HouseExtensions

Planning drawings for a **single-storey rear extension to a typical UK
semi-detached house**, produced as a complete, to-scale A3 drawing set.

The set is generated from a parametric Python script, so changing a few numbers
in `draw/config.py` regenerates every plan, elevation and section. The output is
delivered as **SVG and PDF**, both of which import straight into **SmartDraw**
(or any other editor), and as editable source if you prefer to work in CAD.

---

## About SmartDraw and the `.sdr` file format

SmartDraw's native files (`.sdr` / `.sdd`) are a **proprietary binary format**
that can only be written by SmartDraw itself - there is no open specification
and no third-party library that can generate them. Rather than pretend
otherwise, this repository produces the drawings in formats SmartDraw **imports**
and keeps fully editable:

* **SVG** - `SmartDraw > Import > SVG` (or drag-and-drop). Vector, editable.
* **PDF** - `SmartDraw > Import`, or open the PDF directly (A3 landscape).

If you specifically need a native `.sdr`, open one of the imported drawings in
SmartDraw and `File > Save As` to `.sdr`. Everything then behaves like a native
SmartDraw document.

---

## The drawing set

| No. | Drawing | Scale | File |
|-----|---------|-------|------|
| 00 | Drawing register & permitted development check | NTS | `drawings/00-drawing-register.svg` |
| 01 | Location plan (schematic) | 1:1250 | `drawings/01-location-plan.svg` |
| 02 | Proposed site / block plan | 1:200 | `drawings/02-block-plan.svg` |
| 03 | Existing ground floor plan | 1:100 | `drawings/03-existing-ground-floor-plan.svg` |
| 04 | Existing first floor plan | 1:100 | `drawings/04-existing-first-floor-plan.svg` |
| 05 | Existing elevations (rear, front, flank) | 1:100 | `drawings/05-existing-elevations.svg` |
| 06 | Proposed ground floor plan | 1:100 | `drawings/06-proposed-ground-floor-plan.svg` |
| 07 | Proposed first floor plan | 1:100 | `drawings/07-proposed-first-floor-plan.svg` |
| 08 | Proposed elevations (rear, front, flank) | 1:100 | `drawings/08-proposed-elevations.svg` |
| 09 | Proposed roof plan | 1:100 | `drawings/09-proposed-roof-plan.svg` |
| 10 | Proposed long section A-A | 1:50 | `drawings/10-proposed-section.svg` |

Every sheet is **A3 landscape (420 x 297 mm)** and carries the title, drawing
number, revision, scale, a **scale bar** and a **north point** - the elements UK
local planning authorities expect on a householder application.

---

## UK planning context

The drawings follow the conventions requested by UK councils for a **householder
planning application** and are drawn to the recognised metric scales:

* Site / block plan - **1:200** (or 1:500)
* Floor plans, elevations, roof plan - **1:100** (or 1:50)
* Sections - **1:50** (or 1:100)
* Location plan - **1:1250** (or 1:2500)

The example scheme is set out against the permitted development limits for a
semi-detached house (Class A, Part 1, GPDO), and sheet 00 checks the numbers:

| Requirement | PD limit (non-detached) | Example scheme |
|-------------|-------------------------|----------------|
| Single-storey rear extension depth | 3.0 m | 3.5 m * |
| Maximum height | 4.0 m | 2.7 m |
| Maximum eaves height | 3.0 m | 2.45 m |

\* The example extension is 3.5 m deep, which is **beyond** the 3 m "smaller"
permitted development allowance and would therefore normally require planning
permission (or the larger-extension neighbour consultation route). This is
deliberate - the drawing set is a worked *planning application*, and sheet 00
shows the check honestly rather than assuming a pass. Set `EXT_D` to 3000 in
`draw/config.py` to regenerate a scheme that is clearly within PD.

### Before you submit

1. **Location plan** - buy a licensed Ordnance Survey location plan (1:1250)
   with the site edged red. The one here is a labelled *schematic* only.
2. **Existing vs proposed** - both are provided, as required.
3. **Materials** - annotate the actual brick, roof and window finishes.
4. **Verify** - conservation area, Article 2(3) land, listed status and any
   restrictive covenants all change what is permitted. Check with your LPA.
5. **Checklist** - each council publishes its own validation checklist; confirm
   the drawing list against it.

> This is a worked example for design and illustration, not professional
> architectural, planning or structural advice.

---

## Regenerating the drawings

Requires only Python 3 (no third-party packages) and, for PDF export, a
headless Chromium.

```bash
cd draw
python3 generate.py        # writes ../drawings/*.svg
python3 convert_pdf.py     # writes ../drawings/*.pdf (A3 landscape)
```

### Changing the design

All geometry lives in `draw/config.py`:

| Parameter | Meaning |
|-----------|---------|
| `HOUSE_W`, `HOUSE_D` | existing house width / depth |
| `EAVES`, `RIDGE` | existing eaves / ridge heights |
| `EXT_D`, `EXT_W` | extension depth / width |
| `EXT_X0` | extension offset from the party wall |
| `EXT_HOUSE_H`, `EXT_REAR_H` | extension roof height at house / rear |
| `ROOMS_GF`, `ROOMS_FF` | room layouts (position, size, name) |
| `*_OPENINGS` | doors and windows, measured along each wall |

Edit the numbers and re-run `generate.py`; every sheet updates and stays to
scale.

### Source layout

| File | Role |
|------|------|
| `draw/config.py` | all project dimensions and metadata |
| `draw/svgkit.py` | dependency-free SVG sheet toolkit (frame, title block, scale bar, dimensions, north point) |
| `draw/geometry.py` | real-mm to paper-mm `View`, walls with openings, door/window symbols |
| `draw/plans.py` | floor plans, roof plan, block plan, location plan, register |
| `draw/elevations.py` | rear, front and flank elevations |
| `draw/sections.py` | long section |
| `draw/generate.py` | builds the whole set |
| `draw/convert_pdf.py` | SVG to A3 PDF via headless Chromium |
