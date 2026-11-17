import React,{createContext,useContext,useEffect,useRef,useState} from 'react';
import {createPortal} from 'react-dom';
import {Download,Share,X} from './GlassIcons.jsx';
import './install.css';
const Context=createContext(null);
export function InstallProvider({children}){
 const[prompt,setPrompt]=useState(null),[installed,setInstalled]=useState(()=>Boolean(navigator.standalone||matchMedia('(display-mode: standalone)').matches)),[open,setOpen]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
 const dialog=useRef(null),opener=useRef(null);
 useEffect(()=>{
  const before=e=>{e.preventDefault();setPrompt(e)},done=()=>{setInstalled(true);setPrompt(null);setOpen(false)},mode=matchMedia('(display-mode: standalone)'),change=()=>setInstalled(Boolean(navigator.standalone||mode.matches));
  addEventListener('beforeinstallprompt',before);addEventListener('appinstalled',done);mode.addEventListener?.('change',change);
  if(import.meta.env.PROD&&'serviceWorker'in navigator)navigator.serviceWorker.register('/sw.js',{scope:'/',updateViaCache:'none'}).catch(()=>{});
  return()=>{removeEventListener('beforeinstallprompt',before);removeEventListener('appinstalled',done);mode.removeEventListener?.('change',change)};
 },[]);
 useEffect(()=>{if(!open)return;const overflow=document.body.style.overflow;document.body.style.overflow='hidden';dialog.current?.querySelector('button')?.focus();
  const key=e=>{if(e.key==='Escape'){e.stopImmediatePropagation();setOpen(false)}if(e.key==='Tab'){const buttons=[...dialog.current.querySelectorAll('button,a[href]')],first=buttons[0],last=buttons.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}};document.addEventListener('keydown',key,true);return()=>{document.body.style.overflow=overflow;document.removeEventListener('keydown',key,true);opener.current?.focus()};
 },[open]);
 const install=async e=>{opener.current=e.currentTarget;setMessage('');if(!prompt){setOpen(true);return}setBusy(true);try{await prompt.prompt();const choice=await prompt.userChoice;if(choice.outcome==='accepted')setInstalled(true)}catch{setMessage('Your browser could not open the install prompt. Use its install menu instead.');setOpen(true)}finally{setPrompt(null);setBusy(false)}};
 const ios=/iPhone|iPad|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
 return <Context.Provider value={{installed,busy,install}}>{children}{open&&createPortal(<div className="dm-install-backdrop" onClick={e=>{if(e.target===e.currentTarget)setOpen(false)}}><section className="dm-install-dialog" role="dialog" aria-modal="true" aria-labelledby="dm-install-title" ref={dialog}><button className="dm-install-close" aria-label="Close install instructions" onClick={()=>setOpen(false)}><X size={20}/></button><img src="/icons/divine-192.png" alt=""/><h2 id="dm-install-title">Install Divine Media</h2><p>Keep Divine Media on your home screen for quick access to video, music and live culture.</p>{ios?<p><Share size={17}/> In Safari, open <strong>Share</strong>, then choose <strong>Add to Home Screen</strong>. You may need to scroll through the actions.</p>:<><p>Open your browser menu and choose <strong>Install app</strong> or <strong>Add to Home screen</strong>, if offered.</p><p>On a Mac using Safari, choose <strong>File → Add to Dock</strong>, if available.</p></>}<p>Streaming and account features need an internet connection.</p>{message&&<p role="status">{message}</p>}<button className="dm-install-confirm" onClick={()=>setOpen(false)}>Got it</button></section></div>,document.body)}</Context.Provider>;
}
export default function InstallApp({prominent=false}){
 const context=useContext(Context);if(!context||context.installed)return null;
 return prominent?<aside className="dm-install-card"><img src="/icons/divine-192.png" alt=""/><div><strong>Divine Media, one tap away.</strong><p>Add our app to your home screen.</p></div><button onClick={context.install} disabled={context.busy}><Download size={17}/>Install Divine Media</button></aside>:<button className="dm-install-trigger" aria-label="Install Divine Media" title="Install Divine Media" onClick={context.install} disabled={context.busy}><Download size={17}/><span>Install</span></button>;
}
