# Vakaros Atlas 2 — Express mast mount

A two-part printed mount for the **aft face** of an Express section mast, so
the screen faces the cockpit. It locates in the mainsail luff groove and locks
the Atlas 2 in a hinged, thumbscrew-secured clamshell. Screen fully visible;
every control and the charge port reachable with the device locked in.

Generated parametrically — `src/atlas2_mast_mount.py` re-reads
`reference/Mast.step` and `reference/Atlas_2.step` on every run and derives all
mating geometry and cutout positions from them. Nothing is hand-transcribed.

![assembly](export/render_assembly_closed_iso.png)

## Parts

| Part | File | Notes |
|---|---|---|
| Back plate | `export/back_plate.step` / `.stl` | Groove tongue + saddle + device backing, 122 cm³ |
| Front shell | `export/front_shell.step` / `.stl` | Hinged clamshell, 25 cm³ |
| Luff nut bar | `export/luff_nut_bar.step` / `.stl` | Preferred — one bar spanning both bolts |
| Luff nut slug | `export/luff_nut_slug.step` / `.stl` | Short single-bolt alternative, 25 mm |
| Thumbscrew knob ×2 | `export/thumbscrew_knob.step` / `.stl` | Captures an M3 hex head |
| Assemblies | `export/assembly_*.step` | Named components, see Fusion section |

Back plate 113.5 × 124.0 × 21.3 mm, shell 113.5 × 122.2 × 21.5 mm. The screen
sits **21.75 mm** aft of the mast's aft face.

## How it fixes to the mast

The luff groove measures (see `docs/MEASUREMENTS.md`):

- outer recess **20.00 mm** wide, X 53.4 → 60.0, flaring to 27 mm at the mouth
- throat **5.00 mm** minimum
- bolt-rope channel: a true circle, centre X 50.04, **r 10.05**

Three consequences shaped the design:

1. **The 20 mm parallel recess is a location feature.** The back plate carries
   a full-height **19.4 mm tongue** that slides into it with 0.3 mm a side and
   6.0 mm of engagement in the parallel section. That tongue takes all the
   shear and all the rotation — the bolts only clamp.
2. **The mouth flares outward**, so there is nothing to hook onto from
   outside. The fixing has to reach through the 5.00 mm throat.
3. **The channel is a clean Ø20 bore**, so the nut is a half-round bar — a
   circular segment, flat face aft, tapped M4 — that drops in from the open end
   of the groove. The 90 mm bar spans both bolts, cannot rotate, and bears on
   roughly 190 mm² of channel wall.

> **This works below the gooseneck only.** Above it the mainsail bolt rope
> occupies the channel. Site the mount below the sail feeder, and check that
> lowering the main fully does not run the bolt rope down onto the bar.

## Design

| Feature | Detail |
|---|---|
| Mast location | 19.4 mm full-height tongue in the 20.00 mm recess, 6.0 mm engagement |
| Mast fixing | 2 × **M4** at 70 mm centres, through the throat into the luff bar |
| Saddle | Wings onto the aft skin either side of the groove, 0.5 mm clearance |
| Wall over the aft skin | 7 mm; 17 mm of material through the tongue at the bolts |
| Device clearance | 0.3 mm lateral, 0.2 mm in depth |
| Rear relief | Two 2 mm channels for the Atlas's rear protrusions |
| Front | Fully open — all four buttons and the whole screen exposed |
| Retention | 3 mm lip down each side, overlapping the bezel by 3 mm |
| Top | Notch over the measured power button, 6.0 mm screen-side tie bar |
| Bottom | Notch over the measured charge port, 6.2 mm mast-side tie bar |
| Drainage | 2 × Ø4 mm holes in the bottom wall |
| Hinge | 3-knuckle, 3 mm pin, on the **right** as you face the screen |
| Lock | 2 × M3 thumbscrews at 60 mm centres, on the **left**, into brass inserts |
| Walls | 3 mm minimum throughout |

Facing the screen: hinge right, thumbscrews left, and the Atlas's four buttons,
power button and charge port are all on the **left**.

**The mast bolts sit under the device.** Once the Atlas is in and the
thumbscrews are done up, the mount cannot be unbolted from the mast without
first opening the clamshell.

## Findings that shaped this

Each came out of measuring the CAD, and each would otherwise have produced a
part that did not work.

### M5 will not fit — this uses M4

**Both** slots on this section have a throat measuring exactly **5.000 mm**,
and the section drawing tolerances it `5±0.5`. An M5 screw has a 5.0 mm major
diameter, so it cannot pass. **M4** gives 1.0 mm clearance nominal, 0.5 mm at
the worst end of tolerance. Change `MAST_BOLT` in the build script to revisit.

### The four buttons are on the front face, not the side

They sit in a column 5 mm in from one edge and stand 0.35 mm proud of the
bezel. A side cutout would have missed them; the originally planned corner
retaining tabs would have landed on top of them. Retention is instead a
**full-height lip down each side**, stopping 1.95 mm clear of the buttons.
Because the glass is recessed 1.55 mm below the bezel, the lip never touches
the screen.

The power button and charge port are on the top and bottom edges but **offset
to the same side as the buttons**, so both notches are placed on their measured
positions rather than centrally.

### The Atlas does not have a flat back

Two protrusions stand 1.16 mm proud of the rear plateau, diagonally opposite.
On a flat plate the device would rock on them. Two 2 mm relief channels take
them, and it seats on the true plateau either side.

## Bill of materials

| Qty | Item |
|---|---|
| 2 | **M4 × 25** A4 stainless socket cap screw (M4 × 30 bottoms out — the bar is only 9 mm deep) |
| 2 | M4 A4 washer (Ø9) |
| 1 | Luff nut bar — 90 mm, tapped M4 at 70 mm centres. Aluminium or stainless |
| — | *or* 2 × 25 mm luff nut slug, tapped M4 |
| 1 | 3 mm A4 stainless rod, 114 mm — hinge pin |
| 2 | M3 brass heat-set insert, Ø4.0 × 5.7 mm |
| 2 | M3 × 12 A4 stainless hex-head screw |
| 2 | Printed knob (`thumbscrew_knob.stl`), epoxied to the screw head |
| 2 | M3 silicone O-ring — slip on behind the flange to make the screws captive |
| 1 | 0.5 mm self-adhesive neoprene/EVA pad, ~85 × 110 mm (optional, kills rattle) |
| — | 1 mm seizing wire or a split pin through the Ø1.6 hole at the top of the hinge |

The luff nut is a circular segment sized r 9.70 against the channel's r 10.05,
with its flat at X 49.30. Make it from metal — printed plastic threads will not
hold here. It must be fed in from the open end of the groove; it cannot be
toggled through the 5 mm throat.

## Printing

PETG, ASA or nylon. PLA will creep and go brittle in UV — do not use it on a mast.

| | Back plate | Front shell |
|---|---|---|
| Orientation | Standing on its bottom edge (mast axis vertical) | Screen face down, cavity opening up |
| Support | None — the tongue prints as a vertical rib | Under the hinge knuckle and the two flanges only |
| Bed | Brim recommended | — |
| Perimeters | 5 | 4 |
| Infill | 40 % gyroid | 30 % gyroid |
| Layer | 0.2 mm | 0.2 mm |

Standing the back plate on edge puts the hinge bores vertical so they come out
round without support, and runs both the tongue and the saddle as straight
vertical extrusions.

## Assembly

1. Print both parts. Melt the two M3 inserts into the back plate ears from the
   device face.
2. Feed the luff nut bar into the mainsail groove from its open end and slide
   it to the height you want, **below the gooseneck**.
3. Offer the back plate up so its tongue enters the recess, and run in the two
   M4 × 25 screws with washers. The heads sit in counterbores, flush with the
   plate face. The tongue should feel snug in the groove before you tighten.
4. Optional: stick the neoprene pad to the plate face, clear of the two relief
   channels.
5. Hang the shell on the plate and drop the 3 mm pin down through the knuckles.
   The bottom knuckle is blind so the pin cannot fall through. Secure the top
   with seizing wire through the Ø1.6 cross-hole.
6. Epoxy the knobs onto the two M3 hex-head screws; slip an O-ring on each
   shank behind the flange so they stay captive.
7. Drop the Atlas in — screen aft, controls to the left, rear protrusions into
   the relief channels — swing the shell shut and do up both knobs.

## Opening in Fusion 360

Use the **STEP** files — they import as editable solids. STL is for the slicer.

`assembly_mount_only.step` and `assembly_with_mast_and_device.step` carry STEP
product structure, so they arrive as **named components** (`back_plate`,
`front_shell`, `luff_nut_bar`, plus `mast_express` and `atlas_2` in the in-situ
file), already coloured and positioned. This matters: Fusion applies joints to
*components*, never to loose bodies.

If the model comes in lying on its side, check **Preferences → Default
modeling orientation** — these files are Z-up, with the mast axis on +Z.

### Jointing it up

Everything is already in its assembled position, so use **As-built Joints**
(`Assemble → As-built Joint`). A normal Joint moves parts to mate them and will
pull yours out of position.

| Pair | Joint | How |
|---|---|---|
| `back_plate` → ground | — | Right-click the component → **Ground** |
| `front_shell` ↔ `back_plate` | **Revolute** | As-built Joint, Motion = Revolute, then click the Ø3.2 hinge pin bore as the axis |
| `luff_nut_bar` ↔ `back_plate` | **Rigid** | As-built Joint, Motion = Rigid |
| `atlas_2` ↔ `back_plate` | **Rigid** | As-built Joint, Motion = Rigid |
| `mast_express` ↔ ground | — | **Ground** it |

The hinge axis is at **X = 71.222, Y = +52.50**, parallel to Z — but picking
the cylindrical face of the pin bore snaps it for you.

After creating the revolute joint, right-click → **Edit Joint Limits**, min
**0°**, max **120°**. That range is verified collision-free by the build script.

Other useful axes, all parallel to X:

| Feature | Position |
|---|---|
| Mast bolts (M4) | Y = 0, Z = ±35 |
| Thumbscrews (M3) | Y = −52.5, Z = ±30 |

Single-part STEPs (`back_plate.step`, `front_shell.step`) are one solid and
arrive as a single body — select it and right-click → **Create Components from
Bodies** before jointing.

## Rebuilding

```
pip install cadquery
python3 src/atlas2_mast_mount.py     # writes export/*.step and *.stl
python3 src/render.py                # writes export/render_*.png
```

The build self-checks on every run and will not silently ship a bad part:

- zero interference between plate, shell, luff bar, mast and device
- the saddle and tongue actually seat on the mast rather than floating
- the lid swings clear from 5° to 120°
- each part is a single valid solid, with no loose fragments
- every exported STEP re-imports as one solid with zero volume change

## Caveats

- **Below the gooseneck only** — see the fixing note above.
- `Atlas_2.step` is Vakaros's *simplified* model. Feature positions are solid,
  but small details are approximate. Test-fit before a final print.
- The throat is toleranced `5±0.5`. Check your own extrusion with a caliper.
- The saddle and tongue are cut from the section as-measured with 0.5 mm
  clearance. A different extrusion batch, or anodising build-up, may need
  `CLR_MAST` or `TONGUE_HALF_W` opening up slightly.
- A mount on the aft face adds windage and weight aloft on the sail's leeward
  side. Keep it as low on the spar as sightlines allow.
