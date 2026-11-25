import React,{useState} from 'react';
export default function PagedItems({items=[],children,label='items',size=12}){
 const[page,setPage]=useState(0),last=Math.max(0,Math.ceil(items.length/size)-1),current=Math.min(page,last);
 return <>{items.slice(current*size,(current+1)*size).map(children)}{items.length>size&&<nav className="dm-list-pagination" aria-label={label+' pages'}><button disabled={current===0} onClick={()=>setPage(current-1)}>Previous</button><span role="status">{current*size+1}–{Math.min((current+1)*size,items.length)} of {items.length} loaded {label}</span><button disabled={current===last} onClick={()=>setPage(current+1)}>Next</button></nav>}</>;
}
