import React from 'react';
import './social-links.css';
export const socialProfiles=[
 {name:'Instagram',brand:'Divine Creative Group',handle:'@divinecreativegroup',url:'https://www.instagram.com/divinecreativegroup/',icon:'/icons/social-instagram.svg',description:'Creative projects, behind-the-scenes moments, and community.'},
 {name:'Instagram',brand:'Divine Media',handle:'@divinemedia.us',url:'https://www.instagram.com/divinemedia.us/',icon:'/icons/social-instagram.svg',description:'New releases, creator highlights, and live culture.'},
 {name:'TikTok',brand:'Divine Media',handle:'@divinemedia.us',url:'https://www.tiktok.com/@divinemedia.us',icon:'/icons/social-tiktok.svg',description:'Short clips, live moments, and new discoveries.'}
];
export default function SocialLinks(){return <section className="dm-social" aria-labelledby="dm-social-heading"><div><h2 id="dm-social-heading">Stay connected</h2><p>Follow Divine Media and Divine Creative Group.</p></div><nav className="dm-social-links" aria-label="Divine Media social profiles">{socialProfiles.map(profile=><a className="dm-social-card" key={profile.url} href={profile.url} target="_blank" rel="noopener noreferrer" aria-label={'Follow '+profile.brand+' on '+profile.name+' — '+profile.handle+' (opens in a new tab)'}><img src={profile.icon} width="44" height="44" alt=""/><div><strong>{profile.name}<span>{profile.handle}</span></strong><p>{profile.description}</p></div><span className="dm-social-arrow" aria-hidden="true">↗</span></a>)}</nav></section>}
