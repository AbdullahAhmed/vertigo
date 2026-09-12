const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('src/index.template.html','utf8');
const audio = source.slice(source.indexOf('const Audio = {'), source.indexOf('// ---------------------------------------------------------------- renderer'));
let random = .1;
const math = Object.create(Math); math.random = () => random;
const context = vm.createContext({Math:math, IS_TOUCH:false, P:{fallVoice:false,grounded:true,vel:{x:4.2,z:0}}, G:{state:'play'},
  lerp:(a,b,t)=>a+(b-a)*t, clamp:(v,a,b)=>Math.max(a,Math.min(b,v))});
const A = vm.runInContext(audio+'; Audio;',context);
const events=[];
A.ctx={currentTime:0}; A.master={}; A.worldBus={gain:{setTargetAtTime(){}}}; A.heartbeat=()=>{};
A.voices=Object.fromEntries(['voice_breath','voice_breath2','voice_breath3','voice_panic','voice_panic2','voice_panic3','voice_pain','voice_scream'].map(n=>[n,{duration:3.2}]));
A.voice=(name)=>{events.push({name,t:A.ctx.currentTime});A.voiceUntil=A.ctx.currentTime+3.2;return true;};
for(const [r,want] of [[.1,'voice_scream'],[.9,'voice_pain']]) {
  random=r; context.P.fallVoice=false; const n=events.length;
  A.fallReaction(); A.fallReaction();
  assert.equal(events.length,n+1,'one reaction per fall, despite repeated triggers');
  assert.equal(events.at(-1).name,want,'both random choices are reachable');
}
// Exercise the actual respawn method: it must not append another vocal at impact.
const respawn=source.slice(source.indexOf('  respawn(kind) {'),source.indexOf('\n  use() {',source.indexOf('  respawn(kind) {')));
context.Audio=A;context.FIG={grab:null};context.LINES={fall:['fall'],thrown:['thrown']};context.setTimeout=()=>{};
A.thud=()=>{}; const game=vm.runInContext('({'+respawn+'})',context); game.fade=()=>{};game.say=()=>{};game.falls=0;
const count=events.length;game.respawn('fall');assert.equal(events.length,count,'respawn does not add pain after the fall vocal');
// Run 90 seconds of ordinary movement on a simulated audio clock.
events.length=0;A.voiceUntil=0;A.nextBreathAt=4;A.exertion=0;random=.3;
for(let i=0;i<900;i++){A.ctx.currentTime=i/10;A.panic(0,.1);}
assert(events.length>=7 && events.length<=12, 'ordinary running uses substantially fewer breath cues');
assert(new Set(events.map(e=>e.name)).size>1,'running varies the take');
for(let i=1;i<events.length;i++){
  assert.notEqual(events[i].name,events[i-1].name,'no consecutive identical breaths');
  assert(events[i].t-events[i-1].t>=7.2,'at least four seconds of rest after each breath');
}
// Panic remains responsive, but also varies takes and leaves a pause.
events.length=0;A.voiceUntil=0;A.nextBreathAt=200;A.wasPanicking=false;
for(let i=0;i<300;i++){A.ctx.currentTime=90+i/10;A.panic(1,.1);}
assert(events.length>=4 && events.length<=7);
assert(events.every(e=>e.name.startsWith('voice_panic')));
for(let i=1;i<events.length;i++) assert.notEqual(events[i].name,events[i-1].name);
console.log('PASS: random single fall vocals, no respawn vocal, sparse varied running breaths and responsive varied panic');
