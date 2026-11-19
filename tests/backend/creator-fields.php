<?php
require $argv[1];
function check($ok,$message){if(!$ok)throw new RuntimeException($message);}
$d=DivineCreatorFields::normalize(['title'=>' <b>Project</b> ','description'=>"line one\nline two",'visibility'=>'private','categoryId'=>'2','canShare'=>false,'canDownload'=>true,'rating'=>'pg','tags'=>['1'=>['launch','launch','<script>brand</script>']]]);check($d['title']==='Project'&&$d['categoryId']===2&&$d['canShare']===false,'Metadata contract failed');check(count($d['tags'][1])===2,'Tag normalization failed');
foreach([['title'=>''],['title'=>'x','visibility'=>'admin'],['title'=>'x','categoryId'=>'../../1'],['title'=>'x','canDownload'=>'true'],['title'=>'x','rating'=>'unsafe'],['title'=>'x','tags'=>['1'=>array_fill(0,21,'tag')]]]as $invalid){try{DivineCreatorFields::normalize($invalid);throw new LogicException('Invalid metadata accepted');}catch(InvalidArgumentException $e){}}
$png=base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aGz8AAAAASUVORK5CYII=');check(DivineCreatorFields::imageInfo($png)[2]===IMAGETYPE_PNG,'Valid image rejected');
foreach(['<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>','<?php echo 1;',str_repeat('x',DivineCreatorFields::MAX_IMAGE+1)]as $invalid){try{DivineCreatorFields::imageInfo($invalid);throw new LogicException('Invalid image accepted');}catch(InvalidArgumentException $e){}}
echo json_encode(['result'=>'pass','metadata_and_boolean_types'=>true,'tag_limits'=>true,'image_bytes_and_size_validation'=>true,'unsupported_active_content_rejected'=>true]);
