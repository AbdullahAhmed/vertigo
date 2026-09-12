import urllib.request,re,json
from pathlib import Path
Path('build/sfx_src').mkdir(parents=True, exist_ok=True)
sources={235593:'breathing',235592:'scream',235595:'two_screams'}
for sid,name in sources.items():
 url=f'https://freesound.org/people/tcrocker68/sounds/{sid}/'
 page=urllib.request.urlopen(url).read().decode()
 assert 'publicdomain/zero' in page
 preview=re.search(r'https://cdn\.freesound\.org/[^"\s<>]+-hq\.mp3',page).group()
 urllib.request.urlretrieve(preview, f'build/sfx_src/{name}.mp3')
 Path(f'build/sfx_src/{name}.html').write_text(page,encoding='utf8')
 print(name,preview)
