<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
umask(0077);ini_set('display_errors','0');ini_set('error_log','/dev/null');ob_start();
$dmQueue='/var/www/tmp/divine-thumbnails';if(!is_dir($dmQueue)){exit;}
$dmLock=fopen($dmQueue.'/worker.lock','c');if(!$dmLock||!flock($dmLock,LOCK_EX|LOCK_NB)){exit;}
$_GET=$_POST=$_REQUEST=$_COOKIE=[];$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/Encoder/';
require dirname(__DIR__,2).'/Encoder/videos/configuration.php';
require_once dirname(__DIR__,2).'/Encoder/objects/Encoder.php';
$dmStats=['created'=>0,'preserved'=>0,'failed'=>0,'methods'=>[]];
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
        $dmMethod='frame';
        if(($dmJob['kind']??'video')==='audio'){
            $dmPipes=[];$dmProbe=proc_open(['/usr/bin/timeout','10s','/usr/bin/ffprobe','-v','error','-show_entries','stream=codec_type:stream_disposition=attached_pic:format_tags=artist,album','-of','json',$dmInput],[0=>['file','/dev/null','r'],1=>['pipe','w'],2=>['file','/dev/null','a']],$dmPipes);
            $dmMeta=[];if(is_resource($dmProbe)){$dmMeta=json_decode(stream_get_contents($dmPipes[1],100000),true)?:[];fclose($dmPipes[1]);proc_close($dmProbe);}
            $dmEmbedded=false;foreach($dmMeta['streams']??[] as $dmStream){if(!empty($dmStream['disposition']['attached_pic'])){$dmEmbedded=true;}}
            $dmImage=false;
            if($dmEmbedded){
                // Attached MP3 pictures are not timeline frames: extract without the video helper's seek.
                $dmPipes=[];$dmExtract=proc_open(['/usr/bin/timeout','15s','/usr/bin/ffmpeg','-hide_banner','-loglevel','error','-nostdin','-i',$dmInput,'-map','0:v:0','-frames:v','1','-an','-threads','1','-y',$dmInput.'.jpg'],[0=>['file','/dev/null','r'],1=>['file','/dev/null','a'],2=>['file','/dev/null','a']],$dmPipes);
                if(is_resource($dmExtract)){proc_close($dmExtract);}$dmImage=$dmInput.'.jpg';$dmMethod='embedded';
            }
            if(!$dmImage||$dmImage!==$dmInput.'.jpg'||!is_file($dmImage)){
                $dmTags=array_change_key_case($dmMeta['format']['tags']??[],CASE_LOWER);
                $dmKey=strtolower(trim(preg_replace('/\s+/',' ',(string)($dmTags['artist']??'')))).'|'.strtolower(trim(preg_replace('/\s+/',' ',(string)($dmTags['album']??''))));
                $dmCatalog=json_decode((string)@file_get_contents(__DIR__.'/album-covers.json'),true)?:[];
                $dmCover=isset($dmCatalog[$dmKey])?realpath(__DIR__.'/covers/'.$dmCatalog[$dmKey]):false;
                if($dmCover&&str_starts_with($dmCover,__DIR__.'/covers/')&&is_file($dmCover)){$dmImage=$dmTemp.'/album.jpg';copy($dmCover,$dmImage);$dmMethod='album';}
                else{$dmImage=Encoder::getSpectrum($dmInput);$dmMethod='waveform';}
            }
        }else{$dmImage=Encoder::getImage($dmInput,max(0,min(10,(float)$dmJob['seconds'])));}
        $dmExpected=($dmJob['kind']??'video')==='audio'?[$dmInput.'.jpg',$dmInput.'_spectrum.jpg',$dmTemp.'/album.jpg']:[$dmInput.'.jpg'];
        $dmInfo=$dmImage&&is_file($dmImage)?@getimagesize($dmImage):false;
        if(!$dmInfo||!in_array($dmImage,$dmExpected,true)||$dmInfo[2]!==IMAGETYPE_JPEG||$dmInfo[0]<1||$dmInfo[1]<1){throw new RuntimeException('No image frame');}
        if(($dmJob['kind']??'video')==='audio'&&max($dmInfo[0],$dmInfo[1])>720&&function_exists('imagecreatefromjpeg')){
            $dmDecoded=imagecreatefromjpeg($dmImage);$dmRatio=720/max($dmInfo[0],$dmInfo[1]);$dmSmall=imagecreatetruecolor(max(1,(int)round($dmInfo[0]*$dmRatio)),max(1,(int)round($dmInfo[1]*$dmRatio)));
            imagecopyresampled($dmSmall,$dmDecoded,0,0,0,0,imagesx($dmSmall),imagesy($dmSmall),$dmInfo[0],$dmInfo[1]);imagejpeg($dmSmall,$dmImage,85);imagedestroy($dmSmall);imagedestroy($dmDecoded);
        }
        chmod($dmImage,0644);
        // Hard-link creation is atomic and cannot overwrite an existing/custom cover.
        $dmPublishTemp=tempnam(dirname($dmDest),'.divine-cover-');
        if(!$dmPublishTemp||!copy($dmImage,$dmPublishTemp)){throw new RuntimeException('Cover could not be staged');}
        chmod($dmPublishTemp,0644);
        if(!@link($dmPublishTemp,$dmDest)&&!file_exists($dmDest)){throw new RuntimeException('Cover could not be published');}
        $dmStats['created']++;$dmStats['methods'][$dmMethod]=($dmStats['methods'][$dmMethod]??0)+1;unlink($dmFile);
        $dmPipes=[];$dmProcess=proc_open(['/usr/bin/php',__DIR__.'/clear-cache.php',(string)(int)$dmJob['id']],[0=>['file','/dev/null','r'],1=>['file','/dev/null','a'],2=>['file','/dev/null','a']],$dmPipes);
        if(is_resource($dmProcess)){proc_close($dmProcess);}
    }catch(Throwable $e){$dmStats['failed']++;}
    finally{if($dmPublishTemp){@unlink($dmPublishTemp);}if($dmTemp&&is_dir($dmTemp)){foreach(glob($dmTemp.'/*') as $dmPath){@unlink($dmPath);}@rmdir($dmTemp);}}
}
while(ob_get_level()){ob_end_clean();}
file_put_contents($dmQueue.'/last-result.private.report.tmp',json_encode($dmStats));rename($dmQueue.'/last-result.private.report.tmp',$dmQueue.'/last-result.private.report');
flock($dmLock,LOCK_UN);fclose($dmLock);
// Drain batches beyond eight jobs, including uploads that arrived while this worker held its lock.
if(glob($dmQueue.'/*.json')){execAsync('/usr/bin/timeout -k 2s 45s /usr/bin/php '.escapeshellarg(__FILE__));}
echo json_encode($dmStats);
