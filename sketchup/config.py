"""
config.py - dimensions for the SketchUp massing model.

This mirrors the numbers used by the 2D SVG drawing set (see the
`uk-extension-drawings` branch). It is duplicated here so the SketchUp model is
self-contained on this branch. All values are millimetres.

Change these numbers, re-run `generate.py`, and re-load `house_extension.rb`
in SketchUp to regenerate the model.
"""

# Existing semi-detached house. Origin (0,0) is the rear-left corner at ground
# level; +x runs to the flank wall, +y runs to the front (principal) elevation.
HOUSE_W = 6000.0
HOUSE_D = 8500.0
WALL_EXT = 300.0
EAVES = 2700.0
RIDGE = 6200.0

# Proposed single-storey rear extension (lean-to roof rising to the house).
EXT_D = 4000.0
EXT_W = 5000.0
EXT_X0 = 500.0
EXT_HOUSE_H = 2700.0
EXT_REAR_H = 2450.0

# Garden context.
PATIO_DEPTH = 3000.0
