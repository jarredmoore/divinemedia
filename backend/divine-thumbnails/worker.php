<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
umask(0077);ini_set('display_errors','0');ini_set('error_log','/dev/null');ob_start();
$dmQueue='/var/www/tmp/divine-thumbnails';if(!is_dir($dmQueue)){exit;}
$dmLock=fopen($dmQueue.'/worker.lock','c');if(!$dmLock||!flock($dmLock,LOCK_EX|LOCK_NB)){exit;}
$_GET=$_POST=$_REQUEST=$_COOKIE=[];$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/Encoder/';
require dirname(__DIR__,2).'/Encoder/videos/configuration.php';
require_once dirname(__DIR__,2).'/Encoder/objects/Encoder.php';
$dmStats=['created'=>0,'preserved'=>0,'failed'=>0];
foreach(array_slice(glob($dmQueue.'/*.json'),0,8) as $dmFile){
    $dmJob=json_decode((string)file_get_contents($dmFile),true);$dmTemp=null;$dmPublishTemp=null;
    try{
        if(!is_array($dmJob)||!preg_match('/^\d+\.json$/D',basename($dmFile))||($dmJob['attempts']??0)>=3){rename($dmFile,$dmFile.'.failed');continue;}
        $dmRoot=realpath(dirname(__DIR__,2).'/videos');$dmSource=realpath($dmJob['source']??'');$dmDest=$dmJob['destination']??'';
        if(!$dmRoot||!$dmSource||!str_starts_with($dmSource,$dmRoot.'/')||!is_file($dmSource)||!str_starts_with(realpath(dirname($dmDest)).'/',$dmRoot.'/')||!preg_match('/^[A-Za-z0-9_.-]+\.jpg$/D',basename($dmDest))){throw new RuntimeException('Invalid local source');}
        if(file_exists($dmDest)){$dmStats['preserved']++;unlink($dmFile);continue;}
        $dmJob['attempts']++;file_put_contents($dmFile,json_encode($dmJob));
        $dmTemp=$dmQueue.'/extract-'.bin2hex(random_bytes(12));mkdir($dmTemp,0700);
        // Fixed safe temporary input name avoids native shell interpolation of original filenames.
        $dmInput=$dmTemp.'/source.'.(str_ends_with(strtolower($dmSource),'.webm')?'webm':'mp4');symlink($dmSource,$dmInput);
        $dmImage=Encoder::getImage($dmInput,max(0,min(10,(float)$dmJob['seconds'])));
        $dmInfo=$dmImage&&is_file($dmImage)?@getimagesize($dmImage):false;
        if(!$dmInfo||$dmImage!==$dmInput.'.jpg'||$dmInfo[2]!==IMAGETYPE_JPEG||$dmInfo[0]<1||$dmInfo[1]<1){throw new RuntimeException('No image frame');}
        chmod($dmImage,0644);
        // Hard-link creation is atomic and cannot overwrite an existing/custom cover.
        $dmPublishTemp=tempnam(dirname($dmDest),'.divine-cover-');
        if(!$dmPublishTemp||!copy($dmImage,$dmPublishTemp)){throw new RuntimeException('Cover could not be staged');}
        chmod($dmPublishTemp,0644);
        if(!@link($dmPublishTemp,$dmDest)&&!file_exists($dmDest)){throw new RuntimeException('Cover could not be published');}
        $dmStats['created']++;unlink($dmFile);
        $dmPipes=[];$dmProcess=proc_open(['/usr/bin/php',__DIR__.'/clear-cache.php',(string)(int)$dmJob['id']],[0=>['file','/dev/null','r'],1=>['file','/dev/null','a'],2=>['file','/dev/null','a']],$dmPipes);
        if(is_resource($dmProcess)){proc_close($dmProcess);}
    }catch(Throwable $e){$dmStats['failed']++;}
    finally{if($dmPublishTemp){@unlink($dmPublishTemp);}if($dmTemp&&is_dir($dmTemp)){foreach(glob($dmTemp.'/*') as $dmPath){@unlink($dmPath);}@rmdir($dmTemp);}}
}
while(ob_get_level()){ob_end_clean();}
file_put_contents($dmQueue.'/last-result.private.report.tmp',json_encode($dmStats));rename($dmQueue.'/last-result.private.report.tmp',$dmQueue.'/last-result.private.report');
echo json_encode($dmStats);
