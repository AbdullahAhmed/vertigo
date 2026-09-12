from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
port = int(sys.argv[2]) if len(sys.argv)>2 else 8765
gate = '''<script>
// Test pages get isolated in-memory storage, so save/continue can be tested safely.
const reviewStorage = new Map();
Object.defineProperty(window,'localStorage',{value:{getItem:k=>reviewStorage.get(k)??null,setItem:(k,v)=>reviewStorage.set(k,String(v)),removeItem:k=>reviewStorage.delete(k)}});
window.reviewPaused = false;
window.reviewNext = null;
const reviewNativeRAF = window.requestAnimationFrame.bind(window);
window.requestAnimationFrame = callback => { if(window.reviewPaused){if(callback.name!=="tick")return reviewNativeRAF(callback);window.reviewNext=callback;return 0;} return reviewNativeRAF(t => {
  if (window.reviewPaused) window.reviewNext = callback;
  else callback(t);
});};
</script>'''
panel = '''<style>
#reviewTools{position:fixed;top:5px;left:5px;z-index:100;color:#fff;background:#111d;font:11px monospace;padding:6px;max-width:800px}
#reviewTools button{font:11px monospace;padding:5px;margin:2px}#reviewStats{white-space:pre-wrap;margin:4px 0}
</style><div id="reviewTools">
<button data-review="opening">Opening</button><button data-review="door">Door</button>
<button data-review="stairs">Stairs A1</button><button data-review="ascent2">Stairs A2</button><button data-review="ascent3">Stairs A3</button>
<button data-review="figure">Figure</button><button data-review="face">Face</button>
<button data-review="roof">Roof A1</button><button data-review="rush">Roof rush</button>
<button data-review="collapse">Collapse</button>
<button data-review="one">+1s</button><button data-review="ten">+10s</button><button data-review="run">Run</button><button data-review="pause">Freeze</button>
<button data-review="checks">Run checks</button><pre id="checks"></pre><pre id="reviewStats">Loading review</pre></div>
<script>
SAVE.data = null;
function reviewStats(){document.getElementById('reviewStats').textContent=JSON.stringify({ascent:G.ascent,state:G.state,phase:COL.active?COL.phase:'none',collapseTime:+COL.t.toFixed(2),figureDisperse:FIG.disperse,figureSmoke:FIG.parts.filter(p=>p.sp.visible).length,position:P.pos.toArray().map(n=>+n.toFixed(2)),fov:+P.fov.toFixed(1),nerve:+P.nerve.toFixed(2),samples:Audio.samples?Object.keys(Audio.samples).length:0,voices:Object.keys(Audio.voices),face:faceTexture?.image?.width,bulbs:mastBulbs.map(b=>b.material.color.getHexString()),lights:lampPool.map(l=>l.intensity),paused:window.reviewPaused},null,0)}
function reviewFreeze(){window.reviewPaused=true; reviewStats()}
function reviewAdvance(seconds){window.reviewPaused=true; window.__dt=1/60; const render=composer.render;composer.render=()=>{};for(let i=0;i<Math.round(seconds*60);i++){tick()}composer.render=render;delete window.__dt;composer.render(); reviewStats()}
function reviewReset(n){
  COL.active=false;COL.phase='sway';COL.t=0;COL.ended=false;COL.attached=true;COL.broken=0;COL.said={};COL.impactT=-1;COL.gridStreet=false;COL.tilt=0;COL.tiltV=0;COL.topBreak=0;COL.lean=0;
  segGroups.forEach((g,k)=>{g.quaternion.identity();g.position.y=k?SEGZ[k]-SEGZ[k-1]:0;for(const c of g.children)if(c.isMesh)c.scale.y=1});updateSegXforms();
  for(const st of slabState)st.loose=null;
  G.cine=null;G.intro=null;G.msgT=0;G.lastNote=-1;G.falls=0;G.totalClimb=0;G.setupAscent(n);G.intro=null;G.lookEnabled=true;G.state='play';G.roofSaid=true;G.doorSaid=true;
  if(FIG.after){scene.remove(FIG.after.sp);FIG.after=null}FIG.reset();for(const p of FIG.parts){p.life=0;p.sp.visible=false}
  for(const s of COL.dusts)scene.remove(s);COL.dusts=[];COL.pieces=[];COL.pieceCursor=0;for(let i=0;i<420;i++)COL.debris.setMatrixAt(i,new THREE.Matrix4().makeScale(0,0,0));COL.debris.instanceMatrix.needsUpdate=true;
  const ca=cityPts.geometry.attributes.color;ca.array.set(cityBase);ca.needsUpdate=true;sky.material.uniforms.glow.value=1;
  $('title').style.display='none';$('end').style.display='none';$('fade').style.opacity=0;$('pause').style.display='none';$('msg').style.opacity=0;$('hint').style.opacity=0;for(const id of ['alt','nerve','nervelbl','reticle','lights'])$(id).classList.remove('hidden');
  locked=true;noLock=true;edgeX=edgeY=0;shakeKick=fovKick=vigPulse=panicLevel=scareKick=vertigo=vertigoS=0;P.fov=72;P.nerve=1;FIG.lastLookT=G.t;G.startTime=performance.now();
}
function reviewPlaceSlab(i,pitch=-0.35){const s=SL[i];P.place(s.x+s.inward[0]*0.2,s.top,-s.y-s.inward[1]*0.2,Math.atan2(s.x,-s.y),pitch);P.grounded=true;P.groundRef={slab:i};P.inside=true;P.onRoof=false;P.checkpoint={x:P.pos.x,y:P.pos.y,z:P.pos.z,yaw:P.yaw}}
function reviewScene(name){
  if(G.state==='loading')return; if(name==='checks'){runChecks();return;}
  if(name==='one'||name==='ten'){reviewAdvance(name==='one'?1:10);return}
  if(name==='pause'){reviewFreeze();return}
  if(name==='run'){window.reviewPaused=false;if(window.reviewNext){let fn=window.reviewNext;window.reviewNext=null;reviewNativeRAF(fn)}reviewStats();return}
  window.reviewPaused=true;$('checks').textContent='';
  if(!Audio.master){Audio.init();Audio.ctx.resume()}Audio.master.gain.value=0;
  reviewReset(name==='ascent2'||name==='rush2'?2:name==='ascent3'||name==='collapse'?3:1);
  if(name==='opening'){P.place(SHOT.x,0,SHOT.z,SHOT.yaw,SHOT.pitch);P.roll=SHOT.roll}
  if(name==='door'){P.place(0,0,B+5,0,0.1)}
  if(['stairs','ascent2','ascent3'].includes(name)){reviewPlaceSlab(name==='ascent3'?128:80,-0.7)}
  if(name==='figure'){reviewPlaceSlab(80,-0.85);FIG.spawn(11,0.85)}
  if(name==='face'){reviewPlaceSlab(80,0);FIG.spawn(1,0.85);FIG.grab={t:0,pos:FIG.posAt(79,new THREE.Vector3())};P.thrown='held'}
  if(['roof','rush','rush2','collapse'].includes(name)){const[mx,my]=LAYOUT.mast;P.place(mx-1.8,TOWER_H,-my-0.5,Math.PI*0.75,-0.1);P.grounded=true;P.onRoof=true;P.inside=false;}
  if(name==='rush'||name==='rush2'||name==='collapse')G.use();
  reviewAdvance(name==='face'?0.22:name==='figure'?0.6:0.1);
}
function runChecks(){
 const results=[],check=(label,test)=>{if(!test)throw new Error(label);results.push('PASS '+label)};
 try {
  check('nine embedded female vocals decoded',Object.keys(Audio.voices).length===9);
  check('no old human/monster vocal samples loaded',['scream','scream2','breath','breath2','growl','growl2','bodyfall','bodyfall2'].every(k=>!Audio.samples?.[k]));
  check('original face decoded',faceTexture.image.width===1024);
  reviewScene('ascent3');check('altitude is actual tower height',+$('alt').firstElementChild.textContent<73);
  check('one physical bulb remains',mastBulbs.filter(b=>b.material.color.getHex()===0xfff6dc).length===1);
  check('mobile has no gaps',!IS_TOUCH||[1,2,3].every(n=>buildPattern(n).gap.every(v=>!v)));
  reviewScene('stairs');P.place(B+10,0,B+10,0,0);P.grounded=true;P.wind.set(2,0,0);P.stumble.set(2,0,0);P.stumbleT=1;
  const startX=P.pos.x;updatePlayer(.01);check('platform wind and stumble displacement',Math.abs(P.pos.x-startX-(IS_TOUCH?.02:.04))<.00001);
  P.wind.set(0,0,0);P.stumbleT=0;
  if(IS_TOUCH){const tiny=MOBILE.pad(.05,.05);touchMove.x=tiny.x;touchMove.y=tiny.y;updatePlayer(.01);check('thumb drift cannot move player',P.vel.lengthSq()===0);
   touchMove.y=.25;updatePlayer(.01);check('partial thumb supports slow movement',Math.hypot(P.vel.x,P.vel.z)<1);touchMove.y=0;
   reviewScene('stairs');FIG.spawn(10,.85);MOBILE.recover(G.t);const fi=FIG.idx;FIG.update(.1);check('respawn grace stops stair pursuit',FIG.idx===fi);}
  else{keys.KeyW=true;updatePlayer(.01);check('desktop walking speed unchanged',Math.abs(P.vel.z+4.2)<.00001);keys.ShiftLeft=true;updatePlayer(.01);check('desktop creep speed unchanged',Math.abs(P.vel.z+1.7)<.00001);keys.KeyW=keys.ShiftLeft=false;}
  reviewScene('stairs');const crumble=slabState.findIndex(st=>st.crumble);P.groundRef={slab:crumble};slabState[crumble].timer=1.1;updateSlabs(.01);
  check('platform crumble threshold',slabState[crumble].gone===!IS_TOUCH);slabState[crumble].timer=1.51;updateSlabs(.01);check('mobile crumble still fails eventually',slabState[crumble].gone);
  Audio.stopVoice();let played=0;const play=Audio.play;Audio.play=function(...args){played++;return play.apply(this,args)};
  Audio.windScream(true);Audio.windScream(false);check('wind toggles never trigger vocals',played===0);Audio.play=play;
  Audio.voice('voice_breath');const breath=Audio.voiceSource;check('pain interrupts breathing',Audio.voice('voice_pain',.5,true)&&Audio.voiceSource!==breath);
  check('breathing cannot overlap pain',!Audio.voice('voice_breath'));Audio.stopVoice();
  reviewScene('ascent2');SAVE.write();const savedY=P.checkpoint.y;G.setupAscent(1);SAVE.load();SAVE.restore();
  check('save restores ascent and checkpoint',G.ascent===2&&Math.abs(P.pos.y-savedY-.02)<.001);
  for(const encounter of ['rush','rush2']){reviewScene(encounter);reviewAdvance(3.4);check(encounter+' throws the player',P.thrown==='air'&&!P.grounded);}
  reviewScene('collapse');reviewAdvance(5);check('figure disperses during collapse',FIG.disperse===-1&&FIG.parts.every(p=>!p.sp.visible));
  check('collapse lamps stay off',lampPool.every(l=>l.intensity===0));
  COL.burst(0,0,1,430);check('debris pool wraps without replacing only index zero',new Set(COL.pieces.map(p=>p.idx)).size===420&&COL.pieceCursor!==0);
  reviewAdvance(18);check('four segments pancake',COL.broken===4);
  reviewAdvance(10);check('collapse releases the player',!COL.attached);
 }catch(e){results.push('FAIL '+e.message)}
 $('checks').textContent=results.join('\\n');reviewStats();
}
document.querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>reviewScene(b.dataset.review));
const readyReview=setInterval(()=>{if(G.state==='title'){clearInterval(readyReview);reviewStats()}},100);
</script>'''

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(root),**kwargs)
    def do_GET(self):
        if urlparse(self.path).path in ('/','/review.html','/mobile.html','/fallback.html'):
            content=(root/'vertigo.html').read_text(encoding='utf8')
            test_gate=gate
            if urlparse(self.path).path=='/mobile.html':
                test_gate='<script>Object.defineProperty(navigator,"maxTouchPoints",{value:5});const nativeMatch=window.matchMedia.bind(window);window.matchMedia=q=>q==="(pointer: coarse)"?{matches:true}:nativeMatch(q);</script>'+gate
            if urlparse(self.path).path=='/fallback.html':
                test_gate='<script>window.fetch=()=>Promise.reject(new Error("test: external assets unavailable"));</script>'+gate
            content=content.replace('<script src=',test_gate+'<script src=',1)+panel
            raw=content.encode('utf8')
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        else:
            super().do_GET()
    def log_message(self,*args):pass

print(f'Read-only source review at http://127.0.0.1:{port}/review.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
