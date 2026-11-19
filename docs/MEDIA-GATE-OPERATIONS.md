# Azure media gate operations

Implementation branch: `security/azure-media-gate`. Activation requires the isolated native rehearsal and a backed-up, reversible rollout. Until the deployment evidence is recorded, do not describe the live origin as protected.

## Request paths

`/videos/*`, the guarded `/divine-media/assets/*` alias, native XSendFile/HLS/key aliases, and live `/hls/live/*` resolve through one PHP boundary on Azure. Exact native catalog names and closed derivative scopes establish ownership; unknown paths, scripts, private configuration, traversal and symlink escapes fail closed. Public branding/profile/category imagery has a separate explicit allowlist.

The boundary invokes AVideo visibility, group, password and plugin checks. An editor may preview their inactive draft; this does not make that draft public. Authorized byte bodies use the existing Apache XSendFile module. Private responses cannot inherit legacy public cache headers. HLS manifests expose only guarded references, and every segment/key request is authorized again. Unsupported manifests fail closed rather than redirecting to an unchecked source.

Frontend login obtains a CSRF-protected, single-use 120-second handoff. A credentialed cross-origin POST exchanges it for an opaque host-only, Secure, HttpOnly, SameSite=Lax media cookie. A follow-up check verifies the browser accepted the cookie. The server-side record binds it to the native session and its CSRF identity, expires after eight hours, and becomes unusable when native logout destroys the session. No native session IDs, passwords or gateway secrets appear in media URLs. Native operator cookies continue to work.

Requests through a Netlify preview may be blocked by browser third-party-cookie policy. Do not weaken production cookies to hide that limitation. Canonical `divinemedia.us` and `media.divinemedia.us` are same-site. Test actual target browsers after activation.

## Encoder and live origins

Encoder's existing local-file copy path handles authorized creator jobs. A browser never supplies an arbitrary path: the main adapter checks native edit permission, resolves a catalog-associated local audio/video source, and passes the canonical path through the private CLI boundary. The worker checks the storage root and allowed extensions again. The native downloader must preserve the original when copying and cleaning its temporary output; the isolated rehearsal tests that contract. No public/private URL exemption or second listener is required. Public HTTP access to Encoder's temporary media directory is denied.

Direct live-origin HTTP delivery is denied. RTMP remains available for authenticated publishing and trusted local processing; external RTMP playback must not bypass the HTTPS gate. Preserve all existing ingest callbacks and thumbnail/recording hooks. No global Encoder queue, reencode task, original-media movement or production fixture creation is part of installation.

Password-protected live streams currently fail closed until a verified frontend live-password unlock is integrated. External YouTube/Vimeo privacy is still controlled by the provider. A private Divine catalog page cannot privatize an externally public source. This gate does not provide DRM or revoke bytes a viewer already received.

## Rollout and rollback

1. Rehearse the exact candidate with disposable databases, accounts, media and streams in an internal Docker network. Never run the production container entrypoint; it invokes global reencoding.
2. Record source/config leases, create private backups and verify their off-VM copy before changing live routing.
3. Install the session endpoints and adapter first; deploy the matching frontend handshake; then enable the file/live guards together. Validate Apache/nginx configuration before graceful reloads. Do not restart containers.
4. Check public range requests, anonymous private denial, legacy aliases, cache/CORS headers and alternate protocols/ports. Retain the previous frontend deploy and exact origin configs for rollback.
5. Keep actual media URLs, cookies, grant plans, native logs and fixture credentials out of Git and user-facing reports. Record only case IDs, statuses and content-preservation evidence.

Rehearsal tools: `ops/divinemedia/stage-media-gate.py`, `media-gate-stage-tests.py.txt`, `test-media-delivery.php`, `tests/media-gate-routing.py`, and frontend tests. The read-only production probe is `ops/divinemedia/check-media-access.py`. A build or mock-browser pass alone is not a security release result.
