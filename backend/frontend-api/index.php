<?php
declare(strict_types=1);
// A JSON-only boundary. Native AVideo remains the source of accounts and authorization.
ob_start();
$GLOBALS['dm_sent'] = false;
function dm_reply(array $data, int $status = 200): void {
    $GLOBALS['dm_sent'] = true;
    while (ob_get_level()) { ob_end_clean(); }
    header_remove('Set-Cookie'); header_remove('Location'); header_remove('Access-Control-Allow-Origin');
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: private, no-store'); header('X-Content-Type-Options: nosniff');
    if (preg_match('/^[A-Za-z0-9,-]{22,128}$/', session_id())) { header('X-Divine-Session: '.session_id()); }
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    if (session_status() === PHP_SESSION_ACTIVE) { session_write_close(); }
    exit;
}
function dm_error(string $message, int $status = 400): void { dm_reply(['error'=>$message], $status); }
register_shutdown_function(function () {
    if (!$GLOBALS['dm_sent']) {
        // Native denial/error pages must never become a public HTML response or expose internals.
        dm_reply(['error'=>'The platform could not complete this request.'], http_response_code() >= 400 ? http_response_code() : 502);
    }
});
$keyFile = '/var/www/tmp/divine-frontend-gateway.key';
$expected = is_file($keyFile) ? trim((string)file_get_contents($keyFile)) : '';
if (strlen($expected) < 32 || !hash_equals($expected, (string)($_SERVER['HTTP_X_DIVINE_GATEWAY_KEY'] ?? ''))) { dm_error('Not found', 404); }
define('DM_FRONTEND_API',true);
$frontendOrigin = (string)($_SERVER['HTTP_X_DIVINE_FRONTEND_ORIGIN'] ?? '');
if (!preg_match('~^https://(?:divinemedia\.us|(?:[a-f0-9]{24}|deploy-preview-\d+)--mediaproduction\.netlify\.app)$~D', $frontendOrigin)) { dm_error('Invalid frontend origin',403); }
$action = (string)($_GET['action'] ?? '');
$query = $_GET; unset($query['action']);
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if (!in_array($method, ['GET','POST'], true)) { dm_error('Method not allowed',405); }
$envelope = $method === 'POST' && $action !== 'upload-chunk' ? json_decode((string)file_get_contents('php://input'), true) : [];
$body = $action === 'upload-chunk' ? $_POST : ($method === 'POST' ? ($envelope['payload'] ?? null) : []);
if (!is_array($body)) { dm_error('Invalid request body'); }
$root = dirname(__DIR__) . DIRECTORY_SEPARATOR;
$session = (string)($_SERVER['HTTP_X_DIVINE_SESSION'] ?? '');
if ($session !== '' && !preg_match('/^[A-Za-z0-9,-]{22,128}$/D', $session)) { dm_error('Invalid session',400); }
// AVideo names its native session with md5(systemRootPath). No credential cookies are accepted.
if ($session !== '') { session_id($session); }
$_COOKIE = $session === '' ? [] : [md5($root) => $session];
$_SERVER['HTTP_COOKIE'] = $session === '' ? '' : md5($root).'='.$session;
$clientIp = (string)($_SERVER['HTTP_X_DIVINE_CLIENT_IP'] ?? '');
if (filter_var($clientIp,FILTER_VALIDATE_IP)) { $_SERVER['REMOTE_ADDR'] = $clientIp; }
unset($_SERVER['HTTP_X_FORWARDED_FOR'],$_SERVER['HTTP_FORWARDED'],$_SERVER['HTTP_AUTHORIZATION']);
// The attested same-origin request is represented as a native server-side request.
$_SERVER['HTTP_ORIGIN'] = 'https://media.divinemedia.us';
$_SERVER['HTTP_REFERER'] = 'https://media.divinemedia.us/';
$_GET = $_POST = [];
// Prevent native plugin bootstrap from authenticating raw request input before this boundary's CSRF check.
$_REQUEST = ['do_not_login'=>1];
require $root . 'videos/configuration.php';
require_once $root . 'objects/user.php';
require_once $root . 'objects/video.php';
require_once __DIR__ . '/native.php';
_session_start();
if (empty($_SESSION['dm_frontend_csrf'])) { $_SESSION['dm_frontend_csrf'] = bin2hex(random_bytes(32)); }
$csrf = $_SESSION['dm_frontend_csrf'];
if ($method === 'POST' && !hash_equals($csrf, (string)($_SERVER['HTTP_X_DIVINE_CSRF'] ?? ''))) { dm_error('Your session changed. Refresh and try again.',403); }
enforceRateLimit('divine_frontend_'.$action, $method === 'POST' ? 80 : 300, 60);
try {
    if ($action === 'session' && $method === 'GET') {
        dm_reply(['user'=>dm_user(),'csrf'=>$csrf,'capabilities'=>['comments'=>true,'reactions'=>true,'playlists'=>AVideoPlugin::isEnabledByName('PlayLists'),'live'=>AVideoPlugin::isEnabledByName('Live')],'captchaRequired'=>User::isCaptchaNeed()]);
    }
    if ($action === 'login' && $method === 'POST') {
        $name = dm_text($body['user']??'',254); $password = (string)($body['password']??'');
        if ($name === '' || $password === '' || strlen($password)>200) { dm_error('Enter your username and password.'); }
        $_POST['captcha'] = $_REQUEST['captcha'] = dm_text($body['captcha']??'',30);
        $_POST['rememberme'] = $_REQUEST['rememberme'] = 'false';
        $user = new User(0, $name, $password); $result = $user->login(false,false);
        unset($password, $body['password']);
        if ($result !== User::USER_LOGGED) { dm_error($result === User::CAPTCHA_ERROR ? 'Complete the verification challenge and try again.' : ($result === User::TOO_MANY_FAILED_ATTEMPTS ? 'Too many attempts. Please try later.' : 'Unable to sign in. Check your credentials and account verification.'), $result === User::TOO_MANY_FAILED_ATTEMPTS ? 429 : 401); }
        _session_start(); $_SESSION['dm_frontend_csrf'] = bin2hex(random_bytes(32));
        dm_reply(['user'=>dm_user(),'csrf'=>$_SESSION['dm_frontend_csrf']]);
    }
    if ($action === 'logout' && $method === 'POST') { User::logoff(); dm_reply(['message'=>'Signed out.']); }
    if ($method === 'POST' && $action === 'playback') {
        $id=dm_id($body['video']??0);dm_video($id);
        $position=max(0,min(86400,(int)($body['position']??0)));
        $seconds=max(0,min(30,(int)($body['seconds']??0)));
        dm_native('objects/videoAddViewCount.json.php',['id'=>$id,'currentTime'=>$position,'seconds_watching_video'=>$seconds]);
        dm_reply(['recorded'=>true]);
    }
    if ($method === 'POST' && in_array($action,['register','recover','reset-password','verify-email','video-unlock'],true)) { require __DIR__ . '/anonymous.php'; }
    require __DIR__ . '/read.php';
    if ($method === 'POST') { dm_require_user(); require __DIR__ . '/write.php'; }
    dm_error('Unknown platform action',404);
} catch (Throwable $e) {
    // Do not log credentials, request bodies, native SQL, session identifiers or exception details.
    error_log('Divine frontend API action failed: '.preg_replace('/[^a-z-]/','',$action).' '.get_class($e));
    dm_error('The platform could not complete this action. Please try again.',502);
}
