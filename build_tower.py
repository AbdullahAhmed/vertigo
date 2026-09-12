"""
VERTIGO - low-poly tower builder.
Run headless:  blender -b --python build_tower.py
Outputs (into ./build):
  tower.glb     the tower shell, string courses, cornice, parapet, door surround, roof mast + 3 lamps
  layout.json   spiral slab layout + roof collision rects + lamp/mast/door positions (shared with the game)
  preview.png   workbench render from the base, looking up (sanity check)
Blender is Z-up; the glTF exporter converts to Y-up. Blender (x, y, z) -> three.js (x, z, -y).
"""
import bpy, bmesh, json, math, os
from mathutils import Vector, Quaternion

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- parameters
A        = 4.5          # inner shaft half-width (shaft is 9 x 9 m)
T        = 1.2          # wall thickness
B        = A + T        # outer half-width (5.7)
RISE     = 0.4          # height gained per slab
SLAB_L   = 2.25         # slab length along the wall (4 per wall, 16 per lap)
SLAB_D   = 2.0          # slab depth out from the wall
SLAB_TH  = 0.35
N_SLABS  = 181          # last slab top = 72.4
ROOF_Z0  = 72.0         # roof underside (needs ~2.9 m over any slab you might jump from)
ROOF_Z1  = 72.5         # roof top (walkable)
PARAPET  = 1.1
H        = ROOF_Z1

# ---------------------------------------------------------------- helpers
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, emit=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.95
    m.diffuse_color = (*rgb, 1)
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m

def box_bm(bm, x0, x1, y0, y1, z0, z1):
    """append an axis-aligned box to bmesh bm"""
    verts = [bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    # index: x + 2*y + 4*z
    f = lambda *i: bm.faces.new([verts[j] for j in i])
    f(0, 2, 3, 1)   # bottom
    f(4, 5, 7, 6)   # top
    f(0, 1, 5, 4)   # -y
    f(2, 6, 7, 3)   # +y
    f(0, 4, 6, 2)   # -x
    f(1, 3, 7, 5)   # +x

def mesh_obj(name, build, material):
    bm = bmesh.new()
    build(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if material:
        me.materials.append(material)
    return ob

def boolean_cut(target, cutter):
    mod = target.modifiers.new("cut", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bad = target.data.validate(verbose=False)
    if bad: print(f"[VERTIGO] boolean on {target.name}: fixed invalid geometry")

# ---------------------------------------------------------------- build
clean_scene()
stone   = mat("stone",   (0.62, 0.50, 0.30))
stone2  = mat("stone2",  (0.55, 0.44, 0.26))
dark    = mat("dark",    (0.05, 0.05, 0.06))
lampmat = mat("lamp",    (1.0, 0.98, 0.9), emit=6.0)
metal   = mat("metal",   (0.18, 0.18, 0.2))

# --- the shell is built in stacked segments (seg0 .. seg5) so the game can collapse it; see the end of the layout section
SEG_Z = [0.0, 12.0, 24.0, 36.0, 48.0, 60.0, ROOF_Z1]

# windows: (wall, along [-A..A] centre, z bottom, w, h)   wall 0=-Y(door face) 1=+X 2=+Y 3=-X
WINDOWS = [
    # the photo face (south / -Y): pairs near the right edge, an odd single, tiny vents
    (0,  2.6, 20.5, 1.0, 1.5), (0,  1.2, 20.5, 1.0, 1.5),
    (0,  2.6, 36.5, 1.0, 1.5), (0,  1.2, 36.5, 1.0, 1.5),
    (0, -2.2, 29.0, 0.7, 0.7),
    (0, -0.6, 45.0, 1.0, 1.5),
    (0,  2.6, 52.5, 1.0, 1.5), (0,  1.2, 52.5, 1.0, 1.5),
    (0, -2.8, 61.0, 1.0, 1.5),
    (0,  0.4,  9.0, 0.7, 0.7),
    (1, -2.0, 15.0, 1.0, 1.5), (1, -0.6, 15.0, 1.0, 1.5),
    (1,  2.4, 33.0, 0.7, 0.7),
    (1, -2.0, 47.0, 1.0, 1.5), (1, -0.6, 47.0, 1.0, 1.5),
    (1,  1.6, 58.0, 1.0, 1.5),
    (2,  0.0, 12.0, 0.7, 0.7),
    (2,  2.0, 26.0, 1.0, 1.5), (2,  0.6, 26.0, 1.0, 1.5),
    (2, -2.4, 40.0, 1.0, 1.5),
    (2,  2.0, 55.0, 1.0, 1.5), (2,  0.6, 55.0, 1.0, 1.5),
    (2, -1.0, 64.0, 0.7, 0.7),
    (3,  1.8, 18.0, 1.0, 1.5),
    (3, -2.2, 31.0, 1.0, 1.5), (3, -0.8, 31.0, 1.0, 1.5),
    (3,  2.4, 43.0, 0.7, 0.7),
    (3, -2.2, 60.0, 1.0, 1.5), (3, -0.8, 60.0, 1.0, 1.5),
]
DOOR = (1.7, 2.7)   # width, height on wall 0 at along=0

def wall_box(bm, wall, c, z0, w, h):
    """a box punched through the wall `wall`, centred at `c` along it"""
    lo, hi = -B - 0.1, -A + 0.1
    if wall == 0:   box_bm(bm, c - w/2, c + w/2, lo, hi, z0, z0 + h)
    elif wall == 2: box_bm(bm, c - w/2, c + w/2, -hi, -lo, z0, z0 + h)
    elif wall == 1: box_bm(bm, -hi, -lo, c - w/2, c + w/2, z0, z0 + h)
    else:           box_bm(bm, lo, hi, c - w/2, c + w/2, z0, z0 + h)

# hatch: every slab whose top rises within head height of the roof underside gets a hole above it (computed below)
HATCH = []


# --- string courses (horizontal bands, like the photo) + cornice + parapet - plain boxes, no booleans
def ring(bm, half_in, half_out, z0, z1):
    box_bm(bm, -half_out, half_out, -half_out, -half_in, z0, z1)
    box_bm(bm, -half_out, half_out,  half_in,  half_out, z0, z1)
    box_bm(bm, -half_out, -half_in, -half_in,  half_in, z0, z1)
    box_bm(bm,  half_in,  half_out, -half_in,  half_in, z0, z1)

def seg_of(z):
    return max(k for k in range(len(SEG_Z) - 1) if SEG_Z[k] <= z)

def trim_build(k):
    def build(bm):
        z0, z1 = SEG_Z[k], SEG_Z[k + 1]
        for z in (14.0, 28.0, 42.0, 56.0):
            if z0 <= z < z1: ring(bm, B, B + 0.35, z, z + 0.9)
        if k == len(SEG_Z) - 2:
            ring(bm, B, B + 0.55, H - 1.6, H - 0.3)      # cornice
        if k == 0:
            # plinth, with a gap for the doorway on the -Y face
            w, h = DOOR
            p0, p1 = B + 0.1, B + 0.45
            box_bm(bm, -p1, p1, p0, p1, 0, 1.2)
            box_bm(bm, -p1, -p0, -p0, p0, 0, 1.2)
            box_bm(bm, p0, p1, -p0, p0, 0, 1.2)
            box_bm(bm, -p1, -w/2 - 0.35, -p1, -p0, 0, 1.2)
            box_bm(bm, w/2 + 0.35, p1, -p1, -p0, 0, 1.2)
            # door surround
            box_bm(bm, -w/2 - 0.35, -w/2,   -B - 0.18, -B, 0, h + 0.35)
            box_bm(bm,  w/2,  w/2 + 0.35,   -B - 0.18, -B, 0, h + 0.35)
            box_bm(bm, -w/2 - 0.35, w/2 + 0.35, -B - 0.18, -B, h, h + 0.35)
    return build
for k in range(len(SEG_Z) - 1):
    mesh_obj(f"trim{k}", trim_build(k), stone2)

def parapet_build(bm):
    ring(bm, B - 0.4, B, H, H + PARAPET)
mesh_obj("parapet", parapet_build, stone2)

# --- roof mast with the three lights, hanging just outside the SE corner (like the photo)
MAST = (B - 0.3, -B + 0.3)
LX, LY = B + 1.5, -B - 1.1          # the lights hang out past the corner, clear of the cornice, so they read from the ground
LAMPS = [(LX, LY, H + 3.2), (LX, LY, H + 4.4), (LX, LY, H + 5.6)]
def mast_build(bm):
    mx, my = MAST
    box_bm(bm, mx - 0.12, mx + 0.12, my - 0.12, my + 0.12, H, H + 6.4)
    # arm reaching out over the corner: out along x, then along y, then a drop rod
    box_bm(bm, mx, LX + 0.06, my - 0.06, my + 0.06, H + 6.2, H + 6.32)
    box_bm(bm, LX - 0.06, LX + 0.06, LY - 0.06, my, H + 6.2, H + 6.32)
    box_bm(bm, LX - 0.06, LX + 0.06, LY - 0.06, LY + 0.06, H + 2.8, H + 6.32)
mesh_obj("mast", mast_build, metal)

def lamps_build(bm):
    for (x, y, z) in LAMPS:
        box_bm(bm, x - 0.28, x + 0.28, y - 0.2, y + 0.2, z - 0.24, z + 0.24)
mesh_obj("lamps", lamps_build, lampmat)

# --- interior floor
def floor_build(bm):
    box_bm(bm, -A, A, -A, A, -0.3, 0.02)
mesh_obj("floor", floor_build, dark)

# ---------------------------------------------------------------- spiral layout (data only, slabs are instanced by the game)
# walls: 0: y=-A, x from -A..A (inward +y) | 1: x=A, y -A..A (inward -x) | 2: y=A, x A..-A (inward -y) | 3: x=-A, y A..-A (inward +x)
slabs = []
for i in range(N_SLABS):
    wall = (i // 4 + 1) % 4                           # start on wall 1 so the doorway (wall 0) stays clear at ground level
    u    = (i % 4) * SLAB_L + SLAB_L / 2 - A          # centre along the wall, -A..A in wall order
    lap  = i // 16
    landing = (i % 16 == 0)
    depth = SLAB_D          # landings keep the same depth: a deeper one overhangs the previous wall's last slab and blocks it
    if wall == 0:   cx, cy, ang, ix, iy = u, -A + depth/2, 0.0, 0, 1
    elif wall == 1: cx, cy, ang, ix, iy = A - depth/2, u, math.pi/2, -1, 0
    elif wall == 2: cx, cy, ang, ix, iy = -u, A - depth/2, 0.0, 0, -1
    else:           cx, cy, ang, ix, iy = -A + depth/2, -u, math.pi/2, 1, 0
    top = RISE * (i + 1)
    slabs.append({
        "i": i, "lap": lap, "wall": wall, "pos": i % 4,
        "x": round(cx, 3), "y": round(cy, 3), "top": round(top, 3),
        "len": SLAB_L, "depth": round(depth, 3), "th": SLAB_TH,
        "angle": ang,                      # rotation about Z: 0 = long axis along X
        "inward": [ix, iy],
        "landing": landing,
    })

# hatch holes: rect of each slab that rises within 1.9 m of the roof underside, padded, clipped to the shaft
def slab_rect(sl):
    hx = sl["len"] / 2 if sl["angle"] == 0 else sl["depth"] / 2
    hy = sl["depth"] / 2 if sl["angle"] == 0 else sl["len"] / 2
    return (sl["x"] - hx, sl["x"] + hx, sl["y"] - hy, sl["y"] + hy)
PAD, VOID = 0.15, 1.35   # VOID: the hole also opens a strip of empty shaft beside the slabs - the last step is a hop over the drop
for sl in slabs:
    if sl["top"] >= ROOF_Z0 - 1.9:
        x0, x1, y0, y1 = slab_rect(sl)
        ix, iy = sl["inward"]
        x0 -= PAD + (VOID if ix < 0 else 0); x1 += PAD + (VOID if ix > 0 else 0)
        y0 -= PAD + (VOID if iy < 0 else 0); y1 += PAD + (VOID if iy > 0 else 0)
        HATCH.append((max(-A, x0), min(A, x1), max(-A, y0), min(A, y1)))

# walkable roof = wall tops + the inner square minus the holes (grid decomposition on the holes' edges)
xs = sorted({-A, A, *[h[0] for h in HATCH], *[h[1] for h in HATCH]})
ys = sorted({-A, A, *[h[2] for h in HATCH], *[h[3] for h in HATCH]})
roof_rects = [(-B, B, A, B), (-B, B, -B, -A), (-B, -A, -A, A), (A, B, -A, A)]
for xa, xb in zip(xs, xs[1:]):
    for ya, yb in zip(ys, ys[1:]):
        cx, cy = (xa + xb) / 2, (ya + yb) / 2
        if not any(h[0] <= cx <= h[1] and h[2] <= cy <= h[3] for h in HATCH):
            roof_rects.append((xa, xb, ya, yb))

# openings as (builder, z-range); one boolean per opening per segment - the exact solver dislikes overlapping cutter volumes
cutters = [(lambda bm, wl=wl: wall_box(bm, *wl), wl[2], wl[2] + wl[4]) for wl in WINDOWS]
cutters.append((lambda bm: wall_box(bm, 0, 0.0, -0.1, DOOR[0], DOOR[1] + 0.1), -0.1, DOOR[1]))
for (x0, x1, y0, y1) in HATCH:
    cutters.append((lambda bm, x0=x0, x1=x1, y0=y0, y1=y1: box_bm(bm, x0, x1, y0, y1, ROOF_Z0 - 0.5, ROOF_Z1 + 0.5), ROOF_Z0 - 0.5, ROOF_Z1 + 0.5))

for k in range(len(SEG_Z) - 1):
    z0, z1 = SEG_Z[k], SEG_Z[k + 1]
    top = (k == len(SEG_Z) - 2)
    seg = mesh_obj(f"seg{k}", lambda bm, z0=z0, z1=z1: box_bm(bm, -B, B, -B, B, z0, z1), stone)
    cz1 = ROOF_Z0 if top else z1 + 1.0            # the top segment keeps its roof slab
    boolean_cut(seg, mesh_obj("cavity", lambda bm, z0=z0, cz1=cz1: box_bm(bm, -A, A, -A, A, z0 - 1.0, cz1), None))
    for n, (fn, c0, c1) in enumerate(cutters):
        if c1 > z0 and c0 < z1:
            boolean_cut(seg, mesh_obj(f"cut{k}_{n}", fn, None))
print(f"[VERTIGO] hatch holes={len(HATCH)} roof rects={len(roof_rects)}")
parapet_rects = [(-B, B, -B, -B + 0.4), (-B, B, B - 0.4, B), (-B, -B + 0.4, -B, B), (B - 0.4, B, -B, B)]

layout = {
    "A": A, "B": B, "T": T, "H": H, "roofZ0": ROOF_Z0, "roofZ1": ROOF_Z1, "parapet": PARAPET,
    "rise": RISE, "slabLen": SLAB_L, "slabDepth": SLAB_D, "slabTh": SLAB_TH,
    "door": {"w": DOOR[0], "h": DOOR[1], "wall": 0},
    "hatch": HATCH, "roofRects": roof_rects, "parapetRects": parapet_rects,
    "lamps": LAMPS, "mast": MAST, "segments": SEG_Z,
    "windows": WINDOWS,
    "slabs": slabs,
}
with open(os.path.join(OUT, "layout.json"), "w") as f:
    json.dump(layout, f)

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "tower.glb"),
    export_format='GLB', use_selection=True,
    export_apply=True, export_yup=True,
    export_materials='EXPORT', export_normals=True,
    export_animations=False, export_skins=False, export_cameras=False, export_lights=False,
)

tris = sum(len(p.vertices) - 2 for ob in bpy.data.objects if ob.type == 'MESH' for p in ob.data.polygons)
print(f"[VERTIGO] objects={len(bpy.data.objects)} triangles~{tris}")

# ---------------------------------------------------------------- preview render from the base, looking up (the opening shot)
scene = bpy.context.scene
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 18
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam)
cam.location = (2.5, -B - 3.0, 1.6)
look = Vector((1.0, -B, 58.0)) - Vector(cam.location)
q = look.to_track_quat('-Z', 'Y')
cam.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(12))).to_euler()
scene.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", 'SUN')); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(60), 0, math.radians(30))
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x, scene.render.resolution_y = 720, 960
scene.render.filepath = os.path.join(OUT, "preview.png")
bpy.ops.render.render(write_still=True)
print("[VERTIGO] done")
