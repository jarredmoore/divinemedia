import test from 'node:test';
import assert from 'node:assert/strict';
test('concurrent identical video reads share one request, but later reads refresh',async()=>{
 const before=global.fetch;const calls=[];let release;
 global.fetch=async(url)=>{calls.push(url);if(url.endsWith('/session'))return Response.json({csrf:'test-nonce'});await new Promise(r=>{release=r});return Response.json({item:{id:1}})};
 try{
  const {platform}=await import('../src/platform-client.mjs?coalesce-test');await platform('session');
  const a=platform('video',{query:{id:1}}),b=platform('video',{query:{id:1}});await new Promise(r=>setImmediate(r));
  assert.equal(calls.filter(u=>u.includes('/video')).length,1);release();assert.deepEqual(await a,await b);
  const c=platform('video',{query:{id:1}});await new Promise(r=>setImmediate(r));assert.equal(calls.filter(u=>u.includes('/video')).length,2);release();await c;
 }finally{global.fetch=before}
});
test('different video queries remain separate and mutations invalidate pending reads',async()=>{
 const before=global.fetch;let videoCalls=0;const releases=[];
 global.fetch=async(url,options)=>{if(url.endsWith('/session'))return Response.json({csrf:'test-nonce'});if(options.method==='POST')return Response.json({message:'Saved'});videoCalls++;await new Promise(r=>releases.push(r));return Response.json({item:{}})};
 try{
  const {platform}=await import('../src/platform-client.mjs?invalidate-test');await platform('session');
  const a=platform('video',{query:{id:1}}),b=platform('video',{query:{id:2}});await new Promise(r=>setImmediate(r));assert.equal(videoCalls,2);
  await platform('reaction',{method:'POST',data:{video:1,value:1}});const c=platform('video',{query:{id:1}});await new Promise(r=>setImmediate(r));assert.equal(videoCalls,3);releases.forEach(r=>r());await Promise.all([a,b,c]);
 }finally{global.fetch=before}
});
test('logout rejects older private reads and bootstraps a fresh CSRF token',async()=>{
 const before=global.fetch;let release;const tokens=[];
 global.fetch=async(url,options)=>{if(url.endsWith('/session'))return Response.json({csrf:'fresh'});if(url.includes('/video')){await new Promise(r=>release=r);return Response.json({item:{title:'Private'},csrf:'stale'})}tokens.push(options.headers['x-divine-csrf']);return Response.json({ok:true})};
 try{
  const {platform}=await import('../src/platform-client.mjs?logout-generation');await platform('session');
  const pending=platform('video',{query:{id:1}});const rejected=assert.rejects(pending,/session changed/);await new Promise(r=>setImmediate(r));
  await platform('logout',{method:'POST'});release();await rejected;await platform('reaction',{method:'POST'});assert.deepEqual(tokens,['fresh','fresh']);
 }finally{global.fetch=before}
});
test('expired account request discards CSRF; failed login does not reset a session',async()=>{
 const before=global.fetch;let bootstraps=0;
 global.fetch=async url=>url.endsWith('/session')?(bootstraps++,Response.json({csrf:'nonce'})):Response.json({error:'Denied',csrf:'must-not-retain'},{status:401});
 try{
  const {platform}=await import('../src/platform-client.mjs?expiry-generation');await platform('session');
  await assert.rejects(platform('login',{method:'POST'}));await assert.rejects(platform('library'));assert.equal(bootstraps,1);
  await assert.rejects(platform('library'));assert.equal(bootstraps,2);
 }finally{global.fetch=before}
});
