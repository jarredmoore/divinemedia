<?php
define('DM_ROUTE_SHELL_INCLUDED',true);
require $argv[1].'/public-redirect.php';
$cases=[
 '/'=>'/',
 '/Encoder/'=>'/creator/encoding',
 '/upload'=>'/creator/upload',
 '/user?redirect=https://evil.invalid&password=secret'=>'/account',
 '/video/12/title?theme=cold-black'=>'/watch/12?theme=code-black',
 '/videoEmbed/12'=>'/embed/12',
 '/cat/default'=>'/category/default',
 '/channel/test%20creator'=>'/channel/test%20creator',
 '/recoverPass?user=qa&recoverpass=one-use&password=secret'=>'/recover?user=qa&token=one-use',
 '/anything?url=https://evil.invalid'=>'/',
];
foreach($cases as $input=>$expected){if(dm_frontend_destination($input)!=='https://divinemedia.us'.$expected){fwrite(STDERR,"Route mapping failed\n");exit(1);}}
echo "Native HTML route mapping passed\n";
