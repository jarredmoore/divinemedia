import React,{useEffect,useRef,useState} from 'react';
import {ArrowDown,ArrowUpRight,Headphones,Pause,Play} from './GlassIcons.jsx';

export default function BackstageHero({onWatch,onListen,suspended}){
 const root=useRef(null),[paused,setPaused]=useState(false),[reduced,setReduced]=useState(true),[hidden,setHidden]=useState(false);
 useEffect(()=>{
  const media=matchMedia('(prefers-reduced-motion: reduce)'),connection=navigator.connection;
  const update=()=>setReduced(media.matches||Boolean(connection?.saveData));const visibility=()=>setHidden(document.hidden);
  update();visibility();media.addEventListener('change',update);connection?.addEventListener?.('change',update);document.addEventListener('visibilitychange',visibility);
  return()=>{media.removeEventListener('change',update);connection?.removeEventListener?.('change',update);document.removeEventListener('visibilitychange',visibility)};
 },[]);
 const still=paused||reduced||hidden||Boolean(suspended);
 useEffect(()=>{
  const el=root.current;if(!el)return;let frame=0;
  if(still){el.style.setProperty('--bs-progress','0');return}
  const update=()=>{if(frame)return;frame=requestAnimationFrame(()=>{frame=0;const rect=el.getBoundingClientRect();el.style.setProperty('--bs-progress',String(Math.max(0,Math.min(1,-rect.top/Math.max(rect.height,1)))))})};
  update();addEventListener('scroll',update,{passive:true});addEventListener('resize',update,{passive:true});
  return()=>{removeEventListener('scroll',update);removeEventListener('resize',update);cancelAnimationFrame(frame)};
 },[still]);
 const explore=()=>document.getElementById('discover-grid')?.scrollIntoView({behavior:reduced?'auto':'smooth'});
 return <section ref={root} className={'bs-hero'+(still?' bs-still':'')} aria-label="Backstage at Divine Media">
  <div className="bs-photo" aria-hidden="true"><img src="/themes/cold-black/stage-poster.jpg" alt="" fetchPriority="high"/></div>
  <div className="bs-hero-top"><span>DIVINE MEDIA / INDEPENDENT CULTURE</span><span>VOLUME 01 — ALWAYS ON</span></div>
  <div className="bs-hero-copy"><p className="bs-kicker"><span/> MUSIC. ARTISTS. CULTURE.</p><h1>FEEL<br/>EVERY<br/><em>FRAME.</em></h1><div className="bs-intro"><p>The sound. The stories. The people.<br/>Get closer to the culture.</p><div className="hero-actions"><button className="primary" onClick={onWatch}><Play size={18} fill="currentColor"/>Watch now<ArrowUpRight size={18}/></button><button className="secondary" onClick={onListen}><Headphones size={18}/>Explore music</button></div></div></div>
  <div className="bs-photo-caption" aria-hidden="true"><span>INDEPENDENT VOICES.</span><span>UNFORGETTABLE MOMENTS.</span></div>
  <div className="bs-hero-bottom"><button className="bs-explore" onClick={explore}><ArrowDown size={20}/>ENTER THE COLLECTION</button>{!reduced&&<button className="bs-pause" aria-label={paused?'Play background motion':'Pause background motion'} onClick={()=>setPaused(v=>!v)}>{paused?<Play size={15}/>:<Pause size={15}/>}<span>{paused?'Play motion':'Pause motion'}</span></button>}</div>
  <div className="bs-ticker" aria-hidden="true"><div>{[0,1].map(i=><span key={i}>SOUND <b>✦</b> VISION <b>✦</b> CONNECTION <b>✦</b> CULTURE <b>✦</b> </span>)}</div></div>
 </section>;
}
