// Curated JSON feed adapter: no undocumented AVideo API calls or embedded credentials.
const STORAGE_KEY='divine-media:saved:v1';
const avideoOrigin=(import.meta.env.VITE_AVIDEO_ORIGIN||'https://media.divinecreativegroup.com').replace(/\/$/,'');
const catalogEndpoint=import.meta.env.VITE_AVIDEO_CATALOG_URL||'/api/public-catalog';
// Default album artwork shipped with the frontend; override when a future release needs different artwork.
const murphyAlbumCover=import.meta.env.VITE_MURPHY_LEE_COVER_URL||'/2ndTimeAround.jpg';
export function readSaved(){try{const v=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');return Array.isArray(v)?v.filter(x=>typeof x==='string'):[]}catch{return []}}
export function writeSaved(saved){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(saved))}catch{/* storage may be disabled */}}
const safeUrl=(value)=>{if(typeof value!=='string'||!value.trim())return undefined;try{const u=new URL(value,window.location.origin);return ['http:','https:'].includes(u.protocol)?u.href:undefined}catch{return undefined}};
const safeAVideoUrl=(value)=>{if(typeof value!=='string'||!value.trim())return undefined;try{const u=new URL(value,avideoOrigin+'/');return u.protocol==='https:'&&u.origin===avideoOrigin?u.href:undefined}catch{return undefined}};
export function normalizeMedia(entry){if(!entry||typeof entry!=='object')return null;const title=typeof entry.title==='string'?entry.title.trim():'';const type=entry.type;if(!title||!['Watch','Listen','Live','Creators'].includes(type))return null;return {title:title.slice(0,140),type,tag:typeof entry.tag==='string'?entry.tag.slice(0,100):type.toUpperCase(),img:safeUrl(entry.img)||'/placeholder.svg',videoUrl:safeUrl(entry.videoUrl),audioUrl:safeUrl(entry.audioUrl),watchUrl:safeUrl(entry.watchUrl),creator:typeof entry.creator==='string'?entry.creator.slice(0,100):undefined,channelUrl:safeUrl(entry.channelUrl)}}
export async function loadMedia(){const url=import.meta.env.VITE_MEDIA_FEED_URL||'/media.json';const res=await fetch(url,{cache:'no-store'});if(!res.ok)throw Error('Media feed unavailable');const json=await res.json();if(!Array.isArray(json))throw Error('Media feed must be an array');return {items:json.map(normalizeMedia).filter(Boolean).slice(0,200)}}

/** Identify audio using explicit AVideo metadata and media paths; never infer from title alone. */
function isAVideoAudio(row){
 const fields=[row.type,row.mediaType,row.mimeType,row.mimetype,row.fileType,row.filename,row.fileName,row.file,row.videoFileName,row.videoFilename,row.audioFileName,row.audioFilename,row.path,row.extension,row.ext,row.format,row.category?.type,row.category?.name];
 const explicit=fields.filter(v=>typeof v==='string').map(v=>v.toLowerCase().trim());
 if(explicit.some(v=>v==='audio'||v.startsWith('audio/')||v==='mp3'||v==='m4a'||v==='aac'||v==='ogg'||v==='wav'||/\.(mp3|m4a|aac|ogg|oga|wav|flac)(?:[?#]|$)/i.test(v)))return true;
 if(Array.isArray(row.sources)&&row.sources.some(s=>typeof s?.type==='string'&&s.type.startsWith('audio/')))return true;
 return Boolean(row.audios?.mp3||row.audio?.mp3||row.mp3);
}
function audioSource(row){
 const sources=Array.isArray(row.sources)?row.sources:[];
 const match=sources.find(s=>s&&((typeof s.type==='string'&&s.type.startsWith('audio/'))||/\.(mp3|m4a|aac|ogg|oga|wav|flac)(?:[?#]|$)/i.test(s.src||'')));
 const candidates=[row.audioUrl,match?.src,row.audios?.mp3,row.audio?.mp3,row.mp3,row.audioUrl,row.audioURL,row.audioSrc,row.audioFile,row.mp3File];
 for(const candidate of candidates){const url=safeAVideoUrl(candidate);if(url)return url}
 return undefined;
}
/** Map the public AVideo API response; do not retain user/session fields. */
export function mapAVideoVideo(row){
 if(!row||typeof row!=='object'||!row.title||row.status!=='a'||row.externalOptions?.privacyInfo?.isPrivate||row.externalOptions?.privacyInfo?.password_protectd||row.externalOptions?.privacyInfo?.password_protected||row.isPrivate||row.only_for_paid||row.externalOptions?.privacyInfo?.only_for_paid)return null;
 const watchUrl=safeAVideoUrl(row.pageUrl||row.link||row.wwbnURL);
 if(!watchUrl)return null;
 const image=safeAVideoUrl(row.images?.posterLandscape||row.images?.poster||row.Poster||row.Thumbnail);
 const audio=row.mediaType==='audio'||/\/audio\/\d+(?:\/|$)/i.test(new URL(watchUrl).pathname)||isAVideoAudio(row);
 const sources=Array.isArray(row.sources)?row.sources.filter(s=>s?.type==='video/mp4'&&Number.isFinite(Number(s.res))):[];
 sources.sort((a,b)=>Number(b.res)-Number(a.res));
 const videoUrl=audio?undefined:safeAVideoUrl(sources[0]?.src||row.videos?.mp4?.['720']||row.videos?.mp4?.['480']);
 const item=normalizeMedia({title:row.title,tag:'AVIDEO · '+(row.channelName||(audio?'AUDIO':'VIDEO'))+(row.duration?' · '+row.duration:''),type:audio?'Listen':'Watch',watchUrl,img:audio&&[10,11,12,13,14,15,16].includes(Number(row.id))?murphyAlbumCover:image,videoUrl,audioUrl:audio?audioSource(row):undefined,creator:row.channelName||row.user||'Creator',channelUrl:row.wwbnChannelURL});
 return item?{...item,avideoId:row.id}:null;
}
/** Read sanitized public AVideo catalog from same-origin Netlify function; no credentials. */
export async function loadAVideoCatalog(){
 const res=await fetch(catalogEndpoint,{cache:'no-store',credentials:'omit'});
 if(!res.ok)throw Error('AVideo catalog HTTP '+res.status);
 const data=await res.json();
 if(data.error)throw Error('AVideo catalog API error');
 const rows=data.response?.rows;
 if(!Array.isArray(rows))throw Error('Unexpected AVideo API response');
 return rows.map(mapAVideoVideo).filter(Boolean);
}
