// Presentation profiles only. Native users, playlists and media permissions remain authoritative.
export const managedChannels=[{
 slug:'planet-derrty',name:'PLANET DERRTY',byline:'Derrty Entertainment · Music. Artists. Culture.',
 href:'/channel/planet-derrty',portrait:'/icons/divine-logo.svg',
 description:'A collection of music from Derrty Entertainment artists, curated and presented on Divine Media.',
 ownerId:1,playlistId:372,recordIds:Array.from({length:31},(_,i)=>i+39)
}];
export function managedChannelFromPath(path){return managedChannels.find(c=>path===c.href||path===c.href+'/')||null}
export const planetDerrty=managedChannels[0];
