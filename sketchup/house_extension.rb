# house_extension.rb
#
# Builds the example UK house-extension model natively in SketchUp, using the
# same massing and dimensions as the SVG drawing set and the COLLADA export.
#
# How to run
#   * SketchUp Pro / Make: Window > Ruby Console, then:
#         load '<path>/sketchup/house_extension.rb'
#   * Or wrap in a .rbz extension and load through Extension Manager.
#
# The script creates a model with named groups, materials, and five scenes
# (ground floor plan, rear / front / flank elevations, and a 3D view) so the
# result mirrors the 2D drawing set. Everything is wrapped in one undo step.
#
# All dimensions are millimetres and mirror draw/config.py. Change the CONFIG
# values and re-run to regenerate a different scheme.

module HouseExtensions
  CONFIG = {
    # existing house
    house_w: 6000.0,
    house_d: 8500.0,
    wall_ext: 300.0,
    eaves: 2700.0,
    ridge: 6200.0,
    # proposed single-storey rear extension
    ext_d: 4000.0,
    ext_w: 5000.0,
    ext_x0: 500.0,
    ext_house_h: 2700.0,
    ext_rear_h: 2450.0,
    # context
    patio_depth: 3000.0
  }.freeze

  MATERIALS = {
    brick:          { rgb: [199, 168, 133], name: 'Brick (existing)' },
    brick_existing: { rgb: [184, 184, 184], name: 'Adjoining dwelling' },
    roof:           { rgb: [71, 77, 84],    name: 'Roof (slate/membrane)' },
    paving:         { rgb: [204, 204, 199], name: 'Paving' }
  }.freeze

  # -- helpers --------------------------------------------------------------

  def self.pt(x, y, z)
    Geom::Point3d.new(x.mm, y.mm, z.mm)
  end

  def self.material(model, key)
    spec = MATERIALS[key]
    mat = model.materials[spec[:name]] || model.materials.add(spec[:name])
    mat.color = Sketchup::Color.new(*spec[:rgb])
    mat
  end

  def self.finish(entities, material)
    entities.grep(Sketchup::Face).each do |f|
      f.material = material
      f.back_material = material
    end
  end

  # A rectangular prism. Base rectangle at z0, extruded up to z1.
  def self.box(model, name, x0, y0, z0, x1, y1, z1, material)
    grp = model.active_entities.add_group
    grp.name = name
    ents = grp.entities
    face = ents.add_face(pt(x0, y0, z0), pt(x1, y0, z0),
                         pt(x1, y1, z0), pt(x0, y1, z0))
    face.pushpull((z1 - z0).mm) if face
    finish(ents, material)
    grp
  end

  # A gable prism: pentagon profile in the y-z plane, extruded along x.
  def self.gable(model, name, x0, y0, x1, y1, z_eaves, z_ridge, material)
    grp = model.active_entities.add_group
    grp.name = name
    ents = grp.entities
    ym = (y0 + y1) / 2.0
    profile = [pt(x0, y0, 0), pt(x0, y1, 0), pt(x0, y1, z_eaves),
               pt(x0, ym, z_ridge), pt(x0, y0, z_eaves)]
    face = ents.add_face(profile)
    if face
      d = (face.normal.x >= 0 ? 1 : -1) * (x1 - x0).mm
      face.pushpull(d)
    end
    finish(ents, material)
    grp
  end

  # A shed/lean-to prism: trapezoid profile in the y-z plane, extruded along x.
  def self.lean_to(model, name, x0, y0, x1, y1, h_high, h_low,
                   high_edge, material)
    grp = model.active_entities.add_group
    grp.name = name
    ents = grp.entities
    if high_edge == 'y1'
      profile = [pt(x0, y0, 0), pt(x0, y1, 0), pt(x0, y1, h_high),
                 pt(x0, y0, h_low)]
    else
      profile = [pt(x0, y0, 0), pt(x0, y1, 0), pt(x0, y1, h_low),
                 pt(x0, y0, h_high)]
    end
    face = ents.add_face(profile)
    if face
      d = (face.normal.x >= 0 ? 1 : -1) * (x1 - x0).mm
      face.pushpull(d)
    end
    finish(ents, material)
    grp
  end

  # -- scenes ---------------------------------------------------------------

  def self.add_scene(model, name, eye, target, up, ortho)
    page = model.pages.add(name)
    model.active_view.camera =
      Sketchup::Camera.new(eye, target, up, !ortho)
    model.active_view.zoom_extents
    page.update
    page
  end

  # -- build ----------------------------------------------------------------

  def self.build!
    model = Sketchup.active_model
    model.start_operation('Build UK house extension', true)

    model.options['UnitsOptions']['LengthUnit'] = 2   # millimetres
    model.options['UnitsOptions']['LengthPrecision'] = 0

    c = CONFIG
    mat_brick = material(model, :brick)
    mat_context = material(model, :brick_existing)
    mat_roof = material(model, :roof)
    mat_paving = material(model, :paving)

    # Existing house + adjoining (semi) context.
    gable(model, 'House', 0, 0, c[:house_w], c[:house_d],
          c[:eaves], c[:ridge], mat_brick)
    gable(model, 'Adjoining dwelling', -c[:house_w], 0, 0, c[:house_d],
          c[:eaves], c[:ridge], mat_context)

    # Chimney on the flank of the ridge.
    box(model, 'Chimney',
        c[:house_w] - 900, c[:house_d] / 2.0 - 250, 0,
        c[:house_w] - 100, c[:house_d] / 2.0 + 250, c[:ridge] + 700,
        mat_brick)

    # Proposed single-storey rear extension (lean-to rising to the house).
    ex0 = c[:ext_x0]
    ew  = c[:ext_w]
    ed  = c[:ext_d]
    lean_to(model, 'Extension', ex0, -ed, ex0 + ew, 0,
            c[:ext_house_h], c[:ext_rear_h], 'y1', mat_brick)
    lean_to(model, 'Extension roof', ex0 - 50, -ed - 50, ex0 + ew + 50, 0,
            c[:ext_house_h] + 120, c[:ext_rear_h] + 120, 'y1', mat_roof)

    # Garden patio slab (context).
    box(model, 'Patio', ex0 - 200, -ed - c[:patio_depth], -150,
        ex0 + ew + 200, -ed - 50, 0, mat_paving)

    # Ground plane guide.
    box(model, 'Ground', -c[:house_w] - 500, -ed - c[:patio_depth] - 500, -200,
        c[:house_w] + 500, c[:house_d] + 1500, -150, mat_paving)

    build_scenes(model, c)

    model.commit_operation
    puts 'HouseExtensions: model built with ' \
         "#{model.pages.count} scenes."
    model.pages.selected_page = model.pages['01 Ground floor plan']
    model
  end

  def self.build_scenes(model, c)
    cx = c[:house_w] / 2.0
    cy = (c[:house_d] - c[:ext_d]) / 2.0
    cz = c[:ridge] / 2.0
    span = c[:house_d] + c[:ext_d] + c[:patio_depth] + 6000

    # Plan (orthographic, looking straight down, north up).
    add_scene(model, '01 Ground floor plan',
              pt(cx, cy, span), pt(cx, cy, 0), Geom::Vector3d.new(0, 1, 0), true)
    # Rear elevation (from the garden, -y).
    add_scene(model, '02 Rear elevation',
              pt(cx, -span, cz), pt(cx, cy, cz), Geom::Vector3d.new(0, 0, 1), true)
    # Front elevation (principal, +y).
    add_scene(model, '03 Front elevation',
              pt(cx, c[:house_d] + span, cz), pt(cx, cy, cz),
              Geom::Vector3d.new(0, 0, 1), true)
    # Flank elevation (+x).
    add_scene(model, '04 Flank elevation',
              pt(c[:house_w] + span, cy, cz), pt(cx, cy, cz),
              Geom::Vector3d.new(0, 0, 1), true)
    # 3D view.
    add_scene(model, '05 3D view',
              pt(-c[:house_w] - 3000, -c[:ext_d] - 9000, 9000),
              pt(cx, cy, 1500), Geom::Vector3d.new(0, 0, 1), false)
  end
end

HouseExtensions.build!
