import {useEffect,useRef} from 'react';
import {platform} from './platform-client.mjs';
// Track actual playback, never a preview render or catalog fetch. AVideo owns deduplication.
export default function useNativePlayback(item){
 const id=Number(item?.avideoId),last=useRef(null);
 useEffect(()=>{last.current=null},[id]);
 const report=(event,force=false)=>{
  if(!id||item?.live)return;
  const el=event.currentTarget,now=Date.now(),previous=last.current;
  if(!force&&(!previous||el.paused||now-previous<30000))return;
  last.current=now;
  platform('playback',{method:'POST',data:{video:id,position:Math.floor(el.currentTime||0),seconds:previous?Math.min(30,Math.floor((now-previous)/1000)):0}}).catch(()=>{});
 };
 return {onPlay:e=>report(e,true),onTimeUpdate:e=>report(e),onEnded:e=>report(e,true)};
}
