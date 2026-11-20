<?php
declare(strict_types=1);
require __DIR__.'/../../backend/media-delivery/core.php';
$count=0;
function check(bool $ok): void { global $count;if(!$ok)throw new RuntimeException('Assertion failed');$count++; }
function denied(callable $fn): void { try{$fn();}catch(RuntimeException $e){check(true);return;}throw new RuntimeException('Expected denial'); }
check(DivineMediaAssets::siteAsset('favicon.ico'));check(DivineMediaAssets::siteAsset('favicon.png'));check(DivineMediaAssets::siteAsset('userPhoto/logo.png'));check(!DivineMediaAssets::siteAsset('cache/private.jpg'));
$records=[['id'=>1,'filename'=>'video_abc'],['id'=>2,'filename'=>'audio.xyz'],['id'=>3,'filename'=>'picture']];
foreach(['video_abc.mp4','video_abc_HD.webm','video_abc_portrait_thumbsV2.jpg','video_abc/index.m3u8','video_abc/HD/seg-1.ts','video_abc/encryption.key']as $p)check(DivineMediaAssets::owner($p,$records)===1);
check(DivineMediaAssets::owner('audio.xyz.mp3',$records)===2);check(DivineMediaAssets::owner('picture.png',$records)===3);
foreach(['../video_abc.mp4','video_abc/../x.key','%2e%2e/x.mp4','video_abc.php','video_abc.php.jpg','video_abc_evil.mp4','video_abc/.secret.key','/video_abc.mp4','video_abc\\x.mp4',"video_abc\0.mp4",'video_abc/index.m3u8?token=x','configuration.php','.divine-private/x.jpg']as $p)denied(fn()=>DivineMediaAssets::owner($p,$records));
denied(fn()=>DivineMediaAssets::owner('video_abc_HD.mp4',[...$records,['id'=>4,'filename'=>'video_abc_HD']]));
$tmp=sys_get_temp_dir().'/dm-gate-test-'.bin2hex(random_bytes(6));mkdir($tmp,0700);mkdir($tmp.'/media',0700);file_put_contents($tmp.'/media/picture.png','test');file_put_contents($tmp.'/outside.png','test');symlink($tmp.'/outside.png',$tmp.'/media/escape.png');symlink($tmp.'/media/picture.png',$tmp.'/media/alias.png');
try {
 check(DivineMediaAssets::file($tmp.'/media','picture.png')===$tmp.'/media/picture.png');
 denied(fn()=>DivineMediaAssets::file($tmp.'/media','escape.png'));denied(fn()=>DivineMediaAssets::file($tmp.'/media','alias.png'));denied(fn()=>DivineMediaAssets::file($tmp.'/media','missing.png'));
 $store=new DivineDeliveryStore($tmp.'/store');$grant=$store->issue('grant',['session'=>'opaque-native-session','origin'=>'https://divinemedia.us'],110);
 check($store->read('grant',$grant,100,true)['origin']==='https://divinemedia.us');denied(fn()=>$store->read('grant',$grant,100,true));
 $expired=$store->issue('grant',[],100);denied(fn()=>$store->read('grant',$expired,100,true));
 denied(fn()=>$store->read('grant','../../x',100));
 $session=$store->issue('session',['proof'=>'csrf-digest'],200);check($store->read('session',$session,101)['proof']==='csrf-digest');check($store->read('session',$session,102)['proof']==='csrf-digest');denied(fn()=>$store->read('session',$session,200));
 $manifest="#EXTM3U\n#EXT-X-KEY:METHOD=AES-128,URI=\"key.key\"\nsegment-1.ts\n";
 check(str_contains(DivineMediaAssets::manifest($manifest,'video_abc'),'URI="/divine-media/assets/video_abc/key.key"'));
 foreach(['https://other.test/x.ts','../x.ts','/videos/x.ts','x.ts?token=y','data:x','x.php','%2e%2e/x.ts'] as $uri)denied(fn()=>DivineMediaAssets::manifest("#EXTM3U\n".$uri,'video_abc'));
 denied(fn()=>DivineMediaAssets::manifest("#EXTM3U\n#EXT-X-KEY:URI=https://other.test/key",'video_abc'));
} finally {
 foreach(glob($tmp.'/store/*')?:[] as $p)unlink($p);rmdir($tmp.'/store');unlink($tmp.'/media/escape.png');unlink($tmp.'/media/alias.png');unlink($tmp.'/media/picture.png');rmdir($tmp.'/media');unlink($tmp.'/outside.png');rmdir($tmp);
}
echo json_encode(['result'=>'pass','checks'=>$count])."\n";
