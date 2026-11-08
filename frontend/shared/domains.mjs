// Public addresses only. Keep hosting credentials in provider configuration.
export const WATCH_ORIGIN='https://divinemedia.us';
export const MEDIA_ORIGIN='https://media.divinemedia.us';
export const LEGACY_MEDIA_ORIGIN='https://media.divinecreativegroup.com';
export const MEDIA_ORIGINS=[MEDIA_ORIGIN,LEGACY_MEDIA_ORIGIN];

/** Preserve media paths while migrating only explicitly trusted backend origins. */
export function canonicalMediaUrl(value,origin=MEDIA_ORIGIN){
 if(typeof value!=='string'||!value.trim())return null;
 try{
  const target=new URL(origin);
  const url=new URL(value,target);
  const accepted=MEDIA_ORIGINS.includes(target.origin)?MEDIA_ORIGINS:[target.origin];
  if(target.protocol!=='https:'||target.username||target.password||url.protocol!=='https:'||url.username||url.password||!accepted.includes(url.origin))return null;
  url.protocol=target.protocol;url.host=target.host;
  return url.href;
 }catch{return null}
}
