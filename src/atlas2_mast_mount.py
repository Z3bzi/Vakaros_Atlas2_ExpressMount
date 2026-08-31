#!/usr/bin/env python3
"""
Vakaros Atlas 2  ->  Express-section mast mount  (AFT / mainsail-groove mount)
=============================================================================

The device sits on the AFT face of the mast, screen facing the cockpit.

Fixing uses the mainsail luff groove, which measures (from Mast.step):

    outer recess   20.00 mm wide (Y +/-10.00), X 53.4 .. 60.0, flaring to
                   27 mm at the aft face -- a parallel slot, so a tongue on
                   the back plate locates in it and carries all the shear
    throat         5.00 mm minimum, at X 52.0
    round channel  circle centre X = 50.04, r = 10.05  (the bolt rope's home)

so the back plate gets a full-height tongue into the recess, and two M4 bolts
pass through the throat into a half-round bar lying in the channel.

    NOTE: only usable BELOW the gooseneck, where the mainsail bolt rope is not
    in the groove.  See README.

Coordinate system (world, mm)
    +X aft   (away from the mast, toward the cockpit)
    +Y       athwartships
    +Z up    (mast axis); mount centred on Z = 0

Device frame -> world:  Xw = Ya + DEV_CX ,  Yw = -Xa ,  Zw = Za
(a -90 deg rotation about Z then a translation, so +Ya -- the screen -- faces aft)
"""

import math
import os
import re
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "reference")
OUT = os.path.join(ROOT, "export")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- measured --
MAST_AFT_X       = 63.822    # aft-most point of the section, at Y ~ +/-15
RECESS_HALF_W    = 10.000    # parallel part of the outer recess
RECESS_FLOOR_X   = 53.496    # shoulder the tongue stops short of
THROAT_MIN_W     = 5.000     # at X = 52.0 -- this is what caps bolt size
CHANNEL_CX       = 50.04     # bolt-rope channel: centre and radius
CHANNEL_R        = 10.05
CHANNEL_MOUTH_X  = 49.30     # flat face of the slug sits here

DEV_HALF_W    = 44.44
DEV_FRONT_Y   =  1.00
DEV_BACK_Y    = -13.25
DEV_BACKMOST_Y= -14.41
DEV_TOP_Z     =  57.64
DEV_PORT_BOT_Z= -58.01

BTN_XA  = (36.61, 39.49)     # 4 front buttons, column near one edge
PWR_XA  = (34.19, 38.04)     # power button, top edge
PWR_YA  = (-7.62, -5.91)
PORT_XA = (27.21, 36.94)     # charge port, bottom edge
PORT_YA = (-5.82, -1.86)
PROT_XA = (13.16, 17.03)     # rear protrusions (mirrored pair)

# ------------------------------------------------------------------ design --
CLR         = 0.30
CLR_MAST    = 0.50
WALL        = 3.00
AFT_WALL    = 7.00
PLATE_CORE_T= 7.00

TONGUE_HALF_W = 9.70         # 0.3 mm each side in the 20.00 mm recess
MAST_BOLT     = 4.0          # M4 -- the 5.00 mm throat rules out M5
MAST_BOLT_CLR = 4.5
MAST_BOLT_CBORE   = 9.0
MAST_BOLT_CBORE_D = 4.5
BOLT_DZ       = 35.0

LOCK_SCREW_CLR   = 3.4
LOCK_INSERT_D    = 4.0
LOCK_INSERT_DEEP = 6.5
LOCK_Y           = -52.5     # thumbscrews: same side as the controls
LOCK_DZ          = 30.0

HINGE_Y   = 52.5             # hinge: opposite side to the controls
HINGE_R   = 4.0
HINGE_PIN = 3.2
HINGE_SHELL_HZ = 20.0
HINGE_GAP = 0.4

PLATE_Y0, PLATE_Y1 = -57.0, 47.0
PLATE_HZ = 62.0

# --------------------------------------------------------------- derived ----
PLATE_FACE_X = MAST_AFT_X + CLR_MAST + AFT_WALL
DEV_CX       = PLATE_FACE_X - DEV_BACK_Y

def dvx(ya):  return ya + DEV_CX          # device Ya -> world X
def dvy(xa):  return -xa                  # device Xa -> world Y
def dvxs(a, b): return tuple(sorted((dvx(a), dvx(b))))
def dvys(a, b): return tuple(sorted((dvy(a), dvy(b))))

DEV_SCREEN_X = dvx(DEV_FRONT_Y)
CAV_Y        = DEV_HALF_W + CLR
CAV_TOP_Z    = DEV_TOP_Z + CLR
CAV_BOT_Z    = DEV_PORT_BOT_Z - CLR
CAV_FRONT_X  = DEV_SCREEN_X + 0.20
SHELL_BACK_X = PLATE_FACE_X
SHELL_FRONT_X= CAV_FRONT_X + WALL
SHELL_Y      = CAV_Y + WALL
SHELL_TOP_Z  = CAV_TOP_Z + WALL
SHELL_BOT_Z  = CAV_BOT_Z - WALL
LIP_IN_Y     = DEV_HALF_W - 3.0

# cutouts, derived from the measured feature boxes (not hand-placed)
PWR_CUT_Y  = (dvys(*PWR_XA)[0] - 1.9, dvys(*PWR_XA)[1] + 1.9)
PWR_CUT_X1 = dvxs(*PWR_YA)[1] + 1.2                 # keep a screen-side tie bar
PORT_CUT_Y = (dvys(*PORT_XA)[0] - 2.1, dvys(*PORT_XA)[1] + 2.1)
PORT_CUT_X0= dvxs(*PORT_YA)[0] - 1.2                # keep a mast-side tie bar
RELIEF_Y   = (PROT_XA[0] - 1.2, PROT_XA[1] + 1.5)

# ------------------------------------------------------------- primitives --
def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)).val())

def cyl_z(x, y, z0, z1, r):
    return (cq.Workplane("XY").cylinder(z1 - z0, r, centered=(True, True, False))
            .translate((x, y, z0)).val())

def cyl_x(x0, x1, y, z, r):
    return (cq.Workplane("XY").cylinder(x1 - x0, r, centered=(True, True, False))
            .rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, y, z)).val())

def cyl_y(y0, y1, x, z, r):
    return (cq.Workplane("XY").cylinder(y1 - y0, r, centered=(True, True, False))
            .rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y0, z)).val())

def fuse(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()

def principal(shape, label):
    sols = sorted(shape.Solids(), key=lambda s: s.Volume(), reverse=True)
    if len(sols) > 1:
        print("  !! %s produced %d loose fragment(s): %s -- dropped"
              % (label, len(sols) - 1,
                 ", ".join("%.1f mm^3" % s.Volume() for s in sols[1:])))
    return sols[0]

# --------------------------------------------------------------- geometry ---
print("loading reference geometry ...")
mast_raw = cq.importers.importStep(os.path.join(REF, "Mast.step")).val()
atlas_raw = cq.importers.importStep(os.path.join(REF, "Atlas_2.step"))
mast = mast_raw.translate((0, 0, -250.0))
atlas = (cq.Compound.makeCompound(atlas_raw.solids().vals())
         .rotate((0, 0, 0), (0, 0, 1), -90).translate((DEV_CX, 0, 0)))

_SECT = None
def section_segments():
    global _SECT
    if _SECT is None:
        import numpy as np
        sk = cq.Workplane(obj=mast_raw).section(250.0)
        N = 60000
        segs = []
        for w in sk.wires().vals():
            p = [w.positionAt(k / N) for k in range(N)]
            for i in range(N):
                a, b = p[i], p[(i + 1) % N]
                segs.append((a.x, a.y, b.x, b.y))
        _SECT = np.array(segs)
    return _SECT

def aft_xmax(y):
    """Aft-most material at this Y (traces skin, flare and recess floor)."""
    import numpy as np
    s = section_segments()
    x1, y1, x2, y2 = s[:, 0], s[:, 1], s[:, 2], s[:, 3]
    m = ((y1 <= y) & (y2 > y)) | ((y2 <= y) & (y1 > y))
    if not m.any():
        return None
    t = (y - y1[m]) / (y2[m] - y1[m])
    return float(np.max(x1[m] + t * (x2[m] - x1[m])))

def mast_aft_clearance(clr, ylim=32.0, ny=321, depth=400.0):
    """Prism the mount must stay aft of: the aft face grown by `clr`, with the
    luff groove floored off at the recess shoulder so the plate grows a tongue
    into the recess but never into the throat."""
    import numpy as np
    ys = np.linspace(-ylim, ylim, ny)
    pts = []
    for y in ys:
        xm = aft_xmax(float(y))
        if xm is None:
            xm = RECESS_FLOOR_X
        pts.append((max(xm, RECESS_FLOOR_X) + clr, float(y)))
    poly = pts + [(-100.0, pts[-1][1]), (-100.0, pts[0][1])]
    return (cq.Workplane("XY").polyline(poly).close()
            .extrude(depth).val().translate((0, 0, -depth / 2.0)))

MASTCLR = mast_aft_clearance(CLR_MAST)
print("  aft clearance prism ok, X %.2f..%.2f"
      % (MASTCLR.BoundingBox().xmin, MASTCLR.BoundingBox().xmax))

# ------------------------------------------------------------- back plate ---
def build_back_plate():
    part = box(PLATE_FACE_X - PLATE_CORE_T, PLATE_FACE_X,
               PLATE_Y0, PLATE_Y1, -PLATE_HZ, PLATE_HZ)
    # full-height tongue into the 20 mm recess -- the primary location feature
    part = fuse(part, box(RECESS_FLOOR_X - 3.0, PLATE_FACE_X,
                          -TONGUE_HALF_W, TONGUE_HALF_W, -PLATE_HZ, PLATE_HZ))
    # saddle wings onto the aft skin either side of the groove
    for s in (1, -1):
        part = fuse(part, box(57.0, PLATE_FACE_X,
                              *sorted((s * 12.0, s * 23.0)), -PLATE_HZ, PLATE_HZ))
    # heat-set insert ears
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = fuse(part, box(PLATE_FACE_X - 9.0, PLATE_FACE_X,
                              PLATE_Y0, -46.0, zc - 7.0, zc + 7.0))
    # hinge knuckles + webs, forward of the parting plane
    for z0, z1 in ((-58.0, -HINGE_SHELL_HZ - HINGE_GAP),
                   (HINGE_SHELL_HZ + HINGE_GAP, 58.0)):
        part = fuse(part,
                    cyl_z(PLATE_FACE_X, HINGE_Y, z0, z1, HINGE_R),
                    box(PLATE_FACE_X - 4.0, PLATE_FACE_X, PLATE_Y1, HINGE_Y, z0, z1))

    part = part.cut(MASTCLR)                                   # carve the saddle
    for s in (1, -1):
        part = part.cut(box(PLATE_FACE_X - 2.0, PLATE_FACE_X,
                            *sorted((s * RELIEF_Y[0], s * RELIEF_Y[1])),
                            -57.0, 57.0))
    for zc in (BOLT_DZ, -BOLT_DZ):
        part = part.cut(cyl_x(CHANNEL_MOUTH_X, PLATE_FACE_X + 1.0, 0.0, zc,
                              MAST_BOLT_CLR / 2.0))
        part = part.cut(cyl_x(PLATE_FACE_X - MAST_BOLT_CBORE_D,
                              PLATE_FACE_X + 0.1, 0.0, zc,
                              MAST_BOLT_CBORE / 2.0))
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = part.cut(cyl_x(PLATE_FACE_X - LOCK_INSERT_DEEP,
                              PLATE_FACE_X + 0.1, LOCK_Y, zc,
                              LOCK_INSERT_D / 2.0))
    part = part.cut(cyl_z(PLATE_FACE_X, HINGE_Y, -56.0, 59.0, HINGE_PIN / 2.0))
    part = part.cut(cyl_y(HINGE_Y - 6.0, HINGE_Y + 6.0, PLATE_FACE_X, 56.0, 0.8))
    return part.clean()

# ------------------------------------------------------------ front shell ---
def build_front_shell():
    part = box(SHELL_BACK_X, SHELL_FRONT_X, -SHELL_Y, SHELL_Y,
               SHELL_BOT_Z, SHELL_TOP_Z)
    part = fuse(part,
                cyl_z(SHELL_BACK_X, HINGE_Y, -HINGE_SHELL_HZ, HINGE_SHELL_HZ, HINGE_R),
                box(SHELL_BACK_X, SHELL_BACK_X + 4.0, SHELL_Y, HINGE_Y,
                    -HINGE_SHELL_HZ, HINGE_SHELL_HZ))
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = fuse(part, box(SHELL_BACK_X, SHELL_BACK_X + 4.0,
                              PLATE_Y0, -SHELL_Y, zc - 6.0, zc + 6.0))

    part = part.cut(box(SHELL_BACK_X - 1.0, CAV_FRONT_X,
                        -CAV_Y, CAV_Y, CAV_BOT_Z, CAV_TOP_Z))
    part = part.cut(box(CAV_FRONT_X, SHELL_FRONT_X + 1.0,
                        -LIP_IN_Y, LIP_IN_Y, SHELL_BOT_Z - 5.0, SHELL_TOP_Z + 5.0))
    part = part.cut(box(SHELL_BACK_X - 1.0, PWR_CUT_X1, *PWR_CUT_Y,
                        CAV_TOP_Z - 1.0, SHELL_TOP_Z + 1.0))
    part = part.cut(box(PORT_CUT_X0, SHELL_FRONT_X + 1.0, *PORT_CUT_Y,
                        SHELL_BOT_Z - 1.0, CAV_BOT_Z + 1.0))
    for yc in (10.0, 30.0):
        part = part.cut(cyl_z(SHELL_BACK_X + 8.0, yc,
                              SHELL_BOT_Z - 1.0, CAV_BOT_Z + 1.0, 2.0))
    part = part.cut(cyl_z(SHELL_BACK_X, HINGE_Y,
                          -HINGE_SHELL_HZ - 1.0, HINGE_SHELL_HZ + 1.0, HINGE_PIN / 2.0))
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = part.cut(cyl_x(SHELL_BACK_X - 1.0, SHELL_BACK_X + 5.0,
                              LOCK_Y, zc, LOCK_SCREW_CLR / 2.0))
    return part.clean()

# ------------------------------------------------------- luff-groove nuts ---
def luff_bar(length, holes):
    """Half-round bar for the bolt-rope channel: a circular segment that drops
    in from the open end of the groove.  Flat face aft, tapped M4."""
    seg = cyl_z(CHANNEL_CX, 0.0, -length / 2.0, length / 2.0, CHANNEL_R - 0.35)
    seg = seg.cut(box(CHANNEL_MOUTH_X, CHANNEL_CX + 20.0, -20, 20,
                      -length, length))
    for zc in holes:
        seg = seg.cut(cyl_x(CHANNEL_MOUTH_X - 9.0, CHANNEL_MOUTH_X + 1.0,
                            0.0, zc, MAST_BOLT / 2.0 - 0.35))
    return seg.clean()

def build_knob():
    k = cq.Workplane("XY").circle(11.0).extrude(9.0)
    for i in range(6):
        a = math.radians(i * 60.0)
        k = k.cut(cq.Workplane("XY").center(12.6 * math.cos(a), 12.6 * math.sin(a))
                  .circle(4.2).extrude(9.0))
    k = k.faces("<Z").workplane().polygon(6, 5.5 / math.cos(math.pi / 6)).cutBlind(-3.0)
    k = k.faces("<Z").workplane().circle(1.8).cutBlind(-9.0)
    return k.val()

# ------------------------------------------------------------------ build ---
print("building back plate ...")
plate = principal(build_back_plate(), "back plate")
print("building front shell ...")
shell = principal(build_front_shell(), "front shell")
for nm, sh in (("back plate", plate), ("front shell", shell)):
    print("  %-12s valid=%s  solids=%d  vol=%.1f cm^3"
          % (nm, sh.isValid(), len(sh.Solids()), sh.Volume() / 1000.0))
print("building hardware ...")
bar = luff_bar(90.0, (BOLT_DZ, -BOLT_DZ))
slug = luff_bar(25.0, (0.0,))
knob = build_knob()

# ------------------------------------------------------------- validation ---
def vol(s):
    try: return s.Volume()
    except Exception: return float("nan")

def clash(a, b, label, tol=1.0):
    v = vol(a.intersect(b))
    print("  %s%-40s overlap = %9.3f mm^3" % ("OK " if v < tol else "!! ", label, v))
    return v

print("\n--- interference check -------------------------------------------")
clash(plate, mast,  "back plate  vs  mast")
clash(plate, atlas, "back plate  vs  Atlas 2")
clash(shell, atlas, "front shell vs  Atlas 2")
clash(shell, mast,  "front shell vs  mast")
clash(shell, plate, "front shell vs  back plate")
clash(bar,   mast,  "luff bar    vs  mast")
v = vol(plate.intersect(mast_aft_clearance(CLR_MAST + 0.15)))
print("  %sseat proof: plate meets mast+%.2f      overlap = %9.3f mm^3"
      % ("OK " if v > 1.0 else "!! ", CLR_MAST + 0.15, v))

print("\n--- hinge sweep --------------------------------------------------")
ax0, ax1 = (PLATE_FACE_X, HINGE_Y, -1.0), (PLATE_FACE_X, HINGE_Y, 1.0)
for ang in (5, 15, 30, 45, 60, 90, 120):
    v = vol(shell.rotate(ax0, ax1, ang).intersect(plate))
    print("  %s%4d deg   shell/plate overlap = %9.3f mm^3"
          % ("OK " if v < 1.0 else "!! ", ang, v))

bb = plate.BoundingBox(); print("\nback plate  %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(plate) / 1000.0))
bb = shell.BoundingBox(); print("front shell %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(shell) / 1000.0))
print("stack: mast aft face %.2f -> screen %.2f  = %.2f mm standoff"
      % (MAST_AFT_X, DEV_SCREEN_X, DEV_SCREEN_X - MAST_AFT_X))
print("tongue: %.1f mm wide into a %.2f mm recess, %.1f mm engagement"
      % (2 * TONGUE_HALF_W, 2 * RECESS_HALF_W, 60.0 - (RECESS_FLOOR_X + CLR_MAST)))

# --------------------------------------------------------------- exports ----
print("\nexporting ...")
for name, s in [("back_plate", plate), ("front_shell", shell),
                ("luff_nut_bar", bar), ("luff_nut_slug", slug),
                ("thumbscrew_knob", knob)]:
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".step"))
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".stl"),
                        tolerance=0.02, angularTolerance=0.1)
    back = cq.importers.importStep(os.path.join(OUT, name + ".step"))
    n = len(back.solids().vals()); dv = abs(back.val().Volume() - s.Volume())
    ok = (n == 1 and dv < 1.0)
    print("  %s%s.step / .stl   (round-trip: %d solid, dV=%.3f mm^3)"
          % ("" if ok else "!! ", name, n, dv))

def named_assembly(items, name, path):
    a = cq.Assembly(name=name)
    for nm, sh, col in items:
        a.add(sh, name=nm, color=cq.Color(*col))
    (a.export if hasattr(a, "export") else a.save)(path)

MOUNT = [("back_plate",   plate, (0.74, 0.76, 0.80, 1.0)),
         ("front_shell",  shell, (0.23, 0.41, 0.63, 1.0)),
         ("luff_nut_bar", bar,   (0.78, 0.58, 0.24, 1.0))]
named_assembly(MOUNT, "atlas2_mast_mount",
               os.path.join(OUT, "assembly_mount_only.step"))
named_assembly(MOUNT + [("mast_express", mast,  (0.67, 0.66, 0.63, 1.0)),
                        ("atlas_2",      atlas, (0.15, 0.16, 0.18, 1.0))],
               "atlas2_mast_mount_in_situ",
               os.path.join(OUT, "assembly_with_mast_and_device.step"))
for f in ("assembly_mount_only", "assembly_with_mast_and_device"):
    names = sorted(set(re.findall(r"PRODUCT\s*\(\s*'([^']+)'",
                   open(os.path.join(OUT, f + ".step")).read())))
    print("  %s.step   components: %s" % (f, ", ".join(names)))

mast_stub = mast.intersect(box(-70, 90, -60, 60, -70, 70))
for nm, sh in (("_mesh_mast_stub", mast_stub), ("_mesh_device", atlas),
               ("_mesh_shell_open", shell.rotate(ax0, ax1, 75))):
    cq.exporters.export(cq.Workplane(obj=sh), os.path.join(OUT, nm + ".stl"),
                        tolerance=0.05, angularTolerance=0.2)
print("  assembly meshes")
print("\ndone.")
