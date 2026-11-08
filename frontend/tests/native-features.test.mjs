import test from 'node:test';
import assert from 'node:assert/strict';
import {nativeEmbedUrl,nativeContentUrl} from '../src/native-features.mjs';
const origin='https://media.divinemedia.us';
test('native player retains channel/id routing while enabling configured controls',()=>{
 const url=new URL(nativeEmbedUrl({watchUrl:origin+'/channel/admin/video/18/example?autoplay=1#comments'},origin));
 assert.equal(url.pathname,'/channel/admin/videoEmbed/18/example');assert.equal(url.searchParams.get('controls'),'1');assert.equal(url.searchParams.get('autoplay'),'0');assert.equal(url.hash,'');assert.equal(url.searchParams.get('disableCloseButton'),'1');
});
test('native audio embeds and legacy media links use the canonical backend',()=>{
 assert.match(nativeEmbedUrl({watchUrl:'https://media.divinecreativegroup.com/channel/admin/audio/16/track'},origin),/^https:\/\/media\.divinemedia\.us\/channel\/admin\/audioEmbed\/16\/track\?/);
 assert.equal(nativeContentUrl({watchUrl:'https://media.divinecreativegroup.com/video/1?a=b'},origin),origin+'/video/1?a=b');
});
test('foreign hosts, embedded URL credentials and non-player routes are rejected',()=>{
 for(const watchUrl of ['https://example.com/video/1','https://name:secret@media.divinemedia.us/video/1','http://media.divinemedia.us/video/1',origin+'/user',origin+'/Encoder/'])assert.equal(nativeEmbedUrl({watchUrl},origin),undefined);
 assert.equal(nativeEmbedUrl({},origin),undefined);
});
