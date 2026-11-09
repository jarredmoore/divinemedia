<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
function dm_text($value, int $limit = 200): string { return mb_substr(trim(strip_tags(is_scalar($value)?(string)$value:'')),0,$limit); }
function dm_id($value): int { $id=filter_var($value,FILTER_VALIDATE_INT,['options'=>['min_range'=>1,'max_range'=>2147483647]]); if(!$id){dm_error('Invalid item identifier.');} return $id; }
function dm_require_user(): int { if(!User::isLogged()){dm_error('Sign in to continue.',401);} return (int)User::getId(); }
function dm_user(): ?array {
    if(!User::isLogged()){return null;}
    $row=User::getUserFromID(User::getId());
    return ['id'=>(int)User::getId(),'username'=>dm_text($row['user']??'',100),'name'=>dm_text($row['name']??$row['user']??'',100),
        'permissions'=>['upload'=>(bool)User::canUpload(),'stream'=>(bool)User::canStream(),'comment'=>(bool)User::canComment()]];
}
function dm_native(string $path, array $data=[], bool $binary=false, bool $allowError=false): array {
    // Paths are hard-coded adapter calls, never supplied by the browser.
    $data['globalToken']=getToken(120);$data['do_not_login']=1;
    $cookie=session_name().'='.session_id();
    _session_write_close();
    $c=curl_init('https://media.divinemedia.us/'.$path);
    curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_RESOLVE=>['media.divinemedia.us:443:127.0.0.1'],
        CURLOPT_FOLLOWLOCATION=>false,CURLOPT_CONNECTTIMEOUT=>3,CURLOPT_TIMEOUT=>20,CURLOPT_COOKIE=>$cookie,
        CURLOPT_HTTPHEADER=>['Accept: '.($binary?'image/png':'application/json'),'Origin: https://media.divinemedia.us','Referer: https://media.divinemedia.us/','X-Requested-With: XMLHttpRequest'],
        CURLOPT_USERAGENT=>$_SERVER['HTTP_USER_AGENT']??'Divine Media']);
    if($data!==[]&&!$binary){curl_setopt($c,CURLOPT_POST,true);curl_setopt($c,CURLOPT_POSTFIELDS,http_build_query($data));}
    $raw=curl_exec($c);$status=curl_getinfo($c,CURLINFO_RESPONSE_CODE);$type=curl_getinfo($c,CURLINFO_CONTENT_TYPE);curl_close($c);
    if($raw===false||$status>=400){dm_error('The platform rejected this action.', $status===403?403:502);}
    if($binary){if(!in_array(explode(';',(string)$type)[0],['image/png','image/jpeg','image/gif'],true)||strlen($raw)>150000){dm_error('Verification image unavailable.',502);}return ['image'=>'data:'.explode(';',$type)[0].';base64,'.base64_encode($raw)];}
    $result=json_decode($raw,true);
    if(!is_array($result)){dm_error('The native service returned an unexpected response.',502);}
    if(!empty($result['error'])&&!$allowError){dm_error('The platform rejected this action. Check your permissions and verification.');}
    return $result;
}
function dm_video(int $id): array {
    $row=Video::getVideo($id,Video::canEdit($id)?'':Video::SORT_TYPE_VIEWABLE,false,false,false,true);
    if(empty($row['id'])){dm_error('This title is unavailable.',404);}
    if(!User::canWatchVideoWithAds($id,null,true)){dm_error('This title is unavailable for your account.',403);}
    $cu=AVideoPlugin::loadPluginIfEnabled('CustomizeUser');
    if($cu&&!CustomizeUser::videoPasswordIsGood($id)){dm_reply(['error'=>'Video password required.','code'=>'video_password_required'],403);}
    forbiddenPageIfCannotWatchVideo($id);
    return $row;
}
function dm_media_url($value): ?string {
    if(!is_string($value)||$value===''){return null;}
    $value=str_replace('https://media.divinecreativegroup.com/','https://media.divinemedia.us/',$value);
    if(str_starts_with($value,'/')){$value='https://media.divinemedia.us'.$value;}
    $p=parse_url($value);
    return ($p['scheme']??'')==='https'&&($p['host']??'')==='media.divinemedia.us'&&empty($p['user'])&&empty($p['pass'])?$value:null;
}
function dm_item(array $row): array {
    $id=(int)($row['videos_id']??$row['id']??0);
    static $users=[];$uid=(int)($row['users_id']??0);
    if(!isset($users[$uid])){$users[$uid]=$uid?User::getUserFromID($uid):[];}
    $user=$users[$uid];
    $audio=($row['type']??'')==='audio';
    $allowed=User::canWatchVideoWithAds($id,null,true);
    $cu=AVideoPlugin::loadPluginIfEnabled('CustomizeUser');if($cu&&!CustomizeUser::videoPasswordIsGood($id)){$allowed=false;}
    $source=$allowed?Video::getFirstSource($row['filename']??''):[];
    $url=dm_media_url($source['url']??$source['src']??null);
    return ['id'=>$id,'avideoId'=>$id,'title'=>dm_text($row['title']??'',140),'description'=>dm_text($row['description']??'',10000),
        'userId'=>(int)($row['users_id']??0),'creator'=>dm_text($user['channelName']??$user['name']??$user['user']??'Creator',100),'channel'=>dm_text($user['channelName']??$user['user']??'',100),
        'categoryId'=>(int)($row['categories_id']??0),'image'=>dm_media_url(Video::getPoster($id)),'img'=>dm_media_url(Video::getPoster($id))??'/placeholder.svg',
        'type'=>$audio?'Listen':'Watch','tag'=>dm_text($row['category']??($audio?'AUDIO':'VIDEO'),100),'duration'=>dm_text($row['duration']??'',30),
        'videoUrl'=>$audio?null:$url,'audioUrl'=>$audio?$url:null,'watchUrl'=>'https://divinemedia.us/watch/'.$id];
}
function dm_playlist(int $id): PlayList {
    require_once $GLOBALS['global']['systemRootPath'].'objects/playlist.php'; AVideoPlugin::loadPlugin('PlayLists');
    $p=new PlayList($id);
    if(!$p->getId()||!PlayLists::canManagePlaylist($id)){dm_error('Playlist access denied.',403);}
    return $p;
}
function dm_playlist_items(int $id): array {
    require_once $GLOBALS['global']['systemRootPath'].'objects/playlist.php';
    if(!PlayList::canSee($id,User::getId())){dm_error('Playlist access denied.',403);}
    $out=[];foreach(array_slice(PlayList::getVideosFromPlaylist($id,false),0,100) as $row){
        $video=Video::getVideo((int)($row['videos_id']??$row['id']),Video::SORT_TYPE_VIEWABLE,false,false,false,true);
        if(!empty($video['id'])){$out[]=dm_item($video);}
    }return $out;
}
function dm_encoder(string $op, array $data=[]): array {
    dm_require_user();
    $actor=['userId'=>(int)User::getId(),'username'=>(string)User::getUserName(),'canUpload'=>(bool)User::canUpload(),'isAdmin'=>(bool)User::isAdmin()];
    if($op==='enqueue'){$actor['credential']=(string)User::getUserPass();$actor['allowedResolutions']=UserGroups::getAllowedResolutionsForUser(User::getId());}
    _session_write_close();
    $pipes=[];$process=proc_open(['/usr/bin/php',__DIR__.'/encoder-worker.php'],[0=>['pipe','r'],1=>['pipe','w'],2=>['file','/dev/null','a']],$pipes);
    if(!is_resource($process)){dm_error('Encoder service unavailable.',503);}
    fwrite($pipes[0],json_encode(['actor'=>$actor,'op'=>$op,'data'=>$data]));fclose($pipes[0]);unset($actor);
    stream_set_timeout($pipes[1],20);$output=stream_get_contents($pipes[1],1024*1024);$meta=stream_get_meta_data($pipes[1]);fclose($pipes[1]);if(!empty($meta['timed_out'])){proc_terminate($process);}proc_close($process);
    $result=json_decode((string)$output,true);if(!is_array($result)){dm_error('Encoder service unavailable.',502);}if(!empty($result['error'])){dm_error(dm_text($result['error'],180),403);}
    return $result;
}
