<?php
if(!defined('DM_FRONTEND_API')){http_response_code(404);exit;}
if($action==='register'){
    $name=dm_text($body['name']??'',100);$username=dm_text($body['user']??'',50);$email=dm_text($body['email']??'',254);$pass=(string)($body['password']??'');
    if(!preg_match('/^[a-zA-Z0-9_.-]{3,50}$/D',$username)||!filter_var($email,FILTER_VALIDATE_EMAIL)||$name===''||strlen($pass)<8||strlen($pass)>200){dm_error('Enter a valid username, email, name and password.');}
    $result=dm_native('objects/userCreate.json.php',['user'=>$username,'name'=>$name,'email'=>$email,'pass'=>$pass,'captcha'=>dm_text($body['captcha']??'',30),'is_company'=>0]);
    dm_reply(['message'=>'Account request submitted. Check your email for verification.']);
}
if($action==='recover'){
    $email=dm_text($body['email']??'',254);if(!filter_var($email,FILTER_VALIDATE_EMAIL)){dm_error('Enter your email address.');}
    // Use the native recovery handler; do not expose whether the address is registered.
    enforceRateLimit('divine_recovery',5,3600);
    dm_native('objects/userRecoverPass.php',['user'=>$email,'captcha'=>dm_text($body['captcha']??'',30)],false,true);
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

if($action==='reset-password'){
    $user=dm_text($body['user']??'',254);$token=dm_text($body['token']??'',1024);$pass=(string)($body['password']??'');$confirm=(string)($body['passwordConfirm']??'');
    if($user===''||$token===''||strlen($pass)<8||strlen($pass)>200||$pass!==$confirm){dm_error('Enter matching passwords of at least eight characters.');}
    enforceRateLimit('divine_recovery_reset',10,3600);
    dm_native('objects/userRecoverPassSave.json.php',['user'=>$user,'recoverPassword'=>$token,'newPassword'=>$pass,'newPasswordConfirm'=>$confirm]);
    dm_reply(['message'=>'Password changed. Sign in with your new password.']);
}
if($action==='verify-email'){
    $code=dm_text($body['code']??'',2048);if($code===''){dm_error('Verification code is missing.');}
    enforceRateLimit('divine_verify_email',20,3600);
    if(!User::verifyCode($code)){dm_error('This verification link is invalid or expired.');}
    dm_reply(['message'=>'Email verified. You can sign in now.']);
}
