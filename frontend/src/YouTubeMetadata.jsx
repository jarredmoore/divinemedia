import React from 'react';
export default function YouTubeMetadata({metadata}){
 if(!metadata)return null;const stats=metadata.statistics||{},labels={viewCount:'YouTube views',likeCount:'YouTube likes',commentCount:'YouTube comments'};
 return <details className="dm-provider-metadata"><summary>YouTube metadata</summary>{Object.entries(labels).filter(([key])=>stats[key]!==undefined).map(([key,label])=><p key={key}>{label}: <strong>{String(stats[key])}</strong></p>)}{!Object.keys(stats).length&&<p>Public statistics are not available in this preview.</p>}{metadata.publishedAt&&<p>Published: {metadata.publishedAt}</p>}{metadata.duration&&<p>Duration: {metadata.duration}</p>}{metadata.tags?.length>0&&<p>Source tags: {metadata.tags.join(', ')}</p>}<p>Source snapshot: {metadata.syncedAt}. Divine Media likes and comments remain separate. YouTube shares require authorized creator analytics.</p></details>;
}
