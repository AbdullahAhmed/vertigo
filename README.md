# VERTIGO — a tower, at night

First-person, low-poly, browser-only. You wake at the foot of a sodium-lit concrete
tower, looking straight up it (the opening shot is the photo). Find the door, climb the
railing-less spiral inside, and reach the roof. Press **Extinguish light** to switch off all three
roof lights and ride the tower collapse. One climb, one ending.

**Play:** serve `vertigo.html` together with the `sfx/` folder (needs internet for three.js from a CDN),
or use the published artifact link. Opened straight from disk it still runs, with synthesised sound. Headphones recommended.

**Controls:** WASD move · mouse look · Space jump · Shift creep · E use · Esc pauses.
If the page can't capture the mouse (embedded frames), hold the mouse button to look,
or open it in its own tab.

## What's in it

- **The tower** — modelled headlessly in Blender 5.2 (`build_tower.py`): hollow shell with
  boolean-cut windows, door and roof hatch, string courses, cornice, parapet, mast with the
  three lights. ~1,300 triangles. Exported as glTF and inlined into the page.
- **The spiral** — 181 slabs, 16 per lap, 0.4 m rise each, 72.5 m to the roof. No railing.
  Landings every lap are checkpoints (with a sodium lamp and, sometimes, a note).
- **Vertigo** — looking down over a drop widens the FOV (dolly-zoom), drains *nerve*, adds
  sway and a vignette, then a heartbeat. At zero nerve your knees go. Look at the wall to recover.
- **One climb** — gaps from lap 2 on desktop, crumbling slabs from lap 5, and the figure behind you.
  Phones keep their more forgiving controls and difficulty. Reach the roof once to trigger the ending.
- **The collapse** — with all three roof lights out the tower sways, the city grid blinks out in rings from
  the tower outward until the last ring dies just before the topple, and the tower gives from the bottom:
  each 12 m segment pancakes and the stack you're standing on drops with it, then what's
  left topples with you on the roof until it's past saving. The tower ships from Blender in
  six stacked segments (`seg0..seg5`) so the game can drive this as a chain.
- **The figure** — from lap 3 a column of dark smoke climbs behind you, at about half your walking
  pace, and it never stops; a deep pulsing rumble swells as it closes. Stand still and your head is
  drawn to look for it; let it reach you and a face comes out of the smoke, straight at you, and you
  stumble backwards into the shaft. Panic (breath, blood in the ears, heart) rises
  with nerve loss, the drop in view, and the thing in view.
- **The lights** — three evenly spaced lamps across the front roof edge, at one height, matching
  the reference photo. The opening uses the photo's flat-face, steep upward, rolled composition;
  it gently levels out and widens before you take control.
- **Roof button** — **Extinguish light** appears once you stand on the roof. Tap it, press E/USE,
  or click with the mouse captured to extinguish all three lights and start the collapse immediately.
  There are no forced roof throws or repeat ascents.
- **Save & continue** — last landing and stats are kept in the browser. Old second/third-ascent
  saves keep their checkpoint height and continue within the single climb, with all roof lights on.
- **Phones:** dual fixed pads with a 14% radial dead zone and continuous slow movement, JUMP / USE buttons,
  no jump puzzles or extra crumble penalty, and 1.5-second crumble timing. Wind and nerve-stumble
  displacement are halved; the visual/audio warnings remain. The figure pursues more gently and pauses
  for 6 seconds after respawn. After 3 / 5 deaths at one landing, pursuit eases another 15% / 30% and
  recovery lasts 8 / 10 seconds. This session-only assistance resets at a different landing or ascent.
  The collapse retains its original timing. Desktop movement and first-climb difficulty are unchanged.
  Assisted edge-jumps remain a safety net; fullscreen is top-right, triple-tap top-left = the F8 skip.
- **Debug:** `F8` (or `Shift+End`) during play skips to the roof, ready to extinguish the lights.
- **Falls** over 5.5 m send you back to the last landing. The HUD shows actual height;
  the ending separately reports total distance climbed, including retries.
- **Sound:** recorded CC0 samples in `sfx/` (wind outside and in the shaft, lamp hum, concrete footsteps,
  heartbeats, stone cracks and debris, building collapse, distant booms, a falling whoosh and a switch).
  All protagonist vocals are female recordings from tcrocker68's May 2014 collection, at original pitch.
  Breathing yields to gasps, pain and screams; the creature uses separate non-vocal noise and spatial rumble.
  Each fall randomly uses either the scream or pain reaction, once; respawn adds no second vocal.
  Running and panic each have three breathing takes with no immediate repeats. Normal running leaves
  4–8 seconds between takes; panic leaves 1.6–3.2 seconds. Ordinary breathing is mixed more quietly.
  See `sfx/CREDITS.md` for sources and the performer-identification limitation. Environmental samples are fetched
  before the title enables play, with per-file failure handling and a timeout. The female voice bank is also
  embedded in the HTML; procedural ambience takes over if external fetches fail.
  Host `vertigo.html` and the `sfx/` folder together.
- **Look:** bloom on the lamps, film grain, chromatic aberration and a radial smear that follow vertigo,
  panic and falling, a sodium/blue-shadow grade, a graded sky dome, normal-mapped concrete, lamp halos,
  dust in the shaft, lit windows on the distant blocks, continuous cloud cover, fine formwork and tie holes,
  independent mast bulbs and an original figure-face texture. Phones skip the bloom. Collapse shadows update
  at a capped rate, with grit preceding large debris; the image remains readable through the fall.

## Rebuild

Private first-party gameplay analytics are available to the owner at `/analytics/`. The game tracks anonymous
visits, plays, movement, falls and progression; the dashboard and exports require a password. Players can
opt out from the title's privacy link. See `analytics/README.md` for definitions, deployment and limitations.

```
blender -b --python build_tower.py     # -> build/tower.glb, build/layout.json, build/preview.png
node build.js                         # inlines geometry, layout, face artwork and the female voice bank
```

`src/index.template.html` is the game; `vertigo.html` is the generated single-file build.

The face source is `assets/figure-face.png` (see `assets/CREDITS.md`). Do not edit `vertigo.html` directly.
For local review, run `python tests/review_server.py . 8765`, then open `/vertigo.html` for the game,
`/tools/voice-audition.html` for isolated vocals, or `/review.html` for the scene checks.
See `tests/README.md` for desktop, mobile-mode and audio-failure checks.
