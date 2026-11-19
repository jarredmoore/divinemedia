import test from 'node:test';
import assert from 'node:assert/strict';
import handler,{appOrigin,sessionCookie} from '../netlify/functions/platform.mjs';
test('only the canonical frontend and this site’s HTTPS previews can initiate account actions',()=>{
 assert.equal(appOrigin('https://divinemedia.us'),'https://divinemedia.us');
 assert.equal(appOrigin('https://deploy-preview-15--mediaproduction.netlify.app'),'https://deploy-preview-15--mediaproduction.netlify.app');
 for(const value of ['https://media.divinemedia.us','https://divinemedia.us.evil.test','http://divinemedia.us','https://user@divinemedia.us','https://other.netlify.app'])assert.equal(appOrigin(value),null);
});
test('session bridge ignores credential cookies, malformed IDs and duplicate session names',()=>{
 const id='a'.repeat(26);assert.equal(sessionCookie('credentials=private; __Host-dm_session='+id),id);
 for(const value of ['PHPSESSID='+id,'__Host-dm_session=short','__Host-dm_session='+id+'; __Host-dm_session='+id,'__Host-dm_session=../../private'])assert.equal(sessionCookie(value),'');
});
test('cross-site mutations and arbitrary proxy targets are refused before contacting AVideo',async()=>{
 const before=global.fetch;let calls=0;global.fetch=async()=>{calls++;throw Error('unexpected')};
 try{
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/login',{method:'POST',headers:{origin:'https://evil.test','content-type':'application/json'},body:'{}'}))).status,403);
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/https://evil.test'))).status,404);
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/logout'))).status,405);
  assert.equal(calls,0);
 }finally{global.fetch=before}
});
test('server secret and native cookies stay behind the HttpOnly frontend session boundary',async()=>{
 const before=global.fetch,old=process.env.DIVINE_GATEWAY_KEY;process.env.DIVINE_GATEWAY_KEY='test-only-gateway-key-'.repeat(3);
 const id='b'.repeat(26);let received;
 global.fetch=async(url,options)=>{received={url:String(url),options};return new Response(JSON.stringify({user:{id:7,name:'Creator'},csrf:'test-nonce'}),{headers:{'content-type':'application/json','x-divine-session':id,'set-cookie':'credentials=never-forward-this'}})};
 try{
  const res=await handler(new Request('https://divinemedia.us/api/platform/login',{method:'POST',headers:{origin:'https://divinemedia.us','content-type':'application/json','x-divine-csrf':'test-nonce',cookie:'__Host-dm_session='+id+'; credentials=not-forwarded'},body:JSON.stringify({user:'creator',password:'test-only-password'})}),{ip:'192.0.2.1'});
  assert.equal(res.status,200);assert.equal(received.url,'https://media.divinemedia.us/divine-api/index.php?action=login');assert.equal(received.options.headers['x-divine-session'],id);assert.equal(received.options.headers.cookie,undefined);assert.deepEqual(Object.keys(JSON.parse(received.options.body)),['payload']);assert.equal(JSON.parse(received.options.body).payload.user,'creator');
  const cookie=res.headers.get('set-cookie');assert.match(cookie,/^__Host-dm_session=/);assert.match(cookie,/HttpOnly/);assert.match(cookie,/Secure/);assert.match(cookie,/SameSite=Lax/);assert(!cookie.includes('Domain=')&&!cookie.includes('credentials'));
  assert.equal(res.headers.get('x-divine-session'),null);assert.equal(res.headers.get('x-divine-gateway-key'),null);const body=await res.text();assert(!body.includes(id)&&!body.includes('test-only-gateway-key')&&!body.includes('test-only-password'));
 }finally{global.fetch=before;if(old===undefined)delete process.env.DIVINE_GATEWAY_KEY;else process.env.DIVINE_GATEWAY_KEY=old}
});
test('native HTML errors are never rendered or returned to the frontend',async()=>{
 const before=global.fetch,old=process.env.DIVINE_GATEWAY_KEY;process.env.DIVINE_GATEWAY_KEY='test-key-'.repeat(8);global.fetch=async()=>new Response('<html>private diagnostic</html>',{headers:{'content-type':'text/html'}});
 try{const res=await handler(new Request('https://divinemedia.us/api/platform/session'));assert.equal(res.status,502);assert(!(await res.text()).includes('private diagnostic'))}finally{global.fetch=before;if(old===undefined)delete process.env.DIVINE_GATEWAY_KEY;else process.env.DIVINE_GATEWAY_KEY=old}
});
test('YouTube preview and import require same-origin POST requests',async()=>{
 const before=global.fetch;let calls=0;global.fetch=async()=>{calls++;throw Error('unexpected')};
 try{for(const action of ['embed-preview','embed-add']){
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/'+action))).status,405);
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/'+action,{method:'POST',headers:{origin:'https://evil.test','content-type':'application/json'},body:'{}'}))).status,403);
 }assert.equal(calls,0)}finally{global.fetch=before}
});
test('thumbnail multipart stays binary and enforces the same-origin size boundary',async()=>{
 const before=global.fetch,old=process.env.DIVINE_GATEWAY_KEY;process.env.DIVINE_GATEWAY_KEY='fixture-key-'.repeat(8);let upstream;
 global.fetch=async(url,options)=>{upstream=options;return new Response(JSON.stringify({message:'Thumbnail updated.'}),{headers:{'content-type':'application/json'}})};
 try{
  const form=new FormData();form.set('id','7');form.set('kind','landscape');form.set('file_data',new Blob(['fixture-image'],{type:'image/png'}),'cover.png');
  const result=await handler(new Request('https://divinemedia.us/api/platform/creator-thumbnail',{method:'POST',headers:{origin:'https://divinemedia.us','x-divine-csrf':'fixture'},body:form}));assert.equal(result.status,200);assert.match(upstream.headers['content-type'],/^multipart\/form-data; boundary=/);assert.match(new TextDecoder().decode(upstream.body),/name="file_data"; filename="cover.png"/);
  assert.equal((await handler(new Request('https://divinemedia.us/api/platform/creator-thumbnail'))).status,405);
  const big=new FormData();big.set('file_data',new Blob([new Uint8Array(3*1024*1024)]),'large.jpg');assert.equal((await handler(new Request('https://divinemedia.us/api/platform/creator-thumbnail',{method:'POST',headers:{origin:'https://divinemedia.us'},body:big}))).status,413);
 }finally{global.fetch=before;if(old===undefined)delete process.env.DIVINE_GATEWAY_KEY;else process.env.DIVINE_GATEWAY_KEY=old}
});
