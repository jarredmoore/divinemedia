import React from 'react';
import {ArrowUpRight} from './GlassIcons.jsx';
import './artist-channel.css';

export default function FeaturedArtistCard({artist,onOpen}){return <a className="dm-featured-artist-card" href={"/artists/"+artist.slug} aria-label={"Explore "+artist.name} onClick={e=>{if(e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();onOpen(artist)}}><img src={artist.portrait} alt=""/><div><span className="eyebrow">FEATURED ARTIST</span><h2>{artist.name}</h2><p>{artist.byline}</p><span>Explore artist<ArrowUpRight size={18}/></span></div></a>}
