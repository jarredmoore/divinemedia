const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const repo=path.join(__dirname,'../../..'),origin=process.env.BROWSER_ORIGIN||'http://127.0.0.1:4200',out=process.env.BROWSER_ARTIFACTS||'/tmp/media-management';fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox'],headless:true}),results=[];
for(const width of [1440,390]){
 const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce',serviceWorkers:'block'}),errors=[],orders=[];
 page.on('pageerror',e=>errors.push(e.message));
 const media=Array.from({length:14},(_,i)=>({id:i+1,avideoId:i+1,title:'Title '+(i+1),img:'/icons/divine-192.png',image:'/icons/divine-192.png',categoryId:i+1,type:'Watch',mediaKind:'video',videoUrl:'https://media.divinemedia.us/videos/fixture.mp4',visibility:'public'}));
 const options={formats:{video:['mp4']},maxThumbnailBytes:2097152,categories:[],tagGroups:[],ratings:[''],canChangeCategory:true};
 await page.route('**/*',route=>{const r=route.request(),u=new URL(r.url()),reply=d=>route.fulfill({contentType:'application/json',body:JSON.stringify(d)});
  if(u.pathname==='/divine-media/session')return reply({});
  if(u.pathname.startsWith('/api/platform/')){const a=u.pathname.split('/').at(-1);
   if(a==='session')return reply({csrf:'fixture',user:{id:7,name:'Creator',permissions:{upload:true,embed:true,stream:true}},capabilities:{live:true,playlists:true}});
   if(a==='delivery-grant')return reply({grant:'a'.repeat(64)});
   if(a==='creator-options')return reply(options);
   if(a==='creator-record')return reply({item:{...media[0],embed:{provider:'youtube',id:'M5hZAL_hW7c'},tags:{},providerMetadata:u.searchParams.has('provider')?{syncedAt:'fixture',statistics:{viewCount:'120',likeCount:'0'}}:undefined}});
   if(a==='categories')return reply({items:media.map(v=>({id:v.id,name:'Category '+v.id}))});
   if(a==='creator-videos'||a==='catalog')return reply({items:media});
   if(a==='playlists')return reply({items:[{id:1,name:'My collection',visibility:'private',items:media}]});
   if(a==='playlist-order'){orders.push(r.postDataJSON());return reply({})}
   return reply({items:[]});
  }
  if(u.pathname==='/api/public-catalog')return reply({response:{rows:[]}});
  if(u.pathname==='/media.json')return reply([]);
  if(u.hostname==='divinecreativegroup.square.site')return route.fulfill({contentType:'text/html',body:'<h1>Fixture Square storefront</h1>'});
  if(u.origin!==origin)return route.abort();
  if(!path.extname(u.pathname))return route.fulfill({contentType:'text/html',body:fs.readFileSync(path.join(repo,'frontend/dist/index.html'))});
  return route.continue();
 });
 await page.goto(origin+'/?theme=cozy');
 // Cozy play glyphs are substantially larger without changing Code Black.
 await page.locator('.primary .dm-icon-play').first().waitFor();
 assert.equal(await page.locator('.primary .dm-icon-play svg').first().evaluate(el=>getComputedStyle(el).width),'26px');
 await page.evaluate(()=>window.dispatchEvent(new CustomEvent('divine:workspace',{detail:{view:'categories'}})));
 await page.locator('.dm-category-tile').first().waitFor();assert.equal(await page.locator('.dm-category-tile').count(),12);
 await page.getByRole('navigation',{name:'categories pages'}).getByRole('button',{name:'Next',exact:true}).click();assert.equal(await page.locator('.dm-category-tile').count(),2);
 await page.getByRole('button',{name:'Close workspace'}).click();
 await page.evaluate(()=>window.dispatchEvent(new CustomEvent('divine:workspace',{detail:{view:'playlists'}})));
 await page.getByRole('heading',{name:'My collection'}).waitFor();assert.equal(await page.locator('.dm-playlist-item').count(),12);
 await page.locator('.dm-playlist-item').first().getByRole('button',{name:'Move Title 1 down',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('.dm-workspace button[disabled][aria-label="Close workspace"]'));
 assert.deepEqual(orders[0].ids.slice(0,2),[2,1]);
 const drag=await page.evaluateHandle(()=>new DataTransfer());await page.locator('.dm-playlist-item').first().dispatchEvent('dragstart',{dataTransfer:drag});await page.locator('.dm-playlist-item').nth(2).dispatchEvent('drop',{dataTransfer:drag});await page.waitForTimeout(100);assert.deepEqual(orders[1].ids.slice(0,3),[2,3,1]);
 await page.getByRole('navigation',{name:'playlist titles pages'}).getByRole('button',{name:'Next',exact:true}).click();assert.equal(await page.locator('.dm-playlist-item').count(),2);
 await page.screenshot({path:path.join(out,'playlists-'+width+'.png')});
 await page.getByRole('navigation',{name:'Studio tools'}).getByRole('button',{name:'Your media',exact:true}).click();
 const row=page.locator('.dm-workspace-row').first();await row.getByText('Links & embedding',{exact:true}).click();assert.equal(await row.getByLabel('Media / streaming URL',{exact:true}).inputValue(),media[0].videoUrl);
 await row.getByRole('button',{name:'Edit details & thumbnail',exact:true}).click();await row.getByRole('button',{name:'Refresh YouTube metadata'}).click();await row.getByText('YouTube metadata',{exact:true}).click();await row.getByText('YouTube views:',{exact:false}).waitFor();
 await page.getByRole('button',{name:'Close workspace'}).click();
 await page.evaluate(()=>window.dispatchEvent(new CustomEvent('divine:workspace',{detail:{view:'shop'}})));
 const frame=page.getByTitle('Divine Creative Group Square store');await frame.waitFor();assert.match(await frame.getAttribute('src'),/^https:\/\/divinecreativegroup\.square\.site\/$/);assert(!(await frame.getAttribute('sandbox')).includes('allow-top-navigation'));
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);
 results.push({width,cozy_play_icons:true,category_thumbnails:true,loaded_list_pagination:true,playlist_keyboard_and_drag_order:true,media_links:true,provider_snapshot:true,square_card_fixture_only:true});await page.close();
}
await browser.close();console.log(JSON.stringify({result:'pass',results}));})().catch(e=>{console.error(e);process.exit(1)});
