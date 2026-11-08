import test from 'node:test';import assert from 'node:assert/strict';
import {resolveTheme,themedUrl} from '../shared/theme.mjs';
test('explicit theme wins, then shared preference wins over stale host-local storage',()=>{
 assert.equal(resolveTheme({search:'?theme=default',cookie:'dm_view_theme=code-black',stored:'code-black'}),'default');
 assert.equal(resolveTheme({cookie:'other=1; dm_view_theme=code-black',stored:'default'}),'code-black');
 assert.equal(resolveTheme({cookie:'dm_view_theme=default',stored:'code-black'}),'default');
 assert.equal(resolveTheme({search:'?theme=cold-black'}),'code-black');assert.equal(resolveTheme({search:'?theme=<script>',cookie:'dm_view_theme=invalid'}),'default');
});
test('public route handoff keeps path, existing options and the selected theme on canonical hosts',()=>{
 const u=new URL(themedUrl('https://media.divinecreativegroup.com/Encoder/?noNavbar=0#login','code-black'));
 assert.equal(u.origin,'https://media.divinemedia.us');assert.equal(u.pathname,'/Encoder/');assert.equal(u.searchParams.get('noNavbar'),'0');assert.equal(u.searchParams.get('theme'),'code-black');assert.equal(u.hash,'#login');
 assert.equal(new URL(themedUrl('https://watch.divinecreativegroup.com/','default')).origin,'https://divinemedia.us');
});
test('theme propagation does not rewrite foreign links or credential-bearing URLs',()=>{
 for(const url of ['https://example.com/','mailto:a@example.com','https://u:p@media.divinemedia.us/user','https://media.divinecreativegroup.com/Encoder/?pass=example'])assert.equal(themedUrl(url,'code-black'),url);
});
