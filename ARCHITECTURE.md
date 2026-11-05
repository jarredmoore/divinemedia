# Divine Media — Architecture and Operations

## Known components
- Frontend source: GitHub jarredmoore/divinemedia, branch divine-media-2, folder frontend/.
- Frontend tooling: React 19, React DOM 19, Vite 6, lucide-react (per frontend/package.json).
- Frontend delivery: watch.divinecreativegroup.com, reported Netlify CLI deployment; exact deployed commit not yet verified.
- Backend: AVideo on Azure VM vm-divinemedia-staging; public https://media.divinecreativegroup.com/.
- Encoder: https://media.divinecreativegroup.com/Encoder/; installed within AVideo container rather than a separate Encoder service (per prior troubleshooting).

## Boundaries
Frontend reads published media data and poster URLs from AVideo. Do not expose backend credentials or private administration endpoints in frontend bundles.
Production videos, upload, encoding, and thumbnail pipeline are out of scope for the 3.1 design iteration.

## Deployment safety
1. Inspect current source and configuration; identify live deployment source and branch.
2. Make frontend changes on dev/divine-media-3.1.
3. Run dependency install/build and inspect generated assets.
4. Validate API responses, playback, posters, navigation, mobile layouts, and error states in preview.
5. Review and explicitly approve production deployment.
6. Keep a rollback reference to the last known working production deploy.

## Backup/repair reference
Upload repair backup reported at /srv/divinemedia/backups/upload-restore-20261101T220406Z.
Do not copy secrets or runtime config values into this repository.

## Open questions
- Exact live Netlify site ID and deploy-to-source mapping.
- Current frontend component structure and API integration details.
- Production frontend release SHA and existing automated test coverage.
