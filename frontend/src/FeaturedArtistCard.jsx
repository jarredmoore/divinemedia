import React from 'react';
import {ArrowUpRight} from './GlassIcons.jsx';
import './artist-channel.css';

export default function FeaturedArtistCard({artist,onOpen,eyebrow='FEATURED ARTIST',action='Explore artist'}){return <a className="dm-featured-artist-card" href={artist.href||"/artists/"+artist.slug} aria-label={"Explore "+artist.name} onClick={e=>{if(!onOpen||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();onOpen(artist)}}><img src={artist.portrait} alt=""/><div><span className="eyebrow">{eyebrow}</span><h2>{artist.name}</h2><p>{artist.byline}</p><span>{action}<ArrowUpRight size={18}/></span></div></a>}
