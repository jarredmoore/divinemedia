// Curated JSON feed adapter: no undocumented AVideo API calls or embedded credentials.
const STORAGE_KEY='divine-media:saved:v1';
export function readSaved(){try{const v=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');return Array.isArray(v)?v.filter(x=>typeof x==='string'):[]}catch{return []}}
export function writeSaved(saved){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(saved))}catch{/* storage may be disabled */}}
const safeUrl=(value)=>{if(typeof value!=='string'||!value.trim())return undefined;try{const u=new URL(value,window.location.origin);return ['http:','https:'].includes(u.protocol)?u.href:undefined}catch{return undefined}};
export function normalizeMedia(entry){if(!entry||typeof entry!=='object')return null;const title=typeof entry.title==='string'?entry.title.trim():'';const type=entry.type;if(!title||!['Watch','Listen','Live','Creators'].includes(type))return null;return {title:title.slice(0,140),type,tag:typeof entry.tag==='string'?entry.tag.slice(0,100):type.toUpperCase(),img:safeUrl(entry.img)||'/placeholder.svg',videoUrl:safeUrl(entry.videoUrl),audioUrl:safeUrl(entry.audioUrl),watchUrl:safeUrl(entry.watchUrl),creator:typeof entry.creator==='string'?entry.creator.slice(0,100):undefined,channelUrl:safeUrl(entry.channelUrl)}}
export async function loadMedia(){const url=import.meta.env.VITE_MEDIA_FEED_URL||'/media.json';const res=await fetch(url,{cache:'no-store'});if(!res.ok)throw Error('Media feed unavailable');const json=await res.json();if(!Array.isArray(json))throw Error('Media feed must be an array');return {items:json.map(normalizeMedia).filter(Boolean).slice(0,200)}}

/** Map the actual AVideo API response; no user/session fields are retained. */
export function mapAVideoVideo(row){
 if(!row||typeof row!=='object'||!row.title||row.status!=='a'||row.externalOptions?.privacyInfo?.isPrivate||row.externalOptions?.privacyInfo?.password_protectd||row.only_for_paid||row.externalOptions?.privacyInfo?.only_for_paid)return null;
 const watchUrl=safeUrl(row.pageUrl||row.link||row.wwbnURL);
 if(!watchUrl||new URL(watchUrl).origin!=='https://localhost')return null;
 const image=safeUrl(row.images?.posterLandscape||row.images?.poster||row.Poster||row.Thumbnail);
 const sources=Array.isArray(row.sources)?row.sources.filter(s=>s?.type==='video/mp4'&&Number.isFinite(Number(s.res))):[];
 sources.sort((a,b)=>Number(b.res)-Number(a.res));
 const videoUrl=safeUrl(sources[0]?.src||row.videos?.mp4?.['720']||row.videos?.mp4?.['480']);
 const item=normalizeMedia({title:row.title,tag:'AVIDEO · '+(row.channelName||'VIDEO')+(row.duration?' · '+row.duration:''),type:'Watch',watchUrl,img:image,videoUrl,creator:row.channelName||row.user||'Creator',channelUrl:row.wwbnChannelURL});
 return item?{...item,avideoId:row.id}:null;
}
/** Read public AVideo catalog via local Vite proxy; no credentials. */
export async function loadAVideoCatalog(){
 const res=await fetch('/avideo-local/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1',{cache:'no-store'});
 if(!res.ok)throw Error('AVideo catalog HTTP '+res.status);
 const data=await res.json();
 if(data.error)throw Error('AVideo catalog API error');
 const rows=data.response?.rows;
 if(!Array.isArray(rows))throw Error('Unexpected AVideo API response');
 return rows.map(mapAVideoVideo).filter(Boolean);
}
