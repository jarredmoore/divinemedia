import React,{useEffect,useRef,useState} from 'react';
import {NativeActions} from './NativeActions.jsx';
import {ArrowDown,ArrowUpRight,Menu,Pause,Play,Search,X} from 'lucide-react';

export {THEME_KEY} from '../shared/theme.mjs';
export {readCurrentTheme as readTheme} from '../shared/theme.mjs';
export function ThemePicker({theme,onChange}){
 return <label className="theme-picker"><span className="sr-only">Viewing theme</span><select aria-label="Viewing theme" value={theme} onChange={e=>onChange(e.target.value)}><option value="default">Default</option><option value="code-black">Code Black</option></select></label>;
}
export function ColdBlackHeader({tab,go,query,setQuery,theme,onTheme,links}){
 const[expanded,setExpanded]=useState(false);
 useEffect(()=>{if(!expanded)return;const close=e=>{if(e.key==='Escape')setExpanded(false)};addEventListener('keydown',close);return()=>removeEventListener('keydown',close)},[expanded]);
 return <header className="cb-header">
  <button className="cb-wordmark" aria-label="Divine Media home" onClick={()=>{go('Discover');setExpanded(false)}}><svg viewBox="0 0 42 42" aria-hidden="true"><path d="M4 5v32" stroke="currentColor" strokeWidth="2"/><path d="M12 4h10c12 0 18 6 18 17S34 38 22 38H12zm9 8v18h2c6 0 9-3 9-9s-3-9-9-9z" fill="currentColor" fillRule="evenodd"/></svg><span>DIVINE MEDIA</span></button>
  <nav className={'cb-navigation '+(expanded?'is-open':'')} id="cb-navigation" aria-label="Explore Divine Media">{links.map(([name])=><button type="button" key={name} aria-current={tab===name?'page':undefined} onClick={()=>{go(name);setExpanded(false)}}>{name}</button>)}<label className="cb-mobile-search search"><Search size={17}/><input aria-label="Search titles" placeholder="Search the culture…" value={query} onChange={e=>setQuery(e.target.value)}/></label><div className="cb-mobile-native"><NativeActions/></div></nav>
  <div className="cb-header-tools"><label className="cb-desktop-search search"><Search size={17}/><input aria-label="Search titles" placeholder="Search…" value={query} onChange={e=>setQuery(e.target.value)}/></label><NativeActions/><ThemePicker theme={theme} onChange={onTheme}/><button className="cb-menu" aria-label={expanded?'Close navigation':'Open navigation'} aria-expanded={expanded} aria-controls="cb-navigation" onClick={()=>setExpanded(v=>!v)}>{expanded?<X size={20}/>:<Menu size={20}/>}</button></div>
 </header>;
}

const POSTER='/themes/cold-black/stage-poster.jpg';
export function ColdBlackHero({onWatch,onListen,suspended}){
 const root=useRef(null),video=useRef(null);
 const[motionAllowed,setMotionAllowed]=useState(false),[inView,setInView]=useState(true),[visible,setVisible]=useState(!document.hidden),[paused,setPaused]=useState(false),[playing,setPlaying]=useState(false),[failed,setFailed]=useState(false);
 useEffect(()=>{
  const media=matchMedia('(prefers-reduced-motion: reduce)'),connection=navigator.connection;
  const update=()=>setMotionAllowed(!media.matches&&!connection?.saveData);
  update();media.addEventListener('change',update);connection?.addEventListener?.('change',update);
  const visibility=()=>setVisible(!document.hidden);document.addEventListener('visibilitychange',visibility);
  return()=>{media.removeEventListener('change',update);connection?.removeEventListener?.('change',update);document.removeEventListener('visibilitychange',visibility)};
 },[]);
 useEffect(()=>{
  const el=root.current;if(!el)return;
  const observer=new IntersectionObserver(([entry])=>setInView(entry.isIntersecting),{threshold:0});observer.observe(el);
  if(!motionAllowed){el.style.setProperty('--scene-progress',0);el.dataset.advanced='false';return()=>observer.disconnect()}
  let frame=0;
  const update=()=>{if(frame)return;frame=requestAnimationFrame(()=>{frame=0;const r=el.getBoundingClientRect();const progress=Math.max(0,Math.min(1,-r.top/Math.max(1,r.height-innerHeight)));el.style.setProperty('--scene-progress',progress.toFixed(4));el.dataset.advanced=String(progress>.55)})};
  update();addEventListener('scroll',update,{passive:true});addEventListener('resize',update,{passive:true});
  return()=>{observer.disconnect();removeEventListener('scroll',update);removeEventListener('resize',update);cancelAnimationFrame(frame)};
 },[motionAllowed]);
 useEffect(()=>{
  const el=video.current;if(!el)return;
  if(motionAllowed&&inView&&visible&&!paused&&!suspended&&!failed)el.play().catch(()=>setPlaying(false));else el.pause();
 },[motionAllowed,inView,visible,paused,suspended,failed]);
 const scrollToTitles=()=>document.getElementById('discover-grid')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
 return <section className={"cb-scene "+(!motionAllowed?"cb-still":"")} ref={root} aria-label="The Divine Media experience">
  <div className="cb-stage">
   <div className="cb-scene-backdrop" aria-hidden="true"><img className="cb-poster" src={POSTER} alt="" fetchPriority="high"/>{motionAllowed&&!failed&&<video ref={video} className="cb-background-video" muted loop playsInline preload="none" poster={POSTER} onPlaying={()=>setPlaying(true)} onPause={()=>setPlaying(false)} onError={()=>setFailed(true)}><source src="/themes/cold-black/stage-loop.mp4" type="video/mp4"/></video>}<div className="cb-split cb-split-left" style={{backgroundImage:`url(${POSTER})`}}/><div className="cb-split cb-split-right" style={{backgroundImage:`url(${POSTER})`}}/></div>
   <div className="cb-scene-shade" aria-hidden="true"/>
   <div className="cb-orbit" aria-hidden="true"><span>D</span></div>
   <div className="cb-hero-copy"><div className="eyebrow">THE DIVINE MEDIA EXPERIENCE</div><h1>Stories. Sound.<br/><em>Connection.</em></h1><p>Independent voices. Unforgettable moments.</p><div className="hero-actions"><button className="primary" onClick={onWatch}><Play size={16} fill="currentColor"/> Watch now</button><button className="secondary" onClick={onListen}>Explore music <ArrowUpRight size={16}/></button></div></div>
   <div className="cb-scene-reveal"><span className="eyebrow">A DIFFERENT POINT OF VIEW</span><h2>Find your next<br/><em>connection.</em></h2><button className="secondary" onClick={scrollToTitles}>Discover the collection <ArrowDown size={17}/></button></div>
   <button className="cb-scroll-cue" onClick={scrollToTitles}>SCROLL TO DISCOVER<span/></button>
   {motionAllowed&&!failed&&<button className="cb-motion-control" aria-label={playing?'Pause background animation':'Play background animation'} onClick={()=>{if(playing)setPaused(true);else{setPaused(false);if(!suspended)video.current?.play().catch(()=>setPlaying(false))}}}>{playing?<Pause size={15}/>:<Play size={15}/>}<span>{playing?'Pause motion':'Play motion'}</span></button>}
  </div>
 </section>;
}
