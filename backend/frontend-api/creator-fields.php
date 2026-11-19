<?php
// Small shared validation contract, independent of native bootstrap for contract tests.
class DivineCreatorFields {
    const MAX_MEDIA=4294967296;const MAX_IMAGE=2097152;
    public static function normalize(array $body): array {
        $title=trim(strip_tags((string)($body['title']??'')));if($title===''||mb_strlen($title)>140){throw new InvalidArgumentException('Enter a title of up to 140 characters.');}
        $description=trim(strip_tags((string)($body['description']??'')));if(mb_strlen($description)>10000){throw new InvalidArgumentException('Keep the description under 10,000 characters.');}
        $visibility=(string)($body['visibility']??'private');if(!in_array($visibility,['private','public','unlisted'],true)){throw new InvalidArgumentException('Choose a valid visibility.');}
        $out=['title'=>$title,'description'=>$description,'visibility'=>$visibility];
        if(isset($body['categoryId'])&&$body['categoryId']!==''){$id=filter_var($body['categoryId'],FILTER_VALIDATE_INT,['options'=>['min_range'=>1]]);if(!$id){throw new InvalidArgumentException('Choose a valid category.');}$out['categoryId']=$id;}
        foreach(['canShare','canDownload']as $key){if(array_key_exists($key,$body)){if(!is_bool($body[$key])){throw new InvalidArgumentException('Invalid sharing setting.');}$out[$key]=$body[$key];}}
        if(array_key_exists('rating',$body)){$rating=(string)$body['rating'];if(!in_array($rating,['','g','pg','pg-13','r','nc-17','ma'],true)){throw new InvalidArgumentException('Choose a valid content rating.');}$out['rating']=$rating;}
        if(isset($body['tags'])){
            if(!is_array($body['tags'])||count($body['tags'])>20){throw new InvalidArgumentException('Invalid tag groups.');}$out['tags']=[];
            foreach($body['tags']as $group=>$names){if(!ctype_digit((string)$group)||!is_array($names)||count($names)>20){throw new InvalidArgumentException('Use up to 20 tags per group.');}$clean=[];foreach($names as $name){if(!is_string($name)||mb_strlen($name)>60){throw new InvalidArgumentException('Keep each tag under 60 characters.');}$name=trim(preg_replace('/[^\p{L}\p{N}\s_-]/u','',$name));if($name!==''){$clean[]=$name;}}$out['tags'][(int)$group]=array_values(array_unique($clean));}
        }return $out;
    }
    public static function imageInfo(string $bytes): array {
        if(strlen($bytes)<1||strlen($bytes)>self::MAX_IMAGE){throw new InvalidArgumentException('Choose a thumbnail smaller than 2 MB.');}
        $info=@getimagesizefromstring($bytes);if(!$info||!in_array($info[2],[IMAGETYPE_JPEG,IMAGETYPE_PNG,IMAGETYPE_WEBP],true)||$info[0]>4096||$info[1]>4096){throw new InvalidArgumentException('Use a JPG, PNG or WebP image up to 4096 × 4096 pixels.');}return $info;
    }
}
