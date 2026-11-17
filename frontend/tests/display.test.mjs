import test from 'node:test';
import assert from 'node:assert/strict';
import {activeMedia,castSource,siteFullscreen,castMedia} from '../src/display.mjs';
test('display targets actual program media, excluding decorative videos',()=>{
 const queries=[],program={};const doc={querySelector:s=>{queries.push(s);return s==='audio.real-audio'?program:null}};
 assert.equal(activeMedia(doc),program);assert.deepEqual(queries,['video.real-video','audio.real-audio']);
});
test('cast uses the approved original HLS URL rather than an MSE blob and rejects unsupported URLs',()=>{
 assert.deepEqual(castSource({dataset:{displaySource:'https://media.divinemedia.us/live/index.m3u8?token=x'},currentSrc:'blob:test'}),{url:'https://media.divinemedia.us/live/index.m3u8?token=x',type:'application/x-mpegURL'});
 for(const src of ['blob:x','http://example.com/video.mp4','https://user:secret@example.com/v.mp4'])assert.throws(()=>castSource({src}));
 assert.throws(()=>castSource(null),/Open a video/);
});
test('fullscreen works at document level without a loaded video and supports exit and Safari fallback',async()=>{
 let entered=0,exited=0,safari=0;
 await siteFullscreen({fullscreenEnabled:true,documentElement:{requestFullscreen:()=>entered++}});
 await siteFullscreen({fullscreenElement:{},exitFullscreen:()=>exited++});
 await siteFullscreen({documentElement:{webkitRequestFullscreen:()=>safari++}});
 assert.deepEqual([entered,exited,safari],[1,1,1]);
});
function fixture({cancel=false,loadFailure=false}={}){
 let connected=false,request=null,paused=false;
 const context={setOptions:o=>assert.equal(o.receiverApplicationId,'default'),getCurrentSession:()=>connected?{loadMedia:async r=>{if(loadFailure)throw Error('Receiver cannot load media');request=r}}:null,requestSession:async()=>{if(cancel)throw {code:'cancel'};connected=true}};
 const win={cast:{framework:{CastContext:{getInstance:()=>context}}},chrome:{cast:{AutoJoinPolicy:{TAB_AND_ORIGIN_SCOPED:'tab'},media:{DEFAULT_MEDIA_RECEIVER_APP_ID:'default',StreamType:{LIVE:'live'},MediaInfo:class{constructor(url,type){this.url=url;this.type=type}},LoadRequest:class{constructor(info){this.media=info}}}}}};
 const media={src:'https://media.divinemedia.us/videos/test.mp4',duration:120,currentTime:42,pause:()=>{paused=true}};
 return {win,media,values:()=>({request,paused})};
}
test('Cast resumes VOD position and pauses local playback only after receiver accepts media',async()=>{
 const f=fixture();await castMedia(f.media,f.win);assert.equal(f.values().request.currentTime,42);assert.equal(f.values().request.autoplay,true);assert.equal(f.values().paused,true);
});
test('cancelled connections and receiver failures preserve local playback',async()=>{
 for(const opts of [{cancel:true},{loadFailure:true}]){const f=fixture(opts);await assert.rejects(castMedia(f.media,f.win));assert.equal(f.values().paused,false)}
});
