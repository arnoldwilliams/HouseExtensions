# SketchUp model - UK house extension

A 3D massing model of the same example scheme as the 2D drawing set: a
single-storey rear extension to a typical UK semi-detached house, with the
adjoining dwelling shown for context.

SketchUp's native `.skp` format is proprietary and can only be written by
SketchUp itself. This folder therefore gives you two ways to get the model into
SketchUp, both driven by the same dimensions in `config.py`:

| Approach | File | Works in |
|----------|------|----------|
| **Import a model** | `../models/house-extension.dae` | Every SketchUp (Make, Pro, Go, Web) |
| **Rebuild natively** | `house_extension.rb` | SketchUp Pro / Make (Ruby console or .rbz) |

---

## Option 1 - import the COLLADA model

COLLADA (`.dae`) is an open XML schema that all versions of SketchUp import.

1. In SketchUp: **File > Import...**
2. Set the file type to **COLLADA (\*.dae)**.
3. Choose `models/house-extension.dae` and click **Import**.

You get the house, the adjoining dwelling, the chimney, the proposed extension
with its lean-to roof, and a patio slab, each as a named group with materials
(brick, context, roof, paving).

> Prefer a native file? After importing, **File > Save As** to `.skp`.

## Option 2 - rebuild natively with Ruby

`house_extension.rb` builds the geometry with the SketchUp Ruby API
(`add_face` + `pushpull`), assigns materials, and creates five scenes.

1. Open SketchUp and show the console: **Window > Ruby Console**.
2. Run:

   ```ruby
   load 'C:/path/to/HouseExtensions/sketchup/house_extension.rb'
   ```

   (On macOS use the full POSIX path, e.g. `/Users/you/.../house_extension.rb`.)

3. The model is built as one undoable operation and five scenes are added:

   * `01 Ground floor plan`
   * `02 Rear elevation`
   * `03 Front elevation`
   * `04 Flank elevation`
   * `05 3D view`

To package it as an extension instead, wrap the file in a `.rbz` (a zip with the
`.rb` inside) and load it via **Extension Manager**.

---

## Regenerating

Edit `config.py`, then:

```bash
cd sketchup
python3 generate.py     # rewrites ../models/house-extension.dae
python3 preview.py      # optional: orthographic PNG previews in ../preview
```

Reload `house_extension.rb` in SketchUp to rebuild the native model.

### Parameters (all millimetres)

| Parameter | Meaning |
|-----------|---------|
| `HOUSE_W`, `HOUSE_D` | existing house width / depth |
| `EAVES`, `RIDGE` | existing eaves / ridge heights |
| `EXT_D`, `EXT_W` | extension depth / width |
| `EXT_X0` | extension offset from the party wall |
| `EXT_HOUSE_H`, `EXT_REAR_H` | extension roof height at the house / rear |
| `PATIO_DEPTH` | garden patio slab depth (context) |

## Source layout

| File | Role |
|------|------|
| `config.py` | model dimensions |
| `geometry3d.py` | builds the solids (house gable, extension lean-to, etc.) |
| `collada.py` | writes the COLLADA 1.4.1 `.dae` |
| `generate.py` | entry point: builds the `.dae` |
| `house_extension.rb` | native SketchUp Ruby script |
| `preview.py` | dependency-light orthographic preview renderer |

## Previews

`../preview/` holds orthographic renders produced by `preview.py`, so the massing
can be reviewed without opening SketchUp:

* `plan.png`, `rear-elevation.png`, `flank-elevation.png`, `3d.png`

> The previews are a sanity check on massing only - SketchUp itself gives the
> proper plan, elevation and 3D scenes.

---

> This is a worked example for design and illustration, not professional
> architectural, planning or structural advice.
