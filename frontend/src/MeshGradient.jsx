import React,{useEffect,useRef} from 'react';
import './mesh-gradient.css';
export default function MeshGradient({paused=false}){
 const canvas=useRef(null),engine=useRef(null),current=useRef(paused);current.current=paused;
 useEffect(()=>{
  let active=true,idle=0,frame=0;
  const load=()=>{import('./mesh-gradient.mjs').then(({startMesh})=>{if(active)engine.current=startMesh(canvas.current,{paused:current.current})}).catch(()=>{})};
  // Wait for a painted frame, then load/compile during idle time.
  frame=requestAnimationFrame(()=>{frame=requestAnimationFrame(()=>{if('requestIdleCallback'in window)idle=requestIdleCallback(load,{timeout:900});else idle=setTimeout(load,80)})});
  return()=>{active=false;cancelAnimationFrame(frame);if('cancelIdleCallback'in window)cancelIdleCallback(idle);else clearTimeout(idle);engine.current?.destroy();engine.current=null};
 },[]);
 useEffect(()=>{engine.current?.setPaused(paused)},[paused]);
 return <div className="cb-mesh" aria-hidden="true"><canvas ref={canvas} data-mesh="fallback"/></div>;
}
