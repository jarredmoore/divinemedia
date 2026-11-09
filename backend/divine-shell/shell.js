(() => {
 'use strict';
 const COOKIE='dm_view_theme',KEY='divine-media:theme:v1';
 const normalize=v=>v==='cold-black'?'code-black':['default','code-black'].includes(v)?v:null;
 const params=new URLSearchParams(location.search);
 const shared=document.cookie.split(';').map(v=>v.trim()).find(v=>v.startsWith(COOKIE+'='));
 let theme=normalize(params.get('theme'))||normalize(shared?.slice(COOKIE.length+1))||normalize(document.documentElement.dataset.dmTheme)||'default';
 function persist(){document.documentElement.dataset.dmTheme=theme;try{localStorage.setItem(KEY,theme)}catch{}if(location.hostname==='media.divinemedia.us')document.cookie=COOKIE+'='+theme+'; Domain=divinemedia.us; Path=/; Max-Age=31536000; Secure; SameSite=Lax';}
 function canonical(value){
  try{const u=new URL(value,location.href);if(!['https:','http:'].includes(u.protocol)||u.username||u.password)return value;
   if(!['media.divinemedia.us','divinemedia.us','www.divinemedia.us','media.divinecreativegroup.com','watch.divinecreativegroup.com'].includes(u.hostname))return value;
   if(/\.(mp3|mp4|m3u8|jpg|jpeg|png|gif|webp|vtt|srt|pdf|zip)$/i.test(u.pathname))return value;
   if([...u.searchParams.keys()].some(k=>/^(pass(word)?|token|api_secret|apisecret|key|secret|sid|session)$/i.test(k)))return value;
   if(u.hostname==='media.divinecreativegroup.com')u.hostname='media.divinemedia.us';if(['watch.divinecreativegroup.com','www.divinemedia.us'].includes(u.hostname))u.hostname='divinemedia.us';if(u.hostname==='media.divinemedia.us'&&u.pathname==='/plugin/Gallery/view/mainAreaLive.php')u.pathname='/live';u.protocol='https:';u.searchParams.set('theme',theme);return u.href;
  }catch{return value}
 }
 // Native toast callbacks use PHP_SELF for history entries. Keep the existing public Live alias.
 for(const method of ['pushState','replaceState']){
  const original=history[method];
  history[method]=function(state,title,url){
   let next=url;
   if(url!=null){try{const u=new URL(String(url),location.href);if(u.origin===location.origin&&u.pathname==='/plugin/Gallery/view/mainAreaLive.php'){u.pathname='/live';next=u.href}}catch{}}
   return original.call(this,state,title,next);
  };
 }
 function updateLinks(root=document){for(const a of root.querySelectorAll('a[href]')){const raw=a.getAttribute('href');if(!raw||/^(#|javascript:|mailto:|tel:)/i.test(raw)||a.hasAttribute('download'))continue;const next=canonical(raw);if(next!==raw)a.setAttribute('href',next)}}
 function picker(){const label=document.createElement('label');label.className='dm-route-picker';const name=document.createElement('span');name.className='dm-route-sr';name.textContent='Viewing theme';const select=document.createElement('select');select.setAttribute('aria-label','Viewing theme');for(const [value,text] of [['default','Default'],['code-black','Code Black']]){const option=new Option(text,value);select.add(option)}select.value=theme;select.addEventListener('change',()=>{theme=select.value;persist();const u=new URL(location.href);u.searchParams.set('theme',theme);history.replaceState(null,'',u);for(const s of document.querySelectorAll('.dm-route-picker select'))s.value=theme;updateLinks()});label.append(name,select);return label}
 function mount(){
  persist();if(location.pathname==='/plugin/Gallery/view/mainAreaLive.php'){history.replaceState(null,'',canonical(location.href))}if(location.pathname==='/live'||location.pathname==='/live/'){const link=document.querySelector('link[rel=canonical]');if(link)link.href='https://media.divinemedia.us/live';const meta=document.querySelector('meta[property="og:url"]');if(meta)meta.content='https://media.divinemedia.us/live'}updateLinks();
  // In-page anchors and dynamically inserted native menus keep their native handlers.
  document.addEventListener('click',e=>{const a=e.target.closest?.('a[href]');if(a&&!a.hasAttribute('download')){const raw=a.getAttribute('href');if(raw&&!/^(#|javascript:|mailto:|tel:)/i.test(raw))a.setAttribute('href',canonical(raw))}},true);
  const compact=params.get('noNavbar');
  if(self!==top||window.opener||/\/(?:videoEmbed|audioEmbed|vEmbed|videoEmbeded)\//i.test(location.pathname)||(compact&&compact!=='0'&&compact!=='false'))return;
  document.body.classList.add('dm-route-branded');
  const existing=document.querySelector('.dm-auth-shell .dm-header,.dm-entrance .dm-header,.dmc-header');
  if(existing){const tools=document.createElement('div');tools.className='dm-route-existing-tools';tools.append(picker());existing.append(tools);return}
  const header=document.createElement('header');header.className='dm-route-header';header.innerHTML='<a class="dm-route-brand" href="https://divinemedia.us/"><img src="/divine-shell/mark.svg" width="34" height="34" alt=""><span>DIVINE MEDIA</span></a><nav aria-label="Divine Media navigation"><a href="https://divinemedia.us/">Watch &amp; Listen</a><a href="/view/">Media library</a><a href="/live">Live</a><a href="/upload">Upload</a><a href="/Encoder/">Encoder</a><a href="/user">My account</a></nav><div class="dm-route-tools"></div>';
  header.querySelector('.dm-route-tools').append(picker());document.body.prepend(header);document.body.classList.add('dm-route-shell');updateLinks(header);
  if(['/live','/live/'].includes(location.pathname)){const intro=document.createElement('section');intro.className='dm-route-live-intro';intro.innerHTML='<h1>Live on Divine Media</h1><p>Live broadcasts from Divine creators. Streams appear here when creators go live.</p>';header.after(intro)}
  for(const img of document.querySelectorAll('.navbar-brand img')){if(/(?:avideo|youphptube|logo\.png|logo\.svg)/i.test(img.getAttribute('src')||'')){img.src='/divine-shell/mark.svg';img.alt='Divine Media';img.classList.add('dm-route-native-mark')}}
 }
 persist();if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(mount,0),{once:true});else setTimeout(mount,0);
})();
