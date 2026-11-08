<?php
/* Canonicalize browser entry routes only; Apache excludes media, APIs and POSTs. */
$host = strtolower(explode(':', $_SERVER['HTTP_HOST'] ?? '')[0]);
$method = $_SERVER['REQUEST_METHOD'] ?? '';
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
if ($host !== 'media.divinecreativegroup.com' || !in_array($method, ['GET','HEAD'], true) || !is_string($path) || preg_match('/[\x00-\x20\x7f]/', $path)) {
    http_response_code(404); exit;
}
$allowed = ['theme','noNavbar','page','current','rowCount','search','catName','channelName','videos_id','videoName','type','order','sort','lang','includeType'];
$query = [];
foreach ($allowed as $key) {
    if (isset($_GET[$key]) && is_string($_GET[$key]) && strlen($_GET[$key]) <= 200) $query[$key] = $_GET[$key];
}
if (isset($query['theme']) && !in_array($query['theme'], ['default','code-black','cold-black'], true)) unset($query['theme']);
header('Location: https://media.divinemedia.us'.$path.($query?'?'.http_build_query($query):''), true, 302);
exit;
