# HouseExtensions

Planning and design files for a **single-storey rear extension to a typical UK
semi-detached house**.

| Folder | What it contains |
|--------|------------------|
| `sketchup/` | 3D massing model for SketchUp (COLLADA import + native Ruby script) |
| `models/` | `house-extension.dae` - the SketchUp-importable 3D model |
| `preview/` | orthographic preview renders of the 3D model |

A companion **2D drawing set** (location plan, block plan, existing/proposed
floor plans, elevations, roof plan and section, as SVG + A3 PDF) lives on the
`uk-extension-drawings` branch.

## SketchUp

The 3D model of the scheme is in `sketchup/`. SketchUp's native `.skp` format is
proprietary, so the model is provided two ways:

* **`models/house-extension.dae`** - a COLLADA file that **every version of
  SketchUp** imports via `File > Import > COLLADA`.
* **`sketchup/house_extension.rb`** - a Ruby script that rebuilds the model
  natively inside SketchUp, with named groups, materials and plan/elevation/3D
  scenes.

See [`sketchup/README.md`](sketchup/README.md) for the full workflow.

## Regenerating the model

```bash
cd sketchup
python3 generate.py     # rebuild models/house-extension.dae
python3 preview.py      # optional orthographic previews
```

All dimensions live in `sketchup/config.py` (millimetres); edit and re-run to
change the scheme.

> Worked example for design and illustration - not professional architectural,
> planning or structural advice.

