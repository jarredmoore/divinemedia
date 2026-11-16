# Divine Media architecture

**One public experience: https://divinemedia.us.** Viewers and creators stay in the React/Vite frontend for playback, accounts, sharing, comments, reactions, playlists, discovery, uploads and Live. Do not send users to AVideo pages or embed its full HTML interfaces as substitutes for frontend features.

AVideo on Azure is the existing application backend. It remains the authority for account credentials, permissions, media visibility, categories, channels, playlists, interactions, uploads and processing. Its semi-branded administration is retained for private operator use. It is not a second viewer or creator website.

See [the exact deployment diagram](docs/UNIFIED-FRONTEND-ARCHITECTURE.md) for the current device-testing release, including the still-accessible legacy HTML routes.

## Boundaries

| Component | Responsibility |
| --- | --- |
| React/Vite on Netlify | All viewer and creator presentation, navigation and controls |
| Same-origin /api/platform/* functions | Attest frontend origin, forward only supported actions, hold the server gateway secret, and issue the HttpOnly frontend session cookie |
| Azure divine-api adapter | Project safe JSON using installed native AVideo classes/handlers; enforce native permissions and a session-bound CSRF nonce |
| Existing AVideo, Encoder and stream server | Accounts, persistence, access policies, media processing, streaming and administration |
| media.divinemedia.us | Technical API/media origin; native HTML routes become frontend redirects at the verified cutover |

The API boundary shares the native AVideo session store. It introduces no account, comment, reaction or playlist database. Passwords go only to the server/native authentication path. Native login responses, password hashes, API secrets and credential cookies are never relayed to browser JavaScript. Sessions use an opaque __Host-dm_session cookie with Secure, HttpOnly, Path=/ and SameSite=Lax.

AVideo plugins can attempt request-based authentication during initialization. The adapter suppresses that path and uses a nested server request envelope, then explicitly authenticates only after its own CSRF check. Origin checks and native role/ownership checks apply independently.

## Migration and delivery

Implement and verify authenticated video interactions first, then creator operations and callback compatibility. Do not remove working processing or lock creators out while replacements are incomplete. Frontend controls must report service errors without opening native backend pages.

The frontend has its own /watch/:id and /embed/:id pages. Media bytes can come from the technical media origin; no native HTML player, login, notifications, upload or Encoder page should be presented to users.

Use isolated fixtures for authentication, comments, playlists and uploads. Check session rotation, rejected-login side effects, cross-user ownership, moderation, private media, creator grants and existing media preservation. Never run the native startup entrypoint or reencode existing videos during this integration.

GitHub is source of truth. Work is delivered on feature branches and pull requests, with a verified Netlify preview and deployment/recovery evidence. Never modify or merge into production/divine-media without owner approval. Production cutover follows verification and review; keep a rollback reference to the previous frontend and any backend boundary changes.
