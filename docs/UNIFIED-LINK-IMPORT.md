# Unified link entry and native imports

Status: feature branch and preview, not a production activation. The existing live API continues to handle YouTube embedding; the new import actions, helper and native model hook must be deployed together before live imports are available. No real import, media download or encoding job was queued during implementation.

## Creator experience

`/creator/embed` remains valid and is now labeled **Add a video link**. The shared studio menu calls it **Video link**. There is one URL field:

- Automatic handling keeps supported YouTube videos/channels in the existing embedding workflow.
- **Import a copy through Encoder** explicitly chooses native importing, including for YouTube. Other enabled public providers use importing automatically.
- Preview happens before a queue write. The review exposes title, description, existing category and output profile. Confirmation creates a creator-owned private draft and a native Encoder job.
- The same card then offers processing-queue navigation and the existing metadata/thumbnail editor. Playback and additional encoding stay unavailable for the new placeholder until a source exists.
- Editing the URL or handling choice clears stale previews/selections. Completed items remain accessible in the studio. Existing file uploading is unchanged.

Uploading permission enables imports; native BulkEmbed permission independently controls YouTube embedding. No backend HTML page is opened, and no paid plugin replacement is created.

## Compatibility boundaries

The linked youtube-dl sites page describes download extractors, not universally available embedded players. The installed Encoder selects yt-dlp and its native output profiles. A site's presence in a list is not a successful availability check.

Initial enabled provider families: YouTube, Vimeo, Dailymotion, Twitch, SoundCloud, TikTok, Instagram, Facebook, X/Twitter, Reddit, Bandcamp and Internet Archive, including their listed aliases. The installed extractor must successfully preview the specific public video. This is not a claim that every listed provider or URL was tested or that all youtube-dl sites are enabled.

Only public HTTPS provider pages are accepted. Credentials/private access-token links, private/reserved network addresses, Generic scraping, playlists for importing, live streams and DRM metadata are rejected. YouTube channels retain the existing batch-embed path. Source/media hosts are checked; the backend's outbound-network policy must also be reviewed during native rehearsal. There is no login-cookie upload, provider OAuth flow or access-restriction bypass.

Sources known to exceed 12 hours or 4 GB are rejected from their metadata. That is not a hard downloaded-byte quota for sources with unknown/inaccurate sizes; native storage/download limits and worker operation still require rollout verification. The creator's native output/resolution permissions remain in force. Preview's output choices are validated again when the job is saved.

## API and queue contract

New POST actions: `link-preview` and `link-import`, through the existing same-origin, CSRF-protected gateway.

A preview is an expiring, creator-bound server ticket. Import accepts that ticket, not a client-supplied media URL, actor, catalog ID or Encoder connection. The server creates one private record and saves its ID in the ticket before queuing. The worker uses a deterministic filename and a per-creator DB lock to return the existing queue ID on retry. Each native streamer is limited to three pending frontend imports; the existing rate limits also apply.

The private CLI adapter reuses installed `Encoder`, `Streamer`, `Login`, `Format` and native profile selection. It does not call native `view/queue.php` because that handler creates records and dispatches the global queue. New code only saves the intended job; existing workers retain processing control. No global queue run, reencode, original-media replacement or container restart is part of this feature.

## Private draft hold

The installed receiver differs from this repository's historical receiver. Read-only inspection showed that its completion flow calls `Video::setAutoStatus`, which funnels into `Video::setStatus`. The native model setter is therefore the single guard point; the prototype receiver-specific approach was replaced before release.

`import-hold.php` stores server-owned markers under the already denied `videos/.divine-private/import-drafts/` directory. Records are marked before a job is queued. While a marker is present, the narrow model hook keeps automatic status changes private. Unmarked existing media retains native behavior.

A creator publication request checks the marker's exact native job ID, ownership and completed status before allowing the requested status and removing the marker. Unknown/missing job status fails closed. Retries retain the original draft and marker; deleting a job can require operator review before the hold can be released. Markers are persistent application state and must be included in private backups.

Required native patch: `ops/divinemedia/import_draft_hold.py`, applied only to the verified installed `objects/video.php` source. The patch is pure/idempotent and refuses an unknown setter signature. The installed source accepted it and the patched candidate passed runtime PHP lint during a read-only rehearsal. Nothing was written to the live model.

## Verification and remaining activation work

- 43 frontend tests, Vite build, and 21 Python backend tests pass.
- Disposable PHP tests cover URL/DNS and metadata restrictions; native-stub tests cover actor scoping, private override, job mapping, retries and pending limits; marker tests cover holding and explicit release.
- Synthetic desktop/mobile browser tests cover one field, mode detection, explicit confirmation, private-draft review, inline artwork editing, and preservation of YouTube embedding. Studio/permission and channel retry/player regressions pass.
- Read-only installed-worker previews succeeded for a public SoundCloud track; the public Vimeo sample returned provider unavailable. Neither attempt queued a job. The catalog/queue and container uptimes were unchanged in the preservation probe. Native queue, completion and publication checks remain activation requirements.
- Downloader diagnostics are bounded in memory and mapped to safe creator messages for sign-in blocks, missing runtime, certificate, timeout and configuration failures; raw provider output is never returned.
- Recorded native model fingerprint: `0232aed873b69fd44bb6a7c99b24ecf719970aaffa7468887139bf503b813c21`. Recompute a byte-level source lease immediately before any mutation; this recorded fingerprint is not permission to overwrite newer native source.

Before production activation, rehearse the native queue, completion callbacks, private hold and final publication with disposable records/storage and the installed classes; verify provider previews, worker processing and download/storage controls. Then create verified off-VM backups, apply the helper and leased model hook before exposing import actions, install the adapter files, and deploy the matching frontend. Do not start real imports merely to validate deployment.

Rollback: disable new import actions first. Restore only source files matching the deployment hashes. Retain the model guard, helper and markers while marked imports exist or are processing; removing them can let native automatic status handling publish an unfinished import. Never delete existing creator media or markers as a generic code rollback.
