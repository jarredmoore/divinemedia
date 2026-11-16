# Native upload still covers

The direct-upload handler invokes native AVideo upload hooks but does not run the Encoder's image-extraction step. A direct MP4 can therefore be published and playable while its expected JPEG cover does not exist.

DivineThumbnails is a small native upload hook. It queues a missing cover after a completed local video upload or Encoder completion, and reuses the installed Encoder::getImage helper in a separate CLI process. The helper reads one frame roughly 10% into the video, capped at ten seconds. It does not dispatch the Encoder queue, convert the video, generate GIF/sprite previews or replace a paid plugin suite.

Native Video methods resolve local media and the expected JPEG path. Jobs live outside the webroot. A locked, bounded background worker publishes a validated JPEG atomically without replacing an existing cover. Native Scheduler's minute hook provides another queue-processing opportunity. Failures retain the video and do not make its upload fail; exhausted jobs are set aside after three attempts.

Existing JPEG/PNG/portrait covers and audio artwork are preserved. Version 1.1 also handles local MP3/OGG/M4A/WAV/FLAC audio sources: embedded artwork first, an explicitly registered artist+album match second, otherwise a native waveform JPEG. Audio covers are reduced to at most 720 pixels where GD is available. Local MP4/WebM video sources retain the existing frame-extraction path. Remotely stored sources are skipped, and other video formats depend on the normal Encoder producing a supported local source. Custom covers remain authoritative. No old-catalog thumbnail sweep is performed: the first manually queued existing video was the requested St. Louis Sound Highlight Reel, ID 19. The audio repair additionally targets only the eleven new audio uploads, IDs 20–30.

CLI worker and cache-maintenance files reject HTTP execution. Queue input uses native/server-selected paths, fixed safe temporary filenames and local storage checks. Native extraction runs outside the web request with a 45-second process timeout and a single worker lock. Cover publishing stages its output on the destination filesystem so separate temporary and media mounts are supported.

Verification uses a restored, isolated application: upload a new generated MP4 through the real native handler, wait for its automatic JPEG, check a second invocation preserves that cover, check audio is skipped, and compare all original restored media hashes. Deployment requires those tests to pass and checks staged/native source hashes. Before/after private snapshots are round-trip verified off VM. Existing catalog rows, permissions, queue entries, video/media files, covers and container uptimes are compared around activation.

Rollback disables/removes only the new plugin record and unchanged plugin files. Keep generated covers and all user-created application data; never restore the full database to undo this hook.

## Enabled deployment

DivineThumbnails is active on Azure. Video 19 now has a publicly accessible JPEG cover (81,225 bytes), confirmed through the frontend API and media URL. Installation preserved all 119 existing media/artwork files, catalog rows, permissions, Encoder queue and container uptimes, and all 1,390 audited native PHP source files. Private before/after snapshots were round-trip verified off VM. No frontend deployment or production Git merge was needed. See the stage, deployment and public-verification JSON reports next to this document.

## Audio upload repair

The reported missing covers were audio uploads, not failed video jobs. Inspection found the 1.0 plugin active with no failed/pending jobs; it explicitly returned before queuing audio. Ten new MP3s had artist Murphy Lee and album 2nd Time Around, but no embedded picture. Handle It had neither artist/album tags nor an embedded picture.

Version 1.1 recognizes exact normalized artist+album metadata against album-covers.json; it does not infer identity from filenames or track titles. The registered 2ndTimeAround.jpg is the existing frontend artwork, downloaded once during staging and verified against its pinned SHA-256. It is packaged under the plugin's covers directory at deployment; the worker does not fetch arbitrary URLs or contact external cover services. Unmatched audio gets a deterministic waveform through native Encoder::getSpectrum. Embedded artwork is extracted as a still image without the video timeline-seeking step.

The worker now schedules another bounded batch after releasing its lock when pending jobs remain, so more than eight uploads drain without waiting for Scheduler's next minute. Existing covers remain untouched. The isolated regression checks native video uploads, waveform fallback, tagged-album selection, embedded art, preservation, and a nine-job audio batch with one initial kick.

The upgrade is leased against the installed 1.0 plugin hashes and native sources, with private off-VM before/after snapshots. It changes only the thumbnail hook/configuration and missing covers for the reviewed audio IDs; audio bytes, video bytes, publishing states, account permissions, the Encoder queue and container uptimes are verified unchanged.

### Verified audio rollout

Plugin 1.1 is active. Public HTTP and hash checks passed for all eleven repaired covers: IDs 20–29 use 720px album artwork (106,249 bytes each), and ID 30 uses a waveform cover (26,256 bytes). All 133 existing media/artwork files were preserved. Catalog content, permissions, Encoder queue, container uptimes and native core sources were unchanged. Private upgrade snapshots were verified off VM; deployment state is /srv/divinemedia/backups/audio-cover-upgrade-4cc94d09b447. No Netlify release or production Git merge was needed. The earlier 1.0 deployment section is historical.
