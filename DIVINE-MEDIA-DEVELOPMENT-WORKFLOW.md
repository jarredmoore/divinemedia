# Divine Media — Cloud-first development workflow

Status: Adopted 2026-11-05. This document defines the desired workflow; it does not claim Netlify or Azure settings have been changed.

## Ownership
- Source of truth: https://github.com/jarredmoore/divinemedia
- Frontend: `frontend/` — React/Vite, Netlify-hosted, https://watch.divinecreativegroup.com
- Backend: AVideo and Encoder on Azure, https://media.divinecreativegroup.com
- Workstations (including DIVINE-NODE): browser-based review and administration; no always-on local services required.

## Frontend change flow
1. Create a short-lived feature branch from `dev/divine-media-3.1` (the current frontend integration branch).
2. Make changes in GitHub or a cloud development environment; commit only source/assets, never credentials.
3. Open a pull request targeting `dev/divine-media-3.1`. Confirm Netlify Deploy Preview is enabled and test the preview URL.
4. Test responsive layouts, Listen/Watch classification, album art, player controls, public catalog API, and navigation. Ensure the build succeeds.
5. Merge into the development branch after review. Promote to production only after explicit approval and verification of the Netlify production branch and domain settings.
6. Record the deployed commit SHA and verify the live site. Do not assume that a GitHub commit automatically changes production.

## Netlify configuration to verify in the UI
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `dist` (relative to base directory)
- Functions directory: `netlify/functions` (relative to base directory)
- Deploy Previews enabled for pull requests.
- Confirm production branch before changing it; repository default is `master`, which is NOT automatically the correct frontend production branch.
- Keep `VITE_*` values public-only; never put secrets in Vite frontend variables.
- Verify `/api/public-catalog` on the preview, including audio source detection.

## Azure backend policy
- Existing AVideo/Encoder/database and existing videos remain untouched by frontend releases.
- Treat `vm-divinemedia-staging` as potentially production-serving until DNS, traffic, resource utilization, and backups are checked.
- Before provisioning staging: audit Azure VM size, free disk, CPU/RAM, service map, backups, and monthly cost.
- Backend changes require backup, documented rollback, and separate approval. Do not change thumbnail processing or Encoder during frontend releases.

## DIVINE-NODE policy
- No local Docker/AVideo installation required.
- Optional browser-based editing and preview only.
- The old HP laptop is not a deployment dependency; verify that independently before shutting down any legacy service.

## Release checklist
- [ ] PR reviewed and preview deployed
- [ ] `npm run build` successful in Netlify
- [ ] Listen audio and volume/seek controls tested
- [ ] Murphy Lee artwork loads from `/2ndTimeAround.jpg`
- [ ] Watch playback and public catalog tested
- [ ] Mobile and desktop checked
- [ ] Production branch confirmed
- [ ] User approved promotion
- [ ] Live URL and deployed commit verified
