import React,{createContext,useContext,useEffect,useRef,useState} from 'react';
import {platform,workspace} from './platform-client.mjs';
const Context=createContext(null);
export function PlatformProvider({children}){
 const[session,setSession]=useState(null),[status,setStatus]=useState('loading'),[error,setError]=useState(''),[favoriteIds,setFavoriteIds]=useState(null);const currentUser=useRef(null);
 const refresh=async()=>{try{const data=await platform('session');setSession(data);setStatus('ready');setError('');return data}catch(e){setStatus('error');setError(e.message);throw e}};
 useEffect(()=>{refresh().catch(()=>{})},[]);
 useEffect(()=>{let active=true;const id=session?.user?.id;currentUser.current=id;setFavoriteIds(id?null:[]);if(id)platform('library',{query:{kind:'favorites'}}).then(d=>{if(active)setFavoriteIds((d.items||[]).map(i=>Number(i.id)))}).catch(()=>{});return()=>{active=false}},[session?.user?.id]);
 const requireAccount=()=>{if(session?.user)return true;workspace('account');return false};
 const toggleFavorite=async id=>{if(!requireAccount())return;const owner=session.user.id;let ids=favoriteIds;if(ids===null)ids=(await platform('library',{query:{kind:'favorites'}})).items.map(i=>Number(i.id));await platform('library',{method:'POST',data:{kind:'favorites',video:Number(id),add:!ids.includes(Number(id))}});if(currentUser.current===owner)setFavoriteIds(ids.includes(Number(id))?ids.filter(v=>v!==Number(id)):[...ids,Number(id)])};
 return <Context.Provider value={{session,status,error,refresh,requireAccount,favoriteIds,toggleFavorite}}>{children}</Context.Provider>;
}
export function usePlatform(){return useContext(Context)}
