# Media management refinement — November 25, 2026

Released November 25 through PR #43. Netlify production and the two scoped Azure adapter files are updated. Native catalog rows, playlists, media files, encoding jobs and service uptimes were preserved. See [release verification and rollback reference](MEDIA-MANAGEMENT-RELEASE.json).

## Frontend changes

- Cozy gets 26px black play glyphs and at least 48px targets on transport/cover actions; Code Black keeps its existing treatment.
- Category browsing uses thumbnail cards from matching loaded public catalog artwork, with a branded placeholder where none is available. This does not upload or mutate native category artwork.
- Your Media, category/channel results, playlist collections and playlist entries paginate locally in groups of 12. Counts explicitly describe **loaded** records; existing server-side catalog/playlist limits remain. This is not a claim of unlimited catalog traversal.
- Playlists use the same cover/record style as Your Media. Entries have thumbnails, existing move-up/down controls, and desktop drag/drop reordering through the existing `playlist-order` endpoint. Touch and keyboard users retain the explicit controls.
- `Links & embedding` is available in management rows, after confirmed uploads and in viewer actions where sharing is allowed. It offers canonical watch/embed URLs, iframe code, a native authorized media URL when supplied by the API, and the YouTube source for external embeds. Private URLs still require authorization. No YouTube stream extraction or new public file route is introduced.

## Square

The account menu links to `/shop`, an on-site workspace card containing the fixed public storefront `https://divinecreativegroup.square.site/`. The frame cannot navigate the top-level Divine Media page; Square popups and an explicit new-tab fallback remain available for provider checkout requirements. Divine Media does not collect card numbers or implement a new payment backend.

This is a storefront integration, not a Square Web Payments SDK implementation or proof that every payment method works inside an iframe. Browser cookie policy, wallet/domain requirements and provider frame restrictions can require checkout outside the frame. No transaction, subscription or entitlement was created or tested.

The public storefront returned HTTP 200 during the read-only check. The real Chromium frame check hit `ERR_CERT_AUTHORITY_INVALID` in this managed browser. The product does not disable certificate verification. Browser fixtures verify the card, fixed origin, fallback and sandbox; merchant-side/device checkout testing remains required.

## YouTube metadata

`youtube.php` requests `statistics` with supported API previews and supports an explicit creator-record refresh. Public view, like and comment counts are allowlisted; tags, publication date and duration are exposed as source metadata. Zero counts remain distinct from missing counts. Private or non-embeddable sources are rejected. Single-video oEmbed and channel feed fallbacks still work without usable API quota, but do not fabricate missing statistics.

Snapshots are labeled **YouTube** and remain separate from Divine Media reactions. Share counts require authorized YouTube Analytics access; this change adds no creator OAuth grant or share-count sync. Source tags/descriptions are not automatically written over creator edits. Refresh is on demand, not a scheduled background job, and snapshots are not persisted as a separate analytics database.

Backend rollout completed: `backend/frontend-api/youtube.php` and `creator-details.php`. These files were linted/tested in a disposable PHP container with networking disabled. They were applied to Azure with matching-source checks, verified off-VM before/after backups, runtime PHP lint, anonymous authorization checks and preservation checks. Two earlier verification attempts restored their matching original sources automatically; the successful rollout uses the existing persistent protected gateway configuration. No credentials were exposed or changed. Authenticated creator refresh against the live YouTube key/quota remains a user acceptance check.

## Verification

- 42 frontend Node tests and Vite build pass.
- Synthetic desktop/mobile browser tests cover larger Cozy glyphs, category thumbnails, 12-item paging, playlist button/drag ordering, copy fields, provider snapshots and Square card restrictions.
- PHP provider tests cover URL validation, public-only metadata, supported statistic fields, zero counts, quota/feed fallback and pagination.
- No real account login, payment, provider credential, media upload or native playlist mutation was exercised.

Provider references: [YouTube video resource](https://developers.google.com/youtube/v3/docs/videos), [YouTube Analytics metrics](https://developers.google.com/youtube/analytics/metrics), [Square Web Payments overview](https://developer.squareup.com/docs/web-payments/overview).
