#!/usr/bin/env python3
"""
Vakaros Atlas 2  ->  Express-section mast mount
===============================================
Slide-in cradle, aft face of the mast, screen facing the cockpit.

The device drops in from the TOP and lands on a solid ledge that is part of the
cradle body.  Nothing that moves carries the device:

    weight (-Z)        -> fixed bottom ledge
    fore/aft (X)       -> fixed side-rail lips
    athwartships (Y)   -> fixed side rails
    lift-out (+Z)      -> the rotating lock, which is a retainer only

Rotating lock: a lever that flips over the top edge of the device, pivoting on
a Y-parallel axis BEHIND the plate face.  That position is forced -- the device
sweeps a removal corridor (X 71.22..85.57, |Y| <= 44.44, Z above 57.64) and
anything left in it, latch or pivot, stops the device going in at all.  Flipped
up, the whole lever sits at X < 70 and the corridor is clear.

Mast fixing is unchanged: a full-height tongue in the mainsail luff groove plus
two M4 bolts through the 5.00 mm throat into a half-round bar in the channel.

Coordinate system (world, mm):  +X aft, +Y athwartships, +Z up (mast axis).
Device frame -> world:  Xw = Ya + DEV_CX,  Yw = -Xa,  Zw = Za
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
MAST_AFT_X      = 63.822
RECESS_HALF_W   = 10.000
RECESS_FLOOR_X  = 53.496
THROAT_MIN_W    = 5.000
CHANNEL_CX      = 50.04
CHANNEL_R       = 10.05
CHANNEL_MOUTH_X = 49.30

DEV_HALF_W     = 44.44
DEV_FRONT_Y    =  1.00
DEV_BUTTON_Y   =  1.35
DEV_BACK_Y     = -13.25
DEV_BACKMOST_Y = -14.41
DEV_TOP_Z      =  57.64
DEV_BOT_Z      = -57.64
DEV_PORT_BOT_Z = -58.01

# The device is mounted with its +Za end DOWN: the big raised bar on the front
# face (Za 47.91..51.29) is at the bottom.  So Zw = -Za, and every edge feature
# below lands on the opposite end from its raw Za.
BTN_XA  = (36.61, 39.49)     # 4 front buttons, Za +/-35.40 and +/-11.80
BAR_ZA  = (47.91, 51.29)     # big raised bar on the screen -- this end is DOWN
ENDA_XA = (34.19, 38.04)     # edge control at Za ~ +57 -> lands on the BOTTOM
ENDA_YA = (-7.62, -5.91)
ENDB_XA = (27.21, 36.94)     # edge control at Za ~ -58 -> lands on the TOP
ENDB_YA = (-5.82, -1.86)
PROT_XA = (13.16, 17.03)

# ------------------------------------------------------------------ design --
CLR          = 0.30
CASE_T       = 2.00       # Atlas 2 lives in a 2 mm silicone case
CLR_MAST     = 0.50
RAIL_WALL    = 3.00
LIP_T        = 3.00
LEDGE_T      = 4.00
AFT_WALL     = 7.00
PLATE_CORE_T = 7.00

TONGUE_HALF_W     = 9.70
MAST_BOLT         = 4.0
MAST_BOLT_CLR     = 4.5
MAST_BOLT_CBORE   = 9.0
MAST_BOLT_CBORE_D = 4.5
BOLT_DZ           = 35.0

# Rotating lock: a cam on a vertical axis, on a pad on top of the +Y side rail.
# It has to live OUTBOARD of the device (|Y| > 44.44), not above it: behind the
# plate face the gap between the mast (X 63.82) and the rear-protrusion channels
# (X 70.06) is 5.7 mm, and a lobe swinging at Y = 0 crosses the mast's aft
# shoulders.  Outboard of the rail there is no mast and no corridor, so a proper
# M5 pivot boss fits.  Locked, the lobe reaches inboard over the device's top
# corner; a quarter turn swings it fore-and-aft, clear.
LOCK_PIVOT_X   = 79.0
LOCK_PIVOT_Y   = -53.5       # -Y: all the device's controls are on +Y
LOCK_BOSS_R    = 6.5
LOCK_LOBE_LEN  = 13.5
LOCK_LOBE_HW   = 5.0
LOCK_T         = 6.0
LOCK_BORE      = 5.3         # M5 pivot thumbscrew
LOCK_INSERT_D  = 6.4         # M5 brass heat-set insert
LOCK_INSERT_DP = 9.5
LOCK_HASP_Y    = -47.5       # pin / seizing wire, lines up only when locked
LOCK_HASP_D    = 4.2
LOCK_PAD_X     = (72.0, 86.0)
LOCK_PAD_Y     = -60.0
LOCK_PAD_Z0    = 30.0
LOCK_PAD_DROP  = 0.15        # pad sits just below the device crown
LOCK_PAD_GAP   = 0.50        # running clearance under the cam

PLATE_Y0, PLATE_Y1 = -51.0, 51.0

# --------------------------------------------------------------- derived ----
PLATE_FACE_X = MAST_AFT_X + CLR_MAST + AFT_WALL          # 71.222
CASED_BACK_Y = DEV_BACK_Y - CASE_T
DEV_CX       = PLATE_FACE_X - CASED_BACK_Y

def dvx(ya): return ya + DEV_CX
def dvy(xa): return xa            # flipped device: +Xa -> +Yw
def dvz(za): return -za           # flipped device: +Za is DOWN
def dvxs(a, b): return tuple(sorted((dvx(a), dvx(b))))
def dvys(a, b): return tuple(sorted((dvy(a), dvy(b))))
def dvzs(a, b): return tuple(sorted((dvz(a), dvz(b))))

# envelope = device grown by the silicone case
ENV_HALF_W   = DEV_HALF_W + CASE_T
ENV_TOP_Z    = DEV_TOP_Z + CASE_T
ENV_BOT_Z    = -ENV_TOP_Z
ENV_FRONT_X  = dvx(DEV_FRONT_Y + CASE_T)
DEV_SCREEN_X = dvx(DEV_FRONT_Y)

CAV_Y        = ENV_HALF_W + CLR
CAV_FRONT_X  = ENV_FRONT_X + 0.20
LEDGE_TOP_Z  = ENV_BOT_Z
CRADLE_BOT_Z = LEDGE_TOP_Z - LEDGE_T
RAIL_TOP_Z   = ENV_TOP_Z + 0.40
RAIL_OUT_Y   = CAV_Y + RAIL_WALL
RAIL_FRONT_X = CAV_FRONT_X + LIP_T
LIP_IN_Y     = ENV_HALF_W - 3.0
LOCK_PAD_TOP_Z = ENV_TOP_Z - LOCK_PAD_DROP
LOCK_UNDER_Z = LOCK_PAD_TOP_Z + LOCK_PAD_GAP
LOCK_TOP_Z   = LOCK_UNDER_Z + LOCK_T
LOCK_TIP_Y   = LOCK_PIVOT_Y + LOCK_LOBE_LEN
PLATE_TOP_Z  = ENV_TOP_Z + 0.30

# cutouts derived from the measured feature boxes, widened for the case
_M = CASE_T + 2.0
BOTCTL_Y  = (dvys(*ENDA_XA)[0] - _M, dvys(*ENDA_XA)[1] + _M)
BOTCTL_X1 = dvxs(*ENDA_YA)[1] + _M
TOPCTL_Y  = (dvys(*ENDB_XA)[0] - _M, dvys(*ENDB_XA)[1] + _M)
TOPCTL_X  = dvxs(*ENDB_YA)
RELIEF_Y  = (PROT_XA[0] - 1.2, PROT_XA[1] + 1.5)

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
         .rotate((0, 0, 0), (0, 1, 0), 180)      # upside down: +Za end goes DOWN
         .rotate((0, 0, 0), (0, 0, 1), -90)
         .translate((DEV_CX, 0, 0)))

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
    luff groove floored at the recess shoulder so the plate grows a tongue into
    the recess but never into the throat."""
    import numpy as np
    pts = []
    for y in np.linspace(-ylim, ylim, ny):
        xm = aft_xmax(float(y))
        pts.append((max(xm if xm is not None else RECESS_FLOOR_X,
                        RECESS_FLOOR_X) + clr, float(y)))
    poly = pts + [(-100.0, pts[-1][1]), (-100.0, pts[0][1])]
    return (cq.Workplane("XY").polyline(poly).close()
            .extrude(depth).val().translate((0, 0, -depth / 2.0)))

MASTCLR = mast_aft_clearance(CLR_MAST)
print("  aft clearance prism ok, X %.2f..%.2f"
      % (MASTCLR.BoundingBox().xmin, MASTCLR.BoundingBox().xmax))

# ----------------------------------------------------------------- cradle ---
def build_cradle():
    # back plate
    part = box(PLATE_FACE_X - PLATE_CORE_T, PLATE_FACE_X,
               PLATE_Y0, PLATE_Y1, CRADLE_BOT_Z, PLATE_TOP_Z)
    # full-height tongue into the 20 mm luff-groove recess
    part = fuse(part, box(RECESS_FLOOR_X - 3.0, PLATE_FACE_X,
                          -TONGUE_HALF_W, TONGUE_HALF_W,
                          CRADLE_BOT_Z, PLATE_TOP_Z))
    # saddle wings onto the aft skin either side of the groove
    for s in (1, -1):
        part = fuse(part, box(57.0, PLATE_FACE_X, *sorted((s * 12.0, s * 23.0)),
                              CRADLE_BOT_Z, PLATE_TOP_Z))
    # side rails with front retaining lips -- fixed, they take all the fore/aft
    for s in (1, -1):
        part = fuse(part, box(PLATE_FACE_X, RAIL_FRONT_X,
                              *sorted((s * CAV_Y, s * RAIL_OUT_Y)),
                              CRADLE_BOT_Z, RAIL_TOP_Z))
        part = fuse(part, box(CAV_FRONT_X, RAIL_FRONT_X,
                              *sorted((s * LIP_IN_Y, s * RAIL_OUT_Y)),
                              CRADLE_BOT_Z, RAIL_TOP_Z))
    # pad on top of the +Y rail that carries the rotating lock
    part = fuse(part, box(LOCK_PAD_X[0], LOCK_PAD_X[1],
                          *sorted((-CAV_Y, LOCK_PAD_Y)),
                          LOCK_PAD_Z0, LOCK_PAD_TOP_Z))
    # rail top is cut down under the cam so the lobe can swing over it
    part = part.cut(box(LOCK_PAD_X[0] - 0.6, LOCK_PAD_X[1] + 0.6,
                        *sorted((-CAV_Y, LOCK_PAD_Y - 1.0)),
                        LOCK_PAD_TOP_Z, RAIL_TOP_Z + 1.0))
    # load-bearing bottom ledge -- the device rests here, nothing else
    part = fuse(part, box(PLATE_FACE_X, RAIL_FRONT_X, -RAIL_OUT_Y, RAIL_OUT_Y,
                          CRADLE_BOT_Z, LEDGE_TOP_Z))
    part = part.cut(MASTCLR)
    # rear-protrusion relief channels, open at the top so they guide the slide
    for s in (1, -1):
        part = part.cut(box(PLATE_FACE_X - 2.0, PLATE_FACE_X,
                            *sorted((s * RELIEF_Y[0], s * RELIEF_Y[1])),
                            -57.0, PLATE_TOP_Z + 1.0))
    # bottom-edge control: notch through the ledge, open forward
    part = part.cut(box(PLATE_FACE_X - 1.0, BOTCTL_X1, *BOTCTL_Y,
                        CRADLE_BOT_Z - 1.0, LEDGE_TOP_Z + 0.6))
    # drains
    for yc in (-12.0, -32.0):
        part = part.cut(cyl_z(PLATE_FACE_X + 8.0, yc,
                              CRADLE_BOT_Z - 1.0, LEDGE_TOP_Z + 1.0, 2.0))
    # mast bolts
    for zc in (BOLT_DZ, -BOLT_DZ):
        part = part.cut(cyl_x(CHANNEL_MOUTH_X, PLATE_FACE_X + 1.0, 0.0, zc,
                              MAST_BOLT_CLR / 2.0))
        part = part.cut(cyl_x(PLATE_FACE_X - MAST_BOLT_CBORE_D,
                              PLATE_FACE_X + 0.1, 0.0, zc, MAST_BOLT_CBORE / 2.0))
    # lock: M5 insert for the pivot thumbscrew, plus the hasp pin hole
    part = part.cut(cyl_z(LOCK_PIVOT_X, LOCK_PIVOT_Y,
                          LOCK_PAD_TOP_Z - LOCK_INSERT_DP, LOCK_PAD_TOP_Z + 0.1,
                          LOCK_INSERT_D / 2.0))
    part = part.cut(cyl_z(LOCK_PIVOT_X, LOCK_HASP_Y, LOCK_PAD_TOP_Z - 10.0,
                          LOCK_PAD_TOP_Z + 0.1, LOCK_HASP_D / 2.0))
    return part.clean()

# ------------------------------------------------------------------- lock ---
def build_lock():
    """Cam: lobe inboard = locked, over the device's top corner.  A quarter turn
    swings it fore-and-aft, outboard of the device, and the device lifts out."""
    px, py = LOCK_PIVOT_X, LOCK_PIVOT_Y
    part = fuse(
        cyl_z(px, py, LOCK_UNDER_Z, LOCK_TOP_Z, LOCK_BOSS_R),
        box(px - LOCK_LOBE_HW, px + LOCK_LOBE_HW, *sorted((LOCK_TIP_Y, py)),
            LOCK_UNDER_Z, LOCK_TOP_Z),
        cyl_z(px, LOCK_TIP_Y, LOCK_UNDER_Z, LOCK_TOP_Z, LOCK_LOBE_HW))
    for i in range(8):                                   # finger flutes
        a = math.radians(i * 45.0 + 22.5)
        part = part.cut(cyl_z(px + (LOCK_BOSS_R + 1.6) * math.cos(a),
                              py + (LOCK_BOSS_R + 1.6) * math.sin(a),
                              LOCK_UNDER_Z - 1, LOCK_TOP_Z + 1, 1.7))
    part = part.cut(cyl_z(px, py, LOCK_UNDER_Z - 1, LOCK_TOP_Z + 1, LOCK_BORE / 2.0))
    part = part.cut(cyl_z(px, LOCK_HASP_Y, LOCK_UNDER_Z - 1, LOCK_TOP_Z + 1,
                          LOCK_HASP_D / 2.0))
    return part.clean()

def lock_at(shape, angle):
    return shape.rotate((LOCK_PIVOT_X, LOCK_PIVOT_Y, 0),
                        (LOCK_PIVOT_X, LOCK_PIVOT_Y, 1), angle)

def luff_bar(length, holes):
    seg = cyl_z(CHANNEL_CX, 0.0, -length / 2.0, length / 2.0, CHANNEL_R - 0.35)
    seg = seg.cut(box(CHANNEL_MOUTH_X, CHANNEL_CX + 20.0, -20, 20, -length, length))
    for zc in holes:
        seg = seg.cut(cyl_x(CHANNEL_MOUTH_X - 9.0, CHANNEL_MOUTH_X + 1.0,
                            0.0, zc, MAST_BOLT / 2.0 - 0.35))
    return seg.clean()

# ------------------------------------------------------------------ build ---
print("building cradle ...")
cradle = principal(build_cradle(), "cradle")
print("building lock ...")
lock = principal(build_lock(), "lock")
for nm, sh in (("cradle", cradle), ("lock", lock)):
    print("  %-8s valid=%s  solids=%d  vol=%.1f cm^3"
          % (nm, sh.isValid(), len(sh.Solids()), sh.Volume() / 1000.0))
bar = luff_bar(90.0, (BOLT_DZ, -BOLT_DZ))
slug = luff_bar(25.0, (0.0,))

# ------------------------------------------------------------- validation ---
def vol(s):
    try: return s.Volume()
    except Exception: return float("nan")

def chk(cond, label, extra=""):
    print("  %s%-46s %s" % ("OK " if cond else "!! ", label, extra))
    return cond

def clash(a, b, label, tol=1.0):
    v = vol(a.intersect(b))
    chk(v < tol, label, "overlap = %9.3f mm^3" % v)
    return v

FAIL = []
print("\n--- interference (lock closed) -----------------------------------")
for a, b, l in ((cradle, mast, "cradle vs mast"), (cradle, atlas, "cradle vs Atlas 2"),
                (lock, atlas, "lock   vs Atlas 2"), (lock, cradle, "lock   vs cradle"),
                (lock, mast, "lock   vs mast"), (bar, mast, "luff bar vs mast")):
    if clash(a, b, l) >= 1.0: FAIL.append(l)

v = vol(cradle.intersect(mast_aft_clearance(CLR_MAST + 0.15)))
if not chk(v > 1.0, "seat proof: cradle meets mast+0.65",
           "overlap = %9.3f mm^3" % v): FAIL.append("seat")

# which way does the lock open?
print("\n--- lock rotation ------------------------------------------------")
_ab = atlas.BoundingBox()
_ZTOP = ENV_TOP_Z + 140.0
CORRIDOR = fuse(
    box(PLATE_FACE_X, ENV_FRONT_X, -ENV_HALF_W, ENV_HALF_W, ENV_TOP_Z, _ZTOP),
    box(_ab.xmin - CASE_T, PLATE_FACE_X, PROT_XA[0] - 0.3, PROT_XA[1] + 0.3,
        ENV_TOP_Z, _ZTOP),
    box(_ab.xmin - CASE_T, PLATE_FACE_X, -PROT_XA[1] - 0.3, -PROT_XA[0] + 0.3,
        ENV_TOP_Z, _ZTOP))
# the cased device as a conservative box -- this is what actually has to fit
CASED = box(PLATE_FACE_X, ENV_FRONT_X, -ENV_HALF_W, ENV_HALF_W,
            ENV_BOT_Z, ENV_TOP_Z)
best = None
for ang in (90, -90):
    o = lock_at(lock, ang)
    v = vol(o.intersect(CORRIDOR)) + vol(o.intersect(cradle)) + vol(o.intersect(mast))
    print("     rotate %+4d deg -> obstruction %9.3f mm^3" % (ang, v))
    if best is None or v < best[1]: best = (ang, v)
LOCK_OPEN_ANGLE = best[0]
if not chk(best[1] < 1.0, "lock opens clear at %+d deg" % LOCK_OPEN_ANGLE,
           "residual = %.3f mm^3" % best[1]): FAIL.append("lock open")
lock_open = lock_at(lock, LOCK_OPEN_ANGLE)

print("\n--- slide-in corridor (lock open) --------------------------------")
v = vol(cradle.intersect(CORRIDOR))
if not chk(v < 1.0, "cradle clear of removal corridor",
           "overlap = %9.3f mm^3" % v): FAIL.append("corridor")
worst = 0.0
for dz in (0, 5, 10, 20, 40, 60, 80, 100, 120):
    moved = atlas.translate((0, 0, dz))
    w = vol(moved.intersect(cradle)) + vol(moved.intersect(lock_open))
    worst = max(worst, w)
    if w >= 1.0: print("     !! blocked at +%d mm: %.3f mm^3" % (dz, w))
if not chk(worst < 1.0, "device slides in from the top, 0..120 mm",
           "worst overlap = %.3f mm^3" % worst): FAIL.append("slide")

print("\n--- retention and access -----------------------------------------")
# the lock retains the CASE, not the bare device -- measure against the envelope
free = None
for mm in [x / 20.0 for x in range(1, 61)]:
    if vol(CASED.translate((0, 0, mm)).intersect(lock)) > 0.02:
        free = mm; break
if not chk(free is not None and free <= 0.60,
           "closed lock: free lift before it bites",
           "%.2f mm" % (free if free else 99)): FAIL.append("retain")
v = vol(CASED.translate((0, 0, 1.0)).intersect(lock))
if not chk(v > 1.0, "closed lock resists a 1 mm lift",
           "interference = %9.3f mm^3" % v): FAIL.append("retain force")
SLAB_T = 0.10
slab = box(_ab.xmin, _ab.xmax, _ab.ymin, _ab.ymax,
           LEDGE_TOP_Z - SLAB_T, LEDGE_TOP_Z)
area = vol(cradle.intersect(slab)) / SLAB_T
if not chk(area > 400.0, "load-bearing ledge under the device",
           "bearing area = %.0f mm^2" % area): FAIL.append("ledge area")

# nothing above the power button, nothing over the four front buttons
bot = box(dvxs(*ENDA_YA)[0] - 0.5, dvxs(*ENDA_YA)[1] + 0.5,
          BOTCTL_Y[0] + 1.4, BOTCTL_Y[1] - 1.4, ENV_BOT_Z - 60.0, ENV_BOT_Z)
v = vol(cradle.intersect(bot)) + vol(lock.intersect(bot))
if not chk(v < 1.0, "bottom edge control: clear access from below",
           "obstruction = %.3f mm^3" % v): FAIL.append("bottom control")
btn = box(ENV_FRONT_X - 0.5, ENV_FRONT_X + 40.0, dvys(*BTN_XA)[0] - 0.5,
          dvys(*BTN_XA)[1] + 0.5, -50.0, 50.0)
v = vol(cradle.intersect(btn)) + vol(lock.intersect(btn))
if not chk(v < 1.0, "4 front buttons: nothing in front of them",
           "obstruction = %.3f mm^3" % v): FAIL.append("front buttons")
top = box(TOPCTL_X[0] - 0.5, TOPCTL_X[1] + 0.5, TOPCTL_Y[0] + 1.6,
          TOPCTL_Y[1] - 1.6, ENV_TOP_Z, ENV_TOP_Z + 60.0)
v = vol(cradle.intersect(top)) + vol(lock.intersect(top))
if not chk(v < 1.0, "top edge control: clear access from above",
           "obstruction = %.3f mm^3" % v): FAIL.append("top control")
v = vol(cradle.intersect(CASED)) + vol(lock.intersect(CASED))
if not chk(v < 1.0, "cased device (device + 2 mm) fits the cavity",
           "overlap = %.3f mm^3" % v): FAIL.append("case fit")

bb = cradle.BoundingBox()
print("\ncradle %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(cradle) / 1000.0))
bb = lock.BoundingBox()
print("lock   %.1f x %.1f x %.1f mm   %.1f cm^3"
      % (bb.xlen, bb.ylen, bb.zlen, vol(lock) / 1000.0))
print("stack: mast aft face %.2f -> screen %.2f = %.2f mm standoff"
      % (MAST_AFT_X, DEV_SCREEN_X, DEV_SCREEN_X - MAST_AFT_X))
print("cavity: %.2f x %.2f x %.2f mm for a %.0f mm cased device"
      % (2 * CAV_Y, CAV_FRONT_X - PLATE_FACE_X, RAIL_TOP_Z - LEDGE_TOP_Z, CASE_T))
print("lock: quarter turn (%+d deg) to open; underside sits %.2f mm above the device"
      % (LOCK_OPEN_ANGLE, LOCK_UNDER_Z - ENV_TOP_Z))

# --------------------------------------------------------------- exports ----
print("\nexporting ...")
for name, s in [("cradle", cradle), ("lock", lock), ("luff_nut_bar", bar),
                ("luff_nut_slug", slug)]:
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".step"))
    cq.exporters.export(cq.Workplane(obj=s), os.path.join(OUT, name + ".stl"),
                        tolerance=0.02, angularTolerance=0.1)
    back = cq.importers.importStep(os.path.join(OUT, name + ".step"))
    n = len(back.solids().vals()); dv = abs(back.val().Volume() - s.Volume())
    if not chk(n == 1 and dv < 1.0, "%s.step / .stl" % name,
               "round-trip: %d solid, dV=%.3f mm^3" % (n, dv)):
        FAIL.append(name + ".step")

def named_assembly(items, name, path):
    a = cq.Assembly(name=name)
    for nm, sh, col in items:
        a.add(sh, name=nm, color=cq.Color(*col))
    (a.export if hasattr(a, "export") else a.save)(path)

MOUNT = [("cradle",       cradle, (0.74, 0.76, 0.80, 1.0)),
         ("lock",         lock,   (0.23, 0.41, 0.63, 1.0)),
         ("luff_nut_bar", bar,    (0.78, 0.58, 0.24, 1.0))]
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

mast_stub = mast.intersect(box(-70, 95, -60, 60, -75, 75))
for nm, sh in (("_mesh_mast_stub", mast_stub), ("_mesh_device", atlas),
               ("_mesh_lock_open", lock_open),
               ("_mesh_device_raised", atlas.translate((0, 0, 62.0)))):
    cq.exporters.export(cq.Workplane(obj=sh), os.path.join(OUT, nm + ".stl"),
                        tolerance=0.05, angularTolerance=0.2)
print("  assembly meshes")

print("\n%s" % ("ALL CHECKS PASSED" if not FAIL
                else "FAILURES: " + ", ".join(FAIL)))
