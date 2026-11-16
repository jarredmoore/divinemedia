const albumIds=new Set([10,11,12,13,14,15,16]);
export function artworkFallback(item){return albumIds.has(Number(item?.avideoId||item?.id))?'/2ndTimeAround.jpg':'/placeholder.svg'}
export function recoverArtwork(event,item){const img=event.currentTarget,next=artworkFallback(item);if(img.dataset.dmFallback===next&&img.getAttribute('src')===next)return;img.dataset.dmFallback=next;img.src=next}
