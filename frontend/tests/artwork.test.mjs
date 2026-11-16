import test from 'node:test';
import assert from 'node:assert/strict';
import {artworkFallback,recoverArtwork} from '../src/artwork.mjs';
test('known album items use approved existing artwork and other items use the brand placeholder',()=>{
 assert.equal(artworkFallback({avideoId:10}),'/2ndTimeAround.jpg');
 assert.equal(artworkFallback({id:16}),'/2ndTimeAround.jpg');
 assert.equal(artworkFallback({id:101}),'/placeholder.svg');
});
test('broken image fallback does not loop and works again after a later image URL change',()=>{
 let src='missing.jpg',writes=0;const img={dataset:{},getAttribute:()=>src,set src(value){src=value;writes++}};
 recoverArtwork({currentTarget:img},{id:10});assert.equal(src,'/2ndTimeAround.jpg');
 recoverArtwork({currentTarget:img},{id:10});assert.equal(writes,1);
 src='new-but-missing.jpg';recoverArtwork({currentTarget:img},{id:10});assert.equal(writes,2);
});
