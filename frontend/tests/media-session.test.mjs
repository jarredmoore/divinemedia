import test from 'node:test';
import assert from 'node:assert/strict';
import {connectMediaSession} from '../src/media-session.mjs';
test('media handoff puts only the one-use grant in a credentialed POST and verifies cookies',async()=>{
 const calls=[];await connectMediaSession(async(action,options)=>{assert.equal(action,'delivery-grant');assert.equal(options.method,'POST');return {grant:'a'.repeat(64)}},async(url,options)=>{calls.push({url,options});return new Response('{}')});
 assert.equal(calls.length,2);assert.equal(calls[0].url,'https://media.divinemedia.us/divine-media/session');assert.equal(calls[0].options.credentials,'include');assert.equal(calls[0].options.body,JSON.stringify({grant:'a'.repeat(64)}));assert.equal(calls[1].options.body,undefined);assert.equal(calls[1].options.credentials,'include');
});
test('invalid grants never reach origin; blocked cookies and failed exchange are reported',async()=>{
 await assert.rejects(connectMediaSession(async()=>({grant:'native-session'}),()=>{throw new Error('must not fetch')}),/authorize private media/);
 await assert.rejects(connectMediaSession(async()=>({grant:'b'.repeat(64)}),async()=>new Response('{}',{status:403})),/authorize private media/);
 let n=0;await assert.rejects(connectMediaSession(async()=>({grant:'c'.repeat(64)}),async()=>new Response('{}',{status:++n===1?200:401})),/browser blocked/);
});
test('concurrent media handoffs complete in order so older cookies cannot replace newer login',async()=>{
 const calls=[];let release;
 const first=connectMediaSession(async()=>({grant:'d'.repeat(64)}),async(url,options)=>{calls.push('first');if(options.method==='POST')await new Promise(r=>release=r);return new Response('{}')});
 const second=connectMediaSession(async()=>({grant:'e'.repeat(64)}),async()=>{calls.push('second');return new Response('{}')});
 await new Promise(r=>setImmediate(r));assert.deepEqual(calls,['first']);release();await Promise.all([first,second]);assert.deepEqual(calls,['first','first','second','second']);
});
