const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const repo=path.join(__dirname,'../../..'),out=process.env.BROWSER_ARTIFACTS||'/tmp/link-import-browser';fs.mkdirSync(out,{recursive:true});
(async()=>{const server=await require('./fixture-server.cjs')(path.join(repo,'frontend/dist')),origin=server.origin;const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox'],headless:true}),results=[];
for(const width of [1440,390]){
 const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce',serviceWorkers:'block'}),calls=[],errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',route=>{const r=route.request(),u=new URL(r.url()),reply=(d,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(d)});
  if(u.pathname==='/divine-media/session')return reply({});
  if(u.pathname.startsWith('/api/platform/')){const a=u.pathname.split('/').at(-1);if(r.method()==='POST')calls.push({action:a,data:r.postDataJSON()});
   if(a==='session')return reply({csrf:'fixture',user:{id:7,name:'Creator',permissions:{upload:true,embed:true}},capabilities:{playlists:true}});
   if(a==='delivery-grant')return reply({grant:'a'.repeat(64)});
   if(a==='creator-options')return reply({formats:{video:['mp4']},maxThumbnailBytes:2097152,categories:[{id:2,name:'Film'}],canChangeCategory:true,tagGroups:[],ratings:['']});
   if(a==='link-preview')return reply({ticket:'a'.repeat(48),item:{title:'Vimeo preview',provider:'Vimeo',url:r.postDataJSON().url,durationSeconds:90,description:'Source description'},profiles:['mp4','hls','audio','webm']});
   if(a==='link-import')return reply({id:42,videoId:91,message:'Import queued as a private draft.'});
   if(a==='creator-record')return reply({item:{id:91,title:'My imported video',visibility:'private',tags:{}}});
   if(a==='embed-preview')return reply({items:[{id:'M5hZAL_hW7c',title:'YouTube embed',ticket:'embed-fixture',thumbs:'/icons/divine-192.png'}]});
   return reply({items:[]});
  }
  if(u.pathname==='/api/public-catalog')return reply({response:{rows:[]}});if(u.pathname==='/media.json')return reply([]);if(u.origin!==origin)return route.abort();if(!path.extname(u.pathname))return route.fulfill({contentType:'text/html',body:fs.readFileSync(path.join(repo,'frontend/dist/index.html'))});return route.continue();
 });
 await page.goto(origin+'/creator/embed?theme=code-black');const field=page.getByLabel('Video or channel URL',{exact:true});await field.waitFor();assert.equal(await field.count(),1);
 await field.fill('https://vimeo.com/76979871');await page.getByRole('button',{name:'Preview link',exact:true}).click();const review=page.getByRole('region',{name:'Import preview'});await review.getByRole('heading',{name:'Vimeo preview'}).waitFor();assert.equal(calls.filter(c=>c.action==='link-import').length,0);
 await review.getByLabel('Import title',{exact:true}).fill('My imported video');await review.getByLabel('Category',{exact:true}).selectOption('2');await review.getByLabel('Encoding output',{exact:true}).selectOption('hls');await page.screenshot({path:path.join(out,'import-'+width+'.png')});
 await review.getByRole('button',{name:'Import to private draft',exact:true}).click();await review.getByText('Import queued. Job 42.',{exact:false}).waitFor();const submitted=calls.find(c=>c.action==='link-import').data;assert.equal(submitted.ticket,'a'.repeat(48));assert.equal(submitted.title,'My imported video');assert.equal(submitted.profile,'hls');assert.equal(submitted.categoryId,'2');assert(!('url'in submitted));assert(!('videoId'in submitted));
 await review.getByRole('button',{name:'Edit details & thumbnail',exact:true}).click();await review.getByLabel('Landscape thumbnail',{exact:true}).waitFor();assert.equal(await page.getByRole('dialog').count(),1);
 await field.fill('https://youtu.be/M5hZAL_hW7c');await page.getByRole('button',{name:'Preview link',exact:true}).click();await page.getByText('YouTube embed',{exact:true}).waitFor();assert.equal(calls.filter(c=>c.action==='embed-preview').length,1);
 await page.getByLabel('Link handling',{exact:true}).selectOption('import');await page.getByRole('button',{name:'Preview link',exact:true}).click();await page.getByRole('region',{name:'Import preview'}).waitFor();assert.equal(calls.filter(c=>c.action==='link-preview').length,2);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);results.push({width,one_link_field:true,provider_detection:true,explicit_import_confirmation:true,private_draft:true,metadata_and_thumbnail_in_same_card:true,existing_youtube_embed:true,no_native_navigation:true});await page.close();
}
await browser.close();await server.close();console.log(JSON.stringify({result:'pass',synthetic_records_only:true,results}));})().catch(e=>{console.error(e);process.exit(1)});
