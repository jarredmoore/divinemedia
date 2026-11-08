import {readCurrentTheme} from '../shared/theme.mjs';
import {MEDIA_ORIGINS,canonicalMediaUrl} from '../shared/domains.mjs';
export function nativeEmbedUrl(item,origin){
 if(!item?.watchUrl)return undefined;
 const canonical=canonicalMediaUrl(item.watchUrl,origin);if(!canonical)return undefined;
 const url=new URL(canonical);
 if(!MEDIA_ORIGINS.includes(url.origin))return undefined;
 if(!/\/(video|audio)\/[\w.-]+(?:\/|$)/.test(url.pathname))return undefined;
 url.pathname=url.pathname.replace(/\/(video|audio)\//,'/$1Embed/');url.search='';url.hash='';
 url.searchParams.set('theme',readCurrentTheme());url.searchParams.set('autoplay','0');url.searchParams.set('controls','1');url.searchParams.set('disableCloseButton','1');
 return url.href;
}
export function nativeContentUrl(item,origin){return canonicalMediaUrl(item?.watchUrl,origin)||undefined}
