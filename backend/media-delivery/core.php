<?php
declare(strict_types=1);

if(isset($_SERVER['SCRIPT_FILENAME']) && realpath((string)$_SERVER['SCRIPT_FILENAME'])===__FILE__ && PHP_SAPI!=='cli') {http_response_code(404);exit;}

/** Pure delivery policy. No native bootstrap, network calls, or request side effects. */
final class DivineMediaAssets {
    public const MIME = [
        'mp4'=>'video/mp4','webm'=>'video/webm','mp3'=>'audio/mpeg','ogg'=>'audio/ogg',
        'm4a'=>'audio/mp4','wav'=>'audio/wav','flac'=>'audio/flac',
        'jpg'=>'image/jpeg','jpeg'=>'image/jpeg','png'=>'image/png','webp'=>'image/webp','gif'=>'image/gif',
        'pdf'=>'application/pdf','vtt'=>'text/vtt','srt'=>'application/x-subrip',
        'm3u8'=>'application/vnd.apple.mpegurl','ts'=>'video/mp2t','m4s'=>'video/iso.segment','key'=>'application/octet-stream',
    ];
    public static function path(string $path): string {
        if (strlen($path)>1024 || !preg_match('~^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$~D',$path)) {
            throw new RuntimeException('Invalid asset');
        }
        foreach(explode('/',$path) as $part) {
            if($part[0]==='.' || str_contains($part,'..')) { throw new RuntimeException('Invalid asset'); }
        }
        return $path;
    }
    public static function mime(string $path): string {
        $extension=strtolower(pathinfo(self::path($path),PATHINFO_EXTENSION));
        if(!isset(self::MIME[$extension])) { throw new RuntimeException('Unsupported asset'); }
        return self::MIME[$extension];
    }
    /** Exact native names and a closed variant grammar, never a filename-prefix lookup. */
    public static function owner(string $path, array $records): int {
        self::path($path); self::mime($path); $ids=[];
        foreach($records as $record) {
            $base=(string)($record['filename']??'');
            if($base==='' || str_contains($base,'/') || $base[0]==='.' || str_contains($base,'..')) { continue; }
            $q=preg_quote($base,'~');
            $flat='~^'.$q.'(?:_(?:Low|SD|HD|[0-9]{3,4}|portrait|thumbs|thumbsV2|thumbsSmallV2|portrait_thumbsV2|portrait_thumbsSmallV2|thumbsV2_jpg|thumbsSmallV2_jpg|portrait_thumbsV2_jpg|portrait_thumbsSmallV2_jpg))?\.(?:mp4|webm|mp3|ogg|m4a|wav|flac|jpg|jpeg|png|webp|gif|pdf|vtt|srt)$~D';
            // Each HLS directory belongs to exactly one native record, including adaptive variants.
            $hls='~^'.$q.'(?:_(?:Low|SD|HD|[0-9]{3,4}))?/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+\.(?:m3u8|ts|m4s|mp4|key|vtt)$~D';
            if(preg_match($flat,$path)||str_starts_with($path,$base.'/')&&preg_match($flat,substr($path,strlen($base)+1))||preg_match($hls,$path)) { $ids[(int)$record['id']]=true; }
        }
        if(count($ids)!==1 || (int)array_key_first($ids)<=0) { throw new RuntimeException('Unregistered asset'); }
        return (int)array_key_first($ids);
    }
    public static function siteAsset(string $path): bool {
        self::path($path);
        return (bool)preg_match('~^(?:faviconPWA(?:72|96|120|128|144|152|180|192|384|512)\.png|userPhoto/photo[0-9]+\.(?:jpg|jpeg|png|webp)|categories/(?:assets/)?[A-Za-z0-9_-]+\.(?:jpg|jpeg|png|webp))$~D',$path);
    }
    public static function file(string $root, string $path): string {
        self::path($path);self::mime($path);$base=realpath($root);$file=realpath($root.'/'.$path);
        if(!$base || !$file || !str_starts_with($file,$base.'/') || !is_file($file)) { throw new RuntimeException('Unavailable asset'); }
        // Reject even in-root symlinks: ownership must match the physical registered name.
        $cursor=$base;
        foreach(explode('/',$path) as $part) { $cursor.='/'.$part;if(is_link($cursor)) { throw new RuntimeException('Linked asset'); } }
        return $file;
    }
    /** Keep manifests in one authorized directory. Reject remote/data/escaping URI references. */
    public static function manifest(string $text, string $directory, string $prefix='/divine-media/assets/'): string {
        if(strlen($text)>1048576 || !str_starts_with(ltrim($text),'#EXTM3U')) { throw new RuntimeException('Invalid manifest'); }
        self::path($directory);
        $uri=static function(string $value) use($directory,$prefix): string {
            self::path($value);self::mime($value);
            return $prefix.$directory.'/'.$value;
        };
        $lines=preg_split('/\r?\n/',$text);
        foreach($lines as &$line) {
            $line=trim($line);if($line==='')continue;
            if($line[0]!=='#') { $line=$uri($line); }
            else {
                $line=preg_replace_callback('/URI="([^"]*)"/',static fn($m)=>'URI="'.$uri($m[1]).'"',$line);
                if(preg_match('/URI=(?!")/',$line)) { throw new RuntimeException('Invalid manifest URI'); }
            }
        }
        return implode("\n",$lines);
    }
}

/** Opaque, single-use handoffs. Stored outside the document root, never in URLs. */
final class DivineDeliveryStore {
    public function __construct(private string $root) {
        if(!is_dir($root) && !mkdir($root,0700,true) && !is_dir($root)) { throw new RuntimeException('Delivery unavailable'); }
        if(is_link($root)) { throw new RuntimeException('Invalid delivery store'); }
    }
    private function filename(string $kind,string $token): string {
        if(!in_array($kind,['grant','session'],true)||!preg_match('/^[a-f0-9]{64}$/D',$token)) { throw new RuntimeException('Invalid grant'); }
        return $this->root.'/'.$kind.'-'.hash('sha256',$token).'.json';
    }
    public function issue(string $kind,array $record,int $expires): string {
        $token=bin2hex(random_bytes(32));$file=$this->filename($kind,$token);
        $old=umask(0077);
        try {
            $handle=fopen($file,'x');if(!$handle) { throw new RuntimeException('Delivery unavailable'); }
            try { $json=json_encode(['expires'=>$expires,'record'=>$record],JSON_THROW_ON_ERROR);if(fwrite($handle,$json)!==strlen($json))throw new RuntimeException('Delivery unavailable'); }
            finally { fclose($handle); }
        } finally { umask($old); }
        return $token;
    }
    public function collect(int $now): void {
        $checked=0;
        foreach(new DirectoryIterator($this->root) as $entry) {
            if($entry->isDot()||$entry->isLink()||!$entry->isFile()||!preg_match('/^(?:grant|session)-[a-f0-9]{64}\.json$/D',$entry->getFilename()))continue;
            if(++$checked>100)break;
            $h=@fopen($entry->getPathname(),'r+');if(!$h)continue;
            try {
                if(!flock($h,LOCK_EX|LOCK_NB))continue;
                $data=json_decode(stream_get_contents($h,4097),true);
                if(is_array($data)&&is_int($data['expires']??null)&&$data['expires']<=$now) {
                    ftruncate($h,0);fflush($h);@unlink($entry->getPathname());
                }
            } finally {flock($h,LOCK_UN);fclose($h);}
        }
    }
    public function read(string $kind,string $token,int $now,bool $consume=false): array {
        $file=$this->filename($kind,$token);
        if(is_link($file))throw new RuntimeException('Invalid grant');
        $h=@fopen($file,$consume?'r+':'r');if(!$h)throw new RuntimeException('Invalid grant');
        try {
            if(!flock($h,$consume?LOCK_EX:LOCK_SH))throw new RuntimeException('Delivery unavailable');
            $json=stream_get_contents($h,4097);$data=strlen($json)<=4096?json_decode($json,true):null;
            // Clear under the exclusive lock before unlinking: a concurrent opener cannot replay it.
            if($consume) { ftruncate($h,0);fflush($h);unlink($file); }
            if(!is_array($data)||($data['expires']??0)<=$now||!is_array($data['record']??null)) { throw new RuntimeException('Expired grant'); }
            return $data['record'];
        } finally { flock($h,LOCK_UN);fclose($h); }
    }
}
