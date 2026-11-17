// Isolated install-choice doubles plus a real localhost service worker; never submits live accounts.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),assert=require('assert');
const origin=process.env.PWA_TEST_URL||'http://127.0.0.1:4175',dir=process.env.BROWSER_ARTIFACTS||'/tmp/divine-pwa';fs.mkdirSync(dir,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({reducedMotion:'reduce'}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await context.addInitScript(()=>addEventListener('beforeinstallprompt',e=>{if(e.isTrusted){e.preventDefault();e.stopImmediatePropagation()}},true));
 await context.route('**/api/**',route=>{const path=new URL(route.request().url()).pathname;return route.fulfill({json:path.endsWith('/session')?{user:null,csrf:'isolated-pwa-test',captchaRequired:false}:{items:[]}})});
 const layouts=[];
 for(const theme of ['default','code-black'])for(const width of [1440,390,320]){
  await page.setViewportSize({width,height:900});await page.goto(origin+'/?theme='+theme);await page.locator('header').getByRole('button',{name:'Install Divine Media',exact:true}).click();
  const dialog=page.getByRole('dialog',{name:'Install Divine Media',exact:true});await dialog.waitFor();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,'Install page overflow '+theme+' '+width);
  assert(await dialog.evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1}));
  await page.getByRole('button',{name:'Got it',exact:true}).click();await page.screenshot({path:dir+'/install-'+theme+'-'+width+'.png'});layouts.push({theme,width});
 }
 await page.evaluate(()=>{window.__installPrompts=0;const e=new Event('beforeinstallprompt',{cancelable:true});e.prompt=async()=>window.__installPrompts++;e.userChoice=Promise.resolve({outcome:'dismissed'});dispatchEvent(e)});
 await page.locator('header').getByRole('button',{name:'Install Divine Media',exact:true}).click();assert.equal(await page.evaluate(()=>window.__installPrompts),1);await page.locator('.dm-install-card').waitFor();
 await page.evaluate(()=>{const e=new Event('beforeinstallprompt',{cancelable:true});e.prompt=async()=>window.__installPrompts++;e.userChoice=Promise.resolve({outcome:'accepted'});dispatchEvent(e)});
 await page.locator('header').getByRole('button',{name:'Install Divine Media',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('.dm-install-card'));assert.equal(await page.evaluate(()=>window.__installPrompts),2);
 await page.goto(origin+'/?theme=code-black');await page.evaluate(()=>dispatchEvent(new Event('appinstalled')));await page.waitForFunction(()=>!document.querySelector('.dm-install-card'));
 await page.evaluate(()=>navigator.serviceWorker.ready);await page.waitForFunction(()=>navigator.serviceWorker.controller);
 const manifest=await page.evaluate(async()=>{const r=await fetch('/manifest.webmanifest');return r.json()});assert.equal(manifest.name,'Divine Media');
 const cached=await page.evaluate(async()=>{const c=await caches.open('divine-offline-v3');return(await c.keys()).map(r=>new URL(r.url).pathname)});assert.deepEqual(cached.sort(),['/icons/divine-192.png','/icons/divine-512.png','/offline.html'].sort());
 await context.setOffline(true);await page.goto(origin+'/categories');await page.getByRole('heading',{name:'Reconnect to Divine Media',exact:true}).waitFor();assert.equal(await page.locator('img').evaluate(el=>el.complete&&el.naturalWidth>0),true);
 const iosContext=await browser.newContext({userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile Safari/604.1'});const iosPage=await iosContext.newPage();await iosContext.route('**/api/**',route=>route.fulfill({json:{items:[],user:null,csrf:'isolated-ios'}}));await iosPage.goto(origin+'/?theme=code-black');await iosPage.locator('header').getByRole('button',{name:'Install Divine Media',exact:true}).click();await iosPage.getByText('Add to Home Screen',{exact:true}).waitFor();await iosContext.close();
 const standalone=await browser.newContext();await standalone.addInitScript(()=>Object.defineProperty(navigator,'standalone',{value:true}));const standalonePage=await standalone.newPage();await standalone.route('**/api/**',route=>route.fulfill({json:{items:[],user:null,csrf:'isolated-standalone'}}));await standalonePage.goto(origin+'/?theme=code-black');await standalonePage.locator('.cb-wordmark').waitFor();assert.equal(await standalonePage.locator('.dm-install-card,.dm-install-trigger').count(),0);await standalone.close();
 assert.deepEqual(errors,[]);const report={result:'pass',layouts,native_prompt_accepted_and_dismissed:'simulated choices passed',appinstalled_hides_cta:true,standalone_hides_cta:true,ios_manual_instructions:true,real_service_worker_ready:true,offline_navigation_and_brand_icon:true,cache_paths:cached,errors,real_user_installation:false};fs.writeFileSync(dir+'/pwa-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
