// Approved public presentation only. No masters, private soundtrack files or download grants.
export const featuredArtists=[{
 slug:'murphy-lee',name:'Murphy Lee',byline:'National recording artist · St. Lunatics',
 description:'Music, film, and the artwork behind the releases. Explore Murphy Lee’s world, presented by Divine Media.',
 portrait:'/artists/murphy-lee/portrait.webp',header:'/artists/murphy-lee/header.webp',store:'https://store.newmurph.com/',
 artworkCredit:'Artwork by Divine Creative Group',
 releases:[
  {id:'you-see-me',title:'You See Me',kind:'Documentary + companion soundtrack',cover:'/artists/murphy-lee/you-see-me-cover.webp',description:'The documentary and its companion soundtrack, together as the DVD release.',checkout:'https://store.newmurph.com/Home/Details/2',checkoutLabel:'View DVD release',privateBonus:true,previewIds:[]},
  {id:'2nd-time-around',title:'2nd Time Around',kind:'Album',cover:'/2ndTimeAround.jpg',description:'Explore the project and listen to the artist’s published previews.',checkout:'https://store.newmurph.com/Home/Details/4',checkoutLabel:'View album',nativePlaylistId:129,previewIds:[15,13,11,14,16,21,23,22,25,28,27,29,26,24]},
  {id:'murphys-law',title:'Murphy’s Law DVD',kind:'DVD + free ML10 album',cover:'/artists/murphy-lee/murphys-law.webp',description:'The 10th anniversary documentary, with the ML10 companion album included free.',checkout:'https://store.newmurph.com/Home/Details/1',checkoutLabel:'View DVD package',privateBonus:true,previewIds:[]},
  {id:'ml10',title:'ML10 companion album',kind:'Included free with DVD',cover:'/artists/murphy-lee/murphys-law.webp',description:'Included free with the Murphy’s Law DVD. Shown with the DVD package artwork; not sold separately.',checkout:'https://store.newmurph.com/Home/Details/1',checkoutLabel:'View included DVD package',privateBonus:true,previewIds:[],includedWith:'murphys-law'}
 ],
 gallery:[
  {id:'exterior',title:'You See Me — exterior artwork',image:'/artists/murphy-lee/package-exterior.webp',layout:'wide',width:2400,height:600},
  {id:'interior',title:'You See Me — interior artwork',image:'/artists/murphy-lee/package-interior.webp',layout:'wide',width:2400,height:600},
  {id:'disc',title:'You See Me — companion album disc',image:'/artists/murphy-lee/oncd.webp',layout:'square',width:850,height:850},
  {id:'dvd',title:'You See Me — documentary disc',image:'/artists/murphy-lee/ondvd.webp',layout:'square',width:850,height:850}
 ],merchandise:[]
}];
export function artistFromPath(path){const match=/^\/artists\/([a-z0-9-]+)\/?$/.exec(path);return match?featuredArtists.find(a=>a.slug===match[1])||null:null}
export function releasePreviews(release,items){
 if(release.privateBonus)return [];
 const allowed=new Map((items||[]).filter(i=>i.type==='Listen'&&typeof i.audioUrl==='string'&&i.audioUrl&&!['private','unlisted'].includes(i.visibility)&&(!i.status||i.status==='a')).map(i=>[Number(i.avideoId),i]));
 return (release.previewIds||[]).map(id=>allowed.get(Number(id))).filter(Boolean);
}
export function artistTrackTitle(value){return String(value||'').replace(/^\d+\s*[-_. ]?\s*/,'').replace(/([A-Z]+)([A-Z][a-z])/g,'$1 $2').replace(/([a-z])([A-Z])/g,'$1 $2').trim()}
