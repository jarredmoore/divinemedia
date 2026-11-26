<?php
require $argv[1];
if(!function_exists('mb_substr')){function mb_substr($s,$start,$length){return substr($s,$start,$length);}}
function check($value,$message){if(!$value)throw new RuntimeException($message);}
$public=fn($host)=>['8.8.8.8'];
foreach(['https://vimeo.com/76979871','https://www.youtube.com/watch?v=M5hZAL_hW7c','https://www.dailymotion.com/video/x123456','https://www.twitch.tv/videos/12345']as $url){check(DivineImportSource::url($url,$public)===$url,'Public source rejected');}
foreach(['http://vimeo.com/1','file:///etc/passwd','https://127.0.0.1/x','https://[::1]/x','https://u:p@vimeo.com/1','https://vimeo.com:443/1','https://x.local/video','https://vimeo.com/1?access_token=secret',"https://vimeo.com/1\n--exec=bad",'https://vimeo.com\\@internal/x']as $url){try{DivineImportSource::url($url,$public);throw new LogicException('Unsafe source accepted');}catch(InvalidArgumentException $e){}}
foreach(['127.0.0.1','10.0.0.1','169.254.169.254','192.168.1.1','100.64.0.1','198.18.0.1','::1','::ffff:127.0.0.1']as $ip){try{DivineImportSource::url('https://vimeo.com/video',fn($host)=>[$ip]);throw new LogicException('Private IP accepted');}catch(InvalidArgumentException $e){}}
$info=['title'=>'A public video','extractor_key'=>'Vimeo','duration'=>64,'url'=>'https://cdn.vimeo.com/test.mp4','formats'=>[['url'=>'https://cdn.vimeo.com/test2.mp4']]];
$m=DivineImportSource::metadata($info,'https://vimeo.com/76979871',$public);check($m['title']==='A public video'&&!isset($m['url_media']),'Provider normalization failed');
foreach([['extractor_key'=>'Generic'],['entries'=>[]],['is_live'=>true],['has_drm'=>true],['availability'=>'private'],['duration'=>50000],['filesize'=>5000000000],['url'=>'file:///etc/passwd'],['formats'=>[['url'=>'https://localhost/test.mp4']]]]as $patch){try{DivineImportSource::metadata(array_replace($info,$patch),'https://vimeo.com/1',fn($host)=>$host==='localhost'?['127.0.0.1']:['8.8.8.8']);throw new LogicException('Restricted metadata accepted');}catch(InvalidArgumentException $e){}}
echo "Public import URL and provider metadata policy: pass\n";
