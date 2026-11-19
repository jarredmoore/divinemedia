<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
require_once __DIR__.'/creator-fields.php';
function dm_creator_options(): array {
    global $advancedCustom,$advancedCustomUser;require_once $GLOBALS['global']['systemRootPath'].'objects/category.php';
    $groups=[];if(AVideoPlugin::loadPluginIfEnabled('VideoTags')&&VideoTags::canCreateTag()){
        foreach(TagsTypes::getAll()as $type){if(in_array(mb_strtolower(trim($type['name'])),['tags','keywords','genre','artist','album','topic','topics','mood','people','location','client','project'],true)){$groups[]=['id'=>(int)$type['id'],'name'=>dm_text($type['name'],80)];}}
    }
    $all=Category::getAllCategories(false,false,false,true,true,false);$categories=[];foreach($all as $row){$categories[]=['id'=>(int)$row['id'],'name'=>dm_text($row['name'],140),'parentId'=>(int)($row['parentId']??0)];}
    $formats=['video'=>['mp4','webm'],'audio'=>['mp3','ogg'],'image'=>['jpg','jpeg','png','gif','webp'],'document'=>['pdf']];
    foreach($formats as $kind=>$extensions){$formats[$kind]=array_values(array_filter($extensions,static function($ext)use($kind,$advancedCustom){$flag=match($kind){'image'=>'disableImageUpload','document'=>'disablePDFUpload',default=>'disable'.strtoupper($ext).'Upload'};return in_array($ext,Video::$types,true)&&empty($advancedCustom->$flag);}));}
    return ['formats'=>$formats,'maxMediaBytes'=>DivineCreatorFields::MAX_MEDIA,'limits'=>['video'=>4294967296,'audio'=>1073741824,'image'=>20971520,'document'=>104857600],'maxThumbnailBytes'=>DivineCreatorFields::MAX_IMAGE,'thumbnailFormats'=>['jpg','jpeg','png','webp'],'categories'=>$categories,'canChangeCategory'=>User::isAdmin()||empty($advancedCustomUser->userCanNotChangeCategory),'tagGroups'=>$groups,'ratings'=>Video::$rratingOptions];
}
function dm_creator_validate(array $body): array {
    try{$data=DivineCreatorFields::normalize($body);}catch(InvalidArgumentException $e){dm_error($e->getMessage());}
    $options=dm_creator_options();if(isset($data['categoryId'])&&(!$options['canChangeCategory']||!in_array($data['categoryId'],array_column($options['categories'],'id'),true))){dm_error('This category is not available for your account.',403);}
    foreach(array_keys($data['tags']??[])as $id){if(!in_array((int)$id,array_column($options['tagGroups'],'id'),true)){dm_error('This tag group is not available for your account.',403);}}return $data;
}
function dm_creator_apply(Video $v,array $data,bool $hold=false): void {
    if(!Video::canEdit($v->getId())){throw new RuntimeException('Video access denied.');}
    $v->setTitle($data['title']);$v->setDescription($data['description']);if(isset($data['categoryId'])){$v->setCategories_id($data['categoryId']);}
    if(isset($data['canShare'])){$v->setCan_share($data['canShare']);}if(isset($data['canDownload'])){$v->setCan_download($data['canDownload']);}if(isset($data['rating'])){$v->setRrating($data['rating']);}
    $statuses=['private'=>Video::STATUS_INACTIVE,'public'=>Video::STATUS_ACTIVE,'unlisted'=>Video::STATUS_UNLISTED];if($v->setStatus($hold?Video::STATUS_INACTIVE:$statuses[$data['visibility']])===false){throw new RuntimeException('Publishing permission denied.');}if(!$v->save()){throw new RuntimeException('Video could not be saved.');}
    if(isset($data['tags'])&&AVideoPlugin::loadPluginIfEnabled('VideoTags')){
        // Preserve native/system tag groups, including monetization and permission tags.
        $tags=[];foreach(TagsTypes::getAll()as $type){$id=(int)$type['id'];$tags[]=['id'=>$id,'items'=>$data['tags'][$id]??VideoTags::getArrayFromVideosId($v->getId(),$id)];}VideoTags::saveTags($tags,$v->getId());
    }
}
function dm_creator_record(int $id): array {
    if(!Video::canEdit($id)){dm_error('Video access denied.',403);}$v=new Video('','',$id);$row=Video::getVideo($id,'',false,false,false,true);$item=dm_item($row);$tags=[];foreach(dm_creator_options()['tagGroups']as $g){$tags[(string)$g['id']]=VideoTags::getArrayFromVideosId($id,$g['id']);}
    return $item+['visibility'=>match($v->getStatus()){Video::STATUS_ACTIVE=>'public',Video::STATUS_UNLISTED=>'unlisted',default=>'private'},'status'=>$v->getStatus(),'tags'=>(object)$tags,'canShare'=>(bool)$v->getCan_share(),'canDownload'=>(bool)$v->getCan_download(),'rating'=>(string)$v->getRrating()];
}
if($action==='creator-options'){dm_require_user();dm_reply(dm_creator_options());}
if($action==='creator-record'){dm_require_user();dm_reply(['item'=>dm_creator_record(dm_id($query['id']??0))]);}
if($action==='creator-thumbnail'){
    dm_require_user();$id=dm_id($body['id']??0);if(!Video::canEdit($id)){dm_error('Video access denied.',403);}$kind=(string)($body['kind']??'landscape');if(!in_array($kind,['landscape','portrait'],true)){dm_error('Choose a valid thumbnail type.');}
    $file=$_FILES['file_data']??null;if(!$file||$file['error']!==UPLOAD_ERR_OK||!is_uploaded_file($file['tmp_name'])){dm_error('Choose a thumbnail image.');}
    try{$info=DivineCreatorFields::imageInfo((string)file_get_contents($file['tmp_name']));}catch(InvalidArgumentException $e){dm_error($e->getMessage());}
    // Normalize accepted images to the native JPEG poster contract, stripping embedded metadata.
    $image=@imagecreatefromstring((string)file_get_contents($file['tmp_name']));if(!$image){dm_error('This image could not be decoded.');}$flat=imagecreatetruecolor($info[0],$info[1]);imagefill($flat,0,0,imagecolorallocate($flat,0,0,0));imagecopy($flat,$image,0,0,0,0,$info[0],$info[1]);imagedestroy($image);
    if(!imagejpeg($flat,$file['tmp_name'],88)){imagedestroy($flat);dm_error('This thumbnail could not be prepared.');}imagedestroy($flat);
    $_GET=['video_id'=>$id,'type'=>$kind==='portrait'?'pjpg':'jpg'];$_POST=[];$_REQUEST=$_GET;$_FILES=['file_data'=>['name'=>'thumbnail.jpg','type'=>'image/jpeg','tmp_name'=>$file['tmp_name'],'size'=>filesize($file['tmp_name']),'error'=>0]];
    $GLOBALS['dm_sent']=true;register_shutdown_function(function()use($id){if(!ob_get_level()){return;}$data=json_decode((string)ob_get_contents(),true);if(!is_array($data)||!empty($data['error'])||empty($data['videos_id'])){dm_reply(['error'=>'Thumbnail could not be saved. Your media is still in your library.'],502);}dm_reply(['message'=>'Thumbnail updated.','item'=>dm_creator_record($id)]);});
    chdir($root.'objects');require $root.'objects/uploadPoster.php';exit;
}
