import test from 'node:test';
import assert from 'node:assert/strict';
import handler,{publicAudioSource,isAudio,findPublicAudioUrl} from '../netlify/functions/public-catalog.mjs';
const origin='https://media.divinemedia.us';
const src=origin+'/videos/new/new.mp3';
test('new MP3 sources are discovered without IDs or HTML fetches',async()=>{
 const original=globalThis.fetch;let calls=0;
 globalThis.fetch=async()=>{calls++;return Response.json({response:{rows:[{id:999,status:'a',title:'New upload',pageUrl:origin+'/video/999',sources:[{type:'audio/mpeg',src}],session:'secret'},{status:'a',title:'Private',pageUrl:origin+'/audio/3',isPrivate:true}]}})};
 try{const response=await handler();const body=await response.json();assert.equal(calls,1);assert.equal(body.response.rows.length,1);assert.equal(body.response.rows[0].audioUrl,src);assert.equal(body.response.rows[0].mediaType,'audio');assert.equal(JSON.stringify(body).includes('secret'),false)}finally{globalThis.fetch=original}
});
test('audio candidates skip untrusted URLs and preserve valid later sources',()=>{
 assert.equal(publicAudioSource({audioUrl:'https://evil.example/a.mp3',sources:[{src,type:'audio/mpeg'}]}),src);
 assert.equal(publicAudioSource({sources:[{src:'javascript:alert(1)',type:'audio/mpeg'}]}),null);
 assert.equal(isAudio({type:'audio'},origin+'/video/99'),true);
 assert.equal(isAudio({sources:[{src,type:'application/octet-stream'}]},origin+'/video/99'),true);
 assert.equal(isAudio({type:'video'},origin+'/video/99'),false);
 assert.equal(publicAudioSource({audioUrl:'https://user:password@media.divinemedia.us/a.mp3'}),null);
});
test('legacy public page discovery works for escaped paths',()=>{
 assert.equal(findPublicAudioUrl('<source src="/videos/new/new.mp3">'),src);
 assert.equal(findPublicAudioUrl('<source src="https://evil.example/secret.mp3">'),null);
});
test('upstream failures return a generic error',async()=>{
 const original=globalThis.fetch;globalThis.fetch=async()=>{throw Error('sensitive')};
 try{const response=await handler();assert.equal(response.status,502);assert.equal((await response.text()).includes('sensitive'),false)}finally{globalThis.fetch=original}
});
test('old media URLs move to the new domain without changing paths',()=>{
 assert.equal(publicAudioSource({audioUrl:'https://media.divinecreativegroup.com/videos/new/new.mp3'}),src);
 assert.equal(findPublicAudioUrl('<source src="https://media.divinecreativegroup.com/videos/new/new.mp3">'),src);
 assert.equal(findPublicAudioUrl('<source src="https://evil.example/videos/new/new.mp3">'),null);
 assert.equal(findPublicAudioUrl('<source src="https://media.divinemedia.us.evil.example/videos/new/new.mp3">'),null);
});
