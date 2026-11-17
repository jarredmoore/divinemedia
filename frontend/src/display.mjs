let senderPromise;
export function activeMedia(doc=document){return doc.querySelector('video.real-video')||doc.querySelector('audio.real-audio')||doc.querySelector('.dm-dock audio')}
export function castSource(media){
 const raw=media?.dataset?.displaySource||media?.currentSrc||media?.src;
 let url;try{url=new URL(raw)}catch{throw Error('Open a video or play audio before connecting a display.')}
 if(url.protocol!=='https:'||url.username||url.password)throw Error('This media cannot be sent to a display.');
 const path=url.pathname.toLowerCase(),type=/\.m3u8$/.test(path)?'application/x-mpegURL':/\.mp3$/.test(path)?'audio/mpeg':/\.m4a$/.test(path)?'audio/mp4':/\.webm$/.test(path)?'video/webm':'video/mp4';
 return {url:url.href,type};
}
export async function siteFullscreen(doc=document){
 if(doc.fullscreenElement)return doc.exitFullscreen();
 if(doc.documentElement.requestFullscreen&&doc.fullscreenEnabled)return doc.documentElement.requestFullscreen();
 if(doc.webkitFullscreenElement)return doc.webkitExitFullscreen();
 if(doc.documentElement.webkitRequestFullscreen)return doc.documentElement.webkitRequestFullscreen();
 const media=activeMedia(doc);if(media?.webkitEnterFullscreen)return media.webkitEnterFullscreen();
 throw Error('Site fullscreen is unavailable in this browser. Use the video’s native fullscreen control.');
}
export function loadCastSender(win=window,doc=document){
 if(win.cast?.framework&&win.chrome?.cast?.isAvailable)return Promise.resolve(win.cast.framework);
 if(senderPromise)return senderPromise;
 senderPromise=new Promise((resolve,reject)=>{
  const previous=win.__onGCastApiAvailable;let timer;
  const finish=available=>{clearTimeout(timer);if(available&&win.cast?.framework)resolve(win.cast.framework);else{senderPromise=null;reject(Error('Google Cast could not load. Check your connection and try again.'))}};
  win.__onGCastApiAvailable=(available,...args)=>{try{previous?.(available,...args)}finally{finish(available)}};
  const script=doc.createElement('script');script.src='https://www.gstatic.com/cv/js/sender/v1/cast_sender.js?loadCastFramework=1';script.async=true;script.onerror=()=>finish(false);timer=setTimeout(()=>finish(false),15000);doc.head.append(script);
 });return senderPromise;
}
export async function castMedia(media,win=window){
 const source=castSource(media),framework=win.cast?.framework,api=win.chrome?.cast;
 if(!framework||!api)throw Error('Google Cast is still loading. Try again shortly.');
 const context=framework.CastContext.getInstance();
 context.setOptions({receiverApplicationId:api.media.DEFAULT_MEDIA_RECEIVER_APP_ID,autoJoinPolicy:api.AutoJoinPolicy.TAB_AND_ORIGIN_SCOPED});
 if(!context.getCurrentSession())await context.requestSession();
 const session=context.getCurrentSession();if(!session)throw Error('No display was connected.');
 const info=new api.media.MediaInfo(source.url,source.type);
 if(media.duration===Infinity)info.streamType=api.media.StreamType.LIVE;
 const request=new api.media.LoadRequest(info);request.autoplay=true;
 if(Number.isFinite(media.duration)&&media.currentTime>0)request.currentTime=media.currentTime;
 await session.loadMedia(request);media.pause();return context;
}
