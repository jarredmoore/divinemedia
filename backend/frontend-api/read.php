<?php
if ($method === 'GET') {
    if ($action === 'captcha') { dm_reply(dm_native('objects/getCaptcha.php',[],true)); }
    if (in_array($action,['categories','channels','channel','catalog','creator-videos'],true)) {
        require_once $root.'objects/category.php';
        $_REQUEST['rowCount']=100; $_REQUEST['current']=max(1,min(100,(int)($query['page']??1)));
        if($action==='categories'){
            $rows=Category::getAllCategories(false,false,false,true,true,false);
            dm_reply(['items'=>array_map(fn($r)=>['id'=>(int)$r['id'],'name'=>dm_text($r['name'],100),'parentId'=>(int)($r['parentId']??0)],array_values($rows))]);
        }
        $own=$action==='creator-videos'; if($own){dm_require_user();}
        $rows=Video::getAllVideos($own?'':Video::SORT_TYPE_VIEWABLE,$own);
        $out=[];$channels=[];
        foreach(array_slice(is_array($rows)?$rows:[],0,100) as $row){
            if($own && (int)$row['users_id'] !== (int)User::getId()){continue;}
            $item=dm_item($row);
            if($action==='channels'){
                $key=$item['channel']; if(!isset($channels[$key])){$channels[$key]=['id'=>(int)$row['users_id'],'name'=>$item['creator'],'channel'=>$key,'count'=>0];}
                $channels[$key]['count']++; continue;
            }
            if($action==='catalog'&&!empty($query['category'])&&$item['categoryId']!==(int)$query['category']){continue;}
            if($action==='channel'){
                $filter=(string)($query['channel']??'');
                if(str_starts_with($filter,'category:')){if($item['categoryId']!==(int)substr($filter,9)){continue;}}
                elseif($item['channel']!==$filter && $item['creator']!==$filter){continue;}
            }
            if($own){$item['status']=dm_text($row['status']??'',30);$item['visibility']=($row['status']??'')==='u'?'unlisted':(($row['status']??'')==='a'?'public':'private');}
            $out[]=$item;
        }
        $meta=[];if($action==='channel'&&!empty($out)){require_once $root.'objects/subscribe.php';$target=(int)$out[0]['userId'];$meta=['userId'=>$target,'following'=>User::isLogged()&&!empty(Subscribe::getSubscribeFromID(User::getId(),$target)),'followers'=>(int)Subscribe::getTotalSubscribes($target)];}
        dm_reply(['items'=>$action==='channels'?array_values($channels):$out,'channel'=>$meta,'page'=>(int)$_REQUEST['current']]);
    }
    if($action==='video'){
        $row=dm_video(dm_id($query['id']??0));if(($query['mode']??'')==='embed'){forbiddenPageIfCannotEmbed((int)$row['id']);}$likes=Video::getVideoLikes((int)$row['id']);
        dm_reply(['item'=>dm_item($row),'likes'=>(int)$likes->likes,'dislikes'=>(int)$likes->dislikes,'reaction'=>(int)$likes->myVote]);
    }
    if($action==='comments'){
        require_once $root.'objects/comment.php';$id=dm_id($query['video']??0);dm_video($id);
        $_REQUEST['rowCount']=50;$_REQUEST['current']=max(1,min(100,(int)($query['page']??1)));
        $rows=Comment::getAllComments($id,0,0,true);$out=[];
        foreach($rows as $row){$out[]=['id'=>(int)$row['id'],'author'=>dm_text(User::getNameIdentificationById((int)$row['users_id']),100),
            'text'=>html_entity_decode(dm_text($row['comment']??'',4000),ENT_QUOTES,'UTF-8'),'created'=>dm_text($row['created']??'',30),
            'parentId'=>(int)($row['comments_id_pai']??0),'canDelete'=>User::isLogged()&&(bool)Comment::userCanEditComment((int)$row['id'])];}
        dm_reply(['items'=>$out,'total'=>(int)Comment::getTotalComments($id)]);
    }
    if(in_array($action,['playlists','playlist','library'],true)){
        dm_require_user();require_once $root.'objects/playlist.php';AVideoPlugin::loadPlugin('PlayLists');
        if($action==='library'){
            $kind=($query['kind']??'')==='favorites'?'favorite':'watch_later';
            $p=PlayList::getUserSpecialPlaylist(User::getId(),$kind);
            dm_reply(['items'=>empty($p['id'])?[]:dm_playlist_items((int)$p['id'])]);
        }
        if($action==='playlist'){$p=dm_playlist(dm_id($query['id']??0));dm_reply(['id'=>$p->getId(),'name'=>html_entity_decode($p->getName()),'visibility'=>$p->getStatus(),'items'=>dm_playlist_items((int)$p->getId())]);}
        $rows=PlayList::getAllFromUserLight(User::getId(),false);$out=[];
        foreach($rows as $row){if(in_array($row['status'],['favorite','watch_later'],true)){continue;}$out[]=['id'=>(int)$row['id'],'name'=>html_entity_decode(dm_text($row['name'],100)),'visibility'=>$row['status'],'items'=>dm_playlist_items((int)$row['id'])];}
        dm_reply(['items'=>$out]);
    }
    if($action==='profile'){dm_require_user();dm_reply(['user'=>dm_user()]);}
    if($action==='live'){
        $out=[];$plugin=AVideoPlugin::loadPluginIfEnabled('Live');
        if($plugin){$stats=getStatsNotifications();foreach(($stats['applications']??[]) as $row){
            $key=(string)($row['key']??'');if($key===''||!Live::canSeeLiveFromLiveKey($key)){continue;}
            $url=dm_media_url(Live::getM3U8File($key));if(!$url){continue;}
            $out[]=['id'=>(int)($row['users_id']??0),'title'=>dm_text($row['title']??'Live broadcast',140),'creator'=>dm_text($row['user']??'',100),'type'=>'Live','tag'=>'LIVE','videoUrl'=>$url,'img'=>dm_media_url($row['imgJPG']??null)??'/placeholder.svg'];
        }}dm_reply(['items'=>$out]);
    }
    if($action==='studio'){
        dm_require_user();if(!User::canStream()){dm_error('Streaming permission required.',403);}
        AVideoPlugin::loadPluginIfEnabled('Live');require_once $root.'plugin/Live/Objects/LiveTransmition.php';
        $row=LiveTransmition::getFromDbByUser(User::getId());
        dm_reply(['title'=>dm_text($row['title']??'',140),'visibility'=>empty($row['public'])?'unlisted':'public','server'=>empty($row['key'])?Live::getServer():Live::getRTMPLinkWithOutKey(User::getId()),'key'=>(string)($row['key']??'')]);
    }
    if($action==='notifications'){
        dm_require_user();AVideoPlugin::loadPluginIfEnabled('UserNotifications');
        // The native model is used below after its installed contract is verified.
        require __DIR__.'/notifications.php';
    }
    if($action==='encoder-queue'){dm_require_user();require __DIR__.'/creator.php';}
}
