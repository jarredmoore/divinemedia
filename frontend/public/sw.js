// Only the generic offline page and public brand icons are stored. Account/API/media requests are never cached.
const OFFLINE_CACHE='divine-offline-v1';
self.addEventListener('install',event=>{event.waitUntil(caches.open(OFFLINE_CACHE).then(cache=>cache.addAll(['/offline.html','/icons/divine-192.png','/icons/divine-512.png'])).then(()=>self.skipWaiting()))});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('divine-offline-')&&key!==OFFLINE_CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==self.location.origin)return;
 if(['/offline.html','/icons/divine-192.png','/icons/divine-512.png'].includes(url.pathname)){event.respondWith(caches.open(OFFLINE_CACHE).then(cache=>cache.match(url.pathname)).then(hit=>hit||fetch(request)));return}
 if(request.mode!=='navigate'||url.pathname.startsWith('/api/')||url.pathname.startsWith('/.netlify/'))return;
 event.respondWith(fetch(request).catch(()=>caches.open(OFFLINE_CACHE).then(cache=>cache.match('/offline.html'))));
});
