"""HTTP integration checks against the real PHP backend with isolated storage."""
from pathlib import Path
import concurrent.futures, http.cookiejar, json, os, re, secrets, shutil, subprocess, sys, tempfile, time, urllib.error, urllib.request, uuid
root=Path(__file__).resolve().parents[1];php=str(Path(sys.argv[1]).resolve());origin='http://127.0.0.1:8770'
def check(ok,label):
    assert ok,label
    print('PASS:',label)
with tempfile.TemporaryDirectory(prefix='vertigo-analytics-test-') as tmp:
    tmp=Path(tmp);site=tmp/'site';site.mkdir();shutil.copytree(root/'analytics',site/'analytics',ignore=shutil.ignore_patterns('config.php'))
    password=secrets.token_urlsafe(24)
    hashed=subprocess.check_output([php,'-r','echo password_hash(stream_get_contents(STDIN),PASSWORD_BCRYPT);'],input=password.encode()).decode()
    (site/'analytics/config.php').write_text("<?php return ['password_hash'=>'"+hashed+"','secret'=>'"+secrets.token_hex(32)+"','origin'=>'"+origin+"','data_dir'=>'"+str(tmp/'private').replace('\\','/')+"'];",encoding='utf8')
    server=subprocess.Popen([php,'-S','127.0.0.1:8770','-t',str(site)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def req(path,data=None,opener=None,origin_header=origin):
        body=json.dumps(data).encode() if isinstance(data,dict) else data
        headers={'Origin':origin_header,'Content-Type':'text/plain'} if body is not None else {}
        request=urllib.request.Request(origin+'/analytics/'+path,data=body,headers=headers)
        try:
            with (opener or urllib.request.build_opener()).open(request) as response:return response.status,response.read(),response.headers
        except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
    try:
        for _ in range(60):
            try:req('');break
            except OSError:time.sleep(.1)
        check(req('export.php')[0]==401,'anonymous export is denied')
        check(req('collect.php')[0]==405,'collector cannot read data')
        payload={'v':1,'session':str(uuid.uuid4()),'visitor':str(uuid.uuid4()),'platform':'mobile','build':'analytics-1','seq':1,'test':False,'metrics':{'page_views':1,'plays':1,'new_games':1,'active_seconds':60,'climbed_m':12,'walked_m':20,'falls':2,'climb_attempts':3},'falls_by_lap':[2]+[0]*11,'reached':[1]+[0]*11,'last_lap':0}
        check(req('collect.php',payload,origin_header='https://evil.example')[0]==403,'foreign origin rejected')
        check(req('collect.php',{**payload,'session':'../../evil'})[0]==400,'path traversal rejected')
        check(req('collect.php',{**payload,'metrics':{'unknown':1}})[0]==400,'unknown fields rejected')
        check(req('collect.php',{**payload,'metrics':{'climbed_m':99999}})[0]==400,'impossible distance rejected')
        check(req('collect.php',b'x'*9000)[0]==413,'oversized payload rejected')
        check(req('collect.php',payload)[0]==204,'valid play accepted')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:codes=list(pool.map(lambda _:req('collect.php',payload)[0],range(12)))
        check(all(c==204 for c in codes),'duplicate concurrent uploads succeed')
        jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        code,html,headers=req('',opener=opener);csrf=re.search(rb'name="csrf" value="([^"]+)"',html)[1].decode()
        import urllib.parse
        request=urllib.request.Request(origin+'/analytics/',data=urllib.parse.urlencode({'password':password,'csrf':csrf}).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'})
        with opener.open(request) as response:dashboard=response.read()
        check(b'Total plays' in dashboard,'authenticated dashboard renders')
        check('no-store' in headers.get('Cache-Control',''),'private pages are never cached')
        def report(tests=False):return json.loads(req('export.php?tests='+('1' if tests else '0'),opener=opener)[1])
        r=report();check(r['totals']['plays']==1 and r['totals']['falls']==2 and r['totals']['climbed_m']==12,'duplicates do not inflate counts')
        payload2={**payload,'session':str(uuid.uuid4()),'seq':1,'metrics':{**payload['metrics'],'max_height':20}};req('collect.php',payload2)
        r=report();check(r['unique_players']==1 and r['totals']['plays']==2,'two plays in one browser count as one unique player')
        check(r['totals']['max_height']==20,'maximum height is a maximum, not a sum')
        payload2.update(seq=2,test=True);req('collect.php',payload2)
        r=report();check(r['totals']['plays']==1 and report(True)['totals']['plays']==1,'debug marking removes whole run from normal totals')
        stale={**payload,'seq':0};check(req('collect.php',stale)[0]==400,'invalid sequence rejected')
        updated={**payload,'seq':3,'metrics':{**payload['metrics'],'falls':3},'last_lap':2};req('collect.php',updated);req('collect.php',payload)
        check(report()['totals']['falls']==3,'late stale uploads cannot lower totals')
        check(req('export.php?format=csv',opener=opener)[0]==200,'authenticated CSV export works')
        check(req('../.vertigo-analytics/sessions/')[0]==404,'storage is outside public root')
        (root/'build/deploy/dashboard-preview.html').write_bytes(dashboard.replace(csrf.encode(),b'REDACTED'))
    finally:server.terminate();server.wait(timeout=10)
