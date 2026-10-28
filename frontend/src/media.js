// Curated JSON feed adapter: no undocumented AVideo API calls or embedded credentials.
const STORAGE_KEY='divine-media:saved:v1';
export function readSaved(){try{const v=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');return Array.isArray(v)?v.filter(x=>typeof x==='string'):[]}catch{return []}}
export function writeSaved(saved){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(saved))}catch{/* storage may be disabled */}}
const safeUrl=(value)=>{if(typeof value!=='string'||!value.trim())return undefined;try{const u=new URL(value,window.location.origin);return ['http:','https:'].includes(u.protocol)?u.href:undefined}catch{return undefined}};
export function normalizeMedia(entry){if(!entry||typeof entry!=='object')return null;const title=typeof entry.title==='string'?entry.title.trim():'';const type=entry.type;if(!title||!['Watch','Listen','Live','Creators'].includes(type))return null;return {title:title.slice(0,140),type,tag:typeof entry.tag==='string'?entry.tag.slice(0,100):type.toUpperCase(),img:safeUrl(entry.img)||'/placeholder.svg',videoUrl:safeUrl(entry.videoUrl),audioUrl:safeUrl(entry.audioUrl),watchUrl:safeUrl(entry.watchUrl)}}
export async function loadMedia(){const url=import.meta.env.VITE_MEDIA_FEED_URL||'/media.json';const res=await fetch(url,{cache:'no-store'});if(!res.ok)throw Error('Media feed unavailable');const json=await res.json();if(!Array.isArray(json))throw Error('Media feed must be an array');return {items:json.map(normalizeMedia).filter(Boolean).slice(0,200)}}

/** Public video catalog, using the documented AVideo API plugin. No credentials. */
export async function loadAVideoCatalog(){
 const res=await fetch('/avideo-local/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1',{cache:'no-store'});
 if(!res.ok)throw Error('AVideo catalog HTTP '+res.status);
 const data=await res.json();
 if(data.error)throw Error('AVideo catalog API error');
 const rows=data.response?.rows;
 if(!Array.isArray(rows))throw Error('AVideo API plugin not enabled or unexpected response');
 const base='https://localhost';
 return rows.filter(row=>row&&typeof row==='object'&&row.title).map(row=>{
  const watchUrl=safeUrl(row.link||row.videoLink||row.url||row.href);
  const img=safeUrl(row.poster||row.posterURL||row.image||row.thumbnail||row.img);
  return normalizeMedia({title:row.title,tag:'AVIDEO · '+(row.channelName||row.channel||'VIDEO'),type:'Watch',watchUrl:watchUrl||(row.id===1?'https://localhost/channel/admin/video/1/divine-creative-group-_-new-media-%C2%B7-art-%C2%B7-entertainment':undefined),img:img||'/placeholder.svg'});
 }).filter(item=>item?.watchUrl?.startsWith(base+'/'));
}
