// Same-origin boundary for the native AVideo adapter. Never proxy arbitrary URLs or HTML.
const actions=new Set(['playback','captcha','catalog','session','video-unlock','login','logout','register','recover','reset-password','verify-email','categories','channels','channel','video','comments','comment','reaction','playlists','playlist','playlist-item','library','notifications','notification-read','follow','playlist-order','live','studio','studio-save','creator-videos','creator-video','upload-init','upload-chunk','upload-cancel','encoder-queue','encoder-action','profile']);
const reads=new Set(['captcha','catalog','session','categories','channels','channel','video','comments','playlists','playlist','library','notifications','live','studio','creator-videos','encoder-queue','profile']);
const sessionPattern=/^[A-Za-z0-9,-]{22,128}$/;
export function appOrigin(value){try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&(u.hostname==='divinemedia.us'||/^(?:[a-f0-9]{24}|deploy-preview-\d+)--mediaproduction\.netlify\.app$/.test(u.hostname))?u.origin:null}catch{return null}}
export function sessionCookie(raw=''){const matches=raw.split(';').map(x=>x.trim()).filter(x=>x.startsWith('__Host-dm_session='));if(matches.length!==1)return '';const value=matches[0].slice('__Host-dm_session='.length);return sessionPattern.test(value)?value:''}
const json=(error,status)=>new Response(JSON.stringify({error}),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
export default async function handler(request,context={}){
 const url=new URL(request.url),action=url.pathname.split('/').filter(Boolean).at(-1);
 if(!actions.has(action))return json('Unknown platform action',404);
 if(!['GET','POST'].includes(request.method)||request.method==='GET'&&!reads.has(action))return json('Method not allowed',405);
 const origin=appOrigin(url.origin);
 if(!origin)return json('Unsupported frontend origin',403);
 if(request.method==='POST'&&(request.headers.get('origin')!==origin||request.headers.get('sec-fetch-site')==='cross-site'))return json('Request origin rejected',403);
 const key=process.env.DIVINE_GATEWAY_KEY;
 if(!key||key.length<32)return json('Account services are not configured yet',503);
 const target=new URL('https://media.divinemedia.us/divine-api/index.php');
 target.searchParams.set('action',action);
 for(const name of ['id','video','page','category','channel','kind','playlist','mode']){const value=url.searchParams.get(name);if(value!==null&&value.length<=120)target.searchParams.set(name,value)}
 try{
  let body;
  if(request.method==='POST'){
   const type=request.headers.get('content-type')||'';
   if(action==='upload-chunk'?!type.startsWith('multipart/form-data; boundary='):!type.startsWith('application/json'))return json('Unsupported request format',415);
   if(Number(request.headers.get('content-length'))>2.5*1024*1024)return json('Request is too large',413);
   body=await request.arrayBuffer();if(body.byteLength>2.5*1024*1024)return json('Request is too large',413);
   if(action!=='upload-chunk'){let payload;try{payload=JSON.parse(new TextDecoder().decode(body))}catch{return json('Invalid JSON body',400)}if(!payload||typeof payload!=='object'||Array.isArray(payload))return json('Invalid JSON body',400);body=JSON.stringify({payload})}
  }
  const headers={'accept':'application/json','x-divine-gateway-key':key,'x-divine-session':sessionCookie(request.headers.get('cookie')||''),'x-divine-csrf':request.headers.get('x-divine-csrf')||'','x-divine-client-ip':context.ip||'','x-divine-frontend-origin':origin,'user-agent':request.headers.get('user-agent')||'Divine Media'};
  if(body){headers['content-type']=request.headers.get('content-type');const range=request.headers.get('content-range');if(range&&/^bytes \d+-\d+\/\d+$/.test(range))headers['content-range']=range}
  const upstream=await fetch(target,{method:request.method,headers,body,redirect:'error',signal:AbortSignal.timeout(action==='upload-chunk'?25000:12000)});
  if(!(upstream.headers.get('content-type')||'').includes('application/json'))return json('Account service returned an unexpected response',502);
  const text=await upstream.text();if(text.length>2*1024*1024)return json('Account response is too large',502);
  // The adapter owns a strict response projection. Native login responses are never forwarded.
  const data=JSON.parse(text),out=new Headers({'content-type':'application/json','cache-control':'private, no-store','vary':'Cookie','x-content-type-options':'nosniff'});
  const session=upstream.headers.get('x-divine-session');if(sessionPattern.test(session||''))out.set('set-cookie','__Host-dm_session='+session+'; Path=/; HttpOnly; Secure; SameSite=Lax');
  if(action==='logout'&&upstream.ok)out.set('set-cookie','__Host-dm_session=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0');
  return new Response(JSON.stringify(data),{status:upstream.status,headers:out});
 }catch{return json('Account service is temporarily unavailable',502)}
}
export const config={path:'/api/platform/*'};
