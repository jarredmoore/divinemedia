import React,{useState} from 'react';
export default function MediaLinks({item}){
 const[notice,setNotice]=useState('');const id=Number(item?.id||item?.avideoId);if(!Number.isSafeInteger(id)||id<1)return null;
 const watch='https://divinemedia.us/watch/'+id,embed='https://divinemedia.us/embed/'+id;
 const source=item.audioUrl||item.videoUrl||item.asset?.url;
 const links=[['Watch URL',watch],['Embed URL',embed],['Embed code',`<iframe src="${embed}" title="Divine Media player" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`]];
 if(typeof source==='string'&&source.startsWith('https://media.divinemedia.us/'))links.push(['Media / streaming URL',source]);
 if(item.embed?.provider==='youtube')links.push(['YouTube source','https://www.youtube.com/watch?v='+item.embed.id]);
 return <details className="dm-media-links"><summary>Links & embedding</summary><p>Private media still requires authorization. A copied link does not grant access.</p>{links.map(([label,value])=><label key={label}>{label}<input aria-label={label} readOnly value={value} onFocus={e=>e.target.select()}/><button type="button" onClick={async()=>{try{await navigator.clipboard.writeText(value);setNotice(label+' copied.')}catch{setNotice('Select the field to copy it manually.')}}}>Copy {label.toLowerCase()}</button></label>)}{notice&&<p role="status">{notice}</p>}</details>;
}
