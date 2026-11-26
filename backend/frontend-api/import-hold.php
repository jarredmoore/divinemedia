<?php
declare(strict_types=1);
/** Server-owned draft markers, never a browser-supplied status or public URL. */
final class DivineImportHold {
    private static array $publishing=[];
    public static function approve($video): void { self::$publishing[(int)$video->getId()]=true; }
    public static function status($video,$status,?string $root=null) { if(empty(self::$publishing[(int)$video->getId()])&&self::active($video,$root))return 'i';return $status; }
    private static function directory(?string $root=null): string {return rtrim($root??Video::getStoragePath(),'/').'/.divine-private/import-drafts';}
    private static function file($video,?string $root=null): string {$id=(int)$video->getId();if($id<1)throw new RuntimeException('Invalid import draft.');return self::directory($root).'/'.$id.'.json';}
    public static function active($video,?string $root=null): bool {if((int)$video->getId()<1)return false;$file=self::file($video,$root);return file_exists($file)||is_link($file);}
    public static function read($video,?string $root=null): array {
        $file=self::file($video,$root);if(is_link($file))throw new RuntimeException('Invalid import marker.');$value=json_decode((string)file_get_contents($file),true);
        if(!is_array($value)||($value['id']??0)!==(int)$video->getId()||($value['owner']??0)!==(int)$video->getUsers_id()||!preg_match('/^[a-f0-9]{48}$/D',$value['ticket']??''))throw new RuntimeException('Import marker needs verification.');return $value;
    }
    public static function hold($video,string $ticket,int $job=0,?string $root=null): void {
        if(!preg_match('/^[a-f0-9]{48}$/D',$ticket))throw new RuntimeException('Invalid import ticket.');$dir=self::directory($root);$parent=dirname($dir);
        if(!is_dir($parent)||is_link($parent)||!is_file($parent.'/.htaccess')||!preg_match('/Require\s+all\s+denied/i',(string)file_get_contents($parent.'/.htaccess')))throw new RuntimeException('Private import storage is not configured.');
        if(!is_dir($dir)&&!mkdir($dir,0700))throw new RuntimeException('Private import storage is unavailable.');if(is_link($dir))throw new RuntimeException('Invalid private import storage.');
        $record=['id'=>(int)$video->getId(),'owner'=>(int)$video->getUsers_id(),'ticket'=>$ticket,'jobId'=>$job];
        if(self::active($video,$root)){$old=self::read($video,$root);if(!hash_equals($old['ticket'],$ticket))throw new RuntimeException('Import draft changed.');if(!$job)$record['jobId']=(int)($old['jobId']??0);}
        $file=self::file($video,$root);$tmp=tempnam($dir,'.import-');try{if(file_put_contents($tmp,json_encode($record))===false)throw new RuntimeException('Import marker could not be saved.');chmod($tmp,0600);if(!rename($tmp,$file))throw new RuntimeException('Import marker could not be activated.');}finally{if(is_file($tmp))unlink($tmp);}
    }
    public static function release($video,?string $root=null): void {self::read($video,$root);if(!unlink(self::file($video,$root)))throw new RuntimeException('Import draft hold could not be released.');unset(self::$publishing[(int)$video->getId()]);}
}
