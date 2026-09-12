<?php
declare(strict_types=1);
ini_set('display_errors', '0');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex, nofollow');
header('Referrer-Policy: no-referrer');
header("Content-Security-Policy: default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
function config(): array {
    static $c;
    if (!$c) {
        $path = __DIR__ . '/config.php';
        if (!is_file($path)) { http_response_code(503); exit('Analytics not configured.'); }
        $c = require $path;
        if (strlen($c['secret'] ?? '') < 64 || !str_starts_with($c['password_hash'] ?? '', '$2')) { http_response_code(503); exit('Analytics not configured.'); }
        foreach (['', '/sessions', '/limits'] as $sub) {
            if (!is_dir($c['data_dir'] . $sub) && !mkdir($c['data_dir'] . $sub, 0700, true) && !is_dir($c['data_dir'] . $sub)) throw new RuntimeException('Storage unavailable');
        }
    }
    return $c;
}
function json_read(string $path): array {
    if (!is_file($path)) return [];
    $a = json_decode((string)file_get_contents($path), true);
    if (!is_array($a)) throw new RuntimeException('Invalid stored record');
    return $a;
}
function locked_update(string $path, callable $fn): array {
    $lock = fopen($path . '.lock', 'c');
    if (!$lock || !flock($lock, LOCK_EX)) throw new RuntimeException('Lock unavailable');
    try {
        $a = $fn(json_read($path));
        $tmp = $path . '.' . bin2hex(random_bytes(6)) . '.tmp';
        if (file_put_contents($tmp, json_encode($a, JSON_THROW_ON_ERROR), LOCK_EX) === false) throw new RuntimeException('Write failed');
        chmod($tmp, 0600);
        if (!rename($tmp, $path)) { @unlink($tmp); throw new RuntimeException('Commit failed'); }
        return $a;
    } finally { flock($lock, LOCK_UN); fclose($lock); }
}
function limit(string $scope, int $max, int $seconds): bool {
    $c = config();
    // A daily rotating keyed digest is used only for abuse control; raw addresses are never saved here.
    $key = hash_hmac('sha256', gmdate('Y-m-d') . ':' . ($_SERVER['REMOTE_ADDR'] ?? 'local'), $c['secret']);
    $path = $c['data_dir'] . '/limits/' . $scope . '-' . $key . '.json';
    $r = locked_update($path, function($r) use ($seconds) {
        if (($r['until'] ?? 0) < time()) $r = ['until'=>time()+$seconds, 'count'=>0];
        $r['count']++; return $r;
    });
    if (random_int(1,100) === 1) foreach (glob($c['data_dir'].'/limits/*.json') ?: [] as $f) {
        if (filemtime($f) < time()-172800) @unlink($f);
        if (!is_file($f) && is_file($f.'.lock')) @unlink($f.'.lock');
    }
    return $r['count'] <= $max;
}
function metric_names(): array {
    return ['page_views','plays','new_games','continues','climb_attempts','walked_m','climbed_m','max_height','falls','short_drops','jumps','auto_jumps','crumble_triggers','slabs_broken','figure_grabs','nerve_stumbles','roof_arrivals','button_presses','extinguishes','collapse_starts','completions','debug_skips','active_seconds','panic_seconds','frames','slow_frames'];
}
function auth_start(): void {
    session_name('vertigo_admin');
    ini_set('session.use_strict_mode', '1');
    session_set_cookie_params(['lifetime'=>0,'path'=>'/analytics/','secure'=>str_starts_with(config()['origin'],'https:'),'httponly'=>true,'samesite'=>'Strict']);
    session_start();
    if (!isset($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(24));
}
function authenticated(): bool { return ($_SESSION['authenticated_until'] ?? 0) > time(); }
function require_auth(): void { if (!authenticated()) { http_response_code(401); exit('Sign in required.'); } }
function e($s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function rough_location(): array {
    // Only web-server GeoIP variables are trusted. HTTP_* headers and client payloads are not.
    $read = static function(string $key): string {
        foreach ([$key,'REDIRECT_'.$key] as $name) {
            $value=$_SERVER[$name] ?? getenv($name);
            if (is_string($value) && $value!=='' && strlen($value)<=120 && preg_match('/^[\p{L}\p{N} .,_()\x{2019}\x{0027}-]+$/u',$value)) return trim($value);
        }
        return '';
    };
    $country=strtoupper($read('GEOIP_COUNTRY_CODE'));
    if (!preg_match('/^[A-Z]{2}$/D',$country) || in_array($country,['ZZ','XX','EU','AP'],true)) return ['country'=>null,'country_name'=>null,'region'=>null];
    return ['country'=>$country,'country_name'=>$read('GEOIP_COUNTRY_NAME') ?: $country,'region'=>$read('GEOIP_REGION_NAME') ?: ($read('GEOIP_REGION') ?: null)];
}
function report(string $range, bool $tests): array {
    $now=time(); $since = $range==='today' ? strtotime('today UTC') : ($range==='7' ? $now-7*86400 : ($range==='30' ? $now-30*86400 : 0));
    $totals=array_fill_keys(metric_names(),0); $visitors=[]; $daily=[]; $platforms=[]; $laps=array_fill(0,12,['reached'=>0,'falls'=>0,'last'=>0]); $recent=[]; $allCount=0; $first=null; $testsCount=0;
    $locations=[]; $locationVisitors=[];
    foreach (glob(config()['data_dir'].'/sessions/*/*.json') ?: [] as $f) {
        $s=json_read($f); $allCount++; $first=min($first ?? $s['created'],$s['created']);
        if ($s['test']) $testsCount++;
        if ($s['test']!==$tests || $s['created']<$since) continue;
        $m=$s['metrics']; $date=gmdate('Y-m-d',$s['created']);
        $daily[$date] ??= ['plays'=>0,'completions'=>0,'falls'=>0];
        $platforms[$s['platform']] ??= ['plays'=>0,'completions'=>0,'falls'=>0,'active_seconds'=>0];
        foreach ($totals as $k=>$_) $totals[$k] = $k==='max_height' ? max($totals[$k],$m[$k]) : $totals[$k]+$m[$k];
        foreach ($daily[$date] as $k=>$_) $daily[$date][$k]+=$m[$k];
        foreach ($platforms[$s['platform']] as $k=>$_) $platforms[$s['platform']][$k]+=$m[$k];
        $geo=$s['location'] ?? ['country'=>null,'country_name'=>null,'region'=>null];
        if ($m['plays']>0) {
            $visitors[$s['visitor']]=true;
            $key=($geo['country'] ?? 'Unknown').'|'.($geo['region'] ?? '');
            $locations[$key] ??= $geo+['plays'=>0,'falls'=>0,'completions'=>0,'climbed_m'=>0];
            foreach(['plays','falls','completions','climbed_m'] as $k) $locations[$key][$k]+=$m[$k];
            $locationVisitors[$key][$s['visitor']]=true;
        }
        for($i=0;$i<12;$i++){ $laps[$i]['reached']+=$s['reached'][$i]; $laps[$i]['falls']+=$s['falls_by_lap'][$i]; }
        if ($m['plays'] && !$m['completions'] && $s['last_seen']<$now-120 && $s['last_lap']>=0) $laps[$s['last_lap']]['last']++;
        $recent[]=['started'=>gmdate('c',$s['created']),'updated'=>gmdate('c',$s['last_seen']),'platform'=>$s['platform'],'location'=>$geo,'kind'=>$m['plays']?($m['continues']?'continue':'new'):'visit only','meters'=>$m['climbed_m'],'falls'=>$m['falls'],'height'=>$m['max_height'],'completed'=>(bool)$m['completions'],'debug'=>$s['test']];
    }
    ksort($daily);usort($recent,fn($a,$b)=>strcmp($b['updated'],$a['updated']));
    foreach($locations as $key=>&$location) $location['unique_players']=count($locationVisitors[$key]);
    unset($location); usort($locations,fn($a,$b)=>$b['plays']<=>$a['plays']);
    return ['generated'=>gmdate('c'),'tracking_since'=>$first?gmdate('c',$first):null,'range'=>$range,'test_mode'=>$tests,'unique_players'=>count($visitors),'totals'=>$totals,'daily'=>$daily,'platforms'=>$platforms,'locations'=>$locations,'laps'=>$laps,'recent'=>array_slice($recent,0,100),'test_sessions'=>$testsCount,'stored_sessions'=>$allCount];
}
