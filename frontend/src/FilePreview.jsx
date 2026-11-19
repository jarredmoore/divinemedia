import React from 'react';
import DisplayControls from './DisplayControls.jsx';
export default function FilePreview({asset,title}){
 let url;try{url=new URL(asset.url);if(url.origin!=='https://media.divinemedia.us'||url.username||url.password||!url.pathname.startsWith('/videos/')||!['image','document'].includes(asset.kind))throw Error();}catch{return <p role="alert">This file preview is unavailable.</p>}
 return <div className="dm-player dm-file-preview">{asset.kind==='image'?<img src={url.href} alt={title}/>:<object data={url.href} type="application/pdf" aria-label={title}><p><a href={url.href} target="_blank" rel="noopener noreferrer">Open document</a></p></object>}<div className="dm-player-toolbar"><span className="dm-player-brand">DIVINE MEDIA</span><a href={url.href} target="_blank" rel="noopener noreferrer">{asset.kind==='image'?'Open full image':'Open document'}</a><DisplayControls/></div></div>;
}
