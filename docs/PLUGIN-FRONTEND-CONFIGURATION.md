# Active plugins and frontend configuration

The live read-only audit found **75 active plugin records and no inactive records**. It did not validate external provider credentials, advertising approval, merchant setup, socket connectivity, or every feature schema. No plugin settings were changed by the audit. Native AVideo remains the settings and persistence authority; the custom React frontend requires explicit presentation/API integration.

## Player and popup presentation

- **Playback options** contains playback speed, supported fullscreen and mini-player controls, theater mode and a keyboard shortcut guide. A narrow public JSON projection reads native SeekButton, Hotkeys, TheaterButton and FloatVideo activation/settings. It exposes only booleans and bounded seek intervals; no provider settings or secrets.
- **Share, Like, Comments and Playlist** are primary actions. **More** groups Copy link, Copy embed code, Watch later, Dislike and the creator channel with text labels. The existing Embed action shares a Divine Media player; it does not import a YouTube link.
- Native browser play/pause, volume and timeline controls remain available. Browser picture-in-picture is the new frontend's manual mini-player; it is not the native FloatVideo plugin's automatic scroll-floating behavior. Browser support determines availability.
- Channel cards reserve an image area, wrap long titles, use the existing approved album cover as the fallback for known album IDs, and use the brand placeholder for other broken artwork. This visual fix does not replace or regenerate stored covers.
- Default and Code Black themes retain their shared fonts and theme tokens. New controls use the current accent, dark glass panels, keyboard focus indicators and responsive layouts.

## How to configure the main groups

Use the private operator interface: **Admin Panel → Plugins → plugin → Edit parameters**, plus its own Edit/Settings button where available. Save parameters and reload the frontend player to refresh its projected configuration. Creator/viewer workflows should remain on divinemedia.us.

| Group | What to configure | Frontend integration status |
| --- | --- | --- |
| SeekButton / Hotkeys / TheaterButton / FloatVideo | Seek intervals, hide-on-mobile choice, activation and floating-video preference | First player preference bridge in this change; browser speed/fullscreen also available |
| NextButton / PlayerSkins / VideoLandscapeFullscreen / VideoLogoOverlay | Native next-video behavior, skins, orientation and logo placement | Native Video.js skins/footers do not automatically style the React player; next-video/orientation/watermark parity remains pending |
| PlayLists / Bookmark / VideoTags / ReportVideo / Shorts | Ownership/group permissions, tags, reporting reasons, playlist behavior | Account playlists/favorites/watch-later already wired; timestamp bookmarks, tags, report submission and Shorts-specific presentation remain pending |
| Live / LiveLinks / Scheduler / YPTSocket / WebRTC / Meet | Ingest/HLS settings, stream grants, scheduler cron, socket endpoint, meeting requirements | Live studio/directory integrated; meetings, scheduled channels and full frontend parity require separate verification |
| YouTubeAPI / BulkEmbed / VimeoAPI | Provider keys where required, import/search permissions and supported provider behavior | Enabled does not add a YouTube import form to React; link-import/player integration is pending |
| ADs / AD_Server / AD_Server_Location / AD_Overlay / AdBlockerDetector | Banner positions, VAST campaigns, creative assets, dates and targeting | Campaign/ad rendering is not yet connected to React. Do not assume active campaigns or approved Google demand from activation |
| YPTWallet / MonetizeUsers / StripeYPT / RazorPayYPT / AuthorizeNet / BTCPayments | Currency, merchant credentials, test/live mode, callback/webhook configuration and creator payout rules | Backend modules active; real checkout, wallet and payout UI should be exposed only after account/configuration tests |
| LoginGoogle / LoginApple / LoginFacebook / LoginLinkedin / LoginTwitter / LoginYahoo / LoginWordPress | Provider application, public callback URLs, client credentials and matching frontend return flow | Native username/password login integrated; provider buttons/callback compatibility require setup and testing |
| SlackBot / SlackNotify / DiscordNotify / AutoPostOnSocialMedia / SocialMediaPublisher | Destinations, API/webhook credentials, permissions and posting rules | Background integrations; not player buttons. No test messages/posts are sent during this audit |
| AI / CDN / Cache / User_Location / API / Audit | Provider/service endpoints, credentials, budgets, cache/storage behavior, API permissions and logging | Backend configuration; no credential values belong in frontend configuration or public capability JSON |
| Gallery / Layout / TopMenu / YouPHPFlix2 / FirstPageChannelList / PredefinedCategory / ImageGallery / Articles | Native organization, menus and content/layout preferences | Data/layout concepts can be reflected in React; native HTML themes do not replace the frontend theme |
| DivineThumbnails | Missing-cover behavior and registered album artwork | Active native video/audio generation; preserves existing art and uses embedded → registered album → waveform fallback |

Service activation is not service readiness. Paid modules not present in this active-record list are not made available by turning on the included plugins. See BROADCAST-MONETIZATION-PLAN.md for Rebroadcaster, VideoPlaylistScheduler, GoogleAds_IMA and content-rights planning.

## Encoder import error kept separate

The screenshot shows a YouTube **download/import** attempt through yt-dlp, with a missing supported JavaScript runtime warning and a YouTube bot-verification error. Plugin activation alone does not resolve either issue. Enabling a runtime would not prove that YouTube will accept the server request. This styling/configuration pass does not retry downloads, import browser cookies, change downloader settings, start Encoder jobs or attempt to bypass YouTube verification. Where appropriate, an official YouTube embed remains a different playback path from downloading a file.

## Complete active inventory

Descriptions and guide links below come from AVideo's documentation index, cross-referenced with the live activation audit. Each entry being active does not establish that its UI or external account is configured.

| Active plugin | Version | Purpose | Configuration guide |
| --- | --- | --- | --- |
| AD_Overlay | 2.1 | Simple overlays on the player during playback, like YouTube annotations | [AD_Overlay](https://github.com/WWBN/AVideo/wiki/AD_Overlay-Plugin) |
| AD_Server | 5.0 | Your own VAST video ad server | [AD_Server](https://github.com/WWBN/AVideo/wiki/AD_Server-Plugin) |
| AD_Server_Location | 1.0 | Shows each AD_Server campaign only in chosen countries, regions or cities (needs AD_Server) | [AD_Server_Location](https://github.com/WWBN/AVideo/wiki/AD_Server_Location-Plugin) |
| AdBlockerDetector | 1.0 | Asks visitors to turn off their ad blocker | [AdBlockerDetector](https://github.com/WWBN/AVideo/wiki/AdBlockerDetector-Plugin) |
| ADs | 1.1 | Banner ads on the site (AdSense or similar) | [ADs](https://github.com/WWBN/AVideo/wiki/ADs-plugin) |
| AI | 6.1 | AI suggestions for titles, descriptions and tags, and automatic transcription | [AI](https://github.com/WWBN/AVideo/wiki/AI-Plugin), [AI Video Chat](https://github.com/WWBN/AVideo/wiki/AI-Video-Chat) |
| API | 1.0 | API for apps and other software | [API](https://github.com/WWBN/AVideo/wiki/API-Plugin) |
| Articles | 1.0 | Rich-text articles listed with your videos | [Articles](https://github.com/WWBN/AVideo/wiki/Articles-Plugin) |
| Audit | 2.0 | Logs every insert, update and delete in the database | [Audit](https://github.com/WWBN/AVideo/wiki/Audit-Plugin) |
| AuthorizeNet | 1.2 | Authorize.Net payments | [AuthorizeNet](https://github.com/WWBN/AVideo/wiki/AuthorizeNet-Plugin) |
| AutoPostOnSocialMedia | 1.0 | Posts new content on social media automatically (currently Twitter only) | [AutoPostOnSocialMedia](https://github.com/WWBN/AVideo/wiki/AutoPostOnSocialMedia-Plugin) |
| BitLy | 1.0 | Short links with Bitly | [BitLy](https://github.com/WWBN/AVideo/wiki/BitLy-Plugin) |
| Bookmark | 1.0 | Chapters on videos and audio | [Bookmark](https://github.com/WWBN/AVideo/wiki/Bookmark-Plugin) |
| BTCPayments | 1.1 | Bitcoin payments (needs YPTWallet). Marked as under development. | [BTCPayments](https://github.com/WWBN/AVideo/wiki/BTCPayments-Plugin) |
| BulkEmbed | 1.2 | Searches YouTube and embeds many videos at once | [BulkEmbed](https://github.com/WWBN/AVideo/wiki/BulkEmbed-Plugin) |
| Cache | 10.0 | Page cache to make the site faster | [Cache](https://github.com/WWBN/AVideo/wiki/Cache-Plugin) |
| CDN | 2.0 | StreamPHP CDN delivery and CDN Storage | [CDN](https://github.com/WWBN/AVideo/wiki/CDN-Plugin), [CDN Storage](https://github.com/WWBN/AVideo/wiki/CDN-Storage) |
| CloneSite | 1.1 | Copies (clones) a site to another server | [CloneSite](https://github.com/WWBN/AVideo/wiki/Clone-Site-Plugin) |
| CookieAlert | 1.0 | Cookie notice (EU cookie law) | [CookieAlert](https://github.com/WWBN/AVideo/wiki/CookieAlert-Plugin) |
| CustomizeAdvanced | 1.0 | Many advanced site-wide options | [CustomizeAdvanced](https://github.com/WWBN/AVideo/wiki/CustomizeAdvanced-Plugin) |
| CustomizeUser | 4.1 | User account options: sign-up, profile, e-mail verification, verification marks, donations | [CustomizeUser](https://github.com/WWBN/AVideo/wiki/CustomizeUser-Plugin) |
| DiscordNotify | 1.2 | New-video messages to a Discord webhook | [DiscordNotify](https://github.com/WWBN/AVideo/wiki/DiscordNotify-Plugin) |
| DivineThumbnails | 1.1 | Divine Media native upload-cover helper | Admin Panel → Plugins |
| FirstPageChannelList | 1.0 | Home page as a list of channels | [FirstPageChannelList](https://github.com/WWBN/AVideo/wiki/FirstPageChannelList-Plugin) |
| FloatVideo | 1.0 | Floating video player | [FloatVideo](https://github.com/WWBN/AVideo/wiki/FloatVideo-Plugin) |
| Gallery | 1.0 | Home page as a gallery of rows | [Gallery](https://github.com/WWBN/AVideo/wiki/Gallery-Plugin) |
| Hotkeys | 1.1 | Keyboard shortcuts in the player | [Hotkeys](https://github.com/WWBN/AVideo/wiki/Hotkeys-Plugin) |
| ImageGallery | 1.0 | Photo galleries (many images in one post) | [ImageGallery](https://github.com/WWBN/AVideo/wiki/ImageGallery-Plugin) |
| JustWatch | 1.0 | Feed of your content for JustWatch | [JustWatch](https://github.com/WWBN/AVideo/wiki/JustWatch-Plugin) |
| Layout | 1.1 | Layout and theme fine-tuning | [Layout](https://github.com/WWBN/AVideo/wiki/Layout-Plugin) |
| Live | 15.3 | Live streaming (RTMP in, HLS out) | [Live](https://github.com/WWBN/AVideo/wiki/Live-Plugin) |
| LiveLinks | 4.4 | Adds external live streams from any HLS link (needs Live) | [LiveLinks](https://github.com/WWBN/AVideo/wiki/LiveLinks-Plugin) |
| LoginApple | 1.0 | Sign in with Apple | [LoginApple](https://github.com/WWBN/AVideo/wiki/LoginApple-Plugin) |
| LoginControl | 3.0 | Two-step login by e-mail and single-device login | [LoginControl](https://github.com/WWBN/AVideo/wiki/LoginControl-Plugin) |
| LoginFacebook | 1.0 | Sign in with Facebook | [LoginFacebook](https://github.com/WWBN/AVideo/wiki/LoginFacebook-Plugin) |
| LoginGoogle | 1.0 | Sign in with Google | [LoginGoogle](https://github.com/WWBN/AVideo/wiki/LoginGoogle-Plugin) |
| LoginLinkedin | 1.0 | Sign in with LinkedIn | [LoginLinkedin](https://github.com/WWBN/AVideo/wiki/LoginLinkedin-Plugin) |
| LoginTwitter | 1.0 | Sign in with Twitter (X) | [LoginTwitter](https://github.com/WWBN/AVideo/wiki/LoginTwitter-Plugin) |
| LoginWordPress | 1.0 | Sign in with a WordPress account | [LoginWordPress](https://github.com/WWBN/AVideo/wiki/LoginWordPress-Plugin) |
| LoginYahoo | 1.0 | Sign in with Yahoo | [LoginYahoo](https://github.com/WWBN/AVideo/wiki/LoginYahoo-Plugin) |
| Meet | 3.0 | Video meetings and conferences | [Meet](https://github.com/WWBN/AVideo/wiki/Meet-Plugin) |
| MobileManager | 1.5 | Settings for the AVideo mobile app (needs API) | [MobileManager](https://github.com/WWBN/AVideo/wiki/MobileManager-Plugin) |
| MobileYPT | 1.0 | Support for the YPT Media mobile app (needs API) | [MobileYPT](https://github.com/WWBN/AVideo/wiki/MobileYPT-Plugin) |
| MonetizeUsers | 3.2 | Pays creators into their wallet for the views of their videos (needs YPTWallet) | [MonetizeUsers](https://github.com/WWBN/AVideo/wiki/MonetizeUsers-Plugin) |
| NextButton | 1.0 | Next button in the player control bar | [NextButton](https://github.com/WWBN/AVideo/wiki/NextButton-Plugin) |
| Permissions | 1.0 | Gives user groups selected administrator powers | [Permissions](https://github.com/WWBN/AVideo/wiki/Permissions-Plugin) |
| PlayerSkins | 1.1 | Player skins and player settings | [Player and PlayerSkins](https://github.com/WWBN/AVideo/wiki/Player-and-PlayerSkins-Plugin) |
| PlayLists | 3.0 | Playlists (programs), series, Watch Later and Favorite | [PlayLists](https://github.com/WWBN/AVideo/wiki/PlayLists-Plugin), [Programs and series](https://github.com/WWBN/AVideo/wiki/<Program-(Playlist)-to-series>) |
| PredefinedCategory | 1.0 | Default category and user groups for new videos | [PredefinedCategory](https://github.com/WWBN/AVideo/wiki/PredefinedCategory-Plugin) |
| RazorPayYPT | 1.0 | Razorpay payments | [RazorPayYPT](https://github.com/WWBN/AVideo/wiki/RazorPayYPT-Plugin) |
| ReportVideo | 2.3 | **Report** button for videos and **Block User** button | [ReportVideo](https://github.com/WWBN/AVideo/wiki/ReportVideo-Plugin) |
| Scheduler | 5.4 | Runs background tasks; needs an every-minute cron job | [Scheduler](https://github.com/WWBN/AVideo/wiki/Scheduler-Plugin) |
| SeekButton | 1.1 | Seek buttons in the player control bar | [SeekButton](https://github.com/WWBN/AVideo/wiki/SeekButton-Plugin) |
| Shorts | 1.0 | Shorts row on the home page with a full-screen player | [Shorts](https://github.com/WWBN/AVideo/wiki/Shorts-Plugin) |
| SlackBot | 1.0 | New-video messages to subscribed Slack users | [SlackBot](https://github.com/WWBN/AVideo/wiki/SlackBot-Plugin) |
| SlackNotify | 1.0 | New-video messages to a Slack webhook | [SlackNotify](https://github.com/WWBN/AVideo/wiki/SlackNotify-Plugin) |
| SocialMediaPublisher | 1.0 | Publishes your videos to your YouTube, Facebook, Instagram or LinkedIn account. Marked as under development. | [SocialMediaPublisher](https://github.com/WWBN/AVideo/wiki/SocialMediaPublisher-Plugin) |
| StripeYPT | 2.5 | Stripe payments | [StripeYPT](https://github.com/WWBN/AVideo/wiki/StripeYPT-Plugin) |
| TheaterButton | 1.1 | Theater-mode button in the player control bar | [TheaterButton](https://github.com/WWBN/AVideo/wiki/TheaterButton-Plugin) |
| TopMenu | 2.2 | Your own menus at the top of the site | [TopMenu](https://github.com/WWBN/AVideo/wiki/TopMenu-Plugin) |
| User_Location | 1.0 | Detects the visitor's country from the IP address | [User_Location](https://github.com/WWBN/AVideo/wiki/User_location-Plugin) |
| UserConnections | 1.0 | Friend requests and connections between users | [UserConnections](https://github.com/WWBN/AVideo/wiki/UserConnections-Plugin) |
| UserNotifications | 2.0 | Notifications in the bell icon of the top bar | [UserNotifications](https://github.com/WWBN/AVideo/wiki/UserNotifications-Plugin) |
| VideoLandscapeFullscreen | 1.0 | Automatic fullscreen in landscape on mobile devices | [VideoLandscapeFullscreen](https://github.com/WWBN/AVideo/wiki/VideoLandscapeFullscreen-Plugin) |
| VideoLogoOverlay | 2.2 | Your logo over the video | [VideoLogoOverlay](https://github.com/WWBN/AVideo/wiki/VideoLogoOverlay-Plugin) |
| VideosStatistics | 1.0 | Watch history pages and clean-up of viewing statistics | [VideosStatistics](https://github.com/WWBN/AVideo/wiki/VideosStatistics-Plugin) |
| VideoTags | 3.0 | Tags grouped by type, tag pages and tag subscriptions | [VideoTags](https://github.com/WWBN/AVideo/wiki/VideoTags-Plugin) |
| VimeoAPI | 1.0 | Uploads your videos to Vimeo | [VimeoAPI](https://github.com/WWBN/AVideo/wiki/VimeoAPI-Plugin) |
| VR360 | 1.0 | 360-degree (panoramic) video player | [VR360](https://github.com/WWBN/AVideo/wiki/VR360-Plugin) |
| WebRTC | 1.1 | Go live from the browser camera with one click | [WebRTC](https://github.com/WWBN/AVideo/wiki/WebRTC-plugin) |
| WWBNIndex | 1.0 | Lists your site on SearchTube (beta) | [WWBNIndex](https://github.com/WWBN/AVideo/wiki/WWBNIndex-Plugin) |
| YouPHPFlix2 | 1.0 | Netflix-style home page | [YouPHPFlix2](https://github.com/WWBN/AVideo/wiki/YouPHPFlix2-Plugin) |
| YouTubeAPI | 1.0 | Shows YouTube search results on your home page (does not upload; see SocialMediaPublisher) | [YouTubeAPI](https://github.com/WWBN/AVideo/wiki/YouTubeAPI-Plugin) |
| YPTSocket | 2.3 | Real-time connection (WebSocket) used by chat, notifications and live features | [YPTSocket](https://github.com/WWBN/AVideo/wiki/YPTSocket-Plugin) |
| YPTWallet | 6.3 | User wallet: add funds, pay, donate | [YPTWallet](https://github.com/WWBN/AVideo/wiki/YPTWallet-Usage) |
