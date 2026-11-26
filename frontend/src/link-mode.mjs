export function linkMode(value,preference='auto',canEmbed=true){
 try{const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password||u.port)return 'invalid';const youtube=['youtube.com','www.youtube.com','m.youtube.com','youtu.be','youtube-nocookie.com','www.youtube-nocookie.com'].includes(u.hostname);return youtube&&canEmbed&&preference!=='import'?'embed':'import'}catch{return 'invalid'}
}
