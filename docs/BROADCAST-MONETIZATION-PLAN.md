# Broadcast and monetization plan

Owner direction: U.S. first, international later; both scheduled listening and on-demand selection. AdSense account/site approval is unconfirmed: owner needs to check. Audit only: no purchases, advertising configuration or broadcasts were started.

## Reuse native AVideo modules

Checked against the current upstream documentation index, individual module guides and a fresh read-only Azure inventory on November 9, 2026. Installation/activation must be distinguished from feature availability and from content rights.

| Need | Native module | Distribution | Decision |
| --- | --- | --- | --- |
| Live events | Live | Free | Already enabled; complete production event rehearsal |
| On-demand programs and libraries | PlayLists plus existing VOD/audio support | Free | Already enabled; finish frontend library features |
| Scheduled recorded-video broadcasts | Rebroadcaster | Paid | Not installed; evaluate existing native module before external playout or a replacement |
| Weekly television-style program calendar | VideoPlaylistScheduler | Paid | Not installed; requires Live, PlayLists, Rebroadcaster, and working Scheduler cron |
| Native scheduled task execution | Scheduler | Free | Already active; activation alone does not prove minute-by-minute cron health |
| Page banners / AdSense / sponsor images | ADs | Free | Installed; no active plugin record; frontend placements still required |
| Owned sponsor/commercial campaigns | AD_Server | Free | Installed; no active plugin record; native VAST/VMAP campaigns plus frontend playback integration |
| Google or third-party VAST/VMAP video demand | GoogleAds_IMA | Paid | Not installed; verify account eligibility and custom-player integration before purchase |

Rebroadcaster sends locally stored videos to the native live server through FFmpeg. It does not schedule external embedded video. VideoPlaylistScheduler books playlists into a weekly calendar, with documented half-hour slots. Neither module establishes that a 24/7 radio station, audio-only ad workflow, uninterrupted playout, failover or royalty reports are operational. Validate those requirements using the licensed module/version first.

The previous answer's suggestion of additional playout infrastructure was premature as the default choice: use AVideo's documented module path first, with external services only for a demonstrated gap.

The fresh Azure check confirms Live, PlayLists and Scheduler active; Rebroadcaster, VideoPlaylistScheduler and GoogleAds_IMA absent; ADs and AD_Server files present without active records. The native AdSense configuration field is empty. That does not establish whether the owner holds an external Google account. See BROADCAST-MONETIZATION-AUDIT.json.

## Custom frontend integration boundary

The React player uses HTML5 video and optional hls.js; it does not load AVideo's native player HTML or its plugin footer. Enabling a backend plugin alone will not insert banners, calendar controls or video ads into React. Keep campaign storage, schedule execution, permissions and purchased module logic native; expose only supported, authorized data/actions through the existing gateway, then render branded controls in the frontend. Confirm the vendor's API and integration terms for paid modules before committing to an implementation.

VAST and VMAP are documented interoperability points for AD_Server campaigns. A frontend IMA integration can consume approved ad tags, but that SDK is not an ad network, revenue guarantee or substitute for plugin licensing. Do not execute arbitrary native plugin HTML in React or introduce an unrestricted ad-tag proxy.

AD_Server's guide explicitly excludes audio from its automatic ad placement; it documents live pre-roll only, not television-style live mid-roll insertion. Evaluate audio monetization and live ad breaks separately rather than advertise unsupported parity.

## Google monetization

- Google Ads buys advertising. AdSense monetizes eligible publisher website inventory. Google Ad Manager manages ad inventory; video demand/AdX eligibility is a separate confirmation.
- An existing AdSense account does not establish that divinemedia.us is approved, that video demand is approved, or that ads are active on this frontend.
- Current Google help directs legacy AdSense for Video publishers toward Ad Exchange Video through Google Ad Manager. Use current Google account eligibility and issued ad tags rather than old AVideo source comments about AdSense for Video.
- The checked https://divinemedia.us/ads.txt URL returns the SPA HTML page, not a valid text advertising authorization file. Do not invent a publisher ID or seller relationship. Publish the exact authorized entries only after account confirmation.
- Start with restrained page placements and/or owner-sold sponsor campaigns. Add VOD pre-roll after approved demand and player event verification. Validate live and audio ad behavior independently. Use test ads during implementation, and do not click paid ads to test them.
- Consent, privacy choices, ad eligibility and territorial configuration need review for the U.S. launch and again before international availability. Installing an ad module does not satisfy those requirements.

## Content licensing and territorial rollout

Scheduled noninteractive music listening and user-selected on-demand songs are distinct rights models. A U.S. noninteractive statutory sound-recording license does not by itself cover an interactive music catalog or musical compositions. Music videos, concert recordings, films, shows and channel retransmission require the relevant permissions for the actual use, including monetization and any recording/catch-up rights.

Track licensed territories, dates and permitted live/VOD/ad-supported uses. A U.S.-first business plan is not a geographic restriction: no new U.S.-only availability control was enabled by this audit. Validate native territorial enforcement and protection requirements before distributing restricted content; international launch requires corresponding rights expansion.

## Next configuration order

1. Confirm AdSense site status and whether Google Ad Manager/video demand access exists, without sharing passwords or private tokens.
2. Test an owned sponsor campaign through native AD_Server and the branded player, using isolated fixtures and test ads.
3. Assess Rebroadcaster plus VideoPlaylistScheduler licensing, installed-version compatibility, APIs and native cron; test one new locally stored video/playlist before continuous scheduling.
4. Finish audio-only station, audio-ad and royalty-reporting requirements separately.
5. Add approved advertising placements and rights/territory controls with rollback, then consider international availability.

## Sources

- [AVideo plugin index](https://github.com/WWBN/AVideo/wiki/Plugin-Documentation-Index)
- [Rebroadcaster](https://github.com/WWBN/AVideo/wiki/Rebroadcaster-Plugin)
- [VideoPlaylistScheduler](https://github.com/WWBN/AVideo/wiki/VideoPlaylistScheduler-plugin)
- [ADs](https://github.com/WWBN/AVideo/wiki/ADs-plugin)
- [AD_Server](https://github.com/WWBN/AVideo/wiki/AD_Server-Plugin)
- [GoogleAds_IMA](https://github.com/WWBN/AVideo/wiki/GoogleAds_IMA---Videos-Ads-on-your-page)
- [Google migration guidance: AdSense for Video to AdX Video](https://support.google.com/adsense/answer/1705822?hl=en)
- [Google IMA HTML5 SDK](https://developers.google.com/interactive-media-ads/docs/sdks/html5/client-side)
