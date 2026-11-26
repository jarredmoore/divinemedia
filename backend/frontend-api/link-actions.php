<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
dm_require_user();if(!User::canUpload()){dm_error('Upload permission is required to import media.',403);}
require_once __DIR__.'/import-source.php';
require_once __DIR__.'/import-hold.php';
_session_start();$_SESSION['dm_link_previews']=$_SESSION['dm_link_previews']??[];
foreach($_SESSION['dm_link_previews']as $key=>$value){if(($value['expires']??0)<time())unset($_SESSION['dm_link_previews'][$key]);}
if($action==='link-preview'){
    enforceRateLimit('divine_link_preview_'.User::getId(),5,60);
    try{$url=DivineImportSource::url((string)($body['url']??''));}catch(InvalidArgumentException $e){dm_error($e->getMessage());}
    $owner=(int)User::getId();$preview=dm_encoder('import-preview',['url'=>$url]);_session_start();
    if(!is_array($preview['item']??null)||($preview['item']['url']??'')!==$url)dm_error('The provider preview could not be verified.',502);
    while(count($_SESSION['dm_link_previews'])>=8)array_shift($_SESSION['dm_link_previews']);
    $ticket=bin2hex(random_bytes(24));$_SESSION['dm_link_previews'][$ticket]=['owner'=>$owner,'expires'=>time()+1200,'item'=>$preview['item']];
    dm_reply(['ticket'=>$ticket,'item'=>$preview['item'],'profiles'=>$preview['profiles']??[]]);
}
if($action==='link-import'){
    enforceRateLimit('divine_link_import_'.User::getId(),3,60);
    $ticket=(string)($body['ticket']??'');$preview=$_SESSION['dm_link_previews'][$ticket]??null;
    if(!preg_match('/^[a-f0-9]{48}$/D',$ticket)||!$preview||$preview['owner']!==(int)User::getId())dm_error('Preview this link again before importing.',410);
    if(!empty($preview['jobId']))dm_reply(['id'=>$preview['jobId'],'videoId'=>$preview['videoId'],'duplicate'=>true,'message'=>'This import is already queued.']);
    require_once __DIR__.'/creator-details.php';
    $profile=(string)($body['profile']??'mp4');if(!in_array($profile,['mp4','hls','audio','webm'],true))dm_error('Choose a supported output format.');
    $details=dm_creator_validate(['title'=>$body['title']??$preview['item']['title'],'description'=>$body['description']??$preview['item']['description'],'visibility'=>'private','categoryId'=>$body['categoryId']??null,'canShare'=>false,'canDownload'=>false]);
    // Hold a creator-owned draft before queuing. Retry reuses this ID; no arbitrary catalog IDs are accepted.
    $id=(int)($preview['videoId']??0);
    if(!$id){$video=new Video();$video->setFilename('divine_import_'.$ticket);$video->setUsers_id(User::getId());$video->setType($profile==='audio'?'audio':'video');dm_creator_apply($video,$details);$id=(int)$video->getId();if(!$id)dm_error('The private draft could not be created.',502);$_SESSION['dm_link_previews'][$ticket]['videoId']=$id;}
    elseif(!Video::canEdit($id))dm_error('Draft access denied.',403);
    $video=new Video('','',$id);DivineImportHold::hold($video,$ticket);
    $result=dm_encoder('import',['url'=>$preview['item']['url'],'title'=>$details['title'],'profile'=>$profile,'videoId'=>$id,'ticket'=>$ticket]);_session_start();
    DivineImportHold::hold($video,$ticket,(int)$result['id']);$_SESSION['dm_link_previews'][$ticket]['jobId']=(int)$result['id'];dm_reply($result+['message'=>'Import queued into your private draft.']);
}
