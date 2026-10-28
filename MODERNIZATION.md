# Divine Media 2.0 — Modernization Plan

This branch is the isolated development workspace for the Divine Media streaming relaunch. The legacy application remains intact on `master`.

## Strategy
- Preserve the original AVideo code and history for comparison.
- Use a current, supported upstream AVideo release for a **separate** streaming backend. Do not run the legacy PHP 7 Dockerfile in production.
- Build a modern, responsive interface incrementally. Start by evaluating AVideo's Flix layout and supported theme/CSS customization; use Next.js/React only where justified.
- Keep credentials, media files, and databases outside Git. Never commit environment secrets.
- No production deployment or domain cutover until upload, encoding, playback, moderation and security tests pass.

## Proposed architecture
- **Streaming backend:** current AVideo, database, private encoder, media storage.
- **Frontend:** branded Flix theme first; optional separate Next.js app consuming documented AVideo API/embed interfaces.
- **Infrastructure:** local Docker Compose development; later Azure Linux VM with persistent storage and HTTPS.
- **Monetization:** evaluate current plugin licenses, subscriptions, ad serving, creator accounting and payout workflows before implementation.

## Milestones
1. Inventory old customization, plugins, media dependencies and database compatibility.
2. Build a fresh local stack from a pinned upstream AVideo release; document reproducible startup.
3. Test creator signup, channel ownership, uploads, encoding, VOD playback, mobile viewing and live stream.
4. Establish design tokens, icon system, responsive navigation, browse, creator channel and watch-page UI.
5. Validate copyright reporting/DMCA workflow and creator approval before public uploads.
6. Test monetization, subscriptions and revenue accounting with sandbox transactions.
7. Benchmark Azure costs and deploy a staging instance; preserve old system access separately.

## References
- Legacy code: https://github.com/jarredmoore/divinemedia/tree/master
- Modernization branch: https://github.com/jarredmoore/divinemedia/tree/divine-media-2
- Upstream AVideo: https://github.com/WWBN/AVideo
- Upstream setup: https://github.com/WWBN/AVideo#quickstart-docker-compose

## Safety
The new branch initially contains the legacy snapshot, not an upgraded application. Its existence does not mean the current code is secure or running.
