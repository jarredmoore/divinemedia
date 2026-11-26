<?php
/** Runs only inside the private Encoder worker; never include in a browser endpoint directly. */
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once __DIR__.'/import-source.php';
try{
    $source=DivineImportSource::url((string)($dmEncoderData['url']??''));
    $command=Encoder::getYouTubeDLCommand('',0);
    if(preg_match('/--(?:cookies|username|password|netrc|add-header)/i',$command)){enc_reply(['error'=>'Public preview is not available with this downloader configuration.']);}
    if(!str_contains($command,'yt-dlp')&&!str_contains($command,'yt_dlp')){enc_reply(['error'=>'Public link preview requires the installed yt-dlp importer.']);}
    // No creator cookies/OAuth, arbitrary config, Generic scraper, playlists, download or queue dispatch.
    $command=preg_replace('/(?<!\S)--no-check-certificates?(?=\s|$)/','',$command);
    if(str_contains($command,'--no-check-certificate'))enc_reply(['error'=>'Certificate verification must stay enabled for link preview.']);
    $command.=' --ignore-config --no-cache-dir --no-playlist --no-warnings --skip-download --dump-single-json --use-extractors default,-generic --socket-timeout 5 --retries 0 --extractor-retries 0 -- '.escapeshellarg($source);
    $pipes=[];$process=proc_open(['timeout','-k','1','17','sh','-c',$command],[0=>['pipe','r'],1=>['pipe','w'],2=>['file','/dev/null','a']],$pipes);
    if(!is_resource($process)){enc_reply(['error'=>'The link preview service is unavailable.']);}fclose($pipes[0]);stream_set_blocking($pipes[1],false);$raw='';$started=microtime(true);
    do{$raw.=stream_get_contents($pipes[1],max(1,2000000-strlen($raw)));$status=proc_get_status($process);if(strlen($raw)>=2000000||microtime(true)-$started>18){proc_terminate($process);break;}if($status['running'])usleep(20000);}while($status['running']);
    $raw.=stream_get_contents($pipes[1],max(1,2000000-strlen($raw)));fclose($pipes[1]);proc_close($process);$info=json_decode(trim($raw),true);
    if(!is_array($info)||strlen($raw)>=2000000){enc_reply(['error'=>'The installed downloader could not preview this link. It may require sign-in, be unsupported, or be temporarily unavailable. Try embedding it where available.']);}
    enc_reply(['item'=>DivineImportSource::metadata($info,$source),'profiles'=>['mp4','hls','audio','webm']]);
}catch(Throwable $e){enc_reply(['error'=>$e instanceof InvalidArgumentException?$e->getMessage():'This provider is unavailable for importing.']);}
