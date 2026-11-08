import test from 'node:test';
import assert from 'node:assert/strict';
import {MEDIA_ORIGIN,LEGACY_MEDIA_ORIGIN,canonicalMediaUrl} from '../shared/domains.mjs';
test('migration preserves media paths, query strings and fragments',()=>{
 assert.equal(canonicalMediaUrl(LEGACY_MEDIA_ORIGIN+'/videos/a%20b.mp4?cache=123#t=5'),MEDIA_ORIGIN+'/videos/a%20b.mp4?cache=123#t=5');
 assert.equal(canonicalMediaUrl('/Encoder/'),MEDIA_ORIGIN+'/Encoder/');
 assert.equal(canonicalMediaUrl(MEDIA_ORIGIN+'/videos/x.mp3',LEGACY_MEDIA_ORIGIN),LEGACY_MEDIA_ORIGIN+'/videos/x.mp3');
});
test('foreign hosts, URL credentials and non-HTTPS media stay rejected',()=>{
 for(const value of ['https://evil.example/videos/a.mp3','https://media.divinemedia.us.evil.example/a.mp3','https://u:p@media.divinemedia.us/a.mp3','http://media.divinemedia.us/a.mp3','javascript:alert(1)'])assert.equal(canonicalMediaUrl(value),null);
 assert.equal(canonicalMediaUrl('/a.mp3','https://u:p@media.divinemedia.us'),null);
});
