let csrf='',bootstrapPromise=null;
export class PlatformError extends Error{constructor(message,status,details){super(message);this.status=status;this.details=details}}
async function send(action,{method='GET',data,query,signal}={}){
 const params=new URLSearchParams(query||{}),url='/api/platform/'+action+(params.size?'?'+params:'');
 const headers={accept:'application/json'};if(method==='POST'){headers['x-divine-csrf']=csrf;if(!(data instanceof FormData))headers['content-type']='application/json'}
 const response=await fetch(url,{method,credentials:'same-origin',cache:'no-store',headers,body:method==='POST'?(data instanceof FormData?data:JSON.stringify(data||{})):undefined,signal});
 let result;try{result=await response.json()}catch{throw new PlatformError('Account service returned an unexpected response.',response.status)}
 if(result.csrf)csrf=result.csrf;if(action==='logout'&&response.ok)csrf='';
 if(!response.ok||result.error)throw new PlatformError(typeof result.error==='string'?result.error:'Unable to complete this action.',response.status,result);
 return result;
}
export function platform(action,options={}){
 if(action==='session'){
  if(!bootstrapPromise)bootstrapPromise=send(action,options).finally(()=>{bootstrapPromise=null});
  return bootstrapPromise;
 }
 return (csrf?Promise.resolve():platform('session')).then(()=>send(action,options));
}
export function workspace(view,detail={}){window.dispatchEvent(new CustomEvent('divine:workspace',{detail:{view,...detail}}))}
export function contentUrl(item){const id=Number(item?.avideoId);return id>0?'https://divinemedia.us/watch/'+id:'https://divinemedia.us/'}
