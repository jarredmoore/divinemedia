# Native creator, channel and collection model

Decision recorded November 28, 2026. DivineCreative remains the main administrator/creator identity. Planet Derrty is managed by that administrator. Murphy Lee is the first artist whose page will be managed before artist access is enabled. Use AVideo's native identity, ownership, permissions and organizational objects as the source of truth.

## Verified native terminology

| Product concept | AVideo object | Meaning for Divine Media |
| --- | --- | --- |
| Administrator / creator / artist identity | Native `User` record | Login username, display name and `channelName` are separate fields on the same user. A native user has one channel identity. |
| Independent creator channel | The user's native channel/profile | Planet Derrty and an artist can have their own native identities while DivineCreative administers them. This does not require the administrator to maintain a second interactive login. |
| Program / playlist | Active PlayLists plugin and native playlist membership | Albums, ordered collections and cross-artist selections reference existing media records without copying the audio. A user can own multiple programs. |
| Series | Native PlayLists Series feature | A program can have a native library item with its own title, thumbnail, category and status. A Series is not a second login or a native user channel. |
| Category / subcategory | Native categories and parent relationships | Hierarchical content classification, separate from artist identity or access rights. |
| Tags / credits | Native tag groups plus existing media metadata | Descriptive discovery information; a featured performer credit does not create a creator account or grant ownership. |
| Access groups / administrative delegation | Native user groups and installed permission checks | Restrict access or delegate supported tasks. Do not use artist names or frontend profile mappings as authorization rules. |
| Audio, video and other assets | Native media records, uploader/Encoder and registered storage paths | Preserve native record IDs, source paths and visibility. The existing Azure delivery gate enforces file access. |

The installed `users` table has one `channelName`, profile photo, channel background and About field per user. `Video::canEdit` allows the native administrator or a permitted native video administrator, otherwise checks media ownership. `users_id_company` on videos is not proof that one user supports multiple independent creator-channel identities; no such capability was established in this audit.

## Current state — no implied provisioning

- DivineCreative is the existing native owner/administrator, user 1. Its native channel is not renamed.
- Planet Derrty's 31 recovered tracks are native records owned by user 1, held inactive/private, referenced by private playlist 372. The frontend channel entrance is a managed presentation of this collection, not a second native user/channel.
- Murphy Lee's custom artist page and the public 2nd Time Around program 129 do not establish a separate Murphy Lee native login. Current record ownership is preserved.
- `frontend/src/managed-channels.mjs` and the artist display configuration are presentation references only. They are not an identity database or permission source.
- The channel preview in PR 56 does not provision users, change native identity, transfer media, or activate artist sign-in.

## Native implementation boundary

For a true independent Planet Derrty identity and Murphy Lee creator channel, provision distinct native user/profile records through AVideo's user management, with DivineCreative retaining native administrative control. Keep artist access disabled until the approved native activation/verification flow is ready; do not invent email addresses, distribute passwords, send invitations or activate social providers as part of page styling.

Before connecting an artist login, verify the intended identity/contact, assign only the selected native media and programs through an authorized management workflow, and confirm that the artist can manage their own work while the administrator retains access. Shared Planet Derrty programs can reference artist-owned media; adding a track to a program must not change its ownership or access rules.

Expose management inside the existing frontend studio using native administration/ownership checks. An account/channel selector must not impersonate a user or grant access from a frontend ID alone. Extend the existing authenticated adapter where native controls are missing; do not build a parallel login or permission system. Normal uploads and Encoder intake remain the shared path.

## Official references

- [AVideo User Manual — profile/channel, programs and content privacy](https://github.com/WWBN/AVideo/wiki/User-manual)
- [AVideo Admin Manual — users, activation and native permissions](https://github.com/WWBN/AVideo/wiki/Admin-manual)
- [Programs, playlists and Series](https://github.com/WWBN/AVideo/wiki/Program-(Playlist)-to-series)

This is a verified model and implementation boundary, not a claim that the later artist-invitation workflow has been configured. No runtime users, media ownership or publication settings were changed by this audit.
