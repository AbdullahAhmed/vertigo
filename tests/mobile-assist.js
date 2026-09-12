const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('src/index.template.html', 'utf8');
const mobileSource = source.slice(source.indexOf('const MOBILE = {'), source.indexOf('\nif (IS_TOUCH)', source.indexOf('const MOBILE = {')));
const context = vm.createContext({Math});
const mobile = vm.runInContext(mobileSource + '; MOBILE;', context);
assert.equal(Math.hypot(...Object.values(mobile.pad(.1,.05))),0,'resting thumb has no drift');
assert.equal(Math.hypot(...Object.values(mobile.pad(1,1))),1,'diagonal input is capped');
let previous = 0;
for(let i=15;i<=100;i++) {
  const speed=4.2*Math.pow(mobile.pad(i/100,0).x,1.25);
  assert(speed>previous,'speed rises continuously');previous=speed;
}
assert.equal(previous,4.2,'full thumb keeps walking speed');
const cp={x:1,y:32,z:2,yaw:0};mobile.reached(1,cp);
const normal=mobile.pursuit(2,.85);
for(let i=0;i<3;i++)mobile.failed(1,cp);
assert.equal(mobile.assistance(),1);
mobile.reached(1,{...cp,yaw:2});assert.equal(mobile.assistance(),1,'turning at checkpoint retains aid');
assert.equal(mobile.pursuit(2,.85),normal*.85);
mobile.recover(100);assert.equal(mobile.graceUntil,108);
for(let i=0;i<2;i++)mobile.failed(1,cp);
assert.equal(mobile.assistance(),2);mobile.recover(100);assert.equal(mobile.graceUntil,110);
mobile.reached(1,{...cp,y:38.4});assert.equal(mobile.failures,0,'next landing clears local aid');
mobile.recover(100);assert.equal(mobile.graceUntil,106);
// Exercise actual respawn callbacks, including desktop isolation and mobile base speed preservation.
const respawn=source.slice(source.indexOf('  respawn(kind) {'),source.indexOf('\n  use() {',source.indexOf('  respawn(kind) {')));
for(const touch of [false,true]) {
  mobile.reset();let spawnArgs;
  Object.assign(context,{IS_TOUCH:touch,Audio:{thud(){}},P:{checkpoint:cp,place(){}},FIG:{active:true,speed:2.8,baseSpeed:1,spawn(...args){spawnArgs=args;}},LINES:{fall:['fall'],thrown:['thrown']},setTimeout:fn=>fn(),rebuildSolids(){}});
  const game=vm.runInContext('({'+respawn+'})',context);Object.assign(game,{ascent:1,falls:0,t:50,fade(){},say(){}});
  for(let i=0;i<3;i++)game.respawn('fall');
  assert.equal(mobile.failures,touch?3:0);
  assert.equal(mobile.graceUntil,touch?58:0);
  assert.equal(spawnArgs[1],touch?1:2.8,'desktop respawn speed remains untouched');
}
console.log('PASS: thumb precision, capped speed, local failure assistance, recovery timing and desktop isolation');
