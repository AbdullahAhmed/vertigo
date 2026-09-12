const fs = require('node:fs');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const before = fs.readFileSync('vertigo.html');
execFileSync(process.execPath, ['build.js']);
assert.deepEqual(fs.readFileSync('vertigo.html'), before, 'generated build must be current and deterministic');
const layout = JSON.parse(fs.readFileSync('build/layout.json'));
assert.equal(layout.slabs.length, 181, 'preserve the staircase');
assert.equal(layout.H, 72.5, 'preserve the tower height');
assert.equal(layout.segments.length, 7, 'preserve all six collapse segments');
const manifest = JSON.parse(fs.readFileSync('sfx/manifest.json'));
const voices = Object.entries(manifest.files).filter(([,v])=>v.role==='protagonist');
assert.equal(voices.length, 9);
assert.equal(new Set(voices.map(([,v])=>v.voice)).size, 1, 'one source collection');
for (const [name, entry] of Object.entries(manifest.files)) {
  for (const file of entry.kind==='set' ? entry.items : [name]) {
    const bytes = fs.readFileSync(`sfx/${file}.ogg`);
    assert.equal(bytes.subarray(0,4).toString(), 'OggS', `${file} must be OGG`);
  }
}
for (const [name] of voices) {
  assert.equal(manifest.credits[name].license, 'CC0');
  assert.equal(manifest.credits[name].author, 'tcrocker68');
}
const template = fs.readFileSync('src/index.template.html','utf8');
assert(!template.includes('\u00c2') && !template.includes('\u00e2\u20ac'), 'game copy must not contain UTF-8 decoded as Windows-1252');
const audioBlock = template.slice(template.indexOf('const Audio = {'), template.indexOf('// ---------------------------------------------------------------- renderer'));
const methods = [...audioBlock.matchAll(/^  (?:async )?(\w+)\([^\n]*\) \{/gm)].map(m=>m[1]);
assert.equal(new Set(methods).size, methods.length, 'Audio must not silently shadow a method');
assert(!template.includes('Audio.scream('), 'wind and vocal events must remain distinct');
assert(!fs.readFileSync('vertigo.html','utf8').match(/__(?:VOICE_B64|FACE_B64|LAYOUT|GLB_B64)__/));
console.log('PASS: reproducible build, preserved layout, audio assets, CC0 voice provenance and unique Audio methods');
