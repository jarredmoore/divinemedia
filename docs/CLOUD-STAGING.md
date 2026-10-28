# Divine Media — Cloud Staging Runbook
Updated 2026-10-28. Status: repository prepared; **not deployed**.

## Goal
Allow invited reviewers to browse Divine Media 3.0 and watch **real** AVideo uploads from outside the developer's Windows computer. Preserve local development and the existing branch.

## Target topology
- Frontend: HTTPS static host, built from `frontend/` on `divine-media-2`.
- AVideo: dedicated Linux cloud server running the matching upstream AVideo Docker stack, reachable via HTTPS, with persistent database and media volumes.
- API gateway: same-origin HTTPS reverse proxy or a small allowlisted server-side endpoint for the **public** catalog only. Never expose an administrative AVideo API or credentials to browsers.
- Reviewer gate: identity-aware access policy at the edge (email allowlist + one-time passcode/SSO); apply to the frontend **and** AVideo media/API origin, or use an access-controlled gateway with compatible playback. Test that MP4 range requests and embeds work under the gate.
- No payment processing on staging until security and entitlement checks are separately implemented.

## Frontend environment variables
`VITE_AVIDEO_ORIGIN=https://video-staging.example.com` — public AVideo origin used to validate catalog watch URLs. Replace example domain with the actual deployed backend.
`VITE_AVIDEO_CATALOG_URL=/api/public/videos` — public catalog endpoint proxied server-side to AVideo. The endpoint must return the AVideo API's `{error:false,response:{rows:[...]}}` shape. Do not expose secrets or user/session fields.
These variables are **public build-time values**; never put passwords, API tokens, or private keys in any `VITE_*` value.
Without variables, the local Vite proxy and https://localhost continue to work.

## Migration checklist
1. Select and provision hosting for the AVideo Docker backend and persistent storage; record expected bandwidth, storage and backup costs.
2. Export the existing AVideo database and upload/encoder storage volumes from the Windows Docker instance. Encrypt and securely transfer backups; do not put them in GitHub.
3. Restore to staging; confirm AVideo and Encoder work with public HTTPS hostnames and canonical URLs. Ensure public catalog rows emit staging URLs, not localhost.
4. Configure TLS, firewall, security updates, backups, upload limits and private administrative access.
5. Enable reviewer identity/access policy for the public preview and media/API paths; ensure the browser can request posters, streams, embeds and HTTP Range segments.
6. Publish a sanitized public-catalog proxy; only active public/unpaid titles should be visible. Validate AVideo privacy and paid flags on the server too.
7. Set frontend build variables; build from `frontend/` with `npm run build`, output `frontend/dist`; deploy.
8. Test from a separate phone on mobile data: sign-in gate, catalog, images, video/audio playback, seeking, browser refresh, creator filtering, search, and access denial for non-invited users.
9. Test no local-machine dependency: turn off local Docker and verify staging still works.
10. Document a rollback and remove temporary credentials after tests.

## Security notes
A staging access gate is not a paid-media entitlement system. Current frontend filters private/paid entries in JavaScript and is **not** suitable as a security boundary. Restrict the backend catalog and protect actual media URLs. AVideo source URLs and external embeds must be independently checked for access and licensing. Avoid exposing a self-signed local Docker service or opening your home router to the internet.

## Current limitations
- No cloud host, DNS record, reviewer identity provider or billing account has been configured from this repository.
- No database/video migration has been performed.
- Current frontend still includes illustrative sample cards; distinguish these from verified real catalog videos during review.
- The development proxy at `/avideo-local` is only for Vite development. It is not a production proxy.

## Local development
`cd $HOME\DivineMedia\avideo-current; docker compose up -d`
`cd $HOME\DivineMedia\divinemedia-v2; git pull origin divine-media-2; cd frontend; npm run dev`
