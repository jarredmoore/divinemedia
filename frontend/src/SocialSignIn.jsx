import React from 'react';
const providers=[['Google','G','cyan'],['Apple','A','blue'],['Facebook','f','purple'],['LinkedIn','in','blue'],['X / Twitter','X','pink'],['WordPress','W','green'],['Yahoo','Y!','purple']];
export default function SocialSignIn({account=false}){
 return <section className="dm-social-signin" aria-label="Social sign-in options"><h2>{account?'Sign-in options':'Social sign-in'}</h2><p>{account?'Password sign-in is available. Social sign-in is not active yet.':'Social sign-in is not active yet. Use your Divine Media username and password below.'}</p><div className="dm-social-signin-grid">{providers.map(([name,mark,tone])=><button key={name} type="button" disabled aria-label={name+' sign-in — not active yet'}><span className={'dm-provider-mark '+tone} aria-hidden="true">{mark}</span><span><strong>{name}</strong><small>Not active yet</small></span></button>)}</div></section>;
}
