# Sound credits

All shipped samples are free CC0 recordings from Freesound. No paid assets or attribution-restricted recordings are used.

## Protagonist

All protagonist vocals use the female recordings uploaded by **tcrocker68 on May 1, 2014**, at their original pitch. The uploader does not identify the performer; common source and date are verified, but one actress is not independently documented.

The voice bank is embedded in the HTML as well as supplied in `sfx/`, so the same female voice remains available when external audio fetches fail. Playback uses one voice at a time. Breathing yields to reactions. No human vocal recordings are used for the creature.

- `voice_breath` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 7.0-10.2s, mono, filters, gain and fades. Original pitch.
- `voice_panic` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 17.0-20.4s, mono, filters, gain and fades. Original pitch.
- `voice_gasp` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 17.0-17.85s, mono, filters, gain and fades. Original pitch.
- `voice_pain` — [Girl_Two_Screams.wav](https://freesound.org/people/tcrocker68/sounds/235595/) by tcrocker68 (CC0). Public HQ preview; excerpt 1.4-2.2s, mono, filters, gain and fades. Original pitch.
- `voice_scream` — [Girl_Scream.wav](https://freesound.org/people/tcrocker68/sounds/235592/) by tcrocker68 (CC0). Public HQ preview; excerpt 0.17-2.4s, mono, filters, gain and fades. Original pitch.

- `voice_breath2` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 10.3-13.4s, mono, filters, gain and fades. Original pitch.
- `voice_breath3` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 27.8-31.1s, mono, filters, gain and fades. Original pitch.
- `voice_panic2` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 33.5-36.6s, mono, filters, gain and fades. Original pitch.
- `voice_panic3` — [Girl_Heavy_Breathing.wav](https://freesound.org/people/tcrocker68/sounds/235593/) by tcrocker68 (CC0). Public HQ preview; excerpt 40.0-43.2s, mono, filters, gain and fades. Original pitch.

## Environment and foley

- `wind_in` — [AMBUndr_Subterranean Howling Wind Loop_KOLBYR_FREE SOUNDS](https://freesound.org/s/852822/) (CC0).
- `rumble` — [Low Rumble - loopable ambiance](https://freesound.org/s/638914/) (CC0).
- `drone` — [creepy modular drone](https://freesound.org/s/527671/) (CC0).
- `hum` — [lamp harmonic hum](https://freesound.org/s/210994/) (CC0).
- `heart2` — [Heartbeat FX1 (loop)](https://freesound.org/s/361143/) (CC0).
- `steps` — [Footsteps - Stone, Rock, Concrete, Cement](https://freesound.org/s/813622/) (CC0).
- `steps2` — [ConcreteFootsteps.wav](https://freesound.org/s/554380/) (CC0).
- `crack` — [RockCrack03](https://freesound.org/s/489905/) (CC0).
- `debris` — [Big falling debris (crash)](https://freesound.org/s/703247/) (CC0).
- `collapse` — [building collapse / demolition](https://freesound.org/s/712918/) (CC0).
- `collapse2` — [Bakers house collapse](https://freesound.org/s/721600/) (CC0).
- `boom` — [Huge Distant Explosion](https://freesound.org/s/476225/) (CC0).
- `wind_out` — [Cold Howling Wind/Breeze (Loopable)](https://freesound.org/s/638434/) (CC0).
- `heart` — [heartbeat.mp3](https://freesound.org/s/551437/) (CC0).
- `whoosh` — [FallingWhoosh3](https://freesound.org/s/842984/) (CC0).
- `debris2` — [Fall debris (crash)](https://freesound.org/s/703248/) (CC0).
- `switch` — [Switch Light 05.wav](https://freesound.org/s/348225/) (CC0).
- `rocks` — [Rocks falling over rocks, over a steep hill, like a cliff.flac](https://freesound.org/s/190505/) (CC0).

Environmental recordings retain the existing trims, normalization and OGG conversion. Procedural sound supplies non-vocal body impacts, creature hiss, and fallback ambience. The legacy breathing, horror screams, growls and bodyfall recordings have been removed.

## Reproduce voice assets

Optional tooling requires Python with `numpy`, `scipy` and `soundfile`. Run `python tools/fetch_voice.py` then `python tools/prepare_voice.py` from the repository root. Public HQ previews and source-page license evidence are stored in ignored `build/sfx_src/`. The preparation script records every cut, filter and gain treatment in the manifest. Run `node build.js` afterward.
