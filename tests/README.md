# Local review

Run `node build.js`, `node tests/check-build.js`, then `python tests/review_server.py . 8765`.
Run `node tests/audio-variation.js` to verify one random vocal per fall, no additional respawn vocal,
breathing variation, and the quieter running cadence on a simulated audio clock.
Run `node tests/mobile-assist.js` for thumb dead zones, smooth speed, checkpoint-local assistance,
respawn grace and desktop isolation. Browser Run checks also exercises actual movement, platform
wind/stumble displacement, crumble timing and mobile pursuit grace.

- `http://127.0.0.1:8765/vertigo.html`: normal deployable game.
- `/tools/voice-audition.html`: isolated female voice clips, with sources.
- `/review.html`: scene buttons and **Run checks** for decoded assets, audio interruption, wind/scream separation, bulbs, true altitude, smoke dispersal and the complete collapse.
- `/mobile.html`: the same tests with coarse-pointer/mobile detection enabled. This verifies the no-gap branch, not physical touch hardware or device performance.
- `/fallback.html`: all external audio fetches fail deliberately. The embedded female voice and procedural environment must still work.

The review pages are server-injected test harnesses. They mute audio and freeze/advance the simulation; the normal `vertigo.html` is untouched. They replace storage with an isolated in-memory map so save/continue is exercised without touching the player's save. The tests require a browser with WebGL and network access for the existing three.js CDN dependencies.

Audition and normal gameplay are the remaining subjective checks: voice timbre, perceived loudness, scares and comfort. Browser checks do not certify physical-phone performance or a human full playthrough.

## Verified in this pass

On 2026-09-11, the 17 scene/asset/audio checks passed in desktop, mobile-mode and external-audio-failure pages in the Codex Chromium browser. Save restore, both roof throws, the four pancake events and player release at the end were exercised. No runtime errors were reported; the fallback page logged its expected simulated fetch failure. Build reproducibility, original layout dimensions, asset signatures and unique Audio method names passed `node tests/check-build.js`.

The opening, stairs, face reveal and mid-collapse roof were inspected visually. Physical phones, subjective listening and a human uninterrupted three-ascent playthrough remain unverified. No production deployment was performed.

The mobile assistance pass passed all 23 mobile-mode and 22 desktop browser checks, plus build,
audio and mobile-assistance Node checks. This covers the new tuning and the existing save, roof
encounters and collapse. A physical-phone completion playthrough remains unverified.

The single-climb release replaces the two roof-throw checks with roof-button, single-activation,
legacy-save migration and lamp-row checks: 27 desktop / 28 mobile-mode checks passed. The actual
mobile roof button was clicked and the collapse advanced successfully. The opening composition was
compared with the portrait reference, and the button was inspected at a 390 × 844 phone viewport.
