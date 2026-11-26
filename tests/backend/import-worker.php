<?php
// Capture the worker's contract with disposable native stubs; never connect to AVideo or a downloader.
$source=$argv[1];$base=sys_get_temp_dir().'/dm-import-'.bin2hex(random_bytes(5));mkdir($base);mkdir($base.'/api');mkdir($base.'/Encoder');mkdir($base.'/Encoder/videos');mkdir($base.'/Encoder/objects');
copy($source,$base.'/api/encoder-worker.php');
file_put_contents($base.'/api/import-source.php','<?php class DivineImportSource {static function url($u){if($u!=="https://vimeo.com/76979871")throw new Exception("bad");return $u;}}');
$config= <<<'CODE'
<?php
if(!defined('MYSQLI_ASSOC'))define('MYSQLI_ASSOC',1);
if(!function_exists('mb_substr')){function mb_substr($s,$a,$n){return substr($s,$a,$n);}}
function decideFormatOrder(){return 10;}
function execRun(){file_put_contents(getenv('DM_CAPTURE').'.dispatch','requested');return true;}
class Result {public $q;function __construct($q){$this->q=$q;}function fetch_all($mode){return [['id'=>8]];}function fetch_row(){return [str_contains($this->q,'GET_LOCK')?1:(str_contains($this->q,'id<>?')?(getenv('DM_OTHER_JOBS')?:0):(getenv('DM_PENDING')?:0))];}function fetch_assoc(){return getenv('DM_EXISTING')?['id'=>99]:null;}}
class Statement {public $q;function __construct($q){$this->q=$q;}function bind_param($types,&...$args){}function execute(){}function get_result(){return new Result($this->q);}function close(){}}
class FakeDB {function prepare($q){return new Statement($q);}}
$global=['mysqli'=>new FakeDB()];
CODE;
file_put_contents($base.'/Encoder/videos/configuration.php',$config);
$encoder= <<<'CODE'
<?php
class Encoder {const STATUS_ERROR='error',STATUS_DONE='done';public $fields=[];static function getTableName(){return 'encoder_queue';}function __construct($id){}function __call($name,$args){$this->fields[$name]=$args[0]??null;}function getFormats_id(){return 10;}function setOverride_status($value){$this->fields['private']=$value;}function save(){file_put_contents(getenv('DM_CAPTURE'),json_encode($this->fields));return 42;}}
CODE;
file_put_contents($base.'/Encoder/objects/Encoder.php',$encoder);
file_put_contents($base.'/Encoder/objects/Streamer.php','<?php class Streamer {function __construct($id){}static function getTableName(){return "streamers";}function getSiteURL(){return "https://media.divinemedia.us/";}function getIsAdmin(){return false;}function getPriority(){return 1;}}');
file_put_contents($base.'/Encoder/objects/Login.php','<?php class Login {}');file_put_contents($base.'/Encoder/objects/Format.php','<?php class Format {}');
function invoke($base,$canUpload,$extra=[]){$capture=$base.'/captured.json';@unlink($capture);@unlink($capture.'.dispatch');$env=array_merge($_ENV,['DM_CAPTURE'=>$capture],$extra);$p=proc_open([PHP_BINARY,$base.'/api/encoder-worker.php'],[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$pipes,null,$env);fwrite($pipes[0],json_encode(['actor'=>['userId'=>7,'username'=>'fixture','canUpload'=>$canUpload],'op'=>'import','data'=>['url'=>'https://vimeo.com/76979871','ticket'=>str_repeat('a',48),'videoId'=>31,'title'=>'Private import','profile'=>'mp4']]));fclose($pipes[0]);$out=stream_get_contents($pipes[1]);fclose($pipes[1]);fclose($pipes[2]);proc_close($p);return [json_decode($out,true),is_file($capture)?json_decode(file_get_contents($capture),true):null];}
try{
 [$reply,$fields]=invoke($base,true);if(($reply['id']??0)!==42||($fields['private']??'')!=='i'||($fields['setStreamers_id']??0)!==8||json_decode($fields['setReturn_vars']??'',true)!==['videos_id'=>31]||($fields['setFileURI']??'')!=='https://vimeo.com/76979871')throw new RuntimeException('Native private import mapping failed: '.json_encode([$reply,$fields]));
 if(($reply['dispatch']??'')!=='requested'||!is_file($base.'/captured.json.dispatch'))throw new RuntimeException('Native on-demand dispatch was not requested');
 [$reply,$fields]=invoke($base,true,['DM_OTHER_JOBS'=>'1']);if(($reply['dispatch']??'')!=='waiting'||is_file($base.'/captured.json.dispatch'))throw new RuntimeException('Unrelated Encoder jobs must not be restarted');
 [$reply,$fields]=invoke($base,true,['DM_EXISTING'=>'1']);if(($reply['id']??0)!==99||!$reply['duplicate']||$fields!==null)throw new RuntimeException('Idempotent queue retry failed');
 [$reply,$fields]=invoke($base,true,['DM_PENDING'=>'3']);if(empty($reply['error'])||$fields!==null)throw new RuntimeException('Pending limit failed');
 [$reply,$fields]=invoke($base,false);if(empty($reply['error'])||$fields!==null)throw new RuntimeException('Permission boundary failed');
 echo "Native worker mapping, private override, actor scope, retry and pending limit: pass\n";
}finally{function removeTree($p){foreach(scandir($p)as $n){if($n==='.'||$n==='..')continue;$f=$p.'/'.$n;if(is_dir($f))removeTree($f);else unlink($f);}rmdir($p);}removeTree($base);}
