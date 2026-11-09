<?php
if($action==='reaction'){
    $id=dm_id($body['video']??0);dm_video($id);$value=(int)($body['value']??0);
    if(!in_array($value,[-1,0,1],true)){dm_error('Invalid reaction.');}
    require_once $root.'objects/like.php';new Like($value,$id);$likes=Video::getVideoLikes($id,true);
    dm_reply(['likes'=>(int)$likes->likes,'dislikes'=>(int)$likes->dislikes,'reaction'=>(int)$likes->myVote]);
}
if($action==='comment'){
    require_once $root.'objects/comment.php';
    if(!User::canComment()){dm_error('Commenting is not available for this account.',403);}
    if(!empty($body['remove'])){
        $id=dm_id($body['id']??0);if(!Comment::userCanEditComment($id)){dm_error('Comment access denied.',403);}
        $row=Comment::getComment($id);dm_video((int)$row['videos_id']);$c=new Comment('',0,$id);
        if(!$c->delete()){dm_error('Comment could not be removed.');}dm_reply(['message'=>'Comment removed.']);
    }
    $video=dm_id($body['video']??0);dm_video($video);$text=dm_text($body['text']??'',4000);if($text===''){dm_error('Enter your comment.');}
    $result=dm_native('objects/commentAddNew.json.php',['video'=>$video,'comment'=>$text,'comments_id'=>0]);
    if(empty($result['comments_id'])){dm_error('The comment could not be saved.');}dm_reply(['id'=>(int)$result['comments_id'],'message'=>'Comment submitted.']);
}
if(in_array($action,['playlist','playlist-item','library'],true)){
    require_once $root.'objects/playlist.php';AVideoPlugin::loadPlugin('PlayLists');
    if($action==='playlist'){
        $id=empty($body['id'])?0:dm_id($body['id']);$p=$id?dm_playlist($id):new PlayList(0);
        if(!empty($body['remove'])){if(!$id||!$p->delete()){dm_error('Playlist could not be deleted.');}dm_reply(['message'=>'Playlist deleted.']);}
        $name=dm_text($body['name']??'',100);$status=(string)($body['status']??'private');
        if($name===''||!in_array($status,['private','public','unlisted'],true)){dm_error('Enter a playlist name and visibility.');}
        $p->setName($name);$p->setStatus($status);$p->setUsers_id(User::getId());$id=$p->save();
        if(!$id){dm_error('Playlist could not be saved.');}dm_reply(['id'=>(int)$id,'message'=>'Playlist saved.']);
    }
    $video=dm_id($body['video']??0);dm_video($video);
    if($action==='library'){
        $id=($body['kind']??'')==='favorites'?PlayList::getFavoriteIdFromUser(User::getId()):PlayList::getWatchLaterIdFromUser(User::getId());
        $special=PlayList::getUserSpecialPlaylist(User::getId(),($body['kind']??'')==='favorites'?'favorite':'watch_later');
        $p=dm_playlist((int)($special['id']??$id));$add=!array_key_exists('add',$body)||$body['add']===true;
    }else{$p=dm_playlist(dm_id($body['playlist']??0));$add=($body['add']??false)===true;}
    if(!$p->addVideo($video,$add)){dm_error('Playlist could not be updated.');}dm_reply(['message'=>'Playlist updated.']);
}
if($action==='profile'){
    $u=new User(User::getId());$name=dm_text($body['name']??'',100);if($name===''){dm_error('Enter your display name.');}
    $u->setName($name);if(!$u->save()){dm_error('Profile could not be saved.');}
    dm_reply(['message'=>'Profile saved.']);
}
if($action==='studio-save'){
    if(!User::canStream()){dm_error('Streaming permission required.',403);}
    AVideoPlugin::loadPluginIfEnabled('Live');require_once $root.'plugin/Live/Objects/LiveTransmition.php';
    $title=dm_text($body['title']??'',140);if($title===''){dm_error('Enter a broadcast title.');}
    $row=LiveTransmition::createTransmitionIfNeed(User::getId());$live=new LiveTransmition($row['id']);
    $live->setTitle($title);$live->setPublic(($body['visibility']??'')==='public'?1:0);
    if(!$live->save()){dm_error('Broadcast settings could not be saved.');}dm_reply(['message'=>'Broadcast settings saved.']);
}
if(in_array($action,['upload-init','upload-chunk','creator-video'],true)){require __DIR__.'/creator.php';}
if($action==='notification-read'){require __DIR__.'/notifications.php';}

if($action==='follow'){
    $target=dm_id($body['userId']??0);
    if($target===(int)User::getId()){dm_error('You cannot follow your own channel.');}
    $u=User::getUserFromID($target);if(empty($u)||($u['status']??'')!=='a'){dm_error('Channel unavailable.',404);}
    $result=dm_native('objects/subscribe.json.php',['user_id'=>$target]);
    dm_reply(['following'=>($result['subscribe']??'')==='a','message'=>'Channel follow updated.']);
}
if($action==='playlist-order'){
    require_once $root.'objects/playlist.php';
    $p=dm_playlist(dm_id($body['playlist']??0));$ids=$body['ids']??null;
    if(!is_array($ids)||!$ids||count($ids)>100){dm_error('Invalid playlist order.');}
    $ids=array_map('dm_id',$ids);$existing=array_map('intval',PlayList::getVideosIdFromPlaylist($p->getId()));$sorted=$ids;sort($sorted);sort($existing);
    if($sorted!==$existing){dm_error('The playlist changed. Refresh before reordering.',409);}
    dm_native('objects/playlistSort.php',['playlist_id'=>$p->getId(),'list'=>$ids]);
    dm_reply(['message'=>'Playlist order saved.']);
}
