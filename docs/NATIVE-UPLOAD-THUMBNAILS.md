# Native upload still covers

The direct-upload handler invokes native AVideo upload hooks but does not run the Encoder's image-extraction step. A direct MP4 can therefore be published and playable while its expected JPEG cover does not exist.

DivineThumbnails is a small native upload hook. It queues a missing cover after a completed local video upload or Encoder completion, and reuses the installed Encoder::getImage helper in a separate CLI process. The helper reads one frame roughly 10% into the video, capped at ten seconds. It does not dispatch the Encoder queue, convert the video, generate GIF/sprite previews or replace a paid plugin suite.

Native Video methods resolve local media and the expected JPEG path. Jobs live outside the webroot. A locked, bounded background worker publishes a validated JPEG atomically without replacing an existing cover. Native Scheduler's minute hook provides another queue-processing opportunity. Failures retain the video and do not make its upload fail; exhausted jobs are set aside after three attempts.

Existing JPEG/PNG/portrait covers and audio artwork are preserved. Local MP4/WebM sources are supported; remotely stored sources are skipped, and other formats depend on the normal Encoder producing a supported local source. Custom covers remain authoritative. No old-catalog thumbnail sweep is performed: the only manually queued existing video is the requested St. Louis Sound Highlight Reel, ID 19.

CLI worker and cache-maintenance files reject HTTP execution. Queue input uses native/server-selected paths, fixed safe temporary filenames and local storage checks. Native extraction runs outside the web request with a 45-second process timeout and a single worker lock. Cover publishing stages its output on the destination filesystem so separate temporary and media mounts are supported.

Verification uses a restored, isolated application: upload a new generated MP4 through the real native handler, wait for its automatic JPEG, check a second invocation preserves that cover, check audio is skipped, and compare all original restored media hashes. Deployment requires those tests to pass and checks staged/native source hashes. Before/after private snapshots are round-trip verified off VM. Existing catalog rows, permissions, queue entries, video/media files, covers and container uptimes are compared around activation.

Rollback disables/removes only the new plugin record and unchanged plugin files. Keep generated covers and all user-created application data; never restore the full database to undo this hook.

## Enabled deployment

DivineThumbnails is active on Azure. Video 19 now has a publicly accessible JPEG cover (81,225 bytes), confirmed through the frontend API and media URL. Installation preserved all 119 existing media/artwork files, catalog rows, permissions, Encoder queue and container uptimes, and all 1,390 audited native PHP source files. Private before/after snapshots were round-trip verified off VM. No frontend deployment or production Git merge was needed. See the stage, deployment and public-verification JSON reports next to this document.
