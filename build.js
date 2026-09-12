// inline the Blender output into a single self-contained HTML file
const fs = require('fs');
const tpl = fs.readFileSync('src/index.template.html', 'utf8');
const telemetry = fs.readFileSync('src/telemetry.js', 'utf8');
const glb = fs.readFileSync('build/tower.glb').toString('base64');
const layout = fs.readFileSync('build/layout.json', 'utf8');
const manifest = JSON.parse(fs.readFileSync('sfx/manifest.json', 'utf8'));
const voices = Object.fromEntries(Object.entries(manifest.files)
  .filter(([, entry]) => entry.role === 'protagonist')
  .map(([name]) => [name, fs.readFileSync(`sfx/${name}.ogg`).toString('base64')]));
const face = fs.readFileSync('assets/figure-face.png').toString('base64');
const out = tpl.replace('__TELEMETRY__', () => telemetry).replace('__LAYOUT__', () => layout).replace('__GLB_B64__', () => glb)
  .replace('__VOICE_B64__', () => JSON.stringify(voices)).replace('__FACE_B64__', () => face);
// refuse to write a build whose game script does not parse
const scripts = [...out.matchAll(/<script>([\s\S]*?)<\/script>/g)];
try { new Function(scripts[scripts.length - 1][1]); } catch (e) { console.error('SYNTAX ERROR in game script:', e.message); process.exit(1); }
fs.writeFileSync('vertigo.html', out);
console.log('vertigo.html', (out.length / 1024).toFixed(0) + ' KB');
