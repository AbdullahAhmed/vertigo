<?php
declare(strict_types=1);
require __DIR__.'/../analytics/lib.php';
function check(bool $ok,string $label): void { if(!$ok) throw new RuntimeException($label); echo "PASS: $label\n"; }
foreach(['GEOIP_COUNTRY_CODE','GEOIP_COUNTRY_NAME','GEOIP_REGION_NAME','GEOIP_REGION'] as $key) { putenv($key);putenv('REDIRECT_'.$key); }
$_SERVER=['HTTP_GEOIP_COUNTRY_CODE'=>'US','HTTP_CF_IPCOUNTRY'=>'US','HTTP_X_FORWARDED_FOR'=>'8.8.8.8'];
check(rough_location()['country']===null,'untrusted request headers cannot supply location');
$_SERVER['GEOIP_COUNTRY_CODE']='CA';$_SERVER['GEOIP_COUNTRY_NAME']='Canada';$_SERVER['GEOIP_REGION_NAME']='Alberta';
check(rough_location()===['country'=>'CA','country_name'=>'Canada','region'=>'Alberta'],'server country and region are accepted');
$_SERVER['GEOIP_REGION_NAME']='<script>alert(1)</script>';
check(rough_location()['region']===null,'invalid region is discarded');
$_SERVER['GEOIP_COUNTRY_CODE']='ZZ';
check(rough_location()['country']===null,'unresolved country remains unknown');
$_SERVER=['REDIRECT_GEOIP_COUNTRY_CODE'=>'GB'];
check(rough_location()===['country'=>'GB','country_name'=>'GB','region'=>null],'country-only lookup is supported');
