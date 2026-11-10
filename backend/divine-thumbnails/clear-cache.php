<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
$id=filter_var($argv[1]??0,FILTER_VALIDATE_INT,['options'=>['min_range'=>1]]);if(!$id){exit(1);}
$_GET=$_POST=$_REQUEST=$_COOKIE=[];$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';
require dirname(__DIR__,2).'/videos/configuration.php';
$v=new Video('','',$id);
if($v->getId()){
    // Only this video's metadata/image cache; never delete covers or flush all videos.
    $cache=new VideoCacheHandler($v->getFilename());$cache->deleteCache(false,false);
    Video::clearImageCache($v->getFilename(),'video');
}
