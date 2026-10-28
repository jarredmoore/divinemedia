import React,{useState} from 'react';
import{createRoot}from'react-dom/client';
import{Search,Compass,Clapperboard,Headphones,Radio,Users,Library,Play,ArrowUpRight,Menu,X,Heart,Plus,Volume2}from'lucide-react';
import './style.css';
const photos={
 hero:'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1600&q=85',
 film:'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=720&q=80',
 concert:'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=720&q=80',
 city:'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=720&q=80',
 portrait:'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=720&q=80',
 sound:'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=720&q=80',
 stage:'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=720&q=80',
 artist:'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=720&q=80'
};
const items=[
 {title:'Beyond the Frame',tag:'FILM · 28 MIN',img:photos.film,type:'Watch'},
 {title:'Live from the City',tag:'LIVE PERFORMANCE',img:photos.concert,type:'Live'},
 {title:'The City Speaks',tag:'DOCUMENTARY · 42 MIN',img:photos.city,type:'Watch'},
 {title:'In Her Own Words',tag:'CREATOR SERIES',img:photos.portrait,type:'Creators'},
 {title:'Frequency',tag:'AUDIO · 36 MIN',img:photos.sound,type:'Listen'},
 {title:'After the Lights',tag:'CONCERT FILM',img:photos.stage,type:'Watch'},
 {title:'New Waves',tag:'MUSIC SESSION',img:photos.artist,type:'Listen'}
];
const links=[['Discover',Compass],['Watch',Clapperboard],['Listen',Headphones],['Live',Radio],['Creators',Users],['Library',Library]];
function App(){
 const[tab,setTab]=useState('Discover'),[query,setQuery]=useState(''),[menu,setMenu]=useState(false),[saved,setSaved]=useState([]),[selected,setSelected]=useState(null);
 const visible=items.filter(i=>(tab==='Discover'||tab==='Library'&&saved.includes(i.title)||tab==='Watch'&&i.type==='Watch'||tab==='Listen'&&i.type==='Listen'||tab==='Live'&&i.type==='Live'||tab==='Creators'&&i.type==='Creators')&&(i.title+' '+i.tag).toLowerCase().includes(query.toLowerCase()));
 const go=t=>{setTab(t);setMenu(false);setSelected(null)};
 const toggle=t=>setSaved(v=>v.includes(t)?v.filter(x=>x!==t):[...v,t]);
 return <div className="app">
 <aside className={'sidebar '+(menu?'open':'')}>
 <div className="brand"><div className="brand-icon"><Play size={18} fill="currentColor"/></div><span>DIVINE<span className="brand-light">MEDIA</span><small>INDEPENDENT CULTURE</small></span></div>
 <div className="side-label">EXPLORE</div><nav>{links.map(([name,Icon])=><button key={name} className={'nav-link '+(tab===name?'active':'')} onClick={()=>go(name)}><Icon size={19}/>{name}{name==='Live'&&<span className="live-dot"/>}</button>)}</nav>
 <div className="side-bottom"><div className="side-label">YOUR SPACE</div><p>Independent stories deserve a place to be discovered.</p><span>DISCOVER MORE. FEEL MORE.</span></div>
 </aside>
 <div className="content">
 <header><button className="menu-button" aria-label="Toggle menu" onClick={()=>setMenu(!menu)}>{menu?<X/>:<Menu/>}</button><div className="breadcrumb">EXPLORE <span>/</span> {tab.toUpperCase()}</div><div className="header-actions"><label className="search"><Search size={18}/><input aria-label="Search titles" placeholder="Search the culture..." value={query} onChange={e=>setQuery(e.target.value)}/></label><div className="avatar">DM</div></div></header>
 {tab==='Discover'&&!query&&<section className="hero" style={{backgroundImage:'linear-gradient(90deg,rgba(8,10,13,.95),rgba(8,10,13,.36)),linear-gradient(0deg,#0b0d10,transparent 55%),url('+photos.hero+')'}}><div className="hero-content"><div className="eyebrow"><span className="accent-line"/> THE NEXT WAVE OF INDEPENDENT MEDIA</div><h1>Stories worth<br/><em>staying for.</em></h1><p>Film. Music. Culture. Voices you haven't heard yet. A new home for the creators moving us forward.</p><div className="hero-actions"><button className="primary" onClick={()=>document.getElementById('discover-grid')?.scrollIntoView({behavior:'smooth'})}><Play size={17} fill="currentColor"/> Start exploring</button><button className="secondary" onClick={()=>go('Creators')}>Meet the creators <ArrowUpRight size={17}/></button></div></div><div className="hero-index">01 <span>/</span> 04</div></section>}
 <main><div className="section-head" id="discover-grid"><div><div className="eyebrow small">HANDPICKED FOR YOU</div><h2>{tab==='Discover'?'The spotlight':tab==='Library'?'Your saved collection':query?'Search results':tab}</h2></div><span className="section-sub">{visible.length} {visible.length===1?'TITLE':'TITLES'} <ArrowUpRight size={16}/></span></div>
 {visible.length?<div className="media-grid">{visible.map((item,i)=><article className="media-card" key={item.title}><button className="cover" onClick={()=>setSelected(item)} aria-label={'View '+item.title}><img src={item.img} alt="" loading="lazy"/><span className="play-float"><Play size={22} fill="currentColor"/></span>{i===1&&tab==='Discover'&&<span className="pill">FEATURED</span>}</button><div className="card-meta"><div><span className="card-tag">{item.tag}</span><h3>{item.title}</h3></div><button className={'save '+(saved.includes(item.title)?'is-saved':'')} aria-label={'Save '+item.title} title="Save to library" onClick={()=>toggle(item.title)}><Heart size={19} fill={saved.includes(item.title)?'currentColor':'none'}/></button></div></article>)}</div>:<div className="empty">Nothing here yet. Try another search or explore Discover.</div>}
 <section className="manifesto"><div><span className="eyebrow small">THE DIVINE MEDIA EXPERIENCE</span><h2>More than content.<br/><em>A connection.</em></h2></div><p>A space where independent creators and curious audiences meet. Discover your next favorite voice, sound, or story.</p><button onClick={()=>go('Creators')}>Explore creators <ArrowUpRight size={18}/></button></section>
 <footer><span>© 2026 DIVINE MEDIA</span><span>INDEPENDENT BY DESIGN.</span><span>VISUAL PROTOTYPE · SAMPLE CONTENT</span></footer>
 </main></div>
 {selected&&<div className="modal-backdrop" onClick={()=>setSelected(null)}><div className="modal" role="dialog" aria-modal="true" aria-label={selected.title} onClick={e=>e.stopPropagation()}><button className="close" aria-label="Close" onClick={()=>setSelected(null)}><X/></button><img src={selected.img} alt=""/><div className="modal-body"><div className="eyebrow small">{selected.tag}</div><h2>{selected.title}</h2><p>This is sample content for the Divine Media design preview. Playback will be connected after we verify the AVideo integration.</p><button className="primary" onClick={()=>toggle(selected.title)}><Plus size={17}/>{saved.includes(selected.title)?'Remove from Library':'Save to Library'}</button></div></div></div>}
 </div>
}
createRoot(document.getElementById('root')).render(<App/>);
