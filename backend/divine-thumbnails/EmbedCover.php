<?php
// Fixed-provider artwork only: no video downloads, API keys, or arbitrary remote URLs.
class DivineEmbedCover {
    public static function youtubeId(string $url): ?string {
        $parts=parse_url($url);if(!$parts||!in_array(strtolower($parts['scheme']??''),['http','https'],true)||isset($parts['user'])||isset($parts['pass'])||isset($parts['port'])){return null;}
        $host=strtolower($parts['host']??'');$path=$parts['path']??'';$id=null;
        if($host==='youtu.be'){$id=trim($path,'/');}
        elseif(in_array($host,['youtube.com','www.youtube.com','m.youtube.com','youtube-nocookie.com','www.youtube-nocookie.com'],true)){
            if($path==='/watch'){parse_str($parts['query']??'',$query);$id=$query['v']??null;}
            elseif(preg_match('~^/(?:embed|shorts|live)/([A-Za-z0-9_-]{11})/?$~D',$path,$matches)){$id=$matches[1];}
        }
        return is_string($id)&&preg_match('/^[A-Za-z0-9_-]{11}$/D',$id)?$id:null;
    }
    public static function install(string $url,string $filename,string $storage,string $destination): bool {
        $id=self::youtubeId($url);$root=realpath($storage);$parent=realpath(dirname($destination));
        if(!$id||!$root||!$parent||!preg_match('/^[A-Za-z0-9_.-]+$/D',$filename)||str_contains($filename,'..')||basename($destination)!==$filename.'.jpg'||!str_starts_with($parent.'/',rtrim($root,'/').'/')||is_link($destination)){return false;}
        foreach(['.jpg','.png','_portrait.jpg']as $ext){if(file_exists($parent.'/'.$filename.$ext)){return false;}}
        $image='';$curl=curl_init('https://i.ytimg.com/vi/'.$id.'/hqdefault.jpg');
        curl_setopt_array($curl,[CURLOPT_FOLLOWLOCATION=>false,CURLOPT_CONNECTTIMEOUT=>3,CURLOPT_TIMEOUT=>6,CURLOPT_SSL_VERIFYPEER=>true,CURLOPT_SSL_VERIFYHOST=>2,CURLOPT_WRITEFUNCTION=>static function($handle,$chunk)use(&$image){if(strlen($image)+strlen($chunk)>2097152){return 0;}$image.=$chunk;return strlen($chunk);}]);
        $ok=curl_exec($curl);$status=curl_getinfo($curl,CURLINFO_HTTP_CODE);curl_close($curl);
        $info=$ok&&$status===200?@getimagesizefromstring($image):false;if(!$info||$info[2]!==IMAGETYPE_JPEG||$info[0]<120||$info[1]<90){return false;}
        $temp=tempnam($parent,'.divine-embed-');if(!$temp){return false;}
        try{if(file_put_contents($temp,$image)!==strlen($image)){return false;}chmod($temp,0644);return @link($temp,$destination);}finally{@unlink($temp);}
    }
}
