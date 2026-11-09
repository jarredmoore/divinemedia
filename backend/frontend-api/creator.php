<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
if($action==='encoder-queue'){dm_reply(dm_encoder('queue'));}
if($action==='encoder-action'){
    if(!User::canUpload()){dm_error('Encoding permission required.',403);}
    $op=(string)($body['operation']??'');
    if($op==='enqueue'){
        $id=dm_id($body['video']??0);if(!Video::canEdit($id)){dm_error('Video access denied.',403);}
        $video=new Video('','',$id);$source=Video::getFirstSource($video->getFilename());$url=dm_media_url($source['url']??$source['src']??null);
        if(!$url){dm_error('This title has no supported source to encode.');}
        dm_reply(dm_encoder('enqueue',['videoId'=>$id,'source'=>$url,'title'=>$video->getTitle(),'profile'=>(string)($body['profile']??'mp4')]));
    }
    if(!in_array($op,['retry','remove'],true)){dm_error('Unsupported encoding action.');}
    dm_reply(dm_encoder($op,['id'=>dm_id($body['id']??0)]));
}
if($action==='creator-video'){
    $id=dm_id($body['id']??0);
    if(!Video::canEdit($id)){dm_error('Video access denied.',403);}
    $v=new Video('','',$id);
    $title=dm_text($body['title']??'',140);if($title===''){dm_error('Enter a title.');}
    $visibility=(string)($body['visibility']??'');$states=['public'=>Video::STATUS_ACTIVE,'unlisted'=>Video::STATUS_UNLISTED,'private'=>Video::STATUS_INACTIVE];
    if(!isset($states[$visibility])){dm_error('Invalid visibility.');}
    $v->setTitle($title);$v->setDescription(dm_text($body['description']??'',10000));if($v->setStatus($states[$visibility])===false){dm_error('Your account cannot change this publishing status.',403);}
    if(!$v->save()){dm_error('Video changes could not be saved.');}
    dm_reply(['message'=>'Video updated.']);
}
if(in_array($action,['upload-init','upload-chunk','upload-cancel'],true)){
    if(!User::canUpload()){dm_error('Upload permission required.',403);}
    $base='/var/www/tmp/divine-frontend-uploads';
    if(!is_dir($base)&&!mkdir($base,0700,true)){dm_error('Upload storage unavailable.',503);}
    $_SESSION['dm_uploads']=$_SESSION['dm_uploads']??[];
    foreach($_SESSION['dm_uploads'] as $ticket=>$upload){
        if(($upload['expires']??0)<time()&&preg_match('/^[a-f0-9]{64}$/D',(string)$ticket)){@unlink($base.'/'.$ticket.'.part');unset($_SESSION['dm_uploads'][$ticket]);}
    }
    if($action==='upload-init'){
        $name=basename(dm_text($body['name']??'',180));$extension=strtolower(pathinfo($name,PATHINFO_EXTENSION));$size=filter_var($body['size']??0,FILTER_VALIDATE_INT);
        if(!in_array($extension,['mp4','m4v','mov','webm','mkv','avi','mp3','m4a','ogg','wav','flac'],true)||!in_array($extension,Video::$types,true)){dm_error('This media format is not supported.');}
        if(!$size||$size<1||$size>4*1024*1024*1024){dm_error('Choose a file smaller than 4 GB.');}
        if(count($_SESSION['dm_uploads'])>=2){dm_error('Finish an existing upload before starting another.',429);}
        if(disk_free_space($base)<$size*2+2*1024*1024*1024){dm_error('Insufficient upload capacity. Please try later.',503);}
        $ticket=bin2hex(random_bytes(32));
        $_SESSION['dm_uploads'][$ticket]=['name'=>preg_replace('/[^A-Za-z0-9._-]/','_',$name),'size'=>$size,'title'=>dm_text($body['title']??'',140),'received'=>0,'expires'=>time()+7200,'user'=>(int)User::getId(),'state'=>'uploading'];
        dm_reply(['ticket'=>$ticket,'chunkBytes'=>1024*1024]);
    }
    $ticket=(string)($body['ticket']??'');
    if(!preg_match('/^[a-f0-9]{64}$/D',$ticket)||empty($_SESSION['dm_uploads'][$ticket])){dm_error('Upload session expired.',410);}
    $upload=&$_SESSION['dm_uploads'][$ticket];
    if($upload['user']!==(int)User::getId()||$upload['expires']<time()){dm_error('Upload access denied.',403);}
    if($upload['state']!=='uploading'){dm_error('This upload is already being processed.',409);}
    if($action==='upload-cancel'){
        @unlink($base.'/'.$ticket.'.part');unset($_SESSION['dm_uploads'][$ticket]);
        dm_reply(['message'=>'Upload canceled.']);
    }
    $start=filter_var($body['start']??null,FILTER_VALIDATE_INT);$total=filter_var($body['total']??0,FILTER_VALIDATE_INT);
    $file=$_FILES['file']??null;
    if($start!==$upload['received']||$total!==$upload['size']||!is_array($file)||$file['error']!==UPLOAD_ERR_OK||$file['size']<1||$file['size']>1024*1024||!is_uploaded_file($file['tmp_name'])||$start+$file['size']>$total){dm_error('Invalid upload chunk.',409);}
    $path=$base.'/'.$ticket.'.part';$out=fopen($path,'c+b');if(!$out||!flock($out,LOCK_EX)){dm_error('Upload storage is busy.',503);}
    fseek($out,0,SEEK_END);if(ftell($out)!==$start){fclose($out);dm_error('Upload position changed.',409);}
    $in=fopen($file['tmp_name'],'rb');$written=stream_copy_to_stream($in,$out);fclose($in);fflush($out);flock($out,LOCK_UN);fclose($out);
    if($written!==$file['size']){dm_error('Upload chunk could not be saved.',503);}
    $upload['received']+=$written;
    if($upload['received']<$total){dm_reply(['received'=>$upload['received'],'complete'=>false]);}
    $upload['state']='processing';$name=$upload['name'];$title=$upload['title'];
    unset($_SESSION['dm_uploads'][$ticket]);
    // Reuse the installed uploader and its normal hooks. Never accept an existing video ID.
    $_GET=$_REQUEST=[];$_POST=['title'=>$title];$_FILES=['upl'=>['name'=>$name,'type'=>mime_content_type($path),'tmp_name'=>$path,'error'=>0,'size'=>$total]];
    _session_write_close();ignore_user_abort(true);
    $GLOBALS['dm_sent']=true;
    register_shutdown_function(function() use($path){
        $raw=ob_get_contents();$result=json_decode((string)$raw,true);
        if(is_file($path)){@unlink($path);}
        if(!is_array($result)||!empty($result['error'])){dm_reply(['error'=>'Upload processing failed. Check your library before retrying.'],502);}
        dm_reply(['complete'=>true,'videoId'=>(int)($result['videos_id']??0),'message'=>'Upload received.']);
    });
    chdir($root.'view/mini-upload-form');
    require $root.'view/mini-upload-form/upload.php';
    exit;
}
