# VERTIGO — a tower, at night

First-person, low-poly, browser-only. You wake at the foot of a sodium-lit concrete
tower, looking straight up it (the opening shot is the photo). Find the door, climb the
railing-less spiral inside, reach the three lights on the roof. Then do it again.

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
- **Three ascents** — 1: gaps from lap 2, crumbling slabs from lap 5. 2: wind gusts that
  push you toward the void, more gaps. 3: half the lamps are dead, crumble-then-gap combos,
  and at the top you put the lights out one by one.
- **The collapse** — with the last light out the tower sways, the city grid blinks out in rings from
  the tower outward until the last ring dies just before the topple, and the tower gives from the bottom:
  each 12 m segment pancakes and the stack you're standing on drops with it, then what's
  left topples with you on the roof until it's past saving. The tower ships from Blender in
  six stacked segments (`seg0..seg5`) so the game can drive this as a chain.
- **The figure** — from lap 3 a column of dark smoke climbs behind you, at about half your walking
  pace, and it never stops; a deep pulsing rumble swells as it closes. Stand still and your head is
  drawn to look for it; let it reach you and a face comes out of the smoke, straight at you, and you
  stumble backwards into the shaft. Ascent 3: faster. Panic (breath, blood in the ears, heart) rises
  with nerve loss, the drop in view, and the thing in view.
- **The lights** — one per ascent. Put one out and your controls drop: you turn to the hatch, the
  smoke comes across the roof at you, the face, and you go backwards over the parapet. The next
  ascent wakes higher. The third light starts the collapse.
- **Each ascent wakes higher** (base / lap 4 / lap 7) with its own opening shot (up the outside /
  down the shaft / up the shaft). Ascent 2: haze and guttering lamps. Ascent 3: lamps die behind you.
- **Save & continue** — progress (ascent, last landing, stats) is kept in the browser; the title
  offers *continue* or *start over*. Three lights in the HUD show the ascents done.
- **Phones:** dual fixed pads, JUMP / USE buttons, no jump puzzles (extra crumbling slabs instead),
  assisted edge-jumps as a safety net, fullscreen button top-right, triple-tap top-left = the F8 skip.
- **Debug:** `F8` (or `Shift+End`) during play skips to the roof of ascent 3 beside the lights.
- **Falls** over 5.5 m send you back to the last landing. The HUD shows actual height;
  the ending separately reports total distance climbed across ascents.
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

```
blender -b --python build_tower.py     # -> build/tower.glb, build/layout.json, build/preview.png
node build.js                         # inlines geometry, layout, face artwork and the female voice bank
```

`src/index.template.html` is the game; `vertigo.html` is the generated single-file build.

The face source is `assets/figure-face.png` (see `assets/CREDITS.md`). Do not edit `vertigo.html` directly.
For local review, run `python tests/review_server.py . 8765`, then open `/vertigo.html` for the game,
`/tools/voice-audition.html` for isolated vocals, or `/review.html` for the scene checks.
See `tests/README.md` for desktop, mobile-mode and audio-failure checks.
