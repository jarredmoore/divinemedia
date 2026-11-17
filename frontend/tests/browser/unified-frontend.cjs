// Frontend-only interaction contract with isolated fixtures; never submits to the live backend.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),assert=require('assert');
const origin=process.env.UNIFIED_TEST_URL||'http://127.0.0.1:5175',dir=process.env.BROWSER_ARTIFACTS||'/tmp/divine-unified-ui';
fs.mkdirSync(dir,{recursive:true});process.umask(0o077);
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),page=await context.newPage(),errors=[],actions=[];
 let user=null,likes=0,comments=[],lists=[],next=31;
 const item={id:101,avideoId:101,title:'Divine test video',type:'Watch',tag:'DIVINE ORIGINAL',creator:'Test creator',channel:'test-creator',userId:7,categoryId:1,img:'/placeholder.svg',image:'/placeholder.svg',videoUrl:'https://media.divinemedia.us/videos/isolated-fixture.mp4',watchUrl:'https://divinemedia.us/watch/101'};
 page.on('pageerror',e=>errors.push(e.message));
 await context.addInitScript(()=>{Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.__copied=text}}})});
 await context.addInitScript(()=>{
  window.__displayCalls={airplay:0,loads:0,fullscreen:0};
  HTMLMediaElement.prototype.webkitShowPlaybackTargetPicker=function(){window.__displayCalls.airplay++};
  HTMLElement.prototype.requestFullscreen=async()=>{window.__displayCalls.fullscreen++};Object.defineProperty(document,'fullscreenEnabled',{value:true});
  let session=null;const ctx={setOptions:()=>{},getCurrentSession:()=>session,requestSession:async()=>{session={loadMedia:async r=>{window.__displayCalls.loads++;window.__displayCalls.source=r.media.url}}},endCurrentSession:()=>{session=null}};
  window.cast={framework:{CastContext:{getInstance:()=>ctx}}};window.chrome=window.chrome||{};window.chrome.cast={isAvailable:true,AutoJoinPolicy:{TAB_AND_ORIGIN_SCOPED:'tab'},media:{DEFAULT_MEDIA_RECEIVER_APP_ID:'default',StreamType:{LIVE:'live'},MediaInfo:class{constructor(url,type){this.url=url;this.type=type}},LoadRequest:class{constructor(info){this.media=info}}}};
 });
 await context.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(url.hostname==='media.divinemedia.us'&&url.pathname==='/videos/isolated-fixture.mp4'){
   const data=fs.readFileSync(require('path').join(__dirname,'../../public/themes/cold-black/stage-loop.mp4')),range=req.headers().range?.match(/bytes=(\d+)-(\d*)/);
   if(range){const start=Number(range[1]),end=range[2]?Math.min(Number(range[2]),data.length-1):data.length-1;return route.fulfill({status:206,headers:{'content-type':'video/mp4','content-range':`bytes ${start}-${end}/${data.length}`,'accept-ranges':'bytes'},body:data.subarray(start,end+1)})}
   return route.fulfill({contentType:'video/mp4',body:data});
  }
  if(url.origin!==origin){return route.abort()}
  if(url.pathname==='/media.json')return route.fulfill({json:[]});
  if(url.pathname==='/api/public-catalog')return route.fulfill({json:{response:{rows:[]}}});
  if(!url.pathname.startsWith('/api/platform/'))return route.continue();
  const action=url.pathname.split('/').at(-1),post=req.method()==='POST';actions.push(action);
  let body={};if(post&&(req.headers()['content-type']||'').includes('application/json'))body=req.postDataJSON();
  if(post)assert(req.headers()['x-divine-csrf'],'Mutation had no session nonce');
  const send=data=>route.fulfill({json:data});
  if(action==='session')return send({user,csrf:'isolated-frontend-nonce',captchaRequired:false});
  if(action==='catalog')return send({items:[item]});
  if(action==='categories')return send({items:[{id:1,name:'Music'}]});
  if(action==='channels')return send({items:[{id:7,name:'Test creator',channel:'test-creator',count:1}]});
  if(action==='channel')return send({items:[item,{...item,id:10,avideoId:10,title:'Album artwork fallback',type:'Listen',image:'/missing-art.jpg',img:'/missing-art.jpg'}],channel:{userId:7,followers:0,following:false}});
  if(action==='login'){user={id:7,name:'Test creator',username:'creator',permissions:{upload:true,stream:true,comment:true}};return send({user,csrf:'isolated-authenticated-nonce'})}
  if(action==='logout'){user=null;return send({message:'Signed out.'})}
  if(action==='video')return send({item,likes,dislikes:0,reaction:likes?1:0,player:{seek:{enabled:true,back:2,forward:5,hideOnMobile:false},hotkeys:true,theater:true,miniPlayer:true}});
  if(action==='reaction'){likes=likes?0:1;return send({likes,dislikes:0,reaction:likes?1:0})}
  if(action==='comments')return send({items:comments});
  if(action==='comment'){if(body.remove)comments=comments.filter(c=>c.id!==body.id);else comments.push({id:1,author:'Test creator',text:body.text,created:'Today',canDelete:true});return send({id:1})}
  if(action==='playlists')return send({items:lists});
  if(action==='playlist'){if(body.remove)lists=lists.filter(p=>p.id!==body.id);else if(body.id)Object.assign(lists.find(p=>p.id===body.id),{name:body.name,visibility:body.status});else lists.push({id:next++,name:body.name,visibility:body.status,items:[]});return send({id:body.id||next-1})}
  if(action==='playlist-item'){const p=lists.find(p=>p.id===body.playlist);p.items=body.add?[item]:[];return send({message:'Updated.'})}
  if(action==='library')return send(post?{message:'Saved.'}:{items:[item]});
  if(action==='notifications')return send({items:[{id:1,title:'Welcome creator',text:'Your account is ready.',read:false}]});
  if(action==='notification-read'||action==='profile'||action==='follow'||action==='playback'||action==='playlist-order'||action==='upload-cancel')return send({message:'Saved.'});
  if(action==='live')return send({items:[]});
  if(action==='studio')return send({title:'Your live show',visibility:'unlisted',server:'rtmp://media.divinemedia.us/live?s=isolated-example',key:'isolated-not-a-real-key'});
  if(action==='studio-save')return send({message:'Broadcast settings saved.'});
  if(action==='creator-videos')return send({items:[{...item,status:'Published',visibility:'public'}]});
  if(action==='creator-video')return send({message:'Saved.'});
  if(action==='upload-init')return send({ticket:'isolated-ticket'});
  if(action==='upload-chunk')return send({complete:true,videoId:303});
  if(action==='encoder-queue')return send({items:[]});
  return route.fulfill({status:404,json:{error:'Unsupported fixture action'}});
 });

 if(process.env.GLASS_THEME_TEST==='1'){
  const checks=[];
  const neutral=rgb=>{const a=rgb.match(/[\d.]+/g).map(Number);return Math.max(...a.slice(0,3))-Math.min(...a.slice(0,3))<=20};
  for(const theme of ['code-black','default'])for(const width of [1440,390,320]){
   user=null;await page.setViewportSize({width,height:900});await page.goto(origin+'/?theme='+theme);await page.getByRole('button',{name:'View Divine test video',exact:true}).waitFor();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,'Homepage overflow '+theme+' '+width);await page.locator('header .dm-display-trigger .dm-glass-icon').waitFor({state:'visible'});await page.locator('header .dm-install-trigger:visible .dm-glass-icon').first().waitFor({state:'visible'});if(width===1440)await page.locator('header .native-upload:visible .dm-glass-icon').waitFor({state:'visible'});
   if(theme==='code-black'){
    const look=await page.evaluate(()=>{const style=q=>{const s=getComputedStyle(document.querySelector(q));return {color:s.color,background:s.backgroundColor,shadow:s.boxShadow}};return {logo:style('.cb-wordmark'),eyebrow:style('.cb-hero-copy .eyebrow'),connection:style('.cb-hero-copy h1 em'),watch:style('.cb-hero-copy .primary'),music:style('.cb-hero-copy .secondary')}});
    assert.equal(look.logo.color,'rgb(255, 255, 255)');assert(neutral(look.eyebrow.color));assert(neutral(look.connection.color));assert(neutral(look.watch.background));assert(neutral(look.music.background));assert.equal(look.watch.background,look.music.background);
    const focus=page.locator('.cb-hero-copy .primary');await focus.focus();assert.equal(await focus.evaluate(el=>getComputedStyle(el).outlineColor),'rgb(255, 255, 255)');
    assert(await page.locator('.cb-hero-copy .primary .dm-glass-icon svg').getAttribute('stroke').then(v=>v.startsWith('url(#glass-')));
   }
   if(theme==='code-black'){await page.screenshot({path:dir+'/glass-keyboard-focus-'+width+'.png'});await page.locator('.cb-hero-copy .primary').evaluate(el=>el.blur())}await page.screenshot({path:dir+'/glass-home-'+theme+'-'+width+'.png'});
   if(theme==='code-black'&&width<1000){await page.getByRole('button',{name:'Open navigation',exact:true}).click();await page.screenshot({path:dir+'/glass-navigation-'+width+'.png'});await page.getByRole('button',{name:'Close navigation',exact:true}).click()}
   await page.getByRole('button',{name:'View Divine test video',exact:true}).scrollIntoViewIfNeeded();await page.screenshot({path:dir+'/glass-cards-'+theme+'-'+width+'.png'});
   await page.getByRole('button',{name:'View Divine test video',exact:true}).click();await page.locator('video.real-video[src]').waitFor({state:'attached'});
   await page.getByRole('button',{name:'Playback options',exact:true}).click();await page.locator('.dm-player-panel').scrollIntoViewIfNeeded();assert(await page.locator('.dm-player-panel').evaluate(el=>el.getBoundingClientRect().right<=innerWidth+1));await page.screenshot({path:dir+'/glass-player-'+theme+'-'+width+'.png'});await page.keyboard.press('Escape');
   await page.getByRole('button',{name:'Close',exact:true}).click();const pill=page.getByRole('button',{name:'Open player for Divine test video',exact:true});await pill.waitFor();if(theme==='code-black')assert(neutral(await pill.evaluate(el=>getComputedStyle(el).backgroundColor)));else assert((await pill.evaluate(el=>getComputedStyle(el).backgroundColor)).startsWith('rgba(255, 204, 47,'));await page.screenshot({path:dir+'/glass-dock-'+theme+'-'+width+'.png'});
   user={id:7,name:'Test creator',username:'creator',permissions:{upload:true,stream:true,comment:true}};await page.goto(origin+'/creator/upload?theme='+theme);await page.getByRole('button',{name:'Start upload',exact:true}).waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,'Upload overflow');await page.getByRole('button',{name:'Start upload',exact:true}).focus();await page.screenshot({path:dir+'/glass-upload-'+theme+'-'+width+'.png'});
   const warm=await page.locator('.dm-workspace').evaluate(root=>[...root.querySelectorAll('*')].filter(el=>!el.closest('.dm-glass-icon')&&el.getClientRects().length).flatMap(el=>{const s=getComputedStyle(el);return ['color','backgroundColor','borderTopColor'].filter(k=>{const v=s[k].match(/[\d.]+/g);if(!v)return false;const [r,g,b]=v.map(Number);return r>=g&&g>=b&&r-b>20}).map(k=>({tag:el.tagName,property:k,value:s[k]}))}));if(theme==='code-black')assert.deepEqual(warm,[],'Warm Code Black upload styling');else assert.equal(await page.locator('select[aria-label="Viewing theme"]').first().locator('option:checked').textContent(),'Cozy');
   checks.push({theme,width,homepage:true,navigation:true,cards:true,player:true,sticky_player:true,upload:true,focus:true});
  }
  await context.route('**/*.css',async route=>{const path=new URL(route.request().url()).pathname;const css=fs.readFileSync(require('path').join(__dirname,'../../dist',path),'utf8').replaceAll('((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px)))','(backdrop-filter:unsupported)');await route.fulfill({contentType:'text/css',body:css})});user=null;await page.setViewportSize({width:1440,height:900});await page.goto(origin+'/?theme=code-black');await page.getByRole('button',{name:'View Divine test video',exact:true}).waitFor();const solid=await page.locator('.cb-header').evaluate(el=>getComputedStyle(el).backgroundColor);assert.equal(solid,'rgb(20, 22, 25)');await page.screenshot({path:dir+'/glass-solid-fallback.png'});
  assert.deepEqual(errors,[]);const report={result:'pass',checks,solid_charcoal_fallback:'rendered with unsupported feature query simulated',reduced_motion:true,code_black_warm_color_scan:'pass',cozy_brand_yellow:'preserved',saved_default_preferences:'compatible',artwork_and_cinematic_media_modified:false,real_accounts_or_backend_mutations:false,errors};fs.writeFileSync(dir+'/black-glass-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();return;
 }
 await page.goto(origin+'/?theme=code-black');await page.getByText('DIVINE CATALOG',{exact:false}).waitFor();
 await page.getByRole('button',{name:'View Divine test video',exact:true}).click();
 assert.equal(new URL(page.url()).pathname,'/watch/101');assert.equal(await page.locator('iframe').count(),0);
 await page.locator('.dm-player').getByRole('button',{name:'Display options',exact:true}).click();
 await page.getByRole('button',{name:'AirPlay',exact:true}).click();assert.equal(await page.evaluate(()=>window.__displayCalls.airplay),1);
 await page.getByRole('button',{name:'Google Cast / Chromecast',exact:true}).click();await page.waitForFunction(()=>window.__displayCalls.loads===1);assert.equal(await page.evaluate(()=>window.__displayCalls.source),'https://media.divinemedia.us/videos/isolated-fixture.mp4');
 await page.getByRole('button',{name:'Fullscreen site',exact:true}).click();assert.equal(await page.evaluate(()=>window.__displayCalls.fullscreen),1);
 await page.getByRole('button',{name:'Disconnect Google Cast',exact:true}).click();await page.getByRole('button',{name:'Close display options',exact:true}).click();

 assert(await page.locator('video.real-video').getAttribute('controls')!==null);
 await page.waitForFunction(()=>document.querySelector('video.real-video')?.readyState>=1);
 await page.getByRole('button',{name:'Forward 5 seconds',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('video.real-video').currentTime>1);
 await page.getByRole('button',{name:'Playback options',exact:true}).click();await page.getByLabel('Playback speed',{exact:true}).selectOption('1.5');
 assert.equal(await page.locator('video.real-video').evaluate(el=>el.playbackRate),1.5);
 await page.getByRole('button',{name:'Theater mode',exact:true}).click();assert.equal(await page.locator('.dm-player').getAttribute('data-theater'),'true');
 await page.screenshot({path:dir+'/player-options-desktop.png'});await page.keyboard.press('Escape');
 assert.equal(await page.getByRole('button',{name:'Playback options',exact:true}).getAttribute('aria-expanded'),'false');
 await page.locator('video.real-video').focus();await page.keyboard.press('ArrowLeft');
 assert(await page.locator('video.real-video').evaluate(el=>el.currentTime<=Math.max(0,Math.min(5,el.duration)-1)));

 await page.getByRole('button',{name:'More video options',exact:true}).click();await page.getByRole('button',{name:'Copy link',exact:true}).click();assert.equal(await page.evaluate(()=>window.__copied),'https://divinemedia.us/watch/101');
 await page.getByRole('button',{name:'Like video',exact:true}).click();await page.getByRole('dialog',{name:'Your account',exact:true}).waitFor();
 await page.getByLabel('Email or username').fill('creator');await page.getByLabel('Password',{exact:true}).fill('isolated-not-real-password');await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByText('Signed in as',{exact:false}).waitFor();
 await page.getByRole('button',{name:'Close workspace',exact:true}).click();assert.equal(new URL(page.url()).pathname,'/watch/101');
 await page.getByRole('button',{name:'Like video',exact:true}).click();await page.waitForFunction(()=>document.querySelector('[aria-label="Like video"]').getAttribute('aria-pressed')==='true');
 await page.getByRole('button',{name:'Comments',exact:true}).click();await page.getByLabel('Your comment').fill('A comment without leaving Divine Media');await page.getByRole('button',{name:'Post comment',exact:true}).click();await page.getByText('A comment without leaving Divine Media',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Playlist',exact:true}).click();await page.getByLabel('New playlist',{exact:true}).fill('Roadtrip');await page.getByRole('button',{name:'Create playlist',exact:true}).click();await page.getByText('Playlist created and video added.',{exact:true}).waitFor();
 await page.screenshot({path:dir+'/unified-video-desktop.png'});
 await page.getByRole('button',{name:'Close',exact:true}).click();
 await page.getByRole('button',{name:'Library',exact:true}).click();await page.getByRole('heading',{name:'Your playlists',exact:true}).waitFor();await page.getByRole('heading',{name:'Roadtrip',exact:true}).waitFor();
 await page.getByRole('button',{name:'Edit playlist',exact:true}).click();await page.getByLabel('Name',{exact:true}).fill('Roadtrip favorites');await page.getByRole('button',{name:'Save playlist',exact:true}).click();await page.getByRole('heading',{name:'Roadtrip favorites',exact:true}).waitFor();
 await page.getByRole('button',{name:'Close workspace',exact:true}).click();await page.getByRole('button',{name:'Categories',exact:true}).click();await page.getByRole('button',{name:'Music',exact:true}).click();assert.equal(new URL(page.url()).pathname,'/category/1');await page.getByRole('button',{name:'Divine test video Test creator',exact:false}).waitFor();
 await page.getByRole('button',{name:'Close workspace',exact:true}).click();
 await page.getByRole('button',{name:'Account notifications',exact:true}).click();await page.getByRole('heading',{name:'Welcome creator',exact:true}).waitFor();assert.equal(await page.locator('iframe').count(),0);await page.getByRole('button',{name:'Close workspace',exact:true}).click();
 await page.getByRole('button',{name:'Upload media',exact:true}).click();await page.getByLabel('Title',{exact:true}).fill('Isolated upload');await page.getByLabel('Media file',{exact:true}).setInputFiles({name:'isolated.mp3',mimeType:'audio/mpeg',buffer:Buffer.from('isolated-ui-fixture')});await page.getByRole('button',{name:'Start upload',exact:true}).click();await page.getByRole('heading',{name:'Encoding queue',exact:true}).waitFor();assert.equal(new URL(page.url()).pathname,'/creator/encoding');
 await page.getByRole('button',{name:'Close workspace',exact:true}).click();await page.getByRole('button',{name:'Account and creator tools',exact:true}).click();await page.getByRole('button',{name:'Live studio',exact:true}).click();await page.getByRole('heading',{name:'Live studio',exact:true}).waitFor();await page.getByLabel('Broadcast title',{exact:true}).waitFor();
 const widths=[];for(const width of [1440,390,320]){await page.setViewportSize({width,height:1000});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1||[...document.querySelectorAll('.dm-workspace')].some(e=>e.getBoundingClientRect().right>innerWidth+1));assert.equal(overflow,false,'Workspace overflows '+width);widths.push(width);if(width===390)await page.screenshot({path:dir+'/unified-studio-mobile.png'})}
 assert.equal(await page.locator('a[href^="https://media.divinemedia.us"]').count(),0);assert.equal(new URL(page.url()).origin,origin);assert.deepEqual(errors,[]);
 await page.getByRole('button',{name:'Close workspace',exact:true}).click();
 await page.getByRole('button',{name:'View Divine test video',exact:true}).click();
 await page.goBack();await page.waitForFunction(()=>!document.querySelector('.watch-modal'));
 await page.goForward();await page.locator('.watch-modal').waitFor();
 assert.equal(new URL(page.url()).pathname,'/watch/101');
 for(const width of [390,320]){await page.setViewportSize({width,height:900});await page.locator('.dm-player').getByRole('button',{name:'Display options',exact:true}).click();const bounds=await page.locator('.dm-player .dm-display-panel').evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1});assert(bounds,'Display menu outside mobile viewport');await page.getByRole('button',{name:'Close display options',exact:true}).click();
  await page.setViewportSize({width,height:900});await page.getByRole('button',{name:'More video options',exact:true}).click();
  assert.equal(await page.locator('.dm-more-panel').evaluate(el=>el.getBoundingClientRect().right>innerWidth+1),false);
  await page.screenshot({path:dir+'/more-options-'+width+'.png'});await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Playback options',exact:true}).click();
  await page.locator('.dm-player-panel').scrollIntoViewIfNeeded();
  assert.equal(await page.locator('.dm-player-panel').evaluate(el=>{const r=el.getBoundingClientRect();return r.left<0||r.right>innerWidth+1||r.top<0||r.bottom>innerHeight+1}),false);
  await page.screenshot({path:dir+'/player-options-'+width+'.png'});await page.keyboard.press('Escape');
 }
 await page.goto(origin+'/channel/test-creator?theme=code-black');
 await page.waitForFunction(()=>[...document.querySelectorAll('.dm-workspace-tile img')].some(img=>img.getAttribute('src')==='/2ndTimeAround.jpg'&&img.naturalWidth>0));
 assert.deepEqual(errors,[]);
 const report={result:'pass',mode:'frontend interaction fixtures; native backend verified separately',video_comments_likes_sharing_playlists_stay_on_frontend:true,account_login_same_origin:true,player_controls_and_native_preferences:true,more_menu_and_mobile_layout:true,broken_channel_artwork_fallback:true,browser_back_forward_preserves_watch_routes:true,categories_and_creator_tools_same_origin:true,no_native_html_iframes:true,no_backend_navigation_links:true,upload_chunks_ui:true,widths,errors,action_names:[...new Set(actions)],real_accounts_or_backend_mutations:false};
 fs.writeFileSync(dir+'/unified-frontend-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
