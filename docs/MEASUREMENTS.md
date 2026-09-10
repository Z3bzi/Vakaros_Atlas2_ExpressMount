# Measured geometry

Everything below was extracted from the two supplied STEP files with OpenCASCADE
(`src/atlas2_mast_mount.py` re-derives the mast profile at build time, so the
mount tracks the CAD rather than these notes). Nothing is taken from the
scanned Express section drawing — that drawing was only used to confirm the
result looked sane.

## Units

| File | Declared units | Note |
|---|---|---|
| `Mast.step` | millimetre | Autodesk / ST-Developer, AP214 |
| `Atlas_2.step` | **inch** (`CONVERSION_BASED_UNIT('INCH')`) | SolidWorks 2022, "Atlas 2_SIMPLIFIED" |

`Atlas_2.step` mixes inch and metre unit contexts, so a naive text parse of its
`CARTESIAN_POINT`s gives nonsense (a 36 m bounding box). It must be read
through a real STEP reader.

## Mast — Express section

Straight extrusion along Z, hollow, symmetric about Y = 0.

| Quantity | Value |
|---|---|
| Section envelope | 128.52 (X, chord) × 89.21 (Y) mm |
| Forward-most point (nose) | X = **−64.700** |
| Aft-most point (sail track) | X = +63.823 |
| Half width | Y = ±44.606 |
| Wall (at the nose) | ≈ 4.9 mm |

Drawing says 130 × 90; the solid measures 128.5 × 89.2. The drawing figures are
to the theoretical sharp corners.

### Forward T-slot (accessory track — not used by the current mount)

Traced off the section at Z = 250:

| Feature | Value |
|---|---|
| Throat (mouth) width | **5.000 mm** (Y = ±2.500) |
| Throat depth, parallel portion | X = −64.7 → −62.5 |
| Flare | ≈ 34° out to X = −61.0 |
| Bearing shoulder | X = **−61.000**, Y = ±3.520 … ±6.000 |
| Internal channel width | **12.000 mm** (Y = ±6.000) |
| Channel floor | X = **−57.500** (channel is 3.5 mm deep) |
| Total slot depth from the nose | 7.16 mm |

This matches the drawing's `5±0.5` throat callout. It is a flat rectangular
track, i.e. a fitting/accessory slot. The mount used it up to commit `8bc21e8`;
it now mounts aft instead, so the screen faces the cockpit.

### Aft mainsail luff groove (what the mount now bolts into)

Rasterised as solid material from the section at Z = 250:

| Feature | Value |
|---|---|
| Aft-most point of the section | X = **63.822**, at Y ≈ ±15 |
| Recess mouth | X = 63.5, Y = ±13.52, **flared — no undercut** |
| Recess, parallel portion | **20.000 mm** wide (Y = ±10.000), X = 53.4 … 60.0 |
| Recess shoulder (tongue stops here) | X = **53.496** |
| Throat, narrowest | **5.000 mm**, at X = 52.0 |
| Throat extent | X ≈ 49.7 … 53.4 |
| Bolt-rope channel | circle, centre X = **50.04**, r = **10.05** (Ø20.1) |
| Channel usable face | X ≈ 49.3 forward |

Circle fit residual across six measured points is under 0.1 mm, so the channel
is a true Ø20 circular bore.

The clear opening at each depth:

| X | 63.5 | 62.0 | 60.0 | 56.0 | 53.5 | 53.0 | 52.0 | 50.5 | 49.0 | 45.0 | 41.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| width | 27.03 | 24.03 | 20.02 | 20.00 | 20.00 | 6.03 | **5.01** | 5.95 | 20.00 | 17.62 | 10.60 |

Two consequences drove the design:

1. The **20.00 mm parallel recess** is a genuine location feature, so the back
   plate carries a full-height 19.4 mm tongue that takes all the shear and
   rotation. The bolts only clamp.
2. The mouth **flares outward**, so there is nothing to hook onto from
   outside — the fixing has to reach through the 5.00 mm throat into the round
   channel. Hence a half-round bar that drops in from the end of the groove.

Note both slots on this section have a 5.00 mm throat, so the M4 decision
below applies either way.

## Vakaros Atlas 2

8 solids. Device axes: **Xa** across, **Ya** thickness (+Ya = screen side),
**Za** height.

| Quantity | Value |
|---|---|
| Overall | 88.89 (Xa) × 15.76 (Ya) × 115.66 (Za) mm |
| Body | Xa ±44.44, Ya −14.41 … +1.00, Za ±57.64 |
| Front bezel plane | Ya = +1.00 |
| Cover glass | Ya ≈ −0.55, Xa ±42.70, Za ±55.90 |
| **Flat rear plateau** | Ya = **−13.25**, Xa ±25.20, Za ±51.81 |
| Rear-most feature | Ya = −14.41 |

### Feature positions

| Feature | Xa | Ya | Za |
|---|---|---|---|
| Button 1 (front) | 36.61 … 39.49 | −1.79 … **+1.35** | 29.70 … 41.10 |
| Button 2 (front) | 36.61 … 39.49 | −1.79 … +1.35 | 6.10 … 17.50 |
| Button 3 (front) | 36.61 … 39.49 | −1.79 … +1.35 | −17.50 … −6.10 |
| Button 4 (front) | 36.61 … 39.49 | −1.79 … +1.35 | −41.10 … −29.70 |
| Top-centre bar (logo/status) | ±9.70 | −1.79 … +1.35 | 47.91 … 51.29 |
| **Power button (top edge)** | 34.19 … 38.04 | −5.91 … −7.62 | at Za ≈ +57 |
| **Charge port (bottom edge)** | 27.21 … 36.94 | −1.86 … −5.82 | Za ≈ −58.01 |
| Rear protrusion A | −17.03 … −13.16 | to −14.41 | 34.40 … 55.69 |
| Rear protrusion B | 13.16 … 17.03 | to −14.41 | −55.69 … −34.40 |

Three things here differ from the layout assumed in the original plan:

1. **The four buttons are on the FRONT face**, in a column ~5 mm in from the
   right-hand edge — they are not side buttons. They stand 0.35 mm proud of the
   bezel, making them the front-most feature on the device.
2. **The power button is on the top edge but offset to one side** (Xa 34…38),
   not centred, and it sits toward the rear of the thickness.
3. **The charge port is on the bottom edge**, offset to the *same* side as the
   buttons (Xa 27…37).

So all of the controls plus the charge port are grouped at one end of the
device (+Xa). The two rear protrusions stand 1.16 mm proud of the flat rear
plateau and must be relieved, or the device rocks.

## Derived stack

| | X (world) |
|---|---|
| Mast nose | −64.70 |
| Saddle inner face (nose + 0.4 clearance) | −65.10 |
| Back-plate front face / parting plane | **−73.10** |
| Device rear plateau | −73.10 |
| Device front bezel | −87.35 |
| Shell lip inner face | −87.55 |
| Shell front face | −90.55 |

Total standoff, mast nose to screen: **22.65 mm**.

## Atlas 2 top edge — why retention is a crown contact

The slide-in design retains the device with a cam pressing on its top edge, so
how flat that edge is matters. Measured as horizontal section area of the device
in 4 mm wide Y bands, across its full 14.6 mm depth (58.4 mm² would be fully
flat):

| Y band | Z = 57.50 | 57.20 | 56.80 | 56.00 |
|---|---|---|---|---|
| 0…4 | 7.1 | 18.0 | 32.5 | 32.7 |
| 16…20 | 7.1 | 18.0 | 31.6 | 28.8 |
| 32…36 | 7.1 | 18.0 | 32.5 | 32.6 |
| 38…42 | 0.2 | 2.7 | 9.3 | 24.6 |
| 42…46 | 0.0 | 0.0 | 0.0 | 0.0 |

At the very top (Z = 57.64) there is only **2.0 mm²** of section across the whole
device. The top is a rounded crown, about 1.8 mm of flat across a 14.6 mm depth,
and it rolls off hard past Y ≈ 38.

Consequence: no retainer pressing from above can get a large contact patch. The
cam is set 0.35 mm above the crown, giving 0.40 mm of free lift before it bites.
That stops the device leaving — the rails constrain every other direction — but
it is point contact on a curve, not a flush clamp.

## The removal corridor

Because the device now loads from the top, the volume it sweeps on the way in
is a hard constraint on where anything can live:

| Region | Extent |
|---|---|
| Main body | X 71.22…85.57, \|Y\| ≤ 44.44, Z above 57.64 |
| Rear protrusion channels | X 70.06…71.22, \|Y\| 13.16…17.03, Z above 57.64 |

Anything in that volume blocks insertion regardless of what it does when
locked. Behind the plate face the usable gap between the mast (X 63.82) and the
protrusion channels is only **5.7 mm** — too narrow for a pivot boss, which is
why the lock ended up outboard on the rail pad.

## Orientation

The device is mounted with its **+Za end downward**: the big raised bar on the
front face (Xa ±9.70, Za 47.91…51.29) sits at the bottom of the screen. The
transform is therefore

    Xw = Ya + DEV_CX ,  Yw = +Xa ,  Zw = −Za

a 180° rotation about the device's own Ya axis (the screen normal), then −90°
about Z. Determinant +1, so it is a rotation and not a mirror.

Where the features land, with the 2 mm case (`DEV_CX` = 86.472):

| Feature | Y | Z | X |
|---|---|---|---|
| Big raised bar (screen) | −9.70…9.70 | **−51.29…−47.91** | 84.68…87.82 |
| Edge control A | 34.19…38.04 | **−57.02…−54.19** (bottom) | 78.85…80.56 |
| Edge control B | 27.21…36.94 | **55.30…58.01** (top) | 80.65…84.61 |
| 4 front buttons | 36.61…39.49 | −41.10…−29.70 | 84.68…87.82 |
| Rear protrusion pair | ±13.16…17.03 | ±34.40…55.69 | 72.06…77.46 |

Everything the user touches is on **+Y**, which is the viewer's right when
facing the screen. That is why the lock went to −Y.

## Silicone case

The Atlas 2 is carried in a 2 mm silicone case, so the cradle is built around an
envelope of the device grown by `CASE_T` = 2.0 on every face, plus the usual
0.3 mm fit clearance:

| | Bare device | Envelope |
|---|---|---|
| Half width | 44.44 | **46.44** |
| Top / bottom | ±57.64 | **±59.64** |
| Back → front (Ya) | −13.25 … +1.00 | **−15.25 … +3.00** |
| Depth | 14.25 mm | **18.25 mm** |

Two knock-on effects worth noting. The rear protrusions stand 1.16 mm proud of
the device's rear plateau; a case following that contour bulges the same amount,
so the 2 mm relief channels are still required. And the cam now bears on the
flat top of the case rather than the device's rounded crown, which is a much
better contact — see the README.
