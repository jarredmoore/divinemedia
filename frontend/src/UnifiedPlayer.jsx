import React,{useEffect,useRef,useState} from 'react';
import useNativePlayback from './useNativePlayback.js';
import {usePlatform} from './PlatformContext.jsx';
import {platform} from './platform-client.mjs';
export default function UnifiedPlayer({item,embedded=false}){
 const video=useRef(null),[resolved,setResolved]=useState(()=>item.avideoId?{...item,videoUrl:null,audioUrl:null}:item),[error,setError]=useState(''),[locked,setLocked]=useState(false),[password,setPassword]=useState(''),[busy,setBusy]=useState(false);
 const {session}=usePlatform();
 const playback=useNativePlayback(item);
 const src=resolved.videoUrl||resolved.audioUrl,id=Number(item.avideoId||item.id);
 useEffect(()=>{let active=true;setResolved(item.avideoId?{...item,videoUrl:null,audioUrl:null}:item);setLocked(false);setError('');
  if(item.avideoId&&id>0)platform('video',{query:{id,...(embedded?{mode:'embed'}:{})}}).then(d=>{if(active)setResolved(d.item)}).catch(e=>{if(active){setError(e.message);setLocked(e.details?.code==='video_password_required')}});
  return()=>{active=false};
 },[item,id,embedded,session?.user?.id]);
 useEffect(()=>{let player,active=true;if(!src||!video.current)return;const el=video.current;
  if(/\.m3u8(?:[?#]|$)/i.test(src)&&!el.canPlayType('application/vnd.apple.mpegurl')){
   import('hls.js').then(({default:Hls})=>{if(!active)return;if(!Hls.isSupported()){setError('Live playback is not supported by this browser.');return}player=new Hls();player.loadSource(src);player.attachMedia(el);player.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal)setError('This broadcast is unavailable. Try again shortly.')})}).catch(()=>setError('Unable to load live playback.'));
  }else{el.src=src}
  return()=>{active=false;player?.destroy();el.pause();el.removeAttribute('src');el.load()};
 },[src]);
 if(locked)return <form className="dm-inline-panel" onSubmit={async e=>{e.preventDefault();setBusy(true);try{const d=await platform('video-unlock',{method:'POST',data:{video:id,password}});setResolved(d.item);setLocked(false);setError('');setPassword('')}catch(e){setError(e.message)}finally{setBusy(false)}}}><label>Video password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required maxLength={200}/></label><button disabled={busy}>Unlock video</button>{error&&<p role="alert">{error}</p>}</form>;
 return src?<><video {...playback} ref={video} className="real-video" controls playsInline preload="metadata" poster={resolved.img} onError={()=>setError('This media is unavailable. Please try again.')} aria-label={'Watch '+item.title}/>{error&&<p role="alert">{error}</p>}</>:<p role={error?'alert':'status'}>{error||'Loading playback…'}</p>;
}
export function PublicEmbed(){
 const[id]=useState(()=>Number(location.pathname.split('/')[2])),[item,setItem]=useState(null),[error,setError]=useState('');
 useEffect(()=>{platform('video',{query:{id,mode:'embed'}}).then(d=>setItem(d.item)).catch(e=>setError(e.message))},[id]);
 return <main className="dm-public-embed" style={{background:'#000',color:'#eee',minHeight:'100dvh',display:'grid',placeItems:'center'}}>{item?<UnifiedPlayer item={item} embedded/>:<p role={error?'alert':'status'}>{error||'Loading player…'}</p>}</main>;
}
