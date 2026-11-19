<?php
/* Shared presentation only. Do not include this from API or upload handlers. */
if (!defined('DM_ROUTE_SHELL_INCLUDED')) {
    define('DM_ROUTE_SHELL_INCLUDED', true);
    $dmFrontendRedirect=dirname(__DIR__).'/divine-api/public-redirect.php';
    if(is_file($dmFrontendRedirect)){require_once $dmFrontendRedirect;}

    $dmThemeValues = ['default', 'code-black', 'cold-black', 'cozy'];
    $dmRequestedTheme = $_GET['theme'] ?? null;
    $dmCookieTheme = $_COOKIE['dm_view_theme'] ?? null;
    $dmTheme = is_string($dmRequestedTheme) && in_array($dmRequestedTheme, $dmThemeValues, true)
        ? $dmRequestedTheme : (is_string($dmCookieTheme) && in_array($dmCookieTheme, $dmThemeValues, true) ? $dmCookieTheme : 'default');
    if ($dmTheme === 'cold-black') $dmTheme = 'code-black';
    if ($dmTheme === 'cozy') $dmTheme = 'default';
    $dmHost = strtolower(explode(':', $_SERVER['HTTP_HOST'] ?? '')[0]);
    if (!headers_sent() && in_array($dmHost, ['divinemedia.us', 'www.divinemedia.us', 'media.divinemedia.us'], true)) {
        setcookie('dm_view_theme', $dmTheme, ['expires'=>time()+31536000, 'path'=>'/', 'domain'=>'divinemedia.us', 'secure'=>true, 'httponly'=>false, 'samesite'=>'Lax']);
    }
    $dmInk = '#000000';
    ?>
<script class="doNotSepareteTag" data-divine-route-theme>document.documentElement.dataset.dmTheme=<?= json_encode($dmTheme) ?>;</script>
<style class="doNotSepareteTag" data-divine-route-critical>html,body{background:<?= $dmInk ?>!important;color:#f5f5f7;color-scheme:dark}</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/divine-shell/shell.css?v=34-glass-2">
<meta name="theme-color" content="#000000">
<link rel="apple-touch-icon" sizes="180x180" href="https://divinemedia.us/icons/apple-touch-icon.png">
<link rel="icon" type="image/svg+xml" href="/divine-shell/mark.svg?v=34-glass-1">
<script class="doNotSepareteTag" src="/divine-shell/shell.js?v=34-glass-2" defer></script>
<?php } ?>
