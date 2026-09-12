import json
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

# Public CC0 previews, source URLs and edits recorded in the shipped manifest.
cuts = {
    'voice_breath': ('breathing', 7.0, 10.2, 235593),
    'voice_breath2': ('breathing', 10.3, 13.4, 235593),
    'voice_breath3': ('breathing', 27.8, 31.1, 235593),
    'voice_panic': ('breathing', 17.0, 20.4, 235593),
    'voice_panic2': ('breathing', 33.5, 36.6, 235593),
    'voice_panic3': ('breathing', 40.0, 43.2, 235593),
    'voice_gasp': ('breathing', 17.0, 17.85, 235593),
    'voice_pain': ('two_screams', 1.4, 2.2, 235595),
    'voice_scream': ('scream', 0.17, 2.4, 235592),
}
manifest_path = Path('sfx/manifest.json')
man = json.loads(manifest_path.read_text())
for key in ['breath', 'breath2', 'scream', 'scream2', 'growl', 'growl2', 'bodyfall', 'bodyfall2']:
    man['files'].pop(key, None)
    man['credits'].pop(key, None)
for name, (source, start, end, sid) in cuts.items():
    x, rate = sf.read(f'build/sfx_src/{source}.mp3', always_2d=True)
    x = x[int(start*rate):int(end*rate)].mean(axis=1)
    x = sosfilt(butter(2, 110, btype='highpass', fs=rate, output='sos'), x)
    x = sosfilt(butter(2, 8500, btype='lowpass', fs=rate, output='sos'), x)
    target = .085 if source == 'breathing' else .16
    x *= min(target / max(np.sqrt(np.mean(x*x)), 1e-6), .8 / max(abs(x).max(), 1e-6))
    fade = min(int(rate*.06), len(x)//3)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    sf.write(f'sfx/{name}.ogg', x, rate, format='OGG', subtype='VORBIS')
    man['files'][name] = {'kind': 'one', 'role': 'protagonist', 'voice': 'tcrocker68-female-2014'}
    man['credits'][name] = {'id': sid, 'author': 'tcrocker68', 'title': {'breathing':'Girl_Heavy_Breathing.wav', 'scream':'Girl_Scream.wav', 'two_screams':'Girl_Two_Screams.wav'}[source], 'url': f'https://freesound.org/people/tcrocker68/sounds/{sid}/', 'license':'CC0', 'edits': f'Public HQ preview; excerpt {start}-{end}s, mono, filters, gain and fades. Original pitch.'}
    print(name, round(len(x)/rate,2), 'seconds')
man['voiceNote'] = 'All protagonist vocal assets are female recordings from tcrocker68, uploaded May 1, 2014. The performer is not named; a single actress is not independently documented.'
manifest_path.write_text(json.dumps(man, indent=2)+'\n', encoding='utf8')
