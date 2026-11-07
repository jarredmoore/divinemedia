# Divine Media domain migration

## Approved destination structure

| Destination | Role |
| --- | --- |
| `https://divinemedia.us/` | Canonical Watch frontend on Netlify |
| `https://www.divinemedia.us/` | Netlify-managed redirect to the canonical frontend |
| `https://media.divinemedia.us/` | AVideo entrance and media backend on Azure |
| `https://media.divinemedia.us/user` | Existing native account login |
| `https://media.divinemedia.us/upload` | Existing native direct upload |
| `https://media.divinemedia.us/Encoder/` | Existing Encoder connection and workspace |

The previous Watch hostname redirects to the new frontend with its path/query preserved. The previous media hostname remains a supported HTTPS alias for existing media URLs, embeds, callbacks, and older clients. Do not indiscriminately redirect upload POSTs or credential-bearing Encoder URLs between hosts. Sessions remain host-specific; users sign in on the new media hostname.

## Source and scope

Branch `feat/divine-media-3.3-domains` integrates the already-developed audio, entrance, and creator-workspace feature branches before applying domain changes. It does not merge or modify `production/divine-media`.

`frontend/shared/domains.mjs` defines the public origins. The catalog adapter and frontend normalize only the explicitly trusted old/new media hosts, preserve media paths, and reject foreign hosts and URL credentials. Backend presentation links use the new Watch domain. No video rows, media bytes, thumbnail processing, or encoding jobs are migration targets.

## Hosting inventory before migration

- Existing main-domain site: `mediaproduction`, ID `74211341-4673-4a96-8a18-927fffe55e91`; primary hostname `www.divinemedia.us`; old mockup deploy `5df0740e8350b4ec783ddfd5`.
- Existing Watch site: `divinemedia-staging`, ID `b4e427bb-d612-415c-8458-e24423a9f1ec`; primary hostname `watch.divinecreativegroup.com`; deploy `6aeea28ede7b2dcf0123b163`.
- Main domain DNS is managed in Netlify. Existing apex/www and email records remain intact. New `media` A record points to the existing Azure backend IP with a 300-second TTL.
- The old Watch site is associated with the production Git branch. Any future automated build changes must account for its retirement as a public frontend.

Private provider exports and backup/configuration snapshots belong outside Git. Public deploy IDs are rollback references, not credentials.

## Cutover sequence

1. Record current published deploys, DNS, certificates, source hashes, and backend configuration. Verify recovery coverage and create a private current-state snapshot before backend changes.
2. Add only the new media DNS record. Issue a certificate covering both media hostnames, validate Apache configuration, and gracefully reload HTTPS without restarting containers.
3. Verify new/old host access to the same backend, API, MP3/MP4 range responses, and native login/Encoder routes.
4. Update the two backend public base URLs and branded presentation links with hash-checked backups and rollback. Keep legacy media access working; preserve all existing media and queue state.
5. Build the committed frontend, deploy a Netlify draft with its catalog function, and validate catalog, artwork, playback, login links, and mobile rendering.
6. Publish the verified draft to the existing main-domain site. Set `divinemedia.us` as primary, retaining `www` as an alias/redirect. Avoid an apex/www redirect loop during the transition.
7. Publish the tracked `frontend/legacy-watch/_redirects` artifact on the old Watch site after the destination passes. Preserve its previous deploy for rollback and prevent an automatic legacy build from replacing the redirect.
8. Record final deployment IDs, source commit, certificates, DNS, redirect checks, catalog/media/handler hashes, and recovery instructions. Update repository-facing links after verification.

## Rollback

Restore the original Netlify deploys on their respective sites and the prior main-domain primary/alias settings. Restore any changed legacy build setting. The new DNS record is additive and can be removed by its recorded ID after clients no longer use it.

Restore backend configuration and presentation files only if their installed hashes still match the migration plan; retain the original certificate and vhost snapshot. Validate Apache before a graceful reload. Do not restore whole databases or media directories to undo a hostname change.

## Build and tests

Use `npm ci`, `npm test`, and `npm run build` in `frontend/`. Both `VITE_AVIDEO_ORIGIN` and server-side `AVIDEO_ORIGIN` can explicitly select the old approved media origin for a controlled fallback. Production defaults target the new domain; do not publish until its HTTPS and backend checks pass.
