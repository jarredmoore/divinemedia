# DCG Master Standard — Divine Media 3.1 Adoption

## Reference
DCG master: https://github.com/jarredmoore/dcgcontent/tree/dev/dcg-master-standard
Master style guide: docs/DCG-MASTER-STYLE-GUIDE.md
Starter: templates/starter/
Release checklist: templates/RELEASE-CHECKLIST.md

## Implemented on dev/divine-media-3.1
- Added `frontend/src/dcg-tokens.css` with values extracted from DCG's active One-Pager.
- Added `frontend/src/dcg-theme.css`, a product-specific visual layer imported after the existing stylesheet.
- Kept existing React/Vite UI, AVideo adapter, playback, media cards, navigation and responsive rules intact.
- Introduced consistent gold accent, focus outlines and DCG dark surfaces without copying the corporate layout into a streaming product.
- Existing project, architecture, workflow, changelog and upstream dependency documentation retained.

## Explicitly not changed
- Azure VM, AVideo Upload, Encoder, thumbnails, existing videos and database.
- Netlify deployment, secrets or authentication.
- Media catalog endpoint configuration and content filtering.
- Existing image and poster references.

## Verification required before production
- Run `npm ci` (if lockfile available) or `npm install`, then `npm run build` from `frontend/`.
- Review screenshots at desktop, tablet and mobile widths.
- Check keyboard navigation, contrast and reduced motion.
- Check public AVideo catalog, poster images, featured content and playback in a deployed preview.
- Verify production Netlify site, deployment branch and rollback commit before approval.
- Replace placeholder imagery only after real catalog posters and approved assets are confirmed.

## Follow-up
- Confirm which DCG logo variants are canonical; Divine Media has its own wordmark.
- Add preview and automated smoke tests once deployment mapping is verified.
- Remove development-only localhost assumptions in a separately tested API integration change.
