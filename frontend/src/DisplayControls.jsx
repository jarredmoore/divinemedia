import React,{useEffect,useId,useRef,useState} from 'react';
import {Airplay,Cast,Maximize,MonitorUp,X} from 'lucide-react';
import {activeMedia,castMedia,loadCastSender,siteFullscreen} from './display.mjs';
import './display.css';
export default function DisplayControls(){
 const[open,setOpen]=useState(false),[message,setMessage]=useState(''),[castReady,setCastReady]=useState(false),[busy,setBusy]=useState(false),[connected,setConnected]=useState(false);
 const box=useRef(null),trigger=useRef(null),id=useId(),media=activeMedia();
 const airplay=typeof media?.webkitShowPlaybackTargetPicker==='function';
 const chromium=/Chrome|Chromium|Edg\//.test(navigator.userAgent)&&!/iPhone|iPad|iPod/.test(navigator.userAgent);
 useEffect(()=>{if(!open)return;let active=true;
  if(chromium)loadCastSender().then(()=>{if(active){setCastReady(true);setConnected(Boolean(window.cast.framework.CastContext.getInstance().getCurrentSession()))}}).catch(e=>{if(active)setMessage(e.message)});
  box.current?.querySelector('.dm-display-panel button:not(:disabled)')?.focus();
  const close=e=>{if(e.type==='keydown'&&e.key!=='Escape')return;if(e.type==='pointerdown'&&box.current?.contains(e.target))return;setOpen(false);if(e.type==='keydown'){e.stopImmediatePropagation();trigger.current?.focus()}};
  document.addEventListener('pointerdown',close);document.addEventListener('keydown',close,true);
  return()=>{active=false;document.removeEventListener('pointerdown',close);document.removeEventListener('keydown',close,true)};
 },[open,chromium]);
 const run=async fn=>{setMessage('');setBusy(true);try{await fn()}catch(e){const code=e?.code||e;if(!['cancel','cancelled'].includes(code))setMessage(e?.message||'The display connection was cancelled or unavailable.')}finally{setBusy(false)}};
 return <div className="dm-display" ref={box}><button type="button" className="dm-display-trigger" aria-label="Display options" title="Display options" aria-expanded={open} aria-controls={id} ref={trigger} onClick={()=>{setMessage('');setOpen(v=>!v)}}><MonitorUp size={18}/><span>Display</span></button>{open&&<div className="dm-display-panel" id={id} role="group" aria-label="Display options"><div className="dm-display-heading"><strong>Watch on a display</strong><button type="button" aria-label="Close display options" onClick={()=>{setOpen(false);trigger.current?.focus()}}><X size={16}/></button></div><button type="button" onClick={()=>run(()=>siteFullscreen())}><Maximize size={17}/> {document.fullscreenElement?'Exit fullscreen':'Fullscreen site'}</button>{airplay&&<button type="button" disabled={busy} onClick={()=>run(()=>activeMedia()?.webkitShowPlaybackTargetPicker())}><Airplay size={17}/>AirPlay</button>}{chromium&&<button type="button" disabled={!media||!castReady||busy} onClick={()=>run(async()=>{await castMedia(activeMedia());setConnected(true);setMessage('Connected. Use Google Cast controls to manage playback.');})}><Cast size={17}/>{castReady?'Google Cast / Chromecast':'Loading Google Cast…'}</button>}{connected&&<button type="button" onClick={()=>{window.cast.framework.CastContext.getInstance().endCurrentSession(true);setConnected(false);setMessage('Display disconnected. Press Play to resume here.')}}>Disconnect Google Cast</button>}<p>{!media?'Open a video or play audio to connect it to a display. ':''}AirPlay is available in supported Apple browsers. Google Cast requires a compatible browser and receiver on your network. To mirror the whole site, use your browser’s Cast tab or your device’s Screen Mirroring.</p>{message&&<p role="status">{message}</p>}</div>}</div>;
}
