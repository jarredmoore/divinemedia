<?php
declare(strict_types=1);
// A private CLI adapter: a browser can never establish or impersonate an Encoder session here.
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
ob_start();$finished=false;
function enc_reply(array $dmEncoderData): void {
    global $finished;$finished=true;
    while(ob_get_level()){ob_end_clean();}
    if(session_status()===PHP_SESSION_ACTIVE){$_SESSION=[];session_destroy();}
    echo json_encode($dmEncoderData,JSON_UNESCAPED_SLASHES|JSON_INVALID_UTF8_SUBSTITUTE);exit;
}
register_shutdown_function(function()use(&$finished){if(!$finished){enc_reply(['error'=>'Encoder service unavailable.']);}});
ini_set('display_errors','0');ini_set('error_log','/dev/null');
$dmEncoderInput=json_decode(stream_get_contents(STDIN,32768),true);
if(!is_array($dmEncoderInput)||empty($dmEncoderInput['actor']['userId'])||empty($dmEncoderInput['actor']['username'])){enc_reply(['error'=>'Invalid encoder actor.']);}
$dmEncoderActor=$dmEncoderInput['actor'];$dmEncoderOp=(string)($dmEncoderInput['op']??'');$dmEncoderData=$dmEncoderInput['data']??[];
$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/Encoder/';$_SERVER['SCRIPT_NAME']='/Encoder/divine-cli';
$_GET=$_POST=$_REQUEST=$_COOKIE=[];session_id(bin2hex(random_bytes(24)));
$dmEncoderRoot=dirname(__DIR__).'/Encoder/';
require $dmEncoderRoot.'videos/configuration.php';
require_once $dmEncoderRoot.'objects/Encoder.php';
require_once $dmEncoderRoot.'objects/Streamer.php';
require_once $dmEncoderRoot.'objects/Login.php';
require_once $dmEncoderRoot.'objects/Format.php';
ini_set('display_errors','0');ini_set('error_log','/dev/null');
try{
    $table=Streamer::getTableName();
    if(!preg_match('/^[a-zA-Z0-9_]+$/D',$table)){enc_reply(['error'=>'Encoder configuration unavailable.']);}
    $stmt=$global['mysqli']->prepare('SELECT id FROM '.$table.' WHERE user=? AND LOWER(siteURL) IN (?,?) ORDER BY id DESC');
    $username=(string)$dmEncoderActor['username'];$site='https://media.divinemedia.us/';$legacy='https://media.divinecreativegroup.com/';
    $stmt->bind_param('sss',$username,$site,$legacy);$stmt->execute();$ids=array_map('intval',array_column($stmt->get_result()->fetch_all(MYSQLI_ASSOC),'id'));$stmt->close();
    if($dmEncoderOp==='enqueue'&&!$ids){
        if(empty($dmEncoderActor['canUpload'])||empty($dmEncoderActor['credential'])){enc_reply(['error'=>'Encoding permission required.']);}
        // Respect the installed Encoder's streamer allowlist, including its retained legacy alias.
        $connectionSite=Streamer::isURLAllowed($site)?$site:(Streamer::isURLAllowed($legacy)?$legacy:'');
        if(!$connectionSite){enc_reply(['error'=>'The media platform is not allowed by this Encoder configuration.']);}
        $id=Streamer::createIfNotExists($username,(string)$dmEncoderActor['credential'],$connectionSite,true);
        if(!$id){enc_reply(['error'=>'Unable to create your native Encoder connection.']);}
        $ids=[(int)$id];
    }
    if($dmEncoderOp==='queue'){
        if(!$ids){enc_reply(['items'=>[]]);}
        $table=Encoder::getTableName();if(!preg_match('/^[a-zA-Z0-9_]+$/D',$table)){enc_reply(['error'=>'Encoder configuration unavailable.']);}
        // IDs are native, server-selected integers belonging to this username and our two aliases.
        $query='SELECT id FROM '.$table.' WHERE streamers_id IN ('.implode(',',$ids).') ORDER BY id DESC LIMIT 100';
        $rows=$global['mysqli']->query($query)->fetch_all(MYSQLI_ASSOC);$items=[];
        foreach($rows as $r){$e=new Encoder((int)$r['id']);$vars=json_decode((string)$e->getReturn_vars(),true);$format=new Format($e->getFormats_id());
            $items[]=['id'=>(int)$e->getId(),'title'=>mb_substr(strip_tags((string)$e->getTitle()),0,140),'status'=>(string)$e->getStatus(),'videoId'=>(int)($vars['videos_id']??0),'format'=>mb_substr(strip_tags((string)$format->getName()),0,100),'created'=>(string)$e->getCreated(),'canRetry'=>in_array($e->getStatus(),[Encoder::STATUS_ERROR,Encoder::STATUS_DONE],true),'canRemove'=>in_array($e->getStatus(),[Encoder::STATUS_QUEUE,Encoder::STATUS_ERROR,Encoder::STATUS_DONE],true)];
        }
        enc_reply(['items'=>$items,'source'=>'native-encoder']);
    }
    if(empty($dmEncoderActor['canUpload'])){enc_reply(['error'=>'Encoding permission required.']);}
    if(!$ids){enc_reply(['error'=>'Encoder job access denied.']);}
    $streamerId=$ids[0];$s=new Streamer($streamerId);
    _session_start();
    $_SESSION['login']=(object)['isLogged'=>true,'streamers_id'=>$streamerId,'streamer'=>$s->getSiteURL(),'canUpload'=>true,'isAdmin'=>(bool)$s->getIsAdmin(),'isStreamerAdmin'=>!empty($dmEncoderActor['isAdmin']),'allowedResolutions'=>$dmEncoderActor['allowedResolutions']??[]];
    if($dmEncoderOp==='enqueue'){
        $videoId=(int)($dmEncoderData['videoId']??0);$url=(string)($dmEncoderData['source']??'');$parts=parse_url($url);
        if($videoId<1||($parts['scheme']??'')!=='https'||($parts['host']??'')!=='media.divinemedia.us'||!str_starts_with($parts['path']??'','/videos/')||isset($parts['user'])||isset($parts['pass'])){enc_reply(['error'=>'Unsupported encoding source.']);}
        $profiles=['mp4'=>'inputAutoMP4','hls'=>'inputAutoHLS','audio'=>'inputAutoAudio','webm'=>'inputAutoWebm'];$profile=(string)($dmEncoderData['profile']??'mp4');
        if(!isset($profiles[$profile])){enc_reply(['error'=>'Unsupported encoding profile.']);}
        $_POST=$_REQUEST=[$profiles[$profile]=>'true'];
        $e=new Encoder(0);$e->setStreamers_id($streamerId);$e->setFileURI($url);$e->setVideoDownloadedLink($url);$e->setFilename('divine_'.bin2hex(random_bytes(10)));$e->setTitle(mb_substr(strip_tags((string)($dmEncoderData['title']??'Divine Media')),0,140));$e->setPriority($s->getPriority());$e->setFormats_idFromOrder(decideFormatOrder());if(!(int)$e->getFormats_id()){enc_reply(['error'=>'This output format is not configured.']);}$e->setReturn_vars(json_encode(['videos_id'=>$videoId]));
        $id=$e->save();if(!$id){enc_reply(['error'=>'Encoding job could not be queued.']);}
        // Existing Encoder workers retain control. Never dispatch the global queue during deployment or reads.
        enc_reply(['id'=>(int)$id,'message'=>'Encoding job queued.']);
    }
    $id=(int)($dmEncoderData['id']??0);$e=new Encoder($id);
    if(!$id||!$e->getId()||!in_array((int)$e->getStreamers_id(),$ids,true)){enc_reply(['error'=>'Encoder job access denied.']);}
    if($dmEncoderOp==='retry'){
        if(!in_array($e->getStatus(),[Encoder::STATUS_ERROR,Encoder::STATUS_DONE],true)){enc_reply(['error'=>'This job cannot be retried while active.']);}
        $e->setStatus(Encoder::STATUS_QUEUE);if(!$e->save()){enc_reply(['error'=>'Job could not be queued.']);}enc_reply(['message'=>'Job queued for retry.']);
    }
    if($dmEncoderOp==='remove'){
        if(!in_array($e->getStatus(),[Encoder::STATUS_QUEUE,Encoder::STATUS_ERROR,Encoder::STATUS_DONE],true)){enc_reply(['error'=>'Wait until this job is no longer active.']);}
        if(!$e->delete()){enc_reply(['error'=>'Job could not be removed.']);}enc_reply(['message'=>'Job removed. Original media remains in your library.']);
    }
    enc_reply(['error'=>'Unsupported encoder action.']);
}catch(Throwable $e){enc_reply(['error'=>'Encoder service unavailable.']);}
