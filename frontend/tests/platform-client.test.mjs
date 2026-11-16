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
