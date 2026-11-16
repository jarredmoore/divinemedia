<?php
// Loaded only by the native HTML head. Activation is a separate, verified cutover step.
if(!defined('DM_ROUTE_SHELL_INCLUDED')){http_response_code(404);exit;}
function dm_frontend_destination(string $uri): string {
    $parts=parse_url($uri);$path=rtrim($parts['path']??'/','/');$q=[];parse_str($parts['query']??'',$q);
    $route='/';$id=(string)($q['v']??$q['video_id']??$q['videos_id']??'');
    if(preg_match('~^/(?:video|audio|embed|videoEmbed|audioEmbed)/(\d+)(?:/|$)~',$path,$m)){$id=$m[1];}
    if(ctype_digit($id)&&(int)$id>0){$route=(str_contains(strtolower($path),'embed')?'/embed/':'/watch/').(int)$id;}
    elseif(preg_match('~^/cat/([A-Za-z0-9_-]+)$~',$path,$m)){$route='/category/'.$m[1];}
    elseif(preg_match('~^/channel/([^/]+)$~',$path,$m)){$route='/channel/'.rawurlencode(rawurldecode($m[1]));}
    elseif(str_starts_with(strtolower($path),'/encoder')){$route='/creator/encoding';}
    elseif(preg_match('~(?:live.?studio)~i',$path)){$route='/creator/live';}
    elseif(preg_match('~(?:livegallery|/live$)~i',$path)){$route='/live';}
    elseif(preg_match('~(?:upload)~i',$path)){$route='/creator/upload';}
    elseif(preg_match('~(?:signup|signUp|userCreate)~i',$path)){$route='/signup';}
    elseif(preg_match('~(?:recoverPass)~i',$path)){
        $route='/recover';$user=$q['user']??null;$token=$q['recoverpass']??null;
        if(is_string($user)&&is_string($token)&&strlen($user)<=254&&strlen($token)<=512){$route.='?'.http_build_query(['user'=>$user,'token'=>$token]);}
    }
    elseif(preg_match('~(?:watchlater|watch_later)~i',$path)){$route='/library/watch-later';}
    elseif(preg_match('~(?:favorite)~i',$path)){$route='/library/favorites';}
    elseif(preg_match('~(?:playlist)~i',$path)){$route='/library/playlists';}
    elseif(preg_match('~(?:notification)~i',$path)){$route='/notifications';}
    elseif(preg_match('~(?:channel)~i',$path)){$route='/channels';}
    elseif(preg_match('~(?:categor)~i',$path)){$route='/categories';}
    elseif(preg_match('~(?:login|/user$|/users$)~i',$path)){$route='/account';}
    $theme=$q['theme']??null;
    if(is_string($theme)&&in_array($theme,['default','code-black','cold-black'],true)){$route.=(str_contains($route,'?')?'&':'?').'theme='.($theme==='cold-black'?'code-black':$theme);}
    return 'https://divinemedia.us'.$route;
}
if(PHP_SAPI!=='cli'&&is_file('/var/www/tmp/divine-frontend-public.enabled')){
    // Native loopback handlers and authenticated operator administration remain available.
    $local=in_array($_SERVER['REMOTE_ADDR']??'',['127.0.0.1','::1'],true);
    $admin=class_exists('User',false)&&User::isAdmin();
    if(!$local&&!$admin){
        $destination=dm_frontend_destination($_SERVER['REQUEST_URI']??'/');
        if(!headers_sent()){
            header('Cache-Control: private, no-store');header('Referrer-Policy: no-referrer');header('Location: '.$destination,true,302);
        }else{
            echo '<script>location.replace('.json_encode($destination,JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT).')</script>';
        }
        exit;
    }
}
