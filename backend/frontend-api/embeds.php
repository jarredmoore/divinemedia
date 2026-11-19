<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
dm_require_user();
if(!User::canUpload()||!AVideoPlugin::loadPluginIfEnabled('BulkEmbed')||!BulkEmbed::canBulkEmbed()){dm_error('Your account does not have permission to add external videos. Ask an administrator to review BulkEmbed permissions.',403);}
require_once __DIR__.'/youtube.php';
function dm_existing_embed(string $providerId): int {
    global $global;$owner=(int)User::getId();$pattern='%'.$providerId.'%';
    $statement=$global['mysqli']->prepare("SELECT id,videoLink FROM videos WHERE users_id=? AND type='embed' AND videoLink LIKE ? LIMIT 100");$statement->bind_param('is',$owner,$pattern);$statement->execute();$rows=$statement->get_result();
    while($row=$rows->fetch_assoc()){$source=DivineYouTube::source($row['videoLink']);if(($source['kind']??'')==='video'&&$source['id']===$providerId){$statement->close();return (int)$row['id'];}}$statement->close();return 0;
}
$now=time();$_SESSION['dm_embed_previews']=$_SESSION['dm_embed_previews']??[];
foreach($_SESSION['dm_embed_previews']as $key=>$record){if(($record['expires']??0)<$now){unset($_SESSION['dm_embed_previews'][$key]);}}
if($action==='embed-preview'){
    enforceRateLimit('divine_youtube_preview_'.User::getId(),12,60);
    $continuation=(string)($body['continuation']??'');$page='';
    if($continuation!==''){
        $previous=$_SESSION['dm_embed_previews'][$continuation]??null;if(!$previous||empty($previous['next'])||$previous['owner']!==(int)User::getId()){dm_error('This channel preview expired. Preview the channel again.',410);}$source=$previous['source'];$page=$previous['next'];
    }else{$source=DivineYouTube::source((string)($body['url']??''));if(!$source){dm_error('Enter a YouTube video link, @handle URL, or channel URL.');}}
    try{$preview=(new DivineYouTube())->preview($source,BulkEmbed::getAPIKey(),$page);}catch(RuntimeException $e){
        $messages=['youtube_channel_not_found'=>'This YouTube channel could not be found.','youtube_video_unavailable'=>'This video is unavailable for embedding. Check its privacy and embedding settings on YouTube.','youtube_quota'=>'YouTube API quota is exhausted. Try the first page for recent public uploads, or try again after the quota resets.'];
        dm_error($messages[$e->getMessage()]??'YouTube could not provide this preview. Try again, or paste a direct video link.',502);
    }
    while(count($_SESSION['dm_embed_previews'])>=12){array_shift($_SESSION['dm_embed_previews']);}
    $ticket=bin2hex(random_bytes(24));$items=[];$response=[];
    foreach($preview['items']as $item){$item['title']=dm_text($item['title'],140);$item['description']=dm_text($item['description'],10000);$items[$item['id']]=$item;$response[]=array_merge($item,['existingId'=>dm_existing_embed($item['id']),'ticket'=>$ticket]);}
    $_SESSION['dm_embed_previews'][$ticket]=['owner'=>(int)User::getId(),'expires'=>$now+1800,'source'=>$source,'next'=>$preview['next'],'items'=>$items];
    dm_reply(['channel'=>$preview['channel'],'items'=>$response,'mode'=>$preview['mode'],'notice'=>$preview['notice'],'continuation'=>$preview['next']?$ticket:null]);
}
if($action==='embed-add'){
    $record=$_SESSION['dm_embed_previews'][(string)($body['ticket']??'')]??null;$id=(string)($body['id']??'');
    if(!$record||$record['owner']!==(int)User::getId()||empty($record['items'][$id])){dm_error('This selection expired. Preview the channel again.',410);}
    $lock='divine_embed_'.(int)User::getId();$stmt=$global['mysqli']->prepare('SELECT GET_LOCK(?,0)');$stmt->bind_param('s',$lock);$stmt->execute();$locked=(int)$stmt->get_result()->fetch_row()[0];$stmt->close();if(!$locked){dm_error('Another embed is being added. Try again shortly.',409);}
    try{
        $existing=dm_existing_embed($id);
        if($existing){$reply=['id'=>$existing,'duplicate'=>true,'message'=>'Already in your video library.'];}
        else{
            // Revalidate availability without the Data API, then use AVideo's installed save handler.
            try{(new DivineYouTube())->single($id);}catch(RuntimeException $e){dm_error('This video is no longer available for embedding.',422);}
            $item=$record['items'][$id];$result=dm_native('plugin/BulkEmbed/save.json.php',['itemsToSave'=>[$item]],false,true);
            $saved=dm_existing_embed($id);
            if(!$saved){dm_error('The platform could not confirm this embed. Check your library before retrying.',502);}
            $reply=['id'=>$saved,'duplicate'=>false,'message'=>'Video added to your Divine Media channel.'];
        }
    }finally{$stmt=$global['mysqli']->prepare('SELECT RELEASE_LOCK(?)');$stmt->bind_param('s',$lock);$stmt->execute();$stmt->close();}
    dm_reply($reply);
}
