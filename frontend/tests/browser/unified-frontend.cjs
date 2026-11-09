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
 await context.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
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
  if(action==='channel')return send({items:[item],channel:{userId:7,followers:0,following:false}});
  if(action==='login'){user={id:7,name:'Test creator',username:'creator',permissions:{upload:true,stream:true,comment:true}};return send({user,csrf:'isolated-authenticated-nonce'})}
  if(action==='logout'){user=null;return send({message:'Signed out.'})}
  if(action==='video')return send({item,likes,dislikes:0,reaction:likes?1:0});
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
 await page.goto(origin+'/?theme=code-black');await page.getByText('DIVINE CATALOG',{exact:false}).waitFor();
 await page.getByRole('button',{name:'View Divine test video',exact:true}).click();
 assert.equal(new URL(page.url()).pathname,'/watch/101');assert.equal(await page.locator('iframe').count(),0);
 assert(await page.locator('video.real-video').getAttribute('controls')!==null);
 await page.getByRole('button',{name:'Copy link',exact:true}).click();assert.equal(await page.evaluate(()=>window.__copied),'https://divinemedia.us/watch/101');
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
 const report={result:'pass',mode:'frontend interaction fixtures; native backend verified separately',video_comments_likes_sharing_playlists_stay_on_frontend:true,account_login_same_origin:true,browser_back_forward_preserves_watch_routes:true,categories_and_creator_tools_same_origin:true,no_native_html_iframes:true,no_backend_navigation_links:true,upload_chunks_ui:true,widths,errors,action_names:[...new Set(actions)],real_accounts_or_backend_mutations:false};
 fs.writeFileSync(dir+'/unified-frontend-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
