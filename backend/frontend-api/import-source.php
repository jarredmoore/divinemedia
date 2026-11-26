<?php
declare(strict_types=1);
/** Public provider links only. No credentials, local files, generic scraper or arbitrary redirects. */
final class DivineImportSource {
    public static function url(string $input,?callable $resolve=null): string {
        $input=trim($input);$p=parse_url($input);
        if(strlen($input)>2000||preg_match('/[\x00-\x20\\\\]/',$input)||!$p||strtolower($p['scheme']??'')!=='https'||isset($p['user'])||isset($p['pass'])||isset($p['port'])||isset($p['fragment'])){throw new InvalidArgumentException('Use a public HTTPS video link without credentials.');}
        $host=strtolower($p['host']??'');
        if(!preg_match('/^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/D',$host)||preg_match('/\.(?:local|internal|localhost|test|invalid|example)$/D',$host)){throw new InvalidArgumentException('This host is not supported.');}
        $providers=['youtube.com','youtu.be','youtube-nocookie.com','vimeo.com','dailymotion.com','dai.ly','twitch.tv','soundcloud.com','tiktok.com','instagram.com','facebook.com','fb.watch','twitter.com','x.com','reddit.com','bandcamp.com','archive.org'];
        if(!array_filter($providers,static fn($provider)=>$host===$provider||str_ends_with($host,'.'.$provider))){throw new InvalidArgumentException('This provider is not enabled for frontend importing yet. Use a supported public video page or upload the file.');}
        parse_str($p['query']??'',$query);foreach(array_keys($query)as $key){if(preg_match('/(?:password|token|secret|signature|authorization|cookie)/i',(string)$key)){throw new InvalidArgumentException('Use the public page link, without private access tokens.');}}
        self::publicHost($host,$resolve);return 'https://'.$host.($p['path']??'/').(isset($p['query'])?'?'.$p['query']:'');
    }
    public static function publicHost(string $host,?callable $resolve=null): void {
        $ips=$resolve?$resolve($host):array_unique(array_merge(gethostbynamel($host)?:[],array_column(dns_get_record($host,DNS_AAAA)?:[],'ipv6')));
        if(!$ips||count($ips)>32){throw new InvalidArgumentException('The provider could not be resolved.');}
        foreach($ips as $ip){
            if(!filter_var($ip,FILTER_VALIDATE_IP,FILTER_FLAG_NO_PRIV_RANGE|FILTER_FLAG_NO_RES_RANGE)||str_starts_with(strtolower($ip),'::ffff:')){throw new InvalidArgumentException('Private network sources are not supported.');}
            if(filter_var($ip,FILTER_VALIDATE_IP,FILTER_FLAG_IPV4)){$n=ip2long($ip);foreach([['100.64.0.0',10],['198.18.0.0',15],['192.0.0.0',24]]as [$network,$bits]){if(($n&(-1<<(32-$bits)))===(ip2long($network)&(-1<<(32-$bits)))){throw new InvalidArgumentException('Reserved network sources are not supported.');}}}
        }
    }
    public static function metadata(array $info,string $source,?callable $resolve=null): array {
        $extractor=(string)($info['extractor_key']??$info['extractor']??'');
        if($extractor===''||stripos($extractor,'generic')!==false||isset($info['entries'])||!empty($info['is_live'])||!empty($info['has_drm'])||isset($info['availability'])&&!in_array($info['availability'],['public','unlisted'],true)){throw new InvalidArgumentException('Choose a single public, non-live video supported by the installed downloader.');}
        $hosts=[];foreach(array_merge([$info],$info['formats']??[])as $format){if(!empty($format['has_drm']))continue;$url=$format['url']??null;if(!$url)continue;$p=parse_url($url);if(!$p||!in_array(strtolower($p['scheme']??''),['http','https'],true)||isset($p['user'])||isset($p['pass'])||isset($p['port'])){throw new InvalidArgumentException('Unsupported provider media address.');}$host=strtolower($p['host']??'');if(!isset($hosts[$host])){if(count($hosts)>=32)throw new InvalidArgumentException('Too many provider hosts.');self::publicHost($host,$resolve);$hosts[$host]=true;}}
        $title=mb_substr(trim(strip_tags((string)($info['title']??''))),0,140);if($title===''){throw new InvalidArgumentException('This provider did not return a video title.');}
        $seconds=max(0,(int)($info['duration']??0));if($seconds>43200||(int)($info['filesize']??0)>4294967296){throw new InvalidArgumentException('This source exceeds the import limit (12 hours / 4 GB).');}
        return ['url'=>$source,'title'=>$title,'description'=>mb_substr(strip_tags((string)($info['description']??'')),0,10000),'provider'=>mb_substr($extractor,0,80),'durationSeconds'=>$seconds,'notice'=>'Import uses the existing Encoder. Availability can change; imported media stays private until you publish it.'];
    }
}
