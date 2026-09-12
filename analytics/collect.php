<?php
declare(strict_types=1);
require __DIR__.'/lib.php';
try {
    if ($_SERVER['REQUEST_METHOD']!=='POST') { http_response_code(405);header('Allow: POST');exit; }
    if (($_SERVER['HTTP_ORIGIN'] ?? '')!==config()['origin']) { http_response_code(403);exit; }
    if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0)>8192) { http_response_code(413);exit; }
    if (!limit('collect',240,60)) { http_response_code(429);header('Retry-After: 60');exit; }
    $body=file_get_contents('php://input',false,null,0,8193);
    if (strlen($body)>8192) { http_response_code(413);exit; }
    $d=json_decode($body,true);
    if (!is_array($d) || ($d['v'] ?? 0)!==1) { http_response_code(400);exit; }
    foreach (['session','visitor'] as $key) if (!is_string($d[$key] ?? null) || !preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/D',$d[$key])) { http_response_code(400);exit; }
    if (!in_array($d['platform'] ?? '',['mobile','desktop'],true) || !is_array($d['metrics'] ?? null)) { http_response_code(400);exit; }
    $metrics=array_fill_keys(metric_names(),0);
    foreach ($d['metrics'] as $k=>$v) {
        if (!array_key_exists($k,$metrics) || !is_numeric($v) || !is_finite((float)$v) || $v<0 || $v>10000000) { http_response_code(400);exit; }
        $metrics[$k]=round((float)$v,3);
    }
    foreach(['page_views','plays','new_games','continues','extinguishes','collapse_starts','completions'] as $k) if($metrics[$k]>1){http_response_code(400);exit;}
    if ($metrics['completions']>$metrics['collapse_starts'] || $metrics['collapse_starts']>$metrics['extinguishes'] || $metrics['extinguishes']>$metrics['plays'] || $metrics['plays']>$metrics['page_views'] || $metrics['new_games']+$metrics['continues']!==$metrics['plays']) { http_response_code(400);exit; }
    if ($metrics['active_seconds']>172800 || $metrics['climbed_m']>$metrics['active_seconds']*4+10 || $metrics['walked_m']>$metrics['active_seconds']*12+10 || $metrics['max_height']>73) { http_response_code(400);exit; }
    foreach(['falls_by_lap','reached'] as $key) {
        if (!is_array($d[$key] ?? null) || count($d[$key])!==12 || !array_is_list($d[$key])) { http_response_code(400);exit; }
        foreach($d[$key] as $v) if(!is_int($v)||$v<0||$v>($key==='reached'?1:100000)){http_response_code(400);exit;}
    }
    if (!is_int($d['seq'] ?? null) || $d['seq']<1 || $d['seq']>1000000 || !is_int($d['last_lap'] ?? null) || $d['last_lap'] < -1 || $d['last_lap'] > 11 || !is_bool($d['test'] ?? null)) { http_response_code(400);exit; }
    $c=config(); $id=hash_hmac('sha256',$d['session'],$c['secret']); $visitor=hash_hmac('sha256',$d['visitor'],$c['secret']);
    $dir=$c['data_dir'].'/sessions/'.substr($id,0,2); if(!is_dir($dir))@mkdir($dir,0700,true);
    locked_update($dir.'/'.$id.'.json',function($old)use($d,$metrics,$visitor){
        if (!$old) $old=['created'=>time(),'last_seen'=>time(),'visitor'=>$visitor,'platform'=>$d['platform'],'test'=>false,'seq'=>0,'metrics'=>array_fill_keys(metric_names(),0),'falls_by_lap'=>array_fill(0,12,0),'reached'=>array_fill(0,12,0),'last_lap'=>-1,'build'=>'analytics-1'];
        if($old['visitor']!==$visitor) { http_response_code(409);exit; }
        // Resolve once per visit; older records may gain a location on their next real update.
        if (!array_key_exists('location',$old)) $old['location']=rough_location();
        foreach($metrics as $k=>$v)$old['metrics'][$k]=max($old['metrics'][$k],$v);
        for($i=0;$i<12;$i++){ $old['falls_by_lap'][$i]=max($old['falls_by_lap'][$i],$d['falls_by_lap'][$i]);$old['reached'][$i]=max($old['reached'][$i],$d['reached'][$i]); }
        if($d['seq']>$old['seq']){ $old['seq']=$d['seq'];$old['last_lap']=$d['last_lap'];$old['last_seen']=time(); }
        $old['test']=$old['test']||$d['test'];return $old;
    });
    http_response_code(204);
} catch(Throwable $e){error_log('VERTIGO analytics storage failure');http_response_code(503);}
