<?php
// Standalone PHP contract test: no native login, database, publishing, or network calls.
require $argv[1];
$valid=['https://youtu.be/M5hZAL_hW7c?si=test','https://www.youtube.com/watch?v=M5hZAL_hW7c&t=3','https://youtube.com/embed/M5hZAL_hW7c','https://m.youtube.com/shorts/M5hZAL_hW7c','https://www.youtube-nocookie.com/embed/M5hZAL_hW7c','https://youtube.com/live/M5hZAL_hW7c'];
$invalid=['https://youtube.com.evil.test/watch?v=M5hZAL_hW7c','https://youtube.com@evil.test/watch?v=M5hZAL_hW7c','https://youtu.be:443/M5hZAL_hW7c','file:///M5hZAL_hW7c','https://youtu.be/../../M5hZAL_hW7c','https://youtube.com/watch?v[]=M5hZAL_hW7c','https://youtu.be/invalid','https://example.com/M5hZAL_hW7c'];
foreach($valid as $url){if(DivineEmbedCover::youtubeId($url)!=='M5hZAL_hW7c'){throw new RuntimeException('Valid provider link rejected');}}
foreach($invalid as $url){if(DivineEmbedCover::youtubeId($url)!==null){throw new RuntimeException('Unsafe link accepted');}}
$root=sys_get_temp_dir().'/dm-embed-test-'.bin2hex(random_bytes(8));mkdir($root,0700);
try{
 file_put_contents($root.'/demo.jpg','existing custom cover');
 if(DivineEmbedCover::install($valid[0],'demo',$root,$root.'/demo.jpg')||file_get_contents($root.'/demo.jpg')!=='existing custom cover'){throw new RuntimeException('Existing cover changed');}
 if(DivineEmbedCover::install($valid[0],'../escape',$root,$root.'/../escape.jpg')){throw new RuntimeException('Traversal allowed');}
 if(DivineEmbedCover::install($valid[0],'demo',$root,sys_get_temp_dir().'/demo.jpg')){throw new RuntimeException('Storage boundary escaped');}
}finally{unlink($root.'/demo.jpg');rmdir($root);}
echo json_encode(['result'=>'pass','valid_url_forms'=>count($valid),'unsafe_inputs_rejected'=>count($invalid),'existing_cover_and_storage_boundary_preserved'=>true]);
