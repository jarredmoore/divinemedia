import MeshGradient from './MeshGradient.jsx';
import InstallApp from './InstallApp.jsx';
import DisplayControls from './DisplayControls.jsx';
import React,{useEffect,useRef,useState} from 'react';
import {NativeActions} from './NativeActions.jsx';
import {workspace} from './platform-client.mjs';
import {ArrowDown,ArrowUpRight,Headphones,Menu,Pause,Play,Search,Upload,X} from './GlassIcons.jsx';

export {THEME_KEY} from '../shared/theme.mjs';
export {readCurrentTheme as readTheme} from '../shared/theme.mjs';
export function ThemePicker({theme,onChange}){
 return <label className="theme-picker"><span className="sr-only">Viewing theme</span><select aria-label="Viewing theme" value={theme} onChange={e=>onChange(e.target.value)}><option value="default">Cozy</option><option value="code-black">Code Black</option><option value="backstage">Backstage</option></select></label>;
}
export function ColdBlackHeader({tab,go,query,setQuery,theme,onTheme,links}){
 const[expanded,setExpanded]=useState(false);
 useEffect(()=>{if(!expanded)return;const close=e=>{if(e.key==='Escape')setExpanded(false)};addEventListener('keydown',close);return()=>removeEventListener('keydown',close)},[expanded]);
 return <header className="cb-header">
  <button className="cb-wordmark" aria-label="Divine Media home" onClick={()=>{go('Discover');setExpanded(false)}}><img className="dm-brand-mark" src="/icons/divine-logo.svg" alt="" aria-hidden="true"/><span>DIVINE MEDIA</span></button>
  <nav className={'cb-navigation '+(expanded?'is-open':'')} id="cb-navigation" aria-label="Explore Divine Media">{links.map(([name])=><button type="button" key={name} aria-current={tab===name?'page':undefined} onClick={()=>{go(name);setExpanded(false)}}>{name}</button>)}<a href="/planet-derrty" className="cb-archive-link">Planet Derrty</a><label className="cb-mobile-search search"><Search size={17}/><input aria-label="Search titles" placeholder="Search the culture…" value={query} onChange={e=>setQuery(e.target.value)}/></label><div className="cb-mobile-install"><InstallApp/><ThemePicker theme={theme} onChange={onTheme}/></div><div className="cb-mobile-native"><NativeActions/></div></nav>
  <div className="cb-header-tools"><label className="cb-desktop-search search"><Search size={17}/><input aria-label="Search titles" placeholder="Search…" value={query} onChange={e=>setQuery(e.target.value)}/></label><InstallApp/><DisplayControls/><button className="cb-mobile-create" aria-label="Upload and creator tools" aria-haspopup="dialog" onClick={()=>{setExpanded(false);workspace('creator')}}><Upload size={18}/></button><NativeActions/><ThemePicker theme={theme} onChange={onTheme}/><button className="cb-menu" aria-label={expanded?'Close navigation':'Open navigation'} aria-expanded={expanded} aria-controls="cb-navigation" onClick={()=>setExpanded(v=>!v)}>{expanded?<X size={20}/>:<Menu size={20}/>}</button></div>
 </header>;
}

const POSTER='/themes/cold-black/stage-poster.jpg';
export function ColdBlackHero({onWatch,onListen,suspended}){
 const root=useRef(null);
 const[motionAllowed,setMotionAllowed]=useState(false),[paused,setPaused]=useState(false);
 useEffect(()=>{
  const media=matchMedia('(prefers-reduced-motion: reduce)'),connection=navigator.connection;
  const update=()=>setMotionAllowed(!media.matches&&!connection?.saveData);
  update();media.addEventListener('change',update);connection?.addEventListener?.('change',update);
  return()=>{media.removeEventListener('change',update);connection?.removeEventListener?.('change',update)};
 },[]);
 useEffect(()=>{
  const el=root.current;if(!el)return;
  if(!motionAllowed){el.style.setProperty('--scene-progress',0);el.dataset.advanced='false';return}
  let frame=0;
  const update=()=>{if(frame)return;frame=requestAnimationFrame(()=>{frame=0;const r=el.getBoundingClientRect();const progress=Math.max(0,Math.min(1,-r.top/Math.max(1,r.height-innerHeight)));el.style.setProperty('--scene-progress',progress.toFixed(4));el.dataset.advanced=String(progress>.55)})};
  update();addEventListener('scroll',update,{passive:true});addEventListener('resize',update,{passive:true});
  return()=>{removeEventListener('scroll',update);removeEventListener('resize',update);cancelAnimationFrame(frame)};
 },[motionAllowed]);
 const scrollToTitles=()=>document.getElementById('discover-grid')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
 return <section className={"cb-scene "+(!motionAllowed?"cb-still":"")} ref={root} aria-label="The Divine Media experience">
  <div className="cb-stage">
   <div className="cb-scene-backdrop" aria-hidden="true"><MeshGradient paused={paused||Boolean(suspended)}/><img className="cb-poster" src={POSTER} alt="" fetchPriority="high"/><div className="cb-split cb-split-left" style={{backgroundImage:`url(${POSTER})`}}/><div className="cb-split cb-split-right" style={{backgroundImage:`url(${POSTER})`}}/></div>
   <div className="cb-scene-shade" aria-hidden="true"/>
   <div className="cb-orbit" aria-hidden="true"><span>D</span></div>
   <div className="cb-hero-copy"><div className="eyebrow">THE DIVINE MEDIA EXPERIENCE</div><h1>Stories. Sound.<br/><em>Connection.</em></h1><p>Independent voices. Unforgettable moments.</p><div className="hero-actions"><button className="primary" onClick={onWatch}><Play size={16} fill="currentColor"/> Watch now</button><button className="secondary" onClick={onListen}><Headphones size={16}/>Explore music <ArrowUpRight size={16}/></button></div></div>
   <div className="cb-scene-reveal"><span className="eyebrow">A DIFFERENT POINT OF VIEW</span><h2>Find your next<br/><em>connection.</em></h2><button className="secondary" onClick={scrollToTitles}>Discover the collection <ArrowDown size={17}/></button></div>
   <button className="cb-scroll-cue" onClick={scrollToTitles}>SCROLL TO DISCOVER<span/></button>
   {motionAllowed&&<button className="cb-motion-control" aria-label={paused?'Play background animation':'Pause background animation'} onClick={()=>setPaused(v=>!v)}>{paused?<Play size={15}/>:<Pause size={15}/>}<span>{paused?'Play motion':'Pause motion'}</span></button>}
  </div>
 </section>;
}
