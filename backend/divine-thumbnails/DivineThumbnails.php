<?php
if(!isset($global['systemRootPath'])){http_response_code(404);exit;}
require_once $global['systemRootPath'].'plugin/Plugin.abstract.php';
class DivineThumbnails extends PluginAbstract {
    const UUID='dbdb9ef6-71f0-48e4-b512-67cf98f50b1d';
    const QUEUE='/var/www/tmp/divine-thumbnails';
    public function getName(){return 'DivineThumbnails';}
    public function getUUID(){return self::UUID;}
    public function getPluginVersion(){return '1.0';}
    public function getDescription(){return 'Generate a missing still cover after a new local video upload, using the installed Encoder image extractor. Existing covers are preserved.';}
    public function getEmptyDataObject(){return new stdClass();}
    public function onUploadIsDone($id){self::enqueue((int)$id);}
    public function onEncoderNotifyIsDone($id){self::enqueue((int)$id);}
    public function afterNewVideo($id){self::enqueue((int)$id);}
    public function executeEveryMinute(){self::kick();}
    public static function enqueue(int $id): bool {
        try{
            $v=new Video('','',$id);if(!$id||!$v->getId()||$v->getType()!=='video'){return false;}
            $filename=$v->getFilename();if(!preg_match('/^[A-Za-z0-9_.-]+$/D',$filename)||str_contains($filename,'..')){return false;}
            $root=realpath(Video::getStoragePath());if(!$root){return false;}
            $destination=Video::getPathToFile($filename.'.jpg',true);
            if(!$destination||!str_starts_with(realpath(dirname($destination)).'/',rtrim($root,'/').'/')){return false;}
            foreach(['.jpg','.png','_portrait.jpg'] as $ext){if(file_exists(Video::getPathToFile($filename.$ext))){return false;}}
            $source=null;
            foreach(['.mp4','.webm'] as $ext){$p=realpath(Video::getPathToFile($filename.$ext));if($p&&str_starts_with($p,$root.'/')&&is_file($p)){$source=$p;break;}}
            if(!$source){$s=Video::getHigestResolutionVideoMP4Source($filename,false,true);$p=realpath($s['path']??'');if($p&&str_starts_with($p,$root.'/')&&is_file($p)){$source=$p;}}
            if(!$source){return false;}
            if(!is_dir(self::QUEUE)&&!mkdir(self::QUEUE,0700,true)){return false;}
            $job=self::QUEUE.'/'.$id.'.json';if(!is_file($job)){
                $seconds=max(0,min(10,parseDurationToSeconds($v->getDuration())*0.1));
                $data=['id'=>$id,'source'=>$source,'destination'=>$destination,'root'=>$root,'seconds'=>$seconds,'attempts'=>0];
                $tmp=tempnam(self::QUEUE,'.job-');file_put_contents($tmp,json_encode($data));chmod($tmp,0600);rename($tmp,$job);
            }
            self::kick();return true;
        }catch(Throwable $e){error_log('DivineThumbnails: unable to queue cover for video '.$id);return false;}
    }
    private static function kick(): void {
        if(!is_dir(self::QUEUE)||!glob(self::QUEUE.'/*.json')){return;}
        // One bounded background worker; no Encoder queue dispatch or video conversion.
        execAsync('/usr/bin/timeout -k 2s 45s /usr/bin/php '.escapeshellarg(__DIR__.'/worker.php'));
    }
}
