import React from 'react';
import DisplayControls from './DisplayControls.jsx';
import {youtubeEmbedUrl} from './provider-embed.mjs';
export default function ProviderPlayer({embed,title}){
 const src=youtubeEmbedUrl(embed);if(!src)return <p role="alert">This external video provider is not supported yet.</p>;
 return <div className="dm-player dm-provider-player"><iframe title={'Watch '+title+' on YouTube'} src={src} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen referrerPolicy="strict-origin-when-cross-origin"/><div className="dm-player-toolbar"><span className="dm-player-brand">DIVINE MEDIA · YOUTUBE</span><DisplayControls/></div><p className="dm-provider-note">Playback is provided by YouTube. If this video is restricted here, <a href={'https://www.youtube.com/watch?v='+embed.id} target="_blank" rel="noopener noreferrer">open it on YouTube</a>.</p></div>;
}
