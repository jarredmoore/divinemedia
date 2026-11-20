<?php
define('DM_FRONTEND_API',true);
class Video {const STATUS_ACTIVE='a',STATUS_UNLISTED='u',STATUS_INACTIVE='i',SORT_TYPE_VIEWABLE='viewable';static $status='a',$edit=false;static function canEdit($id){return self::$edit;}static function getVideo(...$args){return ['id'=>1,'status'=>self::$status];}}
class User {static $watch=true;static function canWatchVideoWithAds(...$args){return self::$watch;}}
class AVideoPlugin {static function loadPluginIfEnabled($name){return false;}}
function dm_error($m,$s=400){throw new RuntimeException($m,$s);}function dm_reply($d,$s=200){throw new RuntimeException('Denied',$s);}function forbiddenPageIfCannotWatchVideo($id){}
require __DIR__.'/../../backend/frontend-api/native.php';
$n=0;foreach(['a','u','i','c','e','b','',null]as $status){foreach([false,true]as $owner){Video::$status=$status;Video::$edit=$owner;try{dm_video(1);$ok=true;}catch(RuntimeException $e){$ok=false;}if($ok!==($owner||in_array($status,['a','u'],true)))throw new RuntimeException('Status boundary failed');$n++;}}
Video::$status='a';Video::$edit=false;User::$watch=false;try{dm_video(1);throw new Exception('Group permission bypass');}catch(RuntimeException $e){if($e->getCode()!==403)throw $e;}$n++;
echo json_encode(['result'=>'pass','checks'=>$n])."\n";
