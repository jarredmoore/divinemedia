const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const repo=path.join(__dirname,'../../..'),out=process.env.BROWSER_ARTIFACTS||'/tmp/backstage-browser';fs.mkdirSync(out,{recursive:true});
(async()=>{const server=await require('./fixture-server.cjs')(path.join(repo,'frontend/dist'));const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox'],headless:true});const results=[];
try{for(const width of [1440,390,320]){
 const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce',serviceWorkers:'block'}),errors=[];page.setDefaultTimeout(12000);page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>{const u=new URL(r.request().url()),reply=d=>r.fulfill({contentType:'application/json',body:JSON.stringify(d)});
  if(u.pathname==='/divine-media/session')return reply({});
  if(u.pathname.startsWith('/api/platform/')){const action=u.pathname.split('/').at(-1);
   if(action==='session')return reply({csrf:'fixture',user:{id:7,name:'Creator',permissions:{upload:true,embed:true}},capabilities:{playlists:true}});
   if(action==='delivery-grant')return reply({grant:'a'.repeat(64)});
   if(action==='catalog')return reply({items:[{id:4,avideoId:4,title:'After the lights',type:'Watch',tag:'CONCERT FILM',creator:'Divine Media',img:'/themes/cold-black/stage-poster.jpg',watchUrl:'https://media.divinemedia.us/video/4'}]});
   if(action==='video')return reply({item:{id:4,avideoId:4,title:'After the lights',type:'Watch',img:'/themes/cold-black/stage-poster.jpg',videoUrl:'/fixture.mp4'},player:{}});
   if(action==='creator-options')return reply({formats:{video:['mp4'],audio:['mp3'],image:['png']},maxThumbnailBytes:2097152,categories:[{id:1,name:'Media'}],canChangeCategory:true,tagGroups:[],ratings:['']});
   return reply({items:[]});
  }
  if(u.pathname==='/media.json')return reply([]);if(u.origin!==server.origin)return r.abort();return r.continue();
 });
 await page.goto(server.origin+'/?theme=backstage');await page.getByRole('heading',{name:'FEEL EVERY FRAME.'}).waitFor();await page.getByRole('heading',{name:'After the lights',exact:true}).first().waitFor();
 assert.equal(await page.locator('html').getAttribute('data-theme'),'backstage');assert.equal(await page.getByRole('button',{name:'Pause background motion',exact:true}).count(),0);
 assert.equal(await page.locator('.bs-ticker>div').evaluate(e=>getComputedStyle(e).animationName),'none');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow at '+width);
 await page.screenshot({path:path.join(out,'backstage-'+width+'.png')});
 await page.locator('.bs-hero').getByRole('button',{name:'Watch now',exact:false}).click();await page.getByRole('dialog',{name:'After the lights',exact:true}).waitFor();assert(new URL(page.url()).pathname==='/watch/4');await page.getByRole('button',{name:'Close',exact:true}).click();
 if(width<901){const menu=page.getByRole('button',{name:'Open navigation',exact:true});await menu.click();assert.equal(await page.getByRole('button',{name:'Close navigation',exact:true}).getAttribute('aria-expanded'),'true');await page.keyboard.press('Escape');assert.equal(await page.getByRole('button',{name:'Open navigation',exact:true}).getAttribute('aria-expanded'),'false');}
 if(width<901)await page.getByRole('button',{name:'Open navigation',exact:true}).click();
 const picker=page.getByRole('combobox',{name:'Viewing theme',exact:true});await picker.selectOption('code-black');await page.locator('.cb-scene').waitFor();assert.equal(await page.locator('.bs-hero').count(),0);await picker.selectOption('default');await page.locator('.hero').waitFor();assert.equal(await page.locator('.backstage').count(),0);await page.getByRole('combobox',{name:'Viewing theme',exact:true}).selectOption('backstage');await page.reload();await page.locator('.bs-hero').waitFor();
 await page.goto(server.origin+'/creator/upload');await page.getByLabel('Title',{exact:true}).waitFor().catch(async e=>{console.error(JSON.stringify({width,errors,text:(await page.locator('body').innerText()).slice(-650)}));await page.screenshot({path:path.join(out,'studio-error.png')});throw e});assert.equal(await page.locator('html').getAttribute('data-theme'),'backstage');await page.screenshot({path:path.join(out,'studio-'+width+'.png')});assert.deepEqual(errors,[]);results.push({width,themeSwitching:true,player:true,studio:true,reducedMotion:true,overflow:false});await page.close();
}
 const page=await browser.newPage({viewport:{width:1440,height:950},reducedMotion:'no-preference',serviceWorkers:'block'});await page.route('**/api/**',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({items:[],csrf:'fixture',user:null})}));await page.goto(server.origin+'/?theme=backstage');const pause=page.getByRole('button',{name:'Pause background motion',exact:true});await pause.waitFor();await page.evaluate(()=>scrollTo(0,400));await page.waitForTimeout(150);assert(Number(await page.locator('.bs-hero').evaluate(e=>e.style.getPropertyValue('--bs-progress')))>0);await pause.click();assert.equal(await page.locator('.bs-ticker>div').evaluate(e=>getComputedStyle(e).animationPlayState),'paused');assert.equal(await page.locator('.bs-hero').evaluate(e=>e.style.getPropertyValue('--bs-progress')),'0');await page.close();console.log(JSON.stringify({result:'pass',viewports:results,motionPause:true}));
}finally{await browser.close();await server.close()}})().catch(e=>{console.error(e);process.exit(1)});
