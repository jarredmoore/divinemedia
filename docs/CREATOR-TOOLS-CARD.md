# Unified creator entry

The frontend upload icon now opens one Creator Studio card at `/creator`. Uploading, YouTube single/channel embedding, live preparation, video management, encoding output/queue, playlists, live browsing and account/profile controls use the existing frontend views. The upload icon remains visible on mobile in both Code Black and Cozy. Creator screens provide a return button to the same card; direct URLs remain valid.

The native menu's Articles, browser-camera broadcasting, Live Links, Meet and local Encoder options are represented with a clear Not available yet state. Vimeo/additional embed providers are represented the same way. These entries do not launch native backend pages or imply that an enabled native plugin is already integrated into React. YouTube single and bulk/channel embedding share the existing importer rather than duplicate workflows.

Available actions follow account permissions and current Live/Playlists capability flags. A small read-only permission projection now exposes BulkEmbed's native permission decision as `user.permissions.embed`, rather than assuming upload permission also grants bulk embedding. This projection was applied with an exact source lease, PHP lint, verified private off-VM backups and preservation checks. No media, catalog, queue, other handlers or service uptimes changed. Rollback source: `/srv/divinemedia/backups/creator-card-991e76b8e25a`.

Browser fixtures cover creator, restricted and anonymous sessions, 1440/390/320px widths, both themes, one-card navigation, unavailable actions, permission gating, Escape close, no backend navigation and horizontal overflow. Fixtures do not authenticate real accounts or start upload/broadcast/encoding jobs. The frontend build, 32 Node tests and 19 Python backend tests pass. Production Git/frontend remain unchanged; use the feature preview for review.

Review preview: https://6aff2945e8fd2bd858ffbcab--mediaproduction.netlify.app/creator

PR: https://github.com/jarredmoore/divinemedia/pull/31

## Ambient card treatment

The Creator Studio card uses the reusable `dm-ambient-stroke` treatment: a masked one-pixel cyan/blue/purple/pink/green gradient rim with an 18-second alternating animation. It does not overlay content or intercept pointer input. Reduced-motion mode displays a static gradient; browsers without composite masks retain a cool static border. Forced-colors mode uses the system border.

Overlay scrolling follows a shared `dm-scroll-clean` convention: no visible scrollbar, thumb or track, while native wheel, touch and keyboard scrolling remain intact. This convention also covers workspace, video, native-style and install dialogs. Forced-colors mode restores native scrollbar chrome. Future scrolling overlay components should reuse this treatment.

The ambient update is a frontend preview only; no backend or production settings change.

Ambient-stroke preview: https://6aff32097bcf8e79272f6fd8--mediaproduction.netlify.app/creator ([PR #32](https://github.com/jarredmoore/divinemedia/pull/32)). Served CSS matches the verified build.
