# Vakaros Atlas 2 — Express mast mount

A slide-in cradle for the **aft face** of an Express section mast, screen facing
the cockpit. The Atlas 2 drops in from the top and lands on a solid ledge; a
quarter-turn cam on top retains it. Screen fully visible, every control and the
charge port reachable with the device locked in.

Generated parametrically — `src/atlas2_mast_mount.py` re-reads
`reference/Mast.step` and `reference/Atlas_2.step` on every run and derives all
mating geometry and cutout positions from them. Nothing is hand-transcribed.

![assembly](export/render_assembly_closed_iso.png)

## Load path

Nothing that moves carries the device:

| Direction | Taken by |
|---|---|
| Weight, −Z | **Fixed bottom ledge**, 1156 mm² of bearing area |
| Fore/aft, X | **Fixed side-rail lips** |
| Athwartships, Y | **Fixed side rails** |
| Lift-out, +Z | The rotating lock — a retainer only, never loaded in normal use |

The cradle is a single printed part. The lock is the only moving piece, and it
sees no load unless something tries to throw the device upward.

## Parts

| Part | File | Notes |
|---|---|---|
| Cradle | `export/cradle.step` / `.stl` | One piece: mast tongue, saddle, rails, ledge. 132 cm³ |
| Lock | `export/lock.step` / `.stl` | Quarter-turn cam, 1.2 cm³ |
| Luff nut bar | `export/luff_nut_bar.step` / `.stl` | Preferred — one bar spanning both bolts |
| Luff nut slug | `export/luff_nut_slug.step` / `.stl` | Short single-bolt alternative |
| Assemblies | `export/assembly_*.step` | Named components, see Fusion section |

Cradle 107.0 × 119.7 × 34.8 mm. The screen sits **21.75 mm** aft of the mast's
aft face.

## The rotating lock, and why it sits where it does

Sliding in from the top creates a hard constraint. The device sweeps a
**removal corridor** — X 71.22…85.57, |Y| ≤ 44.44, everything above Z 57.64 —
plus two narrow channels behind the plate face where its rear protrusions
travel. Anything left in that volume stops the device going in at all,
*whatever it does when locked*. That rules out most of the obvious answers:

- A lever on a mast-normal axis above the device keeps its pivot in the
  corridor at every angle. Dead end.
- Behind the plate face, the gap between the mast (X 63.82) and the rear
  protrusion channels (X 70.06) is **5.7 mm**. A Ø5.2 pivot bore needs about
  11 mm of boss. It does not fit — and a first attempt at a 5 mm blade there
  was severed outright by its own pivot bore.
- A lobe swinging at Y = 0 crosses the mast's aft shoulders, which reach
  X 63.82 at Y ±15.

What does work is **outboard of the device**. On a pad on top of the +Y side
rail there is no mast and no corridor, so a proper M5 boss fits. Locked, the
lobe reaches inboard over the device's top corner. A quarter turn swings it
fore-and-aft, clear, and the device lifts straight out.

The cam pivots on an M5 thumbscrew into a brass insert — nip it up and the cam
is friction-locked. A Ø4.2 hasp hole through the lobe lines up with a hole in
the pad **only in the locked position**, for a pin, seizing wire or a small
padlock.

### One honest limitation

The Atlas's top edge is a rounded crown — at the very top there is only about
1.8 mm of flat across its 14.6 mm depth, and just 2 mm² of section. No retainer
pressing from above can get a large contact patch on this device. The cam is set
as low as it will run, which leaves **0.40 mm of free lift** before it bites.
That is enough to stop the device leaving, but it is a crown contact, not a
flush clamp. If you want zero movement, a 1 mm self-adhesive pad on the ledge
takes up the remainder.

## Mast fixing

The mainsail luff groove measures (see `docs/MEASUREMENTS.md`): outer recess
**20.00 mm** wide and parallel over X 53.4→60.0, throat **5.00 mm**, and a
bolt-rope channel that is a true circle, centre X 50.04, r 10.05.

- The cradle carries a **full-height 19.4 mm tongue** into the parallel recess,
  0.3 mm a side, 6.0 mm of engagement. It takes all the shear and rotation.
- Two **M4** bolts pass through the throat into a half-round bar in the channel.
  They only clamp.
- Saddle wings bear on the aft skin either side of the groove.

> **Below the gooseneck only.** Above it the mainsail bolt rope occupies the
> channel. Site the mount below the sail feeder, and check that lowering the
> main fully does not run the bolt rope down onto the bar.

**M5 will not fit.** Both slots on this section have a throat measuring exactly
5.000 mm, toleranced `5±0.5` on the drawing. An M5 screw has a 5.0 mm major
diameter and cannot pass. M4 gives 1.0 mm clearance nominal.

## Access

Facing the screen, the Atlas's controls are all on the **left**. The lock is on
the right, well clear of them. Verified in the build script, not by eye:

| Feature | Provision |
|---|---|
| Screen | Front fully open |
| 4 front buttons | Side lip stops 1.95 mm clear of them |
| Power button (top edge) | Nothing above it — lock is on the opposite side |
| Charge port (bottom edge) | Notch through the ledge, open forward for a plug |
| Drainage | 2 × Ø4 mm holes in the ledge |

## Bill of materials

| Qty | Item |
|---|---|
| 2 | **M4 × 25** A4 stainless socket cap screw (M4 × 30 bottoms out — the bar is 9 mm deep) |
| 2 | M4 A4 washer (Ø9) |
| 1 | Luff nut bar — 90 mm, 3 mm aluminium, tapped M4 at 70 mm centres |
| — | *or* 2 × 25 mm luff nut slug, tapped M4 |
| 1 | M5 × 16 A4 thumbscrew — lock pivot |
| 1 | M5 brass heat-set insert, Ø6.4 × 9.5 mm |
| 1 | Ø4 pin, seizing wire or small padlock for the hasp hole (optional) |
| 1 | 1 mm self-adhesive neoprene/EVA pad, ~85 × 110 mm (optional, kills the 0.4 mm lift) |

The luff nut is a circular segment sized r 9.70 against the channel's r 10.05,
flat face at X 49.30. Make it from metal — printed threads will not hold here.
It feeds in from the open end of the groove; it cannot be toggled through a
5 mm throat.

## Printing

PETG, ASA or nylon. PLA will creep and go brittle in UV — not on a mast.

| | Cradle | Lock |
|---|---|---|
| Orientation | Standing on its bottom edge (mast axis vertical) | Flat |
| Support | None — tongue, rails and saddle are vertical extrusions | None |
| Bed | Brim recommended | — |
| Perimeters | 5 | 4 |
| Infill | 40 % gyroid | 60 % |
| Layer | 0.2 mm | 0.15 mm |

Standing the cradle on its bottom edge runs the tongue, rails and saddle as
straight vertical extrusions and puts the layer lines across the ledge's
bending direction.

## Assembly

1. Print both parts. Melt the M5 insert into the lock pad from above.
2. Feed the luff nut bar into the mainsail groove from its open end and slide it
   to the height you want, **below the gooseneck**.
3. Offer the cradle up so its tongue enters the recess, and run in the two
   M4 × 25 screws with washers. The heads sit in counterbores, flush with the
   plate face. The tongue should feel snug before you tighten.
4. Optional: stick the neoprene pad to the ledge.
5. Fit the lock with its M5 thumbscrew. It should turn firmly, not freely.
6. To load: turn the lock fore-and-aft, slide the Atlas down between the rails —
   screen aft, controls to the left, rear protrusions into the relief channels —
   until it lands on the ledge. Turn the lock inboard over the top corner and
   nip up the thumbscrew. Add a pin or seizing wire through the hasp if you want
   it positively locked.

## Opening in Fusion 360

Use the **STEP** files. `assembly_mount_only.step` and
`assembly_with_mast_and_device.step` carry STEP product structure, so they
arrive as **named components** (`cradle`, `lock`, `luff_nut_bar`, plus
`mast_express` and `atlas_2`), coloured and positioned. Fusion applies joints to
components, never to loose bodies.

If the model comes in lying on its side, check **Preferences → Default modeling
orientation** — these files are Z-up, mast axis on +Z.

Everything is already assembled, so use **As-built Joints**
(`Assemble → As-built Joint`); a normal Joint moves parts to mate them.

| Pair | Joint | How |
|---|---|---|
| `cradle` → ground | — | Right-click → **Ground** |
| `lock` ↔ `cradle` | **Revolute** | As-built Joint, Motion = Revolute, click the Ø5.3 pivot bore |
| `luff_nut_bar` ↔ `cradle` | **Rigid** | As-built Joint, Motion = Rigid |
| `atlas_2` ↔ `cradle` | **Slider** | As-built Joint, Motion = Slider, Z axis — that is how it loads |
| `mast_express` → ground | — | **Ground** it |

Lock pivot axis: **X = 79.0, Y = 51.5**, parallel to Z. Joint limits 0° to 90°.

## Rebuilding

```
pip install cadquery
python3 src/atlas2_mast_mount.py     # writes export/*.step and *.stl
python3 src/render.py                # writes export/render_*.png
```

The build self-checks on every run and prints `ALL CHECKS PASSED` or the list of
failures. It asserts:

- zero interference between cradle, lock, luff bar, mast and device
- the tongue and saddle actually seat on the mast rather than floating
- the cradle is clear of the device's true swept removal corridor
- the device slides in from the top over 0–120 mm without touching
- the lock swings fully clear when open, and which way it has to turn
- free lift under the closed lock, and that it resists a 1 mm lift
- bearing area of the load-bearing ledge
- clear access above the power button, in front of the four front buttons, and
  below the charge port
- each part is a single valid solid with no loose fragments, and every exported
  STEP re-imports as one solid with zero volume change

## Caveats

- **Below the gooseneck only** — see the mast fixing note.
- `Atlas_2.step` is Vakaros's *simplified* model. Feature positions are solid,
  small details are approximate. Test-fit before a final print.
- The throat is toleranced `5±0.5`. Check your own extrusion with a caliper.
- Tongue and saddle are cut from the section as-measured with 0.5 mm clearance.
  A different extrusion batch, or anodising build-up, may need `CLR_MAST` or
  `TONGUE_HALF_W` opening up.
- The device is retained on a rounded crown, not a flat face — see the lock
  section above.
- A mount on the aft face adds windage and weight aloft on the sail's leeward
  side. Keep it as low on the spar as sightlines allow.
