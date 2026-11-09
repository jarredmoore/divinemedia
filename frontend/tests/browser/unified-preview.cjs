// Read-only deployed preview verification, with TLS-verified curl transport for this executor's CA.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto'),{execFile}=require('child_process');
process.umask(0o077);const watch=process.env.UNIFIED_TEST_URL,dir=process.env.BROWSER_ARTIFACTS||'/tmp/divine-unified-preview';
if(!/^https:\/\/(?:divinemedia\.us|[a-f0-9]{24}--mediaproduction\.netlify\.app)$/.test(watch||''))throw Error('Use the canonical Divine Media URL or an immutable draft URL.');
fs.mkdirSync(dir,{recursive:true});let serial=0,blockedWrites=0;const cache=new Map();
function fetchPublic(url,cookie='',requestHeaders={}){
 const key=url+'|'+crypto.createHash('sha256').update(cookie+JSON.stringify(requestHeaders)).digest('hex');if(cache.has(key))return cache.get(key);
 const promise=new Promise((resolve,reject)=>{const headers=dir+'/headers-'+serial++;const args=['-sS','--user-agent',requestHeaders['user-agent']||'Mozilla/5.0 DivineMediaVerification','--max-time','35','-D',headers,'--config','-',url];if(/\.mp4(?:\?|$)/.test(url))args.push('-H','Range: bytes=0-1048575');const child=execFile('curl',args,{encoding:'buffer',maxBuffer:32*1024*1024},(error,data)=>{if(error)return reject(error);const blocks=fs.readFileSync(headers,'utf8').trim().split(/\r?\n\r?\n/).filter(x=>x.startsWith('HTTP/'));const lines=blocks.at(-1).split(/\r?\n/),status=Number(lines.shift().split(' ')[1]),responseHeaders={},cookies=[];for(const line of lines){const i=line.indexOf(':');if(i<0)continue;const name=line.slice(0,i).toLowerCase(),value=line.slice(i+1).trim();if(name==='set-cookie')cookies.push(value);if(['content-type','content-range','accept-ranges','location','access-control-allow-origin'].includes(name))responseHeaders[name]=value}resolve({status,headers:responseHeaders,body:data,cookies})});const safe=cookie.replace(/[\r\n]/g,'').replace(/\\/g,'\\\\').replace(/"/g,'\\"');const headerLines=cookie?['Cookie: '+safe]:[];for(const name of ['referer','origin','x-requested-with']){const value=requestHeaders[name];if(value&&!/[\r\n]/.test(value))headerLines.push(name+': '+value.replace(/\\/g,'\\\\').replace(/"/g,'\\"'));}child.stdin.end(headerLines.map(h=>'header = "'+h+'"\n').join(''));});cache.set(key,promise);return promise;
}
async function addResponseCookies(context,url,lines){for(const line of lines){const pieces=line.split(';'),at=pieces[0].indexOf('=');if(at<1)continue;const item={name:pieces[0].slice(0,at),value:pieces[0].slice(at+1),domain:new URL(url).hostname,path:'/',secure:false,httpOnly:false,sameSite:'Lax'};for(const raw of pieces.slice(1)){const [k,...rest]=raw.trim().split('='),v=rest.join('=');if(k.toLowerCase()==='domain')item.domain=v;if(k.toLowerCase()==='path')item.path=v;if(k.toLowerCase()==='secure')item.secure=true;if(k.toLowerCase()==='httponly')item.httpOnly=true;if(k.toLowerCase()==='samesite')item.sameSite={none:'None',strict:'Strict',lax:'Lax'}[v.toLowerCase()]||'Lax';if(k.toLowerCase()==='max-age')item.expires=Number(v)<=0?1:Math.floor(Date.now()/1000)+Number(v)}try{await context.addCookies([item])}catch{/* Reject cookies outside the source host, as a browser would. */}}}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce',serviceWorkers:'block'}),page=await context.newPage(),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));
 await context.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(req.method()!=='GET'){blockedWrites++;return route.abort()}
  if(![new URL(watch).host,'media.divinemedia.us','images.unsplash.com','fonts.googleapis.com','fonts.gstatic.com'].includes(url.host))return route.abort();
  try{const r=await fetchPublic(url.href,req.headers().cookie||'',req.headers());await addResponseCookies(context,url.href,r.cookies);if(url.origin===watch&&url.pathname.startsWith('/api/platform/'))requests.push({action:url.pathname.split('/').at(-1),status:r.status});await route.fulfill({status:r.status,headers:r.headers,body:r.body})}catch{await route.abort()}
 });
 await page.goto(watch+'/?theme=code-black',{waitUntil:'domcontentloaded',timeout:60000});
 await page.getByText('DIVINE CATALOG',{exact:false}).waitFor({timeout:45000});
 assert.equal(await page.locator('html').getAttribute('data-theme'),'code-black');
 await page.goto(watch+'/watch/1?theme=code-black',{waitUntil:'domcontentloaded',timeout:60000});
 await page.locator('video.real-video[src]').waitFor({state:'attached',timeout:45000});
 assert.equal(await page.locator('iframe').count(),0);assert.equal(await page.locator('video.real-video').getAttribute('controls'),'');
 assert((await page.locator('video.real-video').getAttribute('src')).startsWith('https://media.divinemedia.us/videos/'));
 await page.getByRole('button',{name:'Like video',exact:true}).click();
 await page.getByRole('dialog',{name:'Your account',exact:true}).waitFor();await page.getByLabel('Email or username').waitFor();
 const cookie=(await context.cookies(watch)).find(c=>c.name==='__Host-dm_session');assert(cookie?.httpOnly&&cookie.secure&&cookie.sameSite==='Lax');
 assert.equal(await page.evaluate(()=>document.cookie.includes('__Host-dm_session=')),false);
 await page.screenshot({path:dir+'/unified-preview-account-desktop.png'});
 const checks=[];
 for(const width of [390,320]){
  await page.setViewportSize({width,height:900});
  for(const route of ['/creator/upload','/creator/encoding','/creator/live','/library/playlists','/categories','/category/default','/live']){
   await page.goto(watch+route+'?theme=code-black',{waitUntil:'domcontentloaded',timeout:60000});
   await page.locator('.dm-workspace').waitFor({timeout:30000});
   await page.waitForTimeout(150);
   assert.equal(await page.locator('iframe').count(),0);assert.equal(await page.locator('a[href^="https://media.divinemedia.us"]').count(),0);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert.equal(overflow,false,route+' overflows '+width);
   checks.push({width,route,overflow});
   if(width===390&&route==='/creator/upload')await page.screenshot({path:dir+'/unified-preview-upload-mobile.png'});
  }
 }
 assert.deepEqual(errors,[]);assert.equal(blockedWrites,0);assert(requests.some(r=>r.action==='session'&&r.status===200));assert(requests.some(r=>r.action==='catalog'&&r.status===200));
 const report={result:'pass',preview:watch,transport:'TLS-verified curl responses in Chromium; no certificate bypass',read_only:true,real_accounts_or_content_mutated:false,frontend_video_element:true,native_html_iframes:false,backend_navigation_links:false,httpOnly_secure_frontend_session:true,creator_routes_stay_on_frontend:true,route_checks:checks,errors,requests};
 fs.writeFileSync(dir+'/unified-preview-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({result:'pass',preview:watch,route_checks:checks.length,errors}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
