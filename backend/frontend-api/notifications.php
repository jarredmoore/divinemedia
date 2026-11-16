<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
dm_require_user();AVideoPlugin::loadPluginIfEnabled('UserNotifications');
if($action==='notifications'){
    $rows=User_notifications::getAllForUsers_id(User::getId(),50,false);$out=[];
    foreach(is_array($rows)?$rows:[] as $r){$out[]=['id'=>(int)$r['id'],'title'=>dm_text($r['title']??'',140),'text'=>html_entity_decode(dm_text($r['msg']??'',1500),ENT_QUOTES,'UTF-8'),'created'=>dm_text($r['created']??'',30),'read'=>!empty($r['time_readed'])&&$r['time_readed']!=='0000-00-00 00:00:00'];}
    dm_reply(['items'=>$out]);
}
if($action==='notification-read'){
    $id=dm_id($body['id']??0);
    // The bundled free model exposes no mark-read method. Update only this owner's native row.
    $ok=sqlDAL::writeSql('UPDATE user_notifications SET time_readed=NOW() WHERE id=? AND users_id=?','ii',[$id,User::getId()]);
    if(!$ok){dm_error('Notification could not be updated.');}
    dm_reply(['message'=>'Notification marked read.']);
}
