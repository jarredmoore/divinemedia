import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const publicDir=new URL('../public/',import.meta.url);
test('install manifest points to valid PNG brand icons with required dimensions',()=>{
 const m=JSON.parse(fs.readFileSync(new URL('manifest.webmanifest',publicDir)));assert.equal(m.id,'/');assert.equal(m.scope,'/');assert.equal(m.display,'standalone');assert.equal(m.background_color,'#000000');assert(m.icons.some(i=>i.purpose==='maskable'));
 for(const i of m.icons){const b=fs.readFileSync(new URL(i.src.slice(1),publicDir));assert.equal(b.subarray(1,4).toString(),'PNG');const size=Number(i.sizes.split('x')[0]);assert.equal(b.readUInt32BE(16),size);assert.equal(b.readUInt32BE(20),size)}
 const apple=fs.readFileSync(new URL('icons/apple-touch-icon.png',publicDir));assert.equal(apple.readUInt32BE(16),180);
});
test('offline worker never intercepts accounts, APIs, non-navigation media or mutations',async()=>{
 const handlers={},offline={page:'generic-offline'},cached=[];
 vm.runInNewContext(fs.readFileSync(new URL('sw.js',publicDir),'utf8'),{URL,self:{location:{origin:'https://divinemedia.us'},addEventListener:(n,f)=>handlers[n]=f,skipWaiting:async()=>{},clients:{claim:async()=>{}}},caches:{open:async()=>({addAll:async a=>cached.push(...a),match:async()=>offline}),keys:async()=>[]},fetch:async()=>{throw Error('offline')}});
 let install;handlers.install({waitUntil:p=>install=p});await install;assert.deepEqual(cached,['/offline.html','/icons/divine-192.png','/icons/divine-512.png']);
 for(const [path,method,mode]of [['/api/platform/session','GET','navigate'],['/api/platform/login','POST','navigate'],['/.netlify/functions/platform','GET','navigate'],['/videos/test.mp4','GET','cors']]){let intercepted=false;handlers.fetch({request:{url:'https://divinemedia.us'+path,method,mode},respondWith:()=>intercepted=true});assert.equal(intercepted,false,path)}
 let response;handlers.fetch({request:{url:'https://divinemedia.us/categories',method:'GET',mode:'navigate'},respondWith:p=>response=p});assert.equal(await response,offline);
});
