import React from 'react';
import {Upload,Link2,Clapperboard,Library,Radio,Video,Settings2,Newspaper,Users,MonitorUp,Code,UserRound} from './GlassIcons.jsx';
import {workspace} from './platform-client.mjs';
const tools=[
 ['upload','Upload media','Add video, audio, images or documents.',Upload,'upload','Create'],
 ['embed','Add a video link','Embed YouTube or import a supported public video link.',Link2,'upload','Create'],
 ['studio','Live studio','Prepare a broadcast and connect your streaming software.',Radio,'stream','Create'],
 ['videos','Your videos','Preview titles, edit details and manage visibility.',Clapperboard,'upload','Manage'],
 ['encode','Encode video & audio','Choose an uploaded title and its encoding output.',Settings2,'upload','Manage','videos'],
 ['queue','Encoding queue','Check processing, retry jobs and manage the queue.',MonitorUp,'upload','Manage'],
 ['playlists','Playlists','Organize videos into collections.',Library,'playlists','Manage'],
 ['live','Live broadcasts','Browse broadcasts and preview live content.',Video,'live','Manage'],
 ['account','Account & profile','Manage your display name and account.',UserRound,'account','Manage'],
 ['articles','Add article','Write stories and updates for your audience.',Newspaper,null,'Additional tools'],
 ['camera','Go live with your camera','Broadcast directly from your browser camera.',Video,null,'Additional tools'],
 ['live-link','Add a live link','Add an existing external live stream.',Link2,null,'Additional tools'],
 ['meet','Meet','Host a creator meeting.',Users,null,'Additional tools'],
 ['local-encoder','Use a local encoder','Connect encoding tools on your computer.',MonitorUp,null,'Additional tools'],
 ['providers','Additional embedded players','More hosted players will appear when available.',Code,null,'Additional tools']
];
export default function CreatorTools({session}){
 const p=session?.user?.permissions||{},cap=session?.capabilities||{};
 const grants={...p,account:true,playlists:Boolean(cap.playlists),live:Boolean(cap.live),stream:Boolean(p.stream&&cap.live)};
 return <div className="dm-creator-tools"><p className="dm-creator-intro">Create, publish and manage your work from one place.</p>{['Create','Manage','Additional tools'].map(group=><section className="dm-creator-section" key={group} aria-label={group+' tools'}><h2>{group}</h2><div className="dm-creator-tool-list">{tools.filter(t=>t[5]===group).map(([id,label,description,Icon,grant,,destination])=>{
 const ready=Boolean(grant&&grants[grant]);const status=!grant?'Not available yet':ready?'':grant==='playlists'||grant==='live'?'Not enabled':'Permission required';
 return <button className="dm-creator-tool" key={id} disabled={!ready} onClick={()=>workspace(destination||id)}><Icon size={30}/><span><strong>{label}</strong><small>{description}</small>{status&&<span className="dm-creator-tool-status">{status}</span>}</span></button>;
 })}</div></section>)}</div>;
}
