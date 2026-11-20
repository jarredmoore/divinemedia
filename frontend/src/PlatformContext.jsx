import React,{createContext,useContext,useEffect,useRef,useState} from 'react';
import {connectMediaSession,clearMediaSession} from './media-session.mjs';
import {platform,workspace} from './platform-client.mjs';
const Context=createContext(null);
export function PlatformProvider({children}){
 const[session,setSession]=useState(null),[status,setStatus]=useState('loading'),[error,setError]=useState(''),[favoriteIds,setFavoriteIds]=useState(null);const currentUser=useRef(null),sessionVersion=useRef(0);
 const refresh=async()=>{const version=++sessionVersion.current;try{const data=await platform('session');if(data.user)await connectMediaSession(platform);if(version!==sessionVersion.current)return null;setSession(data);setStatus('ready');setError('');return data}catch(e){if(version!==sessionVersion.current)return null;setStatus('error');setError(e.message);throw e}};
 useEffect(()=>{const ended=()=>{sessionVersion.current++;clearMediaSession();currentUser.current=null;setSession(null);setFavoriteIds([]);setStatus('ready');setError('');};window.addEventListener('divine:session-ended',ended);refresh().catch(()=>{});return()=>{sessionVersion.current++;window.removeEventListener('divine:session-ended',ended)}},[]);
 useEffect(()=>{let active=true;const id=session?.user?.id;currentUser.current=id;setFavoriteIds(id?null:[]);if(id)platform('library',{query:{kind:'favorites'}}).then(d=>{if(active)setFavoriteIds((d.items||[]).map(i=>Number(i.id)))}).catch(()=>{});return()=>{active=false}},[session?.user?.id]);
 const requireAccount=()=>{if(session?.user)return true;workspace('account');return false};
 const toggleFavorite=async id=>{if(!requireAccount())return;const owner=session.user.id;let ids=favoriteIds;if(ids===null)ids=(await platform('library',{query:{kind:'favorites'}})).items.map(i=>Number(i.id));await platform('library',{method:'POST',data:{kind:'favorites',video:Number(id),add:!ids.includes(Number(id))}});if(currentUser.current===owner)setFavoriteIds(ids.includes(Number(id))?ids.filter(v=>v!==Number(id)):[...ids,Number(id)])};
 return <Context.Provider value={{session,status,error,refresh,requireAccount,favoriteIds,toggleFavorite}}>{children}</Context.Provider>;
}
export function usePlatform(){return useContext(Context)}
