// Public-only AVideo catalog adapter. Never return the upstream API response verbatim.
const ORIGIN='https://media.divinecreativegroup.com';
const endpoint=new URL('/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1',ORIGIN);
function mediaUrl(value){
 if(typeof value!=='string'||!value.trim())return null;
 try{
  const u=new URL(value,ORIGIN);
  if(u.protocol!=='https:'||u.origin!==ORIGIN)return null;
  return u.href;
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
  const publicRows=rows.filter(isPublic).slice(0,50).map(row=>{
   const sources=Array.isArray(row.sources)?row.sources.filter(s=>s?.type==='video/mp4').sort((a,b)=>Number(b.res||0)-Number(a.res||0)):[];
   const pageUrl=mediaUrl(row.pageUrl||row.link||row.wwbnURL);
   if(!pageUrl)return null;
   return {
    id:row.id,title:String(row.title||'').slice(0,140),status:'a',
    pageUrl,channelName:String(row.channelName||'').slice(0,100),
    duration:String(row.duration||'').slice(0,30),
    images:{posterLandscape:mediaUrl(row.images?.posterLandscape||row.images?.poster||row.Poster||row.Thumbnail)},
    sources:sources.slice(0,1).map(s=>({type:'video/mp4',res:Number(s.res)||0,src:mediaUrl(s.src)})).filter(s=>s.src)
   };
  }).filter(row=>row?.title);
  return new Response(JSON.stringify({response:{rows:publicRows}}),{status:200,headers:{'content-type':'application/json','cache-control':'public, max-age=60'}});
 }catch{
  return new Response(JSON.stringify({error:'Public media catalog unavailable'}),{status:502,headers:{'content-type':'application/json','cache-control':'no-store'}});
 }
}
export const config={path:'/api/public-catalog'};
