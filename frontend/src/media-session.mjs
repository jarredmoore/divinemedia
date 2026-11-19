// Exchange only opaque one-use grants; native sessions remain server-side.
let pending=Promise.resolve();
function ordered(operation){const next=pending.catch(()=>{}).then(operation);pending=next.catch(()=>{});return next;}
export function connectMediaSession(platform,fetcher=fetch){return ordered(async()=>{
 const {grant}=await platform('delivery-grant',{method:'POST'});
 if(!/^[a-f0-9]{64}$/.test(grant||''))throw new Error('Unable to authorize private media.');
 const url='https://media.divinemedia.us/divine-media/session';
 const response=await fetcher(url,{method:'POST',credentials:'include',cache:'no-store',redirect:'error',headers:{'content-type':'application/json'},body:JSON.stringify({grant}),signal:AbortSignal.timeout(10000)});
 if(!response.ok)throw new Error('Unable to authorize private media. Try signing in again.');
 // A successful exchange alone cannot prove the browser accepted the media-origin cookie.
 const check=await fetcher(url,{credentials:'include',cache:'no-store',redirect:'error',signal:AbortSignal.timeout(10000)});
 if(!check.ok)throw new Error('This browser blocked the media session. Open divinemedia.us directly to sign in.');
});}
export function clearMediaSession(){
 return ordered(()=>fetch('https://media.divinemedia.us/divine-media/logout',{method:'POST',credentials:'include',cache:'no-store',redirect:'error',signal:AbortSignal.timeout(10000)}).catch(()=>{}));
}
