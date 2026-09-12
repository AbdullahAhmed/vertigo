<?php
declare(strict_types=1);
require __DIR__.'/lib.php';
try {
    auth_start();require_auth();
    $range=in_array($_GET['range']??'all',['all','today','7','30'],true)?($_GET['range']??'all'):'all';
    $r=report($range,($_GET['tests']??'0')==='1');
    if(($_GET['format']??'json')==='csv') {
        header('Content-Type: text/csv; charset=utf-8');header('Content-Disposition: attachment; filename="vertigo-metrics.csv"');
        $f=fopen('php://output','w');fputcsv($f,['metric','value'],',','"','');fputcsv($f,['unique_players',$r['unique_players']],',','"','');
        foreach($r['totals'] as $k=>$v)fputcsv($f,[$k,$v],',','"','');fclose($f);
    } else {header('Content-Type: application/json');header('Content-Disposition: attachment; filename="vertigo-analytics.json"');echo json_encode($r,JSON_PRETTY_PRINT|JSON_THROW_ON_ERROR);}
}catch(Throwable $e){http_response_code(503);echo 'Analytics unavailable.';}
