# Divine Media 3.3 audit and implementation plan

Baseline: `dev/divine-media-3.1` at `4860459c`. Production is `production/divine-media`; no production merge or deployment is authorized.

## Findings and priorities

1. Complete MP3 discovery: the public API currently returns seven audio entries with `sources` containing `audio/mpeg`. The Netlify function discarded those sources and unnecessarily scraped public HTML. Prefer validated source URLs, retain the legacy fallback, and remove the frontend ID 16 stream override. Regression-test new IDs, rejected origins, privacy filtering, and upstream failures.
2. Playback: selecting a track and previous/next only changed selection. Start selected tracks, advance on end, preserve volume, display playback errors, and verify seek and mute restoration. Scope Murphy Lee artwork to the known album entries (10–16), preserving posters for future audio uploads.
3. Mobile: the single-row dock could exceed narrow phone widths. Use two rows with all controls accessible.
4. Builds: commit a dependency lockfile, use `npm ci`, and run catalog regression tests before Vite builds in GitHub Actions.
5. Deployment: open a feature PR against development, inspect Netlify status and preview API, artwork, desktop/mobile playback. Do not infer Netlify's production branch from GitHub's default branch (`master`). The repository's older architecture/README branch descriptions are historical; the adopted development workflow and user instructions govern.

## Validation boundaries

Local fixture tests and browser tests use sanitized public catalog fields. Public API inspection is read-only. No uploads, encodes, thumbnail jobs, media deletions, or Azure configuration changes belong to this frontend release. Browser automation can establish decoding and control state, but physical iOS/Safari playback and hardware volume require device review.

## Phase 2 — separate read-only investigation

Treat `vm-divinemedia-staging` as potentially production-serving. Establish subscription/resource group, VM SKU, disks, DNS and traffic before deciding staging requirements. Collect CPU history, memory metrics or guest observations, filesystem capacity/inodes, service/container map, storage growth, backup policies and most recent restore evidence, plus current and forecast costs. Compare an isolated staging environment against resource headroom and minimum runtime requirements. Do not resize or stop resources during the audit.

Investigate Upload/Encoder independently: inventory versions, service health, configured public URLs, queue/error metadata, and existing backup/rollback references. Avoid submitting uploads or encoding jobs and do not touch existing videos or thumbnail processing. Backend changes require separate approval, backup and rollback per the adopted workflow.

This environment has no configured Azure or Netlify identity. Connected GitHub and public HTTP evidence can validate checks/previews; subscription costs, VM metrics and Netlify dashboard settings require authorized account access. Never put credentials in this document or frontend variables.

## Phase 1 verification evidence

- Clean `npm ci`, four catalog regression tests, and production Vite build pass. Initial GitHub Actions PR build also passed.
- Read-only live catalog inspection found 16 public entries, including seven audio sources. Passing that public response through the updated handler yields seven playable audio entries without HTML requests.
- Chromium decoded and played the downloaded public MP3. Automated checks passed for artwork loading, volume adjustment, mute/unmute restoration, seeking, previous/next playback, and control bounds at 320, 375, 390, 768 and 1440 pixels. Browser media requests used a local copy of that MP3; this establishes frontend behavior, not preview network delivery or physical-device audio output.
- Direct Node fetch from this workspace timed out (the shell HTTP client uses the environment proxy successfully). Live function execution in Netlify must still be checked.
- The live frontend responds with Netlify headers. At initial PR inspection, GitHub showed the Actions build but no Netlify status, deployment or preview comment. This does not establish whether Deploy Previews are enabled or the site is linked to this repository. Site dashboard settings and production deploy/source mapping remain unverified.
