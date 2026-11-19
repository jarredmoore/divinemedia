# YouTube creator embedding playbook

Creators add YouTube-hosted videos to their Divine Media channel, play them within Divine Media, and use the existing share, comment, reaction and playlist controls. AVideo remains the catalog and permission system. No YouTube video file is downloaded or sent to Encoder by this workflow.

## First test

1. In YouTube Studio, choose one video intended for public visitors. Set Visibility to **Public** and enable **Allow embedding**. Other archived/client work can remain private.
2. Sign in to the Divine Media feature preview. Open **Account → Add from YouTube**, or `/creator/embed`.
3. Preview `https://www.youtube.com/@divinemediaUS`. If YouTube has not yet updated the feed, paste the test video's direct link instead.
4. Select only the test video, then **Add selected**. The screen explains that the selection is added publicly to Divine Media, subject to the account's native publishing permissions. Nothing is added during preview alone.
5. Open **Your videos**. Check the thumbnail, open Preview, and play the YouTube player. Share, comments, likes and playlists remain on the Divine Media frontend.
6. Preview the source again: the added video should be marked **Already in your library**. Completed additions are retained if a later selection fails; retry adds only the remaining videos.

Full channel discovery uses YouTube Data API `channels.list`, the uploads playlist via `playlistItems.list`, and `videos.list`. It avoids keyword searches and excludes private videos and videos that disallow embedding. Next-page cursors are issued and held server-side.

If the API quota is unavailable, the first page falls back to YouTube's official public feed, limited to 15 recent uploads. The UI labels this limitation; it is not a complete archive import. Private channel collections are not enumerated. Playlists and authenticated private-channel browsing are not included in this first implementation.

## YouTube visibility

- **Public:** discoverable from the channel and playable where embedding is allowed.
- **Unlisted:** use the video's direct URL. Adding it publicly on Divine Media makes its link discoverable there; an unlisted source is not a private access control.
- **Private:** not suitable for public embedded playback. This flow does not request creator Google OAuth access or change YouTube privacy settings.

Embedding can still be restricted by YouTube, the video's owner, region or age rules. The actual YouTube player supplies provider playback controls and a clearly labelled link lets the viewer open YouTube when needed. Site controls do not pretend to control a cross-origin player's local seek, speed or casting APIs.

## AVideo configuration

The installed **BulkEmbed** plugin owns permission checks and the native save handler. `onlyAdminCanBulkEmbed` remains enabled as currently configured; no creator permissions are silently broadened. An administrator must explicitly allow additional creator accounts through the native plugin's existing settings before those creators can use this import flow. **YouTubeAPI** is a separate plugin, with a separate key field; enabling it alone does not configure BulkEmbed or add this frontend integration.

The gateway exposes only two authenticated, CSRF-protected POST actions. Preview metadata is held in the server session for 30 minutes, bound to the creator; add requests carry only a ticket and selected video ID. Only fixed YouTube endpoints are contacted, with verified TLS, no redirects and bounded responses. Adds are serialized per creator, recheck existing owner-specific records and revalidate availability. The existing BulkEmbed save handler and thumbnail plugin run normally. Embeds are not offered as Encoder conversion jobs.

## Current channel and quota audit

Google Cloud CLI connected to the owner's account on November 19, 2026. The supplied key belongs to project `divine-creative`. YouTube's normal project daily default is 10,000 units, but the project has a Google-side producer override with zero effective daily allowance. Provider calls return `quotaExceeded`; another key in the same project shares that limit. No quota, billing or API-key restrictions were changed. The project needs a Google quota review/restoration, rather than a second key. Console: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas?project=divine-creative

`@divinemediaUS` resolves to “Divine Media,” channel `UCBrib_Esy01Ma_97Ae_BCRA`. Its public page currently exposes only Home, and its official feed has zero entries. The owner confirmed the archive has not been made public; this is expected visibility behavior, not a failed import.

## Thumbnail and playback fixes

The reported existing “Chill Hop” embed already has a valid 480 × 360 JPEG on Azure. The creator frontend previously rendered no image in Your videos, and its unified player understood only local audio/video sources. This feature renders creator thumbnails, projects validated YouTube embed descriptors from the adapter, and displays a fixed privacy-enhanced YouTube player in the existing modal. Existing video publishing status is preserved.

## Verification and deployment

The PHP provider contract covers supported and hostile URLs, channel identity, both official feed channel-ID forms, XML external-entity rejection, API quota fallback, pagination, privacy and embedding filters, and direct video previews without an API key. The browser fixture uses synthetic accounts and metadata at 1440 and 390 pixels to test selection, disabled duplicates, partial retries, loaded creator images, in-site frames and horizontal overflow. It does not claim a real authenticated import or media-stream playback test.

The native adapter additions were applied with exact source leases and verified private off-VM before/after backups. Anonymous add/preview requests and missing CSRF are rejected. Existing media, catalog rows, Encoder queue, other handlers and container uptimes were preserved; no videos were imported or published by deployment. Rollback state: `/srv/divinemedia/backups/youtube-channel-api-1993cc5d5c53`. Restore the two original adapter files and remove only the two new PHP files if their hashes still match this change. The production frontend and production Git branch are unchanged; test the feature on its Netlify preview first.

Next provider: Vimeo, using its supported embed/API capabilities and the same AVideo catalog boundary. No paid-plugin replacement suite is introduced.
