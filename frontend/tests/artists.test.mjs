import test from 'node:test';import assert from 'node:assert/strict';
import {artistFromPath,featuredArtists,releasePreviews,artistTrackTitle} from '../src/artists.mjs';
test('artist routes resolve only the approved roster',()=>{
 assert.equal(artistFromPath('/artists/murphy-lee').name,'Murphy Lee');assert.equal(artistFromPath('/artists/murphy-lee/').name,'Murphy Lee');
 for(const p of ['/artists/unknown','/artists/../admin','/artists/murphy-lee/private','/channel/admin'])assert.equal(artistFromPath(p),null);
});
test('DVD bonus never becomes a public listening or download product',()=>{
 const release=featuredArtists[0].releases.find(r=>r.id==='you-see-me');assert.equal(release.privateBonus,true);assert.deepEqual(release.previewIds,[]);
 assert.deepEqual(releasePreviews({...release,previewIds:[1]},[{avideoId:1,type:'Listen',audioUrl:'https://media.divinemedia.us/videos/bonus.mp3'}]),[]);
 assert(!('downloadUrl'in release));assert(!('archive'in release));
});
test('listening previews preserve approved selection and drop private, absent and non-audio records',()=>{
 const release={previewIds:[4,1,2,3,5,6]},items=[{avideoId:1,type:'Listen',audioUrl:'/a.mp3'}, {avideoId:2,type:'Listen',audioUrl:'/private.mp3',visibility:'private'},{avideoId:3,type:'Listen',audioUrl:null},{avideoId:4,type:'Listen',audioUrl:'/b.mp3',status:'a'},{avideoId:5,type:'Watch',audioUrl:'/not-audio.mp3'},{avideoId:6,type:'Listen',audioUrl:'/draft.mp3',status:'i'}];
 assert.deepEqual(releasePreviews(release,items).map(i=>i.avideoId),[4,1]);
});
test('official purchase destinations remain release specific; masters are not web assets',()=>{
 const artist=featuredArtists[0];assert.equal(new URL(artist.releases[0].checkout).pathname,'/Home/Details/2');assert.equal(new URL(artist.releases[1].checkout).pathname,'/Home/Details/4');
 for(const release of artist.releases){const u=new URL(release.checkout);assert.equal(u.origin,'https://store.newmurph.com');assert(!u.username&&!u.password)}
 for(const art of artist.gallery){assert(art.image.startsWith('/artists/murphy-lee/'));assert(art.image.endsWith('.webp'));assert(art.width>0&&art.height>0)}
 assert.equal(artist.merchandise.length,0);
});
test('track display formatting leaves native records untouched',()=>{const item={title:'1DIVINEIntro'};assert.equal(artistTrackTitle(item.title),'DIVINE Intro');assert.equal(item.title,'1DIVINEIntro');assert.equal(artistTrackTitle('12FlowersandBars'),'Flowersand Bars')});

test('four offerings pair the colorful companion CD with the You See Me DVD',()=>{const releases=featuredArtists[0].releases;assert.equal(releases.length,4);const dvd=releases.find(r=>r.id==='you-see-me'),album=releases.find(r=>r.id==='you-see-me-cd');assert.equal(album.includedWith,dvd.id);assert.notEqual(album.cover,dvd.cover);assert.equal(album.cover,'/artists/murphy-lee/you-see-me-cover.webp');assert(!releases.some(r=>r.id==='ml10'));assert.equal(album.checkout,dvd.checkout);assert.equal(album.privateBonus,true);assert.deepEqual(releasePreviews(album,[]),[])});
