"""
collada.py - write the massing model as a COLLADA 1.4.1 (.dae) file.

COLLADA is an open XML schema that every version of SketchUp (Make, Pro, Go,
Web) can import via File > Import > COLLADA (.dae). This gives a SketchUp-
ready model without needing the proprietary .skp format.

Geometry is written in metres with Z up, which is what SketchUp expects.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

MM = 0.001   # millimetres -> metres


def _fmt(v):
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def write_dae(path, solids, materials, up_axis="Z_UP"):
    L = []
    a = L.append
    a('<?xml version="1.0" encoding="utf-8"?>')
    a('<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" '
      'version="1.4.1">')
    a('  <asset>')
    a('    <contributor><authoring_tool>HouseExtensions sketchup '
      'generator</authoring_tool></contributor>')
    a('    <created>2026-10-07T00:00:00Z</created>')
    a('    <unit meter="1" name="meter"/>')
    a(f'    <up_axis>{up_axis}</up_axis>')
    a('  </asset>')

    # ---- effects & materials ----
    a('  <library_effects>')
    for key, mat in materials.items():
        r, g, b = mat["rgb"]
        a(f'    <effect id="{key}-effect">')
        a('      <profile_COMMON><technique sid="common"><lambert>')
        a(f'        <diffuse><color sid="diffuse">'
          f'{_fmt(r)} {_fmt(g)} {_fmt(b)} 1</color></diffuse>')
        a('      </lambert></technique></profile_COMMON>')
        a('    </effect>')
    a('  </library_effects>')

    a('  <library_materials>')
    for key, mat in materials.items():
        a(f'    <material id="{key}-material" name="{escape(mat["name"])}">')
        a(f'      <instance_effect url="#{key}-effect"/>')
        a('    </material>')
    a('  </library_materials>')

    # ---- geometries ----
    a('  <library_geometries>')
    for i, s in enumerate(solids):
        gid = f"{_safe(s.name)}-geo"
        pos = []
        for (x, y, z) in s.verts:
            pos += [x * MM, y * MM, z * MM]
        flat = " ".join(_fmt(p) for p in pos)
        idx = []
        for tri in s.faces:
            idx += list(tri)
        a(f'    <geometry id="{gid}" name="{escape(s.name)}">')
        a('      <mesh>')
        a(f'        <source id="{_safe(s.name)}-pos">')
        a(f'          <float_array id="{_safe(s.name)}-pos-array" '
          f'count="{len(pos)}">{flat}</float_array>')
        a('          <technique_common>')
        a(f'            <accessor source="#{_safe(s.name)}-pos-array" '
          f'count="{len(s.verts)}" stride="3">')
        a('              <param name="X" type="float"/>')
        a('              <param name="Y" type="float"/>')
        a('              <param name="Z" type="float"/>')
        a('            </accessor>')
        a('          </technique_common>')
        a('        </source>')
        a(f'        <vertices id="{_safe(s.name)}-verts">')
        a(f'          <input semantic="POSITION" '
          f'source="#{_safe(s.name)}-pos"/>')
        a('        </vertices>')
        a(f'        <triangles material="{s.material}-material" '
          f'count="{len(s.faces)}">')
        a(f'          <input semantic="VERTEX" '
          f'source="#{_safe(s.name)}-verts" offset="0"/>')
        a(f'          <p>{" ".join(str(x) for x in idx)}</p>')
        a('        </triangles>')
        a('      </mesh>')
        a('    </geometry>')
    a('  </library_geometries>')

    # ---- scene ----
    a('  <library_visual_scenes>')
    a('    <visual_scene id="Scene" name="HouseExtensions">')
    for s in solids:
        gid = f"{_safe(s.name)}-geo"
        a(f'      <node id="{_safe(s.name)}" name="{escape(s.name)}" '
          f'type="NODE">')
        a(f'        <instance_geometry url="#{gid}">')
        a('          <bind_material><technique_common>')
        a(f'            <instance_material symbol="{s.material}-material" '
          f'target="#{s.material}-material"/>')
        a('          </technique_common></bind_material>')
        a('        </instance_geometry>')
        a('      </node>')
    a('    </visual_scene>')
    a('  </library_visual_scenes>')

    a('  <scene><instance_visual_scene url="#Scene"/></scene>')
    a('</COLLADA>')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def _safe(name):
    return "".join(c if c.isalnum() else "_" for c in name)
