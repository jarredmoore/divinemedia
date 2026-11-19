<?php
declare(strict_types=1);
// Azure origin boundary. Byte bodies are served only after native authorization.
ob_start();
require_once __DIR__.'/core.php';
$sent=false;
function delivery_headers(): void {
    header_remove('Location');header_remove('Set-Cookie');header_remove('Access-Control-Allow-Origin');
    header('Cache-Control: private, no-store, max-age=0');header('Pragma: no-cache');header('Expires: 0');
    header('Vary: Cookie, Origin');header('X-Content-Type-Options: nosniff');header('Referrer-Policy: no-referrer');
    $origin=(string)($_SERVER['HTTP_ORIGIN']??'');
    if(delivery_origin($origin)) { header('Access-Control-Allow-Origin: '.$origin);header('Access-Control-Allow-Credentials: true');header('Access-Control-Expose-Headers: Content-Range, Accept-Ranges'); }
}
function delivery_origin(string $origin): bool {
    return (bool)preg_match('~^https://(?:divinemedia\.us|(?:[a-f0-9]{24}|deploy-preview-\d+)--mediaproduction\.netlify\.app)$~D',$origin);
}
function delivery_deny(int $status=404): never {
    global $sent;$sent=true;while(ob_get_level())ob_end_clean();delivery_headers();http_response_code($status);header('Content-Type: application/json');echo '{"error":"Media unavailable."}';exit;
}
// Native permission helpers may exit/redirect; never expose their HTML or an XSendFile on denial.
register_shutdown_function(static function(){global $sent;if(!$sent)delivery_deny();});
function dm_error(string $message,int $status=400): never { delivery_deny($status); }
function dm_reply(array $data,int $status=200): never { delivery_deny($status>=400?$status:404); }
function delivery_json(array $data): never {
    global $sent;$sent=true;while(ob_get_level())ob_end_clean();delivery_headers();header('Content-Type: application/json');echo json_encode($data);exit;
}
try {
    $path=parse_url((string)($_SERVER['REQUEST_URI']??''),PHP_URL_PATH);
    if(!is_string($path))delivery_deny();
    $legacy=$_GET;
    $method=(string)($_SERVER['REQUEST_METHOD']??'GET');$origin=(string)($_SERVER['HTTP_ORIGIN']??'');
    if($origin!==''&&!delivery_origin($origin)&&$origin!=='https://media.divinemedia.us')delivery_deny(403);
    if($method==='OPTIONS') {
        if($path!=='/divine-media/session'||!delivery_origin($origin))delivery_deny(403);
        $sent=true;while(ob_get_level())ob_end_clean();delivery_headers();header('Access-Control-Allow-Methods: POST');header('Access-Control-Allow-Headers: Content-Type');http_response_code(204);exit;
    }
    $store=new DivineDeliveryStore('/var/www/tmp/divine-delivery');
    if($path==='/divine-media/session'&&$method!=='GET') {
        if($method!=='POST'||!delivery_origin($origin)||!str_starts_with($_SERVER['CONTENT_TYPE']??'','application/json'))delivery_deny(403);
        if((int)($_SERVER['CONTENT_LENGTH']??0)>256)delivery_deny(413);
        $body=file_get_contents('php://input',false,null,0,257);if(strlen($body)>256)delivery_deny(413);
        $input=json_decode($body,true);$record=$store->read('grant',(string)($input['grant']??''),time(),true);
        if(!hash_equals((string)($record['origin']??''),$origin))delivery_deny(403);
        // The handoff does not contain native credentials and cannot be used twice.
        $record['origin']=$origin;$cookie=$store->issue('session',$record,time()+8*3600);
        $sent=true;while(ob_get_level())ob_end_clean();delivery_headers();
        setcookie('__Host-dm_delivery',$cookie,['expires'=>time()+8*3600,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);
        header('Content-Type: application/json');echo '{"ready":true}';exit;
    }
    if($path==='/divine-media/logout') {
        if($method!=='POST'||!delivery_origin($origin))delivery_deny(403);
        $token=(string)($_COOKIE['__Host-dm_delivery']??'');
        if($token!=='') {try{$store->read('session',$token,time(),true);}catch(Throwable $e){}}
        $sent=true;while(ob_get_level())ob_end_clean();delivery_headers();
        setcookie('__Host-dm_delivery','',['expires'=>1,'path'=>'/','secure'=>true,'httponly'=>true,'samesite'=>'Lax']);
        header('Content-Type: application/json');echo '{"cleared":true}';exit;
    }
    if(!in_array($method,['GET','HEAD'],true))delivery_deny(405);
    $root=dirname(__DIR__).'/';$session='';$proof=null;
    $deliveryCookie=(string)($_COOKIE['__Host-dm_delivery']??'');
    if($deliveryCookie!=='') {
        try {$record=$store->read('session',$deliveryCookie,time());$session=(string)($record['session']??'');$proof=(string)($record['proof']??'');}
        catch(Throwable $e) { $session=''; }
    }
    // Native operator sessions continue to work; arbitrary cookie-based auto-login does not.
    if($session==='')$session=(string)($_COOKIE[md5($root)]??'');
    if(!preg_match('/^[A-Za-z0-9,-]{22,128}$/D',$session))$session='';
    $_COOKIE=$session===''?[]:[md5($root)=>$session];$_SERVER['HTTP_COOKIE']=$session===''?'':md5($root).'='.$session;
    if($session!=='')session_id($session);
    $_GET=$_POST=[];$_REQUEST=['do_not_login'=>1];
    unset($_SERVER['HTTP_AUTHORIZATION'],$_SERVER['HTTP_X_DIVINE_SESSION'],$_SERVER['HTTP_X_FORWARDED_FOR']);
    require $root.'videos/configuration.php';require_once $root.'objects/user.php';require_once $root.'objects/video.php';
    _session_start();
    // The native session and its CSRF identity must still exist: logout or CSRF rotation revokes access.
    if($proof!==null&&(!User::isLogged()||!hash_equals($proof,hash('sha256',(string)($_SESSION['dm_frontend_csrf']??'')))))delivery_deny(401);
    if($path==='/divine-media/session') {if(!User::isLogged()||$proof===null)delivery_deny(401);delivery_json(['ready'=>true]);}
    define('DM_FRONTEND_API',true);require_once $root.'divine-api/native.php';
    if(str_starts_with($path,'/hls/live/')) {
        $asset=DivineMediaAssets::path(substr($path,10));$parts=explode('/',$asset);
        if(count($parts)<2||!in_array(strtolower(pathinfo($asset,PATHINFO_EXTENSION)),['m3u8','ts','m4s','mp4','key'],true))delivery_deny();
        $key=$parts[0];if(!AVideoPlugin::loadPluginIfEnabled('Live')||!Live::canSeeLiveFromLiveKey($key))delivery_deny();
        // Password-protected live needs its own verified unlock flow; never silently bypass it.
        if(!method_exists('Live','isPasswordProtected')||Live::isPasswordProtected($key))delivery_deny(403);
        $file=DivineMediaAssets::file('/HLS/live',$asset);$prefix='/hls/live/';
    } else {
        if(str_starts_with($path,'/videos/'))$asset=substr($path,8);
        elseif(str_starts_with($path,'/divine-media/assets/'))$asset=substr($path,21);
        elseif($path==='/view/xsendfile.php')$asset=(string)($legacy['folder']??'').(string)($legacy['file']??'');
        elseif($path==='/view/hls.php')$asset=(string)($legacy['videoDirectory']??'').'/index.m3u8';
        elseif($path==='/plugin/VideoHLS/downloadProtection.php')$asset=(string)($legacy['filename']??'').'/'.(string)($legacy['key']??'').'.key';
        else delivery_deny();
        // Asset ownership comes from exact catalog names and closed variant scopes on every request.
        if(!DivineMediaAssets::siteAsset($asset)) {
            $res=sqlDAL::readSql('SELECT id, filename FROM videos','',[],true);$rows=sqlDAL::fetchAllAssoc($res);sqlDAL::close($res);
            $id=DivineMediaAssets::owner($asset,$rows);dm_video($id);
        }
        $file=DivineMediaAssets::file(Video::getStoragePath(),$asset);$prefix='/divine-media/assets/';
    }
    $mime=DivineMediaAssets::mime($asset);$manifest=null;
    if(str_ends_with($asset,'.m3u8'))$manifest=DivineMediaAssets::manifest((string)file_get_contents($file,false,null,0,1048577),dirname($asset),$prefix);
    // Release native locks before Apache transfers bytes, ranges, or a long response.
    if(session_status()===PHP_SESSION_ACTIVE)session_write_close();
    $sent=true;while(ob_get_level())ob_end_clean();delivery_headers();header('Content-Type: '.$mime);header('Content-Disposition: inline');
    if($manifest!==null) { header('Content-Length: '.strlen($manifest));if($method!=='HEAD')echo $manifest; }
    else { header('X-Sendfile: '.$file); }
} catch(Throwable $e) { delivery_deny(); }
