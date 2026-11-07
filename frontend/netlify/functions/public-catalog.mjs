// Public-only AVideo catalog adapter. Never return the upstream API response verbatim.
import {MEDIA_ORIGIN,MEDIA_ORIGINS,canonicalMediaUrl} from '../../shared/domains.mjs';
const ORIGIN=process.env.AVIDEO_ORIGIN||MEDIA_ORIGIN;
if(!MEDIA_ORIGINS.includes(ORIGIN))throw Error('Unsupported public media origin');
const endpoint=new URL('/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1',ORIGIN);
const mediaUrl=(value)=>canonicalMediaUrl(value,ORIGIN);

function isAudioPage(url){try{return /\/audio\/\d+(?:\/|$)/i.test(new URL(url).pathname)}catch{return false}}
export function findPublicAudioUrl(html){
 // Read only public HTML. Never expose tokens, query-string credentials, or private media.
 const text=html.replaceAll('&amp;','&').replaceAll('\\/','/');
 // Consume complete external URLs before relative paths, so an untrusted host
 // cannot be mistaken for a relative /videos/ URL during HTML discovery.
 const candidates=[...text.matchAll(/https?:\/\/[^\s"'<>\\]+|\/videos\/[a-zA-Z0-9_./%-]+\.(?:mp3|m4a|ogg|wav)(?![a-zA-Z0-9])/gi)];
 for(const match of candidates){
  const url=mediaUrl(match[0]);
  if(url&&new URL(url).pathname.startsWith('/videos/')&&/\.(mp3|m4a|ogg|wav)$/i.test(new URL(url).pathname)&&!new URL(url).search)return url;
 }
 return null;
}
export function publicAudioSource(row){
 const sources=Array.isArray(row.sources)?row.sources:[];
 const candidates=[row.audioUrl,row.audioURL,row.mp3,row.audios?.mp3,row.audio?.mp3,
 ...sources.filter(s=>s&&(/^audio\//i.test(s.type||'')||/\.(mp3|m4a|aac|ogg|oga|wav|flac)(?:[?#]|$)/i.test(s.src||''))).map(s=>s.src)];
 for(const candidate of candidates){const url=mediaUrl(candidate);if(url)return url}
 return null;
}
export function isAudio(row,pageUrl){
 return isAudioPage(pageUrl)||[row.type,row.mediaType,row.mimeType].some(v=>typeof v==='string'&&(v.toLowerCase()==='audio'||/^audio\//i.test(v)))||Boolean(publicAudioSource(row));
}
async function resolveAudio(pageUrl){
 if(!isAudioPage(pageUrl))return null;
 try{
  const response=await fetch(pageUrl,{signal:AbortSignal.timeout(3500),headers:{accept:'text/html'}});
  if(!response.ok||!(response.headers.get('content-type')||'').includes('text/html'))return null;
  const html=(await response.text()).slice(0,650000);
  return findPublicAudioUrl(html);
 }catch{return null}
}
function isPublic(row){
 const p=row?.externalOptions?.privacyInfo||{};
 return row?.status==='a'&&!p.isPrivate&&!p.password_protectd&&!p.password_protected&&!p.only_for_paid&&!row.only_for_paid&&!row?.isPrivate;
}
export default async function handler(){
 try{
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),8000);
  let response;
  try{response=await fetch(endpoint,{signal:controller.signal,headers:{accept:'application/json'}})}
  finally{clearTimeout(timer)}
  if(!response.ok)throw Error('Upstream catalog unavailable');
  const data=await response.json();
  const rows=data?.response?.rows;
  if(!Array.isArray(rows))throw Error('Unexpected upstream catalog format');
  const publicRows=await Promise.all(rows.filter(isPublic).slice(0,50).map(async row=>{
   const sources=Array.isArray(row.sources)?row.sources.filter(s=>s?.type==='video/mp4').sort((a,b)=>Number(b.res||0)-Number(a.res||0)):[];
   const pageUrl=mediaUrl(row.pageUrl||row.link||row.wwbnURL);
   if(!pageUrl)return null;
   const audio=isAudio(row,pageUrl);
   const directAudio=audio?publicAudioSource(row)||await resolveAudio(pageUrl):null;
   return {
    mediaType:audio?'audio':'video',audioUrl:directAudio,
    id:row.id,title:String(row.title||'').slice(0,140),status:'a',
    pageUrl,channelName:String(row.channelName||'').slice(0,100),
    duration:String(row.duration||'').slice(0,30),
    images:{posterLandscape:mediaUrl(row.images?.posterLandscape||row.images?.poster||row.Poster||row.Thumbnail)},
    sources:sources.slice(0,1).map(s=>({type:'video/mp4',res:Number(s.res)||0,src:mediaUrl(s.src)})).filter(s=>s.src)
   };
  }));
  const sanitizedRows=publicRows.filter(row=>row?.title);
  return new Response(JSON.stringify({response:{rows:sanitizedRows}}),{status:200,headers:{'content-type':'application/json','cache-control':'public, max-age=60'}});
 }catch{
  return new Response(JSON.stringify({error:'Public media catalog unavailable'}),{status:502,headers:{'content-type':'application/json','cache-control':'no-store'}});
 }
}
export const config={path:'/api/public-catalog'};
