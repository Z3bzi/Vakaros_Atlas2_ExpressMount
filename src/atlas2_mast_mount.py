#!/usr/bin/env python3
"""
Vakaros Atlas 2  ->  Express-section mast mount
==============================================

Two printed parts plus hardware:

  * back_plate   -- conforming saddle that bolts into the mast's forward
                    T-slot and forms the flat backing for the device
  * front_shell  -- hinged clamshell that captures the Atlas 2
  * toggle_nut / slide_nut_bar -- what the mast bolts thread into

EVERY dimension that touches the mast or the device is measured from the
supplied STEP files at import time -- nothing is copied from a drawing.

Coordinate system (world, mm)
    +X aft   (into the mast)         mast nose measured at X = -64.700
    +Y       athwartships
    +Z up    (mast axis)             mount is centred on Z = 0

Device frame -> world:  Xw = -Ya + DEV_CX ,  Yw = Xa ,  Zw = Za
(a +90 deg rotation about Z followed by a translation).
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
# Mast (Mast.step, mm, extruded along Z) -- forward T-slot on the nose
MAST_NOSE_X          = -64.700   # forward-most point of the section
MAST_SLOT_THROAT_W   = 5.000     # mouth width  (Y = +/-2.500)
MAST_SLOT_SHOULDER_X = -61.000   # face the nut bears against
MAST_SLOT_FLOOR_X    = -57.500   # back of the internal channel
MAST_SLOT_CHANNEL_W  = 12.000    # internal channel width (Y = +/-6.000)
MAST_SLOT_SHOULDER_Y = 3.520     # inner edge of the bearing shoulder
MAST_HALF_W          = 44.606

# Vakaros Atlas 2 (Atlas_2.step, converted from inch)
DEV_HALF_W    = 44.44    # Xa
DEV_FRONT_Y   =  1.00    # Ya, front bezel plane
DEV_BUTTON_Y  =  1.35    # Ya, front button crowns (highest front feature)
DEV_BACK_Y    = -13.25   # Ya, flat rear plateau  (Xa +/-25.20, Za +/-51.81)
DEV_BACKMOST_Y= -14.41   # Ya, two rear protrusions
DEV_TOP_Z     =  57.64
DEV_BOT_Z     = -57.64
DEV_PORT_BOT_Z= -58.01   # charge port lip sits proud of the bottom face

# rear protrusions to be relieved   (Xa, Za)
PROT = [((-17.03, -13.16), (34.40, 55.69)),
        (( 13.16,  17.03), (-55.69, -34.40))]
# front buttons (4)  Xa 36.61..39.49, Za centres +/-35.40, +/-11.80
BTN_XA = (36.61, 39.49)
# power button, top edge
PWR_XA = (34.19, 38.04)
# charge port, bottom edge
PORT_XA = (27.21, 36.94)

# ------------------------------------------------------------------ design --
CLR         = 0.30   # device clearance
CLR_MAST    = 0.40   # mast clearance
WALL        = 3.00   # shell wall
NOSE_WALL   = 8.00   # saddle wall over the mast nose (carries the bolts)
PLATE_CORE_T= 7.00   # flat part of the back plate

MAST_BOLT   = 4.0    # M4 -- see README, the 5.0 mm throat rules out M5
MAST_BOLT_CLR   = 4.5
MAST_BOLT_CBORE = 9.0
MAST_BOLT_CBORE_D = 4.5
BOLT_DZ     = 35.0   # bolts at Z = +/-35 (70 mm apart)

LOCK_SCREW_CLR   = 3.4   # M3 clearance in the shell flange
LOCK_INSERT_D    = 4.0   # M3 brass heat-set insert
LOCK_INSERT_DEEP = 6.5
LOCK_Y           = 52.5
LOCK_DZ          = 30.0  # thumbscrews at Z = +/-30 (60 mm apart)

HINGE_Y   = -52.5
HINGE_R   = 4.0
HINGE_PIN = 3.2      # M3 / 3 mm rod
HINGE_SHELL_HZ = 20.0    # shell knuckle  Z -20..+20
HINGE_GAP = 0.4

PLATE_Y0, PLATE_Y1 = -47.0, 57.0
PLATE_HZ = 62.0

# --------------------------------------------------------------- derived ----
PLATE_FRONT_X = MAST_NOSE_X - CLR_MAST - NOSE_WALL      # -73.10
PLATE_BACK_X  = PLATE_FRONT_X + PLATE_CORE_T            # -66.10
DEV_CX        = PLATE_FRONT_X - (-DEV_BACK_Y)           # -86.35

def dx(ya):
    """device Ya -> world X"""
    return -ya + DEV_CX

DEV_FRONT_X   = dx(DEV_FRONT_Y)                         # -87.35
CAV_Y         = DEV_HALF_W + CLR                        # 44.74
CAV_TOP_Z     = DEV_TOP_Z + CLR                         # 57.94
CAV_BOT_Z     = DEV_PORT_BOT_Z - CLR                    # -58.31
CAV_FRONT_X   = DEV_FRONT_X - 0.20                      # 0.2 mm preload gap
SHELL_BACK_X  = PLATE_FRONT_X                           # parting plane
SHELL_FRONT_X = CAV_FRONT_X - WALL
SHELL_Y       = CAV_Y + WALL                            # 47.74
SHELL_TOP_Z   = CAV_TOP_Z + WALL
SHELL_BOT_Z   = CAV_BOT_Z - WALL
LIP_IN_Y      = DEV_HALF_W - 3.0                        # lip overlaps 3 mm
PWR_CUT_X0    = -81.5    # top-wall notch: front tie bar is -87.55..-81.50
PORT_CUT_X1   = -79.5    # bottom-wall notch: rear tie bar is -79.50..-73.10

# ------------------------------------------------------------- primitives --
def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)).val())

def cyl_z(x, y, z0, z1, r):
    return (cq.Workplane("XY")
            .cylinder(z1 - z0, r, centered=(True, True, False))
            .translate((x, y, z0)).val())

def cyl_x(x0, x1, y, z, r):
    return (cq.Workplane("XY")
            .cylinder(x1 - x0, r, centered=(True, True, False))
            .rotate((0, 0, 0), (0, 1, 0), 90)
            .translate((x0, y, z)).val())

def cyl_y(y0, y1, x, z, r):
    return (cq.Workplane("XY")
            .cylinder(y1 - y0, r, centered=(True, True, False))
            .rotate((0, 0, 0), (1, 0, 0), -90)
            .translate((x, y0, z)).val())

def principal(shape, label):
    """Return the single largest solid, warn about any loose fragments."""
    sols = sorted(shape.Solids(), key=lambda s: s.Volume(), reverse=True)
    if len(sols) > 1:
        print("  !! %s produced %d loose fragment(s): %s -- dropped"
              % (label, len(sols) - 1,
                 ", ".join("%.1f mm^3" % s.Volume() for s in sols[1:])))
    return sols[0]

def fuse(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()

# --------------------------------------------------------------- geometry ---
print("loading reference geometry ...")
mast_raw = cq.importers.importStep(os.path.join(REF, "Mast.step")).val()
atlas_raw = cq.importers.importStep(os.path.join(REF, "Atlas_2.step"))

mast = mast_raw.translate((0, 0, -250.0))          # centre the mast on Z=0
atlas = (cq.Compound.makeCompound(atlas_raw.solids().vals())
         .rotate((0, 0, 0), (0, 0, 1), 90)
         .translate((DEV_CX, 0, 0)))

def mast_nose_profile(ylim=30.0, ny=181, samples=40000):
    """Forward face of the mast as Xmin(Y), sampled straight off the STEP.

    The T-slot is deliberately skipped (|Y| < 2.5 is capped at the nose apex)
    so the saddle cannot grow a tongue -- or loose fragments -- into it.
    """
    import numpy as np
    sec = cq.Workplane(obj=mast_raw).section(250.0)
    outer = max(sec.wires().vals(), key=lambda w: w.BoundingBox().xlen)
    arr = np.array([[(pt := outer.positionAt(k / samples)).x, pt.y]
                    for k in range(samples)])
    ys = np.linspace(-ylim, ylim, ny)
    band = (ys[1] - ys[0])
    prof = []
    for y in ys:
        if abs(y) < 2.5:                      # bridge the T-slot mouth
            prof.append((MAST_NOSE_X, float(y)))
            continue
        m = np.abs(arr[:, 1] - y) <= band
        if not m.any():
            raise RuntimeError("no mast profile point near Y=%.2f" % y)
        prof.append((float(arr[m, 0].min()), float(y)))
    return prof


def mast_clearance_solid_at(clr, height=400.0):
    """Prism of everything the mount must stay clear of: the mast nose grown
    outward along its own normal by `clr`, closed off well aft."""
    import numpy as np
    prof = np.array(mast_nose_profile())
    off = []
    n = len(prof)
    for i in range(n):
        a = prof[max(i - 1, 0)]
        b = prof[min(i + 1, n - 1)]
        t = b - a
        L = float(np.hypot(*t)) or 1.0
        nx, ny_ = -t[1] / L, t[0] / L          # outward for increasing Y
        off.append((float(prof[i][0] + nx * clr), float(prof[i][1] + ny_ * clr)))
    poly = off + [(100.0, off[-1][1]), (100.0, off[0][1])]
    sol = (cq.Workplane("XY").polyline(poly).close()
           .extrude(height).val().translate((0, 0, -height / 2.0)))
    return sol


MASTCLR = mast_clearance_solid_at(CLR_MAST)
print("  mast clearance solid ok, bbox X %.2f..%.2f" %
      (MASTCLR.BoundingBox().xmin, MASTCLR.BoundingBox().xmax))

# ------------------------------------------------------------- back plate ---
def build_back_plate():
    # flat core
    part = box(PLATE_FRONT_X, PLATE_BACK_X, PLATE_Y0, PLATE_Y1,
               -PLATE_HZ, PLATE_HZ)

    # tapered saddle boss over the mast nose (profile in XY, extruded along Z)
    saddle = (cq.Workplane("XY")
              .polyline([(PLATE_FRONT_X, -24.0), (-58.5, -19.0),
                         (-58.5, 19.0), (PLATE_FRONT_X, 24.0)])
              .close().extrude(2 * PLATE_HZ).val()
              .translate((0, 0, -PLATE_HZ)))
    part = fuse(part, saddle)

    # thickened ears for the two heat-set inserts
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = fuse(part, box(PLATE_FRONT_X, PLATE_FRONT_X + 9.0,
                              46.0, PLATE_Y1, zc - 7.0, zc + 7.0))

    # hinge: two knuckles + webs back to the plate
    for z0, z1 in ((-58.0, -HINGE_SHELL_HZ - HINGE_GAP),
                   (HINGE_SHELL_HZ + HINGE_GAP, 58.0)):
        part = fuse(part,
                    cyl_z(PLATE_FRONT_X, HINGE_Y, z0, z1, HINGE_R),
                    box(PLATE_FRONT_X, PLATE_FRONT_X + 4.0,
                        HINGE_Y, PLATE_Y0, z0, z1))

    # ---- cuts
    part = part.cut(MASTCLR)                                    # the saddle

    # relief channels for the two rear protrusions on the Atlas
    for y0, y1 in ((-18.5, -12.0), (12.0, 18.5)):
        part = part.cut(box(PLATE_FRONT_X, PLATE_FRONT_X + 2.0,
                            y0, y1, -57.0, 57.0))

    # mast bolts: through hole + counterbore for cap head and washer
    for zc in (BOLT_DZ, -BOLT_DZ):
        part = part.cut(cyl_x(PLATE_FRONT_X - 1.0, -58.0, 0.0, zc,
                              MAST_BOLT_CLR / 2.0))
        part = part.cut(cyl_x(PLATE_FRONT_X - 0.1,
                              PLATE_FRONT_X + MAST_BOLT_CBORE_D,
                              0.0, zc, MAST_BOLT_CBORE / 2.0))

    # M3 heat-set inserts for the two thumbscrews
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = part.cut(cyl_x(PLATE_FRONT_X - 0.1,
                              PLATE_FRONT_X + LOCK_INSERT_DEEP,
                              LOCK_Y, zc, LOCK_INSERT_D / 2.0))

    # hinge pin bore -- blind at the bottom so the pin cannot drop out
    part = part.cut(cyl_z(PLATE_FRONT_X, HINGE_Y, -56.0, 59.0, HINGE_PIN / 2.0))
    # transverse seizing-wire / split-pin hole near the top
    part = part.cut(cyl_y(HINGE_Y - 6.0, HINGE_Y + 6.0,
                          PLATE_FRONT_X, 56.0, 0.8))
    return part.clean()

# ------------------------------------------------------------ front shell ---
def build_front_shell():
    part = box(SHELL_FRONT_X, SHELL_BACK_X, -SHELL_Y, SHELL_Y,
               SHELL_BOT_Z, SHELL_TOP_Z)

    # hinge knuckle + web (both forward of the parting plane)
    part = fuse(part,
                cyl_z(SHELL_BACK_X, HINGE_Y,
                      -HINGE_SHELL_HZ, HINGE_SHELL_HZ, HINGE_R),
                box(SHELL_BACK_X - 4.0, SHELL_BACK_X,
                    HINGE_Y, -SHELL_Y, -HINGE_SHELL_HZ, HINGE_SHELL_HZ))

    # thumbscrew flanges
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = fuse(part, box(SHELL_BACK_X - 4.0, SHELL_BACK_X,
                              SHELL_Y, PLATE_Y1, zc - 6.0, zc + 6.0))

    # ---- cuts
    # device cavity, open at the rear
    part = part.cut(box(CAV_FRONT_X, SHELL_BACK_X + 1.0,
                        -CAV_Y, CAV_Y, CAV_BOT_Z, CAV_TOP_Z))
    # front window -- leaves a retaining lip down each side only
    part = part.cut(box(SHELL_FRONT_X - 1.0, CAV_FRONT_X,
                        -LIP_IN_Y, LIP_IN_Y,
                        SHELL_BOT_Z - 5.0, SHELL_TOP_Z + 5.0))
    # power button, top edge -- button measured at X -80.44..-78.73.
    # Cut only the rear of the top wall; the front 6 mm stays as a tie bar.
    part = part.cut(box(PWR_CUT_X0, SHELL_BACK_X + 1.0,
                        32.5, 39.9, CAV_TOP_Z - 1.0, SHELL_TOP_Z + 1.0))
    # charge port, bottom edge -- port measured at X -84.49..-80.53.
    # Cut only the front of the bottom wall; the rear 6.4 mm stays as a tie bar.
    part = part.cut(box(SHELL_FRONT_X - 1.0, PORT_CUT_X1,
                        25.5, 39.0, SHELL_BOT_Z - 1.0, CAV_BOT_Z + 1.0))
    # drains
    for yc in (-10.0, -30.0):
        part = part.cut(cyl_z(-80.0, yc, SHELL_BOT_Z - 1.0,
                              CAV_BOT_Z + 1.0, 2.0))
    # hinge pin bore
    part = part.cut(cyl_z(SHELL_BACK_X, HINGE_Y,
                          -HINGE_SHELL_HZ - 1.0, HINGE_SHELL_HZ + 1.0,
                          HINGE_PIN / 2.0))
    # thumbscrew clearance holes
    for zc in (LOCK_DZ, -LOCK_DZ):
        part = part.cut(cyl_x(SHELL_BACK_X - 5.0, SHELL_BACK_X + 1.0,
                              LOCK_Y, zc, LOCK_SCREW_CLR / 2.0))
    return part.clean()

# ------------------------------------------------------------- mast nuts ----
def build_toggle_nut():
    """10.8 x 4.2 x 3.2 -- goes through the 5 mm throat edge-on, then turns
    90 deg to catch both shoulders.  Diagonal 11.59 < 12.0 channel."""
    n = box(0, 3.2, -5.4, 5.4, -2.1, 2.1)
    n = n.cut(cyl_x(-1, 4.2, 0, 0, MAST_BOLT / 2.0 - 0.35))   # tapping drill
    return n.clean()

def build_slide_nut_bar():
    """11.5 x 3.2 x 90 bar, drops in from the mast head; far stronger."""
    b = box(0, 3.2, -5.75, 5.75, -45, 45)
    for zc in (BOLT_DZ, -BOLT_DZ):
        b = b.cut(cyl_x(-1, 4.2, 0, zc, MAST_BOLT / 2.0 - 0.35))
    return b.clean()

def build_knob():
    """Thumbscrew knob: captures an M3 hex head, 6 finger lobes."""
    k = cq.Workplane("XY").circle(11.0).extrude(9.0)
    for i in range(6):
        a = math.radians(i * 60.0)
        k = k.cut(cq.Workplane("XY")
                  .center(12.6 * math.cos(a), 12.6 * math.sin(a))
                  .circle(4.2).extrude(9.0))
    k = k.faces("<Z").workplane().polygon(6, 5.5 / math.cos(math.pi / 6)).cutBlind(-3.0)
    k = k.faces("<Z").workplane().circle(1.8).cutBlind(-9.0)
    return k.val()

# ------------------------------------------------------------------ build ---
print("building back plate ...")
plate_raw = build_back_plate()
plate = principal(plate_raw, "back plate")
print("building front shell ...")
shell_raw = build_front_shell()
shell = principal(shell_raw, "front shell")
for nm, sh in (("back plate", plate), ("front shell", shell)):
    print("  %-12s valid=%s  solids=%d  vol=%.1f cm^3"
          % (nm, sh.isValid(), len(sh.Solids()), sh.Volume() / 1000.0))
print("building hardware ...")
tnut = build_toggle_nut().translate((MAST_SLOT_SHOULDER_X, 0, BOLT_DZ))
bar = build_slide_nut_bar().translate((MAST_SLOT_SHOULDER_X, 0, 0))
knob = build_knob()

# ------------------------------------------------------------- validation ---
def vol(s):
    try:
        return s.Volume()
    except Exception:
        return float("nan")

def clash(a, b, label, tol=1.0):
    v = vol(a.intersect(b))
    flag = "OK " if v < tol else "!! "
    print("  %s%-38s overlap = %9.3f mm^3" % (flag, label, v))
    return v

print("\n--- interference check -------------------------------------------")
clash(plate, mast, "back plate  vs  mast")
clash(plate, atlas, "back plate  vs  Atlas 2")
clash(shell, atlas, "front shell vs  Atlas 2")
clash(shell, mast, "front shell vs  mast")
clash(shell, plate, "front shell vs  back plate")

# does the saddle actually touch the mast, or is it floating?
probe = mast_clearance_solid_at(CLR_MAST + 0.15)
v = vol(plate.intersect(probe))
print("  %sseat proof: plate meets mast+%.2f    overlap = %9.3f mm^3"
      % ("OK " if v > 1.0 else "!! ", CLR_MAST + 0.15, v))

# can the lid actually swing open?
print("\n--- hinge sweep (shell rotated about the pin) ---------------------")
ax0 = (PLATE_FRONT_X, HINGE_Y, -1.0)
ax1 = (PLATE_FRONT_X, HINGE_Y, 1.0)
for ang in (5, 15, 30, 45, 60, 90, 120):
    sw = shell.rotate(ax0, ax1, ang)
    v = vol(sw.intersect(plate))
    print("  %s%4d deg   shell/plate overlap = %9.3f mm^3"
          % ("OK " if v < 1.0 else "!! ", ang, v))

bb = plate.BoundingBox()
print("\nback plate  %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(plate) / 1000.0))
bb = shell.BoundingBox()
print("front shell %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(shell) / 1000.0))
print("stack: mast nose %.2f -> screen %.2f  = %.2f mm standoff"
      % (MAST_NOSE_X, DEV_FRONT_X, DEV_FRONT_X - MAST_NOSE_X))

# --------------------------------------------------------------- exports ----
print("\nexporting ...")
BAD = []
jobs = [("back_plate", plate), ("front_shell", shell),
        ("toggle_nut", build_toggle_nut()),
        ("slide_nut_bar", build_slide_nut_bar()),
        ("thumbscrew_knob", knob)]
for name, s in jobs:
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".step"))
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".stl"),
                        tolerance=0.02, angularTolerance=0.1)
    back = cq.importers.importStep(os.path.join(OUT, name + ".step"))
    nsol = len(back.solids().vals())
    dv = abs(back.val().Volume() - s.Volume())
    ok = (nsol == 1 and dv < 1.0)
    print("  %s%s.step / .stl   (round-trip: %d solid, dV=%.3f mm^3)"
          % ("" if ok else "!! ", name, nsol, dv))
    BAD.extend([] if ok else [name])

# Named-component assemblies.  These carry STEP product structure, so Fusion
# 360 / SolidWorks import them as named, separately selectable COMPONENTS --
# Fusion can only apply joints to components, never to loose bodies.
def named_assembly(items, name, path):
    a = cq.Assembly(name=name)
    for nm, sh, col in items:
        a.add(sh, name=nm, color=cq.Color(*col))
    (a.export if hasattr(a, "export") else a.save)(path)   # .save is deprecated
    return a

MOUNT_ITEMS = [("back_plate",  plate, (0.74, 0.76, 0.80, 1.0)),
               ("front_shell", shell, (0.23, 0.41, 0.63, 1.0)),
               ("toggle_nut",  tnut,  (0.78, 0.58, 0.24, 1.0))]
named_assembly(MOUNT_ITEMS, "atlas2_mast_mount",
               os.path.join(OUT, "assembly_mount_only.step"))
named_assembly(MOUNT_ITEMS + [("mast_express", mast,  (0.67, 0.66, 0.63, 1.0)),
                              ("atlas_2",      atlas, (0.15, 0.16, 0.18, 1.0))],
               "atlas2_mast_mount_in_situ",
               os.path.join(OUT, "assembly_with_mast_and_device.step"))
for f in ("assembly_mount_only", "assembly_with_mast_and_device"):
    names = sorted(set(re.findall(r"PRODUCT\s*\(\s*'([^']+)'", 
                   open(os.path.join(OUT, f + ".step")).read())))
    print("  %s.step   components: %s" % (f, ", ".join(names)))

asm = cq.Compound.makeCompound([plate, shell, tnut])

# meshes used by src/render.py for the assembly views
mast_stub = mast.intersect(box(-70, 70, -60, 60, -70, 70))
for nm, sh in (("_mesh_mast_stub", mast_stub), ("_mesh_device", atlas),
               ("_mesh_shell_open", shell.rotate((PLATE_FRONT_X, HINGE_Y, -1),
                                                 (PLATE_FRONT_X, HINGE_Y, 1), 75))):
    cq.exporters.export(cq.Workplane(obj=sh), os.path.join(OUT, nm + ".stl"),
                        tolerance=0.05, angularTolerance=0.2)
print("  assembly meshes")

views = {"iso": (-1.4, -1.0, 0.9), "front": (-1, 0, 0),
         "side": (0, -1, 0), "top": (0, 0, 1)}
for nm, d in views.items():
    cq.exporters.export(cq.Workplane(obj=asm), os.path.join(OUT, "view_%s.svg" % nm),
        opt={"width": 900, "height": 900, "marginLeft": 20, "marginTop": 20,
             "projectionDir": d, "showAxes": False,
             "strokeWidth": 0.3, "showHidden": False})
    print("  view_%s.svg" % nm)
print("\ndone.")
