# Flat Studio upload and record editing

The existing Studio card now exposes file selection, metadata, artwork and publishing together. Creator screens retain the ambient gradient rim, invisible scrollbar/track, existing focus handling and a return to Creator Studio. Uploading stays in the same card; successful uploads are not automatically sent away to the queue. Your videos offers an inline **Edit details & thumbnail** form for existing uploads and embeds.

## Available controls

- File type: video, audio, image or document. Formats come from the installed native direct uploader's supported types and disabled flags: MP4/WebM, MP3/OGG, JPG/JPEG/PNG/GIF/WebP and PDF. ZIP remains disabled by the existing native configuration. This does not add the Encoder's broader raw ingest formats.
- Size/name/type summary and enforced limits: video 4 GB, audio 1 GB, image 20 MB, PDF 100 MB. Media transfers use the existing 1 MB chunk path; authenticated chunks have their own bounded allowance so large transfers do not hit the ordinary metadata POST limit. Login/authentication limits remain unchanged.
- Title, plain-text description, existing category, visibility, optional descriptive tag groups, content rating, sharing and download settings. The native Video model owns saves and publishing permissions.
- Landscape and portrait thumbnail selection, previews and automatic JPEG optimization. JPG/PNG/WebP source images up to 20 MB are resized to a maximum 1920px edge and optimized to at most 2 MB. The server independently validates image bytes, size and dimensions and normalizes to native JPEG posters; SVG/active content is rejected. Image updates use the installed `objects/uploadPoster.php` handler and its cache invalidation.
- Optional existing encoding profiles for uploaded video/audio: MP4, adaptive HLS, audio MP3 and WebM. Enqueueing is explicit and retains the existing Encoder actor/permission boundary. Embeds, images and documents do not get meaningless encoding buttons.
- Images and PDFs can be previewed within the frontend using fixed native media URLs. Sharing buttons follow the saved native flag, and native download policy controls the download link. These controls are UI/policy behavior, not DRM.

## Categories and tags

The existing category records were preserved: Media → Audio → Music → Hip Hop / Rhythm and Blues; Media → Video → Film. The selector shows complete parent paths while retaining native IDs. No category was created, renamed, moved or deleted.

VideoTags was enabled but its native tag-type table was empty. One standard **Keywords** group was configured through the native TagsTypes model after a verified private backup. It is optional and appears only when native tag permissions allow it. The adapter only edits descriptive groups and preserves native/system tag groups such as permission and monetization tags. It does not create another tag database or replace the plugin.

## Draft and retry behavior

New Studio uploads carry their selected details in their creator-bound server upload ticket. A narrow trusted-adapter guard in the native uploader holds these new uploads as inactive drafts rather than auto-publishing them before metadata/artwork finishes. After the media ID is confirmed, the client saves thumbnail images and then the chosen metadata/visibility. A thumbnail failure retains the confirmed media ID and completed artwork; retry finishes that record instead of uploading the media again. Unknown final transfer failures still tell the creator to check the library before retrying.

Legacy frontend uploads without the new visibility/details handshake and direct native uploads keep their existing behavior. The patch is defined by `ops/divinemedia/creator-upload-hold.py` and only changes the one native auto-status call when `DM_FRONTEND_API` and a server-owned hold flag are present. It neither accepts arbitrary existing video IDs during upload nor starts global Encoder work.

## Account, login and routes

Account, registration, password recovery, upload, record editing, encoding, embedding and live preparation stay in frontend workspace views. Native page aliases arriving on the frontend domain map to supported clean routes; old recovery query names retain their token for the existing reset flow. Native API endpoints, administration and OAuth callbacks are not blindly redirected.

The native login plugin inventory supports Google, Apple, Facebook, LinkedIn, X/Twitter, WordPress and Yahoo. These are visible as **Not active yet** options in account/login/registration. No fake sign-in, account linking, provider credential changes or OAuth callback changes were introduced. Username/password sign-in stays first. Actual social authentication and the native-host email/callback cutover require a separately verified integration; frontend aliases alone do not redirect external backend-host requests. Operator access and existing callback handlers are preserved.

## Verification and rollout

Build, Node tests and Python backend tests pass. PHP contract tests cover metadata types and limits, tags, invalid image payloads and size limits. The trusted draft guard is exercised with held and legacy branches. Browser fixtures use synthetic accounts/records at desktop/mobile widths for all four type choices, metadata, thumbnail optimization, two-artwork uploads, partial failure/retry without duplicate media, inline editing, image previews, permission gating, account aliases, inactive providers, recovery tokens and no horizontal overflow. They do not claim a real authenticated upload, OAuth, email delivery or provider streaming test.

The native adapter and narrow uploader guard were applied with source leases, PHP lint, private before/after backups verified off-VM, anonymous/CSRF denial checks and preservation checks. Existing media, catalog rows, queue, other handlers and container uptimes were preserved. No real uploads, thumbnail replacements or encoding jobs were started by deployment.

Private rollback states:
- `/srv/divinemedia/backups/creator-details-74fd0f4e5a68`: original adapter files, original native uploader, and the two newly added PHP helpers.
- `/srv/divinemedia/backups/creator-keywords-4c8d0233d8d2`: viewer policy projection and the previously empty tag-type table. Remove the Keywords type only if it has no links and its contents remain unchanged; never delete creator tags to roll back code.
- `/srv/divinemedia/backups/creator-categories-b79a365b52e2`: parent-ID projection only; no category data changes.
- `/srv/divinemedia/backups/creator-upload-rate-ce77657151c0`: bounded upload-chunk allowance; authentication limits unchanged.

Rollback code only against matching installed hashes; preserve later creator edits and uploads. Production Git and the production frontend remain unchanged; the updated experience is delivered as a Netlify feature preview.
