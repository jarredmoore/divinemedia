import React,{useId} from 'react';
import * as Lucide from 'lucide-react';
export * from 'lucide-react';
// A single treatment for action icons; dismiss/back arrows remain quiet neutral glyphs.
const tones={cyan:['#a4f5ff','#32caff','#657dff'],blue:['#a5ecff','#729fff','#8176ff'],purple:['#dfc2ff','#af7bff','#ff8bd7'],pink:['#ffd1ed','#ff83c8','#a387ff'],green:['#bcffe6','#5de5b3','#45b8e9']};
function glass(Icon,tone,kind=''){return function GlassIcon({size=20,className='',fill='none',...props}){
 const id='glass-'+useId().replace(/[^A-Za-z0-9_-]/g,''),width=Math.max(20,Number(size)||20),colors=tones[tone];
 return <span className={'dm-glass-icon dm-icon-'+tone+' dm-icon-'+kind+' '+className} style={{'--dm-icon-size':width+'px'}} aria-hidden="true"><Icon {...props} stroke={'url(#'+id+')'} fill={fill==='currentColor'?'url(#'+id+')':fill} size={width-6}><defs><linearGradient id={id} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="24" y2="24"><stop offset="0" stopColor={colors[0]}/><stop offset=".48" stopColor={colors[1]}/><stop offset="1" stopColor={colors[2]}/></linearGradient></defs></Icon></span>;
}}

export const Play=glass(Lucide.Play,'cyan','play');
export const Pause=glass(Lucide.Pause,'blue');
export const Headphones=glass(Lucide.Headphones,'purple');
export const Music=glass(Lucide.Music,'purple');
export const Compass=glass(Lucide.Compass,'cyan');
export const Clapperboard=glass(Lucide.Clapperboard,'blue');
export const Radio=glass(Lucide.Radio,'green');
export const Users=glass(Lucide.Users,'pink');
export const Library=glass(Lucide.Library,'purple');
export const Upload=glass(Lucide.Upload,'green');
export const Download=glass(Lucide.Download,'cyan');
export const MonitorUp=glass(Lucide.MonitorUp,'blue');
export const Airplay=glass(Lucide.Airplay,'cyan');
export const Cast=glass(Lucide.Cast,'purple');
export const Bell=glass(Lucide.Bell,'pink');
export const UserRound=glass(Lucide.UserRound,'blue');
export const Heart=glass(Lucide.Heart,'pink');
export const Share2=glass(Lucide.Share2,'cyan');
export const Share=glass(Lucide.Share,'cyan');
export const MessageCircle=glass(Lucide.MessageCircle,'blue');
export const ThumbsUp=glass(Lucide.ThumbsUp,'green');
export const ThumbsDown=glass(Lucide.ThumbsDown,'pink');
export const ListPlus=glass(Lucide.ListPlus,'purple');
export const PictureInPicture=glass(Lucide.PictureInPicture,'blue');
export const Maximize=glass(Lucide.Maximize,'blue');
export const Settings2=glass(Lucide.Settings2,'purple');
export const SkipBack=glass(Lucide.SkipBack,'blue');
export const SkipForward=glass(Lucide.SkipForward,'blue');
export const Volume2=glass(Lucide.Volume2,'green');
export const Clock=glass(Lucide.Clock,'purple');
export const Copy=glass(Lucide.Copy,'cyan');
export const Code=glass(Lucide.Code,'purple');
export const MoreHorizontal=glass(Lucide.MoreHorizontal,'blue');
export const Plus=glass(Lucide.Plus,'cyan');
