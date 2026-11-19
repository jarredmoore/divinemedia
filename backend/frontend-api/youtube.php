<?php
/** Fixed YouTube metadata endpoints; never fetch creator-supplied hosts or download media. */
class DivineYouTube {
    private $transport;
    public function __construct(?callable $transport=null){$this->transport=$transport;}
    public static function source(string $input): ?array {
        $p=parse_url(trim($input));if(!$p||strtolower($p['scheme']??'')!=='https'||isset($p['user'])||isset($p['pass'])||isset($p['port'])){return null;}
        $host=strtolower($p['host']??'');$path=rtrim($p['path']??'','/');
        if(!in_array($host,['youtube.com','www.youtube.com','m.youtube.com','youtu.be','youtube-nocookie.com','www.youtube-nocookie.com'],true)){return null;}
        $id=null;if($host==='youtu.be'){$id=ltrim($path,'/');}
        elseif($path==='/watch'){parse_str($p['query']??'',$q);$id=$q['v']??null;}
        elseif(preg_match('~^/(?:embed|shorts|live)/([A-Za-z0-9_-]{11})$~D',$path,$m)){$id=$m[1];}
        if(is_string($id)&&preg_match('/^[A-Za-z0-9_-]{11}$/D',$id)){return ['kind'=>'video','id'=>$id,'url'=>'https://www.youtube.com/watch?v='.$id];}
        if($host==='youtu.be'){return null;}
        if(preg_match('~^/channel/(UC[A-Za-z0-9_-]{22})(?:/(?:videos|shorts|streams))?$~D',$path,$m)){return ['kind'=>'channel','id'=>$m[1],'url'=>'https://www.youtube.com/channel/'.$m[1]];}
        if(preg_match('~^/@([A-Za-z0-9_.-]{3,100})(?:/(?:videos|shorts|streams))?$~D',$path,$m)){return ['kind'=>'channel','handle'=>$m[1],'url'=>'https://www.youtube.com/@'.$m[1]];}
        return null;
    }
    private function fetch(string $url): array {
        if($this->transport){return ($this->transport)($url);}
        $body='';$c=curl_init($url);curl_setopt_array($c,[CURLOPT_FOLLOWLOCATION=>false,CURLOPT_CONNECTTIMEOUT=>3,CURLOPT_TIMEOUT=>8,CURLOPT_SSL_VERIFYPEER=>true,CURLOPT_SSL_VERIFYHOST=>2,CURLOPT_USERAGENT=>'Mozilla/5.0 DivineMedia/3.3',CURLOPT_WRITEFUNCTION=>static function($c,$chunk)use(&$body){if(strlen($body)+strlen($chunk)>3000000){return 0;}$body.=$chunk;return strlen($chunk);}]);
        $ok=curl_exec($c);$status=(int)curl_getinfo($c,CURLINFO_HTTP_CODE);curl_close($c);if($ok===false){throw new RuntimeException('youtube_unavailable');}return ['status'=>$status,'body'=>$body];
    }
    private function api(string $resource,array $params,string $key): array {
        if($key===''){throw new RuntimeException('youtube_key_missing');}
        $response=$this->fetch('https://www.googleapis.com/youtube/v3/'.$resource.'?'.http_build_query($params+['key'=>$key]));$data=json_decode($response['body'],true);
        if($response['status']!==200||!is_array($data)){
            $reasons=array_column($data['error']['errors']??[],'reason');
            if(array_intersect($reasons,['quotaExceeded','dailyLimitExceeded'])){throw new RuntimeException('youtube_quota');}
            throw new RuntimeException('youtube_api_unavailable');
        }return $data;
    }
    public static function channelIdFromHtml(string $html): ?string {
        foreach(['~<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']https://www\.youtube\.com/channel/(UC[A-Za-z0-9_-]{22})["\'])[^>]*>~i','~"channelMetadataRenderer"\s*:\s*\{.{0,2400}?"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"~s']as $pattern){if(preg_match($pattern,$html,$m)){return $m[1];}}return null;
    }
    private static function item(string $id,array $snippet,array $extra=[]): array {
        return ['id'=>$id,'title'=>(string)($snippet['title']??'YouTube video'),'description'=>(string)($snippet['description']??''),'channelTitle'=>(string)($snippet['channelTitle']??''),'date'=>(string)($snippet['publishedAt']??''),'duration'=>(string)($extra['duration']??'PT0S'),'thumbs'=>'https://i.ytimg.com/vi/'.$id.'/hqdefault.jpg','link'=>'https://www.youtube.com/embed/'.$id];
    }
    public static function feed(string $xml,string $channelId): array {
        if(stripos($xml,'<!DOCTYPE')!==false){throw new RuntimeException('youtube_feed_invalid');}
        $previous=libxml_use_internal_errors(true);try{$feed=simplexml_load_string($xml,'SimpleXMLElement',LIBXML_NONET);}finally{libxml_clear_errors();libxml_use_internal_errors($previous);}
        $feedId=$feed?(string)$feed->children('http://www.youtube.com/xml/schemas/2015')->channelId:'';
        if(!$feed||!in_array($feedId,[$channelId,substr($channelId,2)],true)){throw new RuntimeException('youtube_feed_invalid');}
        $items=[];foreach($feed->entry as $entry){$yt=$entry->children('http://www.youtube.com/xml/schemas/2015');$id=(string)$yt->videoId;if(!preg_match('/^[A-Za-z0-9_-]{11}$/D',$id)){continue;}$media=$entry->children('http://search.yahoo.com/mrss/')->group;$items[]=self::item($id,['title'=>(string)$entry->title,'description'=>(string)$media->description,'channelTitle'=>(string)$feed->title,'publishedAt'=>(string)$entry->published]);if(count($items)>=15){break;}}
        return ['channel'=>['id'=>$channelId,'title'=>(string)$feed->title,'url'=>'https://www.youtube.com/channel/'.$channelId],'items'=>$items,'mode'=>'feed','notice'=>'Showing up to 15 recent public uploads from YouTube’s channel feed. Full channel browsing needs available YouTube API quota.','next'=>null];
    }
    public function single(string $id): array {
        $response=$this->fetch('https://www.youtube.com/oembed?format=json&url='.rawurlencode('https://www.youtube.com/watch?v='.$id));$data=json_decode($response['body'],true);
        if($response['status']!==200||!is_array($data)||empty($data['title'])){throw new RuntimeException('youtube_video_unavailable');}
        return self::item($id,['title'=>$data['title'],'channelTitle'=>$data['author_name']??'']);
    }
    public function preview(array $source,string $key,string $page=''): array {
        if($source['kind']==='video'){return ['channel'=>null,'items'=>[$this->single($source['id'])],'mode'=>'single','notice'=>'YouTube hosts this video. Its own playback and embedding restrictions still apply.','next'=>null];}
        $channelId=$source['id']??null;
        try{
            $lookup=$channelId?['id'=>$channelId]:['forHandle'=>$source['handle']];$data=$this->api('channels',['part'=>'id,snippet,contentDetails']+$lookup,$key);$channel=$data['items'][0]??null;
            if(!$channel){throw new RuntimeException('youtube_channel_not_found');}$channelId=$channel['id'];
            $params=['part'=>'snippet,contentDetails','playlistId'=>$channel['contentDetails']['relatedPlaylists']['uploads'],'maxResults'=>25];if($page!==''){$params['pageToken']=$page;}
            $list=$this->api('playlistItems',$params,$key);$ids=[];foreach($list['items']??[]as $item){$id=$item['contentDetails']['videoId']??'';if(preg_match('/^[A-Za-z0-9_-]{11}$/D',$id)){$ids[]=$id;}}
            $videos=$ids?$this->api('videos',['part'=>'snippet,contentDetails,status','id'=>implode(',',$ids)],$key):['items'=>[]];$items=[];
            foreach($videos['items']??[]as $v){if(($v['status']['privacyStatus']??'')!=='public'||empty($v['status']['embeddable'])||!preg_match('/^[A-Za-z0-9_-]{11}$/D',$v['id']??'')){continue;}$items[]=self::item($v['id'],$v['snippet'],$v['contentDetails']);}
            return ['channel'=>['id'=>$channelId,'title'=>$channel['snippet']['title'],'url'=>'https://www.youtube.com/channel/'.$channelId],'items'=>$items,'mode'=>'api','notice'=>'Public videos that allow embedding. Select the videos to add to your Divine Media channel.','next'=>$list['nextPageToken']??null];
        }catch(RuntimeException $e){
            if($page!==''||$e->getMessage()==='youtube_channel_not_found'){throw $e;}
            if(!$channelId){$response=$this->fetch($source['url']);if($response['status']!==200||!($channelId=self::channelIdFromHtml($response['body']))){throw new RuntimeException('youtube_channel_unavailable');}}
            $response=$this->fetch('https://www.youtube.com/feeds/videos.xml?channel_id='.$channelId);if($response['status']!==200){throw new RuntimeException('youtube_feed_unavailable');}return self::feed($response['body'],$channelId);
        }
    }
}
