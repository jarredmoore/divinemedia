# Artist channel and featured album setup

Status: native feature audit complete; artist identity, selected releases, payment model and assets are awaiting owner input. No artist account, payment configuration, media ownership or production files were changed by this audit. Work branch: `feat/artist-channel-albums`.

## Reuse the installed AVideo features

| Artist-page requirement | Native capability verified in the installed runtime | Frontend integration needed |
| --- | --- | --- |
| Artist identity, biography and channel address | `User` name, channel name and About fields | Extend the existing account/channel views; keep usernames, display names and channel identifiers distinct |
| Profile image and wide header | Native `userSavePhoto.php` and `userSaveBackground.php`; authenticated image validation, 2 MB maximum | Expose these controls in the existing studio card and project public image URLs without returning native filesystem paths |
| One or two albums | Active PlayLists plugin, ordered public programs and native Series helpers (`saveSerie`, `getImage`, `getDescriptionIfIsSerie`) | Present native programs as album cards and reuse native Series artwork/description where applicable; do not invent a second album database |
| Track listening | Existing native audio records, playlist order and frontend player | Show the album track list and play through the existing player |
| Whole-album archive | Native `zip` media type and direct-upload handler; ZIP handling honors `disableZipUpload` and server advanced-configuration restrictions | Add ZIP to the existing creator upload choices only when native configuration permits it; use native records and normal artwork/metadata controls |
| Download authorization | CustomizeUser download permissions plus existing native visibility/group/paid-access checks | Extend the Azure gate for registered ZIP assets, enforce native download permission before sending bytes, and use an attachment response |
| Support/payment links | Native channel Donation Link; active wallet/gateway records; existing Square storefront card | Distinguish optional artist support from buying an album; use real, album-specific checkout links where a sale is intended |
| Follows and community | Existing native channel follows, comments, likes, shares and playlists | Keep the current frontend controls and native account permissions |

The public playlist **Murphy Lee – 2nd Time Around**, native ID **129**, already exists under the current administrator account. It is a candidate for the first featured album, not an inferred choice of artist identity. Featuring or referencing it must not silently rename the administrator's channel, transfer existing media ownership or claim an artist account has been created.

## Integration gaps found

- The current channel response exposes followers and media but omits native biography, avatar, header and public album/program metadata. A native channel/profile projection is needed, including channels with no published media yet.
- The frontend account editor currently changes the display name only. Native image/profile controls should be exposed in that same card, not linked to a second website.
- The native header handler stores `videos/userPhoto/background<userId>.png`. The current public-site-asset allowlist recognizes profile photos but not this header pattern. Add only the exact native image pattern and test anonymous banner delivery; do not open arbitrary files under `videos/`.
- ZIP is a native upload/media type, but the current frontend format list and Azure delivery MIME/record-name grammar do not include it. ZIP must remain a registered, authorized record; adding its extension to a public allowlist would bypass the intended access model.
- Wallet and gateway activation records do not establish valid credentials, working checkout, installed paid packages or album-download fulfillment. PayPerView was not present in the inspected package inventory. Its documented paid viewing window is not proof of a permanent album ZIP entitlement.
- The current Square card embeds a fixed general storefront. It does not associate purchases with an album, verify payment, or grant file access. Never unlock a ZIP from a checkout return URL, a client-side flag or a click on a payment link.

## Artist setup worksheet

Required before configuring real records:

1. Artist/channel name and whether this is an existing native channel or a new artist identity.
2. One or two album names/native playlists, their track order, and the approved album artwork.
3. Header artwork and profile image, or direction for creating them. A native channel-art source near 2560 × 1440 pixels supports the built-in crop guides; keep the uploaded image within 2 MB. Use square album art within the existing thumbnail limits.
4. Download model: free ZIP with an optional support/payment link, or purchase-required fulfillment.
5. Actual album-specific payment URLs and prices when selling. The existing general Square storefront is not automatically an album checkout.
6. Existing album ZIPs or the explicitly selected source tracks to package once, without changing or reencoding the originals.

## Implementation order

1. Confirm the artist identity and preserve the current account/media ownership. Use native profile fields, public programs/Series and download flags as the source of truth.
2. Add the artist header, avatar, biography, follow controls, featured album cards and track lists to the existing frontend channel view. Add profile/artwork/album selection controls inside the same studio card.
3. Reuse native direct upload for opaque ZIP records. Extend the existing upload validation and origin gate narrowly, with tests for private/public access, native download denial, exact record ownership, traversal, unregistered archives and public header images. Do not extract archives or add an encoding job for a ZIP.
4. Wire optional support links directly to the native setting when that is the chosen model. For purchase-required downloads, first verify a compatible native entitlement/fulfillment path or the chosen checkout provider's fulfillment. Keep the archive private and its public download unavailable until that path is verified.
5. Build a frontend preview, test as visitor and owner, and only then configure/publish the approved artist and releases. Production source changes retain the feature-branch, PR, backup and approval workflow.

## Official references

- [AVideo user manual: profile, channel art, programs and permissions](https://github.com/WWBN/AVideo/wiki/User-manual)
- [PlayLists plugin](https://github.com/WWBN/AVideo/wiki/PlayLists-Plugin)
- [Native uploads, including ZIP](https://github.com/WWBN/AVideo/wiki/About-Video-Upload)
- [Native download settings](https://github.com/WWBN/AVideo/wiki/Enable-Video-Download)
- [PayPerView scope and wallet requirements](https://github.com/WWBN/AVideo/wiki/PayPerView-Plugin)
