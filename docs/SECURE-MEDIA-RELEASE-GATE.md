# Secure media delivery release gate

Status: Azure gate activated on November 19, 2026 (America/Chicago). PR #36 supplies the implementation; the follow-up fixes enforce it at Apache server scope above native child-directory rules and explicitly deny unpublished states to non-editors. Production smoke checks pass.

## Release state

Approved feature PRs #27–#34 are merged into `production/divine-media` at `884c152625d4620e8dbe30e7ed8bffa5041f56a7`. Its application tree matches the tested Studio feature. The documentation-only taxonomy proposal remains unapplied to the catalog. Older unrelated PRs were not merged.

The owner-approved Studio release is live as Netlify deploy `6aff8200cde8a464895f94cc`, with production Git at `c272e5178640728211a4aa6f2c22c4806dea151b`. Earlier deploy IDs above were part of the previous hold. The new Azure gate is a separate release and remains under verification. No protected files have been moved or deleted, no blanket media deny rule was activated, and no container was restarted by this audit.

## Confirmed gap

An anonymous request for a nonpublic record's API metadata returned HTTP 404. The same record's direct artwork URL returned HTTP 200. The private URL is deliberately omitted here. This demonstrates that hiding a catalog record does not secure every associated asset. A failed check on artwork is not evidence that every private video/audio path has already been tested.

The current native catalog has nonpublic external embed/link records. Public/unlisted external media remains governed by its provider: making the Divine catalog entry private cannot make a public/unlisted YouTube source private. Site-controlled private delivery requires a protected source and authorization at the delivery layer. Unlisted is discoverability behavior, not authentication.

## Native capability audit

- Apache's `xsendfile_module` and rewrite module are loaded.
- SecureVideosDirectory is not installed and has no native plugin row.
- The videos directory has existing PHP restrictions, but no recognized secure-video/token guard.
- Live, LiveLinks and WebRTC are active. Their presence is not proof of protected private playback.
- Current native secure-source hooks mention MP4/WebM/M3U8/PDF/ZIP. That hook alone does not prove MP3/image coverage or live-origin segment protection.

## Delivery implementation decision

The owner selected a first-party delivery boundary on November 19, 2026 to cover the broader all-media requirement. No paid module purchase is needed for this direction. AVideo remains the account, catalog and permission authority; this is not a second identity system or replacement plugin suite.

See [protected delivery design](PROTECTED-DELIVERY-DESIGN.md). The implementation is staged: session cleanup first, then origin authorization and efficient serving, then all-asset/live integration and bypass closure. The existing file privacy gap remains open until the acceptance matrix passes. No protection activation or container restart was performed.

## Acceptance matrix

| Area | Required behavior |
| --- | --- |
| Session/workflow | Login persists through Studio, upload, metadata, thumbnails, libraries and playback; logout/session expiry revoke private access |
| Public | Guests can access intentionally public records and supported media; seek/range/playback remain functional |
| Unlisted | Hidden from discovery according to native policy; UI does not call a shareable unlisted URL private |
| Private | Owner and authorized viewers succeed; guests and unrelated accounts fail at both metadata and delivery endpoints |
| Direct URL bypass | Raw paths, copied URLs, spoofed referrers and expired grants do not bypass private access |
| Audio/video | Original files, alternate encodings, range requests, captions and downloads follow native permission decisions |
| HLS/live | Manifests, segments and encryption keys (when used) are protected; gating only the first manifest is insufficient |
| Images/documents | Original images, landscape/portrait art, derived thumbnails and PDFs follow the associated record's privacy |
| External embeds | Explain the provider boundary; do not advertise Divine-only private delivery for an externally public/unlisted source |
| Operator/backend | Creator-facing flows remain on the frontend; native authorization and operator access stay intact |
| Caching | Private responses never enter shared caches; storage/proxy alternate paths cannot bypass the guard |

URL expiration and domain/referrer whitelists alone do not prove session-bound access. Confirm the threat model with full copied URLs, a logged-out browser, an unrelated logged-in account, logout/revocation and token expiry. Authorized public links and native operator workflows must keep working.

## Read-only check harness

`ops/divinemedia/check-media-access.py` accepts a private 0600 plan outside Git containing test URLs and optional private cookie-jar paths. It sends byte-range GETs, verifies TLS, follows no redirects, and logs only case IDs and HTTP statuses. It does not create sessions, upload content, enable plugins or start broadcasts. Complete required cases are mandatory for a passing result; missing cases block the release. Reports are also private because results can identify configured cases.

Example command (the plan contains real URLs/cookies and must never be committed):

`python3 ops/divinemedia/check-media-access.py --plan /private/path/plan.json --report /private/path/report.json`

The harness is one part of verification. It cannot replace browser testing of seek, long playback, cookie behavior, logout and live segment/key access. Synthetic public/private fixtures should be prepared in isolation or with explicitly authorized test content before making destructive or visibility-changing changes to existing records.

## Next implementation sequence

1. Implement session cleanup and prevent late account responses from restoring stale private UI.
2. Build the native origin boundary and frontend-to-origin session exchange in isolation, reusing AVideo permissions.
3. Integrate catalog-associated artwork/audio/video/documents plus live manifests, segments and keys; close raw and alternate-origin paths only after rehearsal.
4. Run the full matrix, including copied URLs, expiry, logout and actual browser cookie/range behavior.
5. Promote only the verified candidate, retaining the previous deploy and origin configuration for rollback.

Vendor documentation: https://github.com/WWBN/AVideo/wiki/SecureVideosDirectory-Plugin

## Activation evidence

- Netlify frontend: `6affa1537fb77d3ce2c60c61` at `https://divinemedia.us`.
- Azure rollback state: `/srv/divinemedia/backups/media-gate-deploy-04335f61a552`; before backup verified off VM.
- Existing media hashes, catalog and Encoder queue preserved; containers not restarted and native startup not invoked.
- Production public MP4/MP3 range requests: HTTP 206 with no-store. The previously exposed nonpublic artwork: HTTP 404 anonymously. Hidden storage/Git and Encoder media aliases: HTTP 403. Homepage and session API: HTTP 200.
- Full isolated native rehearsal passed login/grant replay, public/private video/audio/image/PDF ranges, owner/unrelated/guest access, VOD group grants and revocation, actual encrypted HLS keys/segments, raw RTMP denial, Encoder copy/cleanup preserving originals, and logout revocation.
- Additional regression: 17 cases cover nonpublic states even when the native watch helper is permissive. Native child `.htaccess` is now copied into future rehearsals; server-scope routing prevents it from bypassing the guard.

Browser/device testing remains appropriate after refreshing the app. Password-protected Live and authenticated private casting need their separate frontend/device flows; external provider privacy and already-delivered bytes remain outside this gate's control.
