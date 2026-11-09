<?php
if($action==='register'){
    $name=dm_text($body['name']??'',100);$username=dm_text($body['user']??'',50);$email=dm_text($body['email']??'',254);$pass=(string)($body['password']??'');
    if(!preg_match('/^[a-zA-Z0-9_.-]{3,50}$/D',$username)||!filter_var($email,FILTER_VALIDATE_EMAIL)||$name===''||strlen($pass)<8||strlen($pass)>200){dm_error('Enter a valid username, email, name and password.');}
    $result=dm_native('objects/userCreate.json.php',['user'=>$username,'name'=>$name,'email'=>$email,'pass'=>$pass,'captcha'=>dm_text($body['captcha']??'',30),'is_company'=>0]);
    dm_reply(['message'=>'Account request submitted. Check your email for verification.']);
}
if($action==='recover'){
    $email=dm_text($body['email']??'',254);if(!filter_var($email,FILTER_VALIDATE_EMAIL)){dm_error('Enter your email address.');}
    // Use the native recovery handler; do not expose whether the address is registered.
    dm_native('objects/userRecoverPass.php',['user'=>$email,'captcha'=>dm_text($body['captcha']??'',30)]);
    dm_reply(['message'=>'If this account exists, reset instructions will be sent.']);
}

if($action==='video-unlock'){
    $id=dm_id($body['video']??0);
    if(!User::canWatchVideoWithAds($id,null,true)){dm_error('This title is unavailable.',403);}
    enforceRateLimit('divine_video_password',10,60);
    AVideoPlugin::loadPluginIfEnabled('CustomizeUser');
    $_REQUEST['video_password']=$_POST['video_password']=dm_text($body['password']??'',200);
    if(!CustomizeUser::videoPasswordIsGood($id)){dm_error('The video password was not accepted.',403);}
    dm_reply(['item'=>dm_item(dm_video($id)),'message'=>'Video unlocked.']);
}
