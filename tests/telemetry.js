const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/telemetry.js','utf8');
let now=0,requests=[];
const memory=new Map();
const ctx=vm.createContext({console,Math,Array,JSON,Blob,crypto:require('node:crypto').webcrypto,
 localStorage:{getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)},location:{hostname:'vertigo.alphasquaredgames.com',protocol:'https:'},
 window:{},performance:{now:()=>now},setInterval(){},addEventListener(){},document:{hidden:false,addEventListener(){}},navigator:{sendBeacon(){return true;}},
 fetch:async(url,opts)=>{requests.push(JSON.parse(opts.body));return {ok:true};},
 P:{pos:{x:0,y:0,z:0},grounded:true,groundRef:{slab:0},onRoof:false,nerve:1},G:{state:'play'},COL:{active:false},locked:true,STEP:.55});
const s=vm.runInContext(source+';STATS;',ctx);s.init(true);s.begin(false);
assert.equal(s.metrics.plays,1);assert.equal(s.metrics.new_games,1);
const visitor=s.visitor;assert.equal(memory.get('vertigo.visitor.v1'),visitor);
now=100;s.frame();ctx.P.pos={x:.4,y:.4,z:0};s.step(0,0,0,.1);
assert.equal(s.metrics.climbed_m,.4);assert.equal(s.metrics.walked_m,.4);assert.equal(s.metrics.climb_attempts,1);
// Teleports and airborne rises are not counted as walked/climbed distance.
ctx.P.pos={x:40,y:40,z:0};s.step(.4,.4,0,.1);assert.equal(s.metrics.climbed_m,.4);assert.equal(s.metrics.walked_m,.4);
ctx.P.grounded=false;ctx.P.pos.y=40.4;s.step(40,40,0,.1);assert.equal(s.metrics.climbed_m,.4);
s.fall(2);assert.equal(s.fallsByLap[2],1);ctx.P.grounded=true;s.step(40,40.4,0,.1);assert.equal(s.metrics.climb_attempts,2);
ctx.P.onRoof=true;s.step(40,40.4,0,.1);s.step(40,40.4,0,.1);assert.equal(s.metrics.roof_arrivals,1);
const active=s.metrics.active_seconds;ctx.document.hidden=true;now=200;s.frame();assert.equal(s.metrics.active_seconds,active);
s.markTest();assert.equal(requests.at(-1).test,true);assert(requests.every(r=>!('userAgent' in r)&&!('referrer' in r)));
const count=requests.length;const local=vm.createContext({...ctx,location:{hostname:'127.0.0.1',protocol:'http:'}});const localStats=vm.runInContext(source+';STATS;',local);localStats.init(false);assert.equal(requests.length,count);
memory.set('vertigo.analytics.optout','1');const off=vm.runInContext(source+';STATS;',vm.createContext({...ctx}));off.init(false);assert.equal(off.enabled,false);
console.log('PASS: counters, retries, movement bounds, roof deduplication, hidden time, debug isolation, local exclusion and opt-out');
