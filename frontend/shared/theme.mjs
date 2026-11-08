export const THEME_KEY='divine-media:theme:v1';
export const THEME_COOKIE='dm_view_theme';
export function normalizeTheme(value){return value==='cold-black'?'code-black':['default','code-black'].includes(value)?value:null}
export function resolveTheme({search='',cookie='',stored=null}={}){
 const requested=normalizeTheme(new URLSearchParams(search).get('theme'));if(requested)return requested;
 const match=cookie.split(';').map(v=>v.trim()).find(v=>v.startsWith(THEME_COOKIE+'='));
 const shared=match&&normalizeTheme(match.slice(THEME_COOKIE.length+1));return shared||normalizeTheme(stored)||'default';
}
export function readCurrentTheme(){let stored=null,cookie='';try{cookie=globalThis.document?.cookie||''}catch{};try{stored=globalThis.localStorage?.getItem(THEME_KEY)}catch{/* storage can be blocked */}return resolveTheme({search:globalThis.location?.search,cookie,stored})}
export function persistTheme(value){const theme=normalizeTheme(value)||'default';try{localStorage.setItem(THEME_KEY,theme)}catch{/* optional preference */}
 try{const host=location.hostname;if(host==='divinemedia.us'||host.endsWith('.divinemedia.us'))document.cookie=THEME_COOKIE+'='+theme+'; Domain=divinemedia.us; Path=/; Max-Age=31536000; Secure; SameSite=Lax'}catch{/* previews use the URL handoff */}}
export function themedUrl(value,theme=readCurrentTheme()){
 try{const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password)return value;
  if([...u.searchParams.keys()].some(k=>/^(pass(word)?|token|api_secret|apisecret|key|secret|sid|session)$/i.test(k)))return value;
  if(['divinemedia.us','www.divinemedia.us','media.divinemedia.us','media.divinecreativegroup.com','watch.divinecreativegroup.com'].includes(u.hostname)){
   if(u.hostname==='media.divinecreativegroup.com')u.hostname='media.divinemedia.us';if(u.hostname==='watch.divinecreativegroup.com'||u.hostname==='www.divinemedia.us')u.hostname='divinemedia.us';u.searchParams.set('theme',normalizeTheme(theme)||'default');return u.href;
  }
 }catch{/* leave unsupported links unchanged */}return value;
}
