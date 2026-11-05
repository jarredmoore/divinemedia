# Divine Media — Project Charter

Status: Production publishing workflow restored; Watch 3.1 in development.
Owner: Divine Creative Group (DCG).
Development model: DCG One-Pager and DCG workflow are the standards for all current and future projects.

## Product
Divine Media is a video publishing and viewing platform for films, performances, episodes, and creator content.

## Public endpoints
- Watch frontend: https://watch.divinecreativegroup.com/
- AVideo streamer/backend: https://media.divinecreativegroup.com/
- Encoder: https://media.divinecreativegroup.com/Encoder/

## Confirmed baseline (2026-11-01)
User confirmed upload, thumbnails, and playback working after the Upload repair.
Do not modify existing videos, thumbnail processing, or production encoder configuration as part of the Watch redesign.

## Current work
- Branch: dev/divine-media-3.1 (based on divine-media-2)
- Frontend: frontend/ (React 19 + Vite 6)
- Goal: cinematic, lightweight, mobile-first public Watch experience using existing AVideo catalog and posters.
- Priorities: featured content, collections, accessible video cards, watch pages, responsive layout.

## Decisions
- Existing working production is the baseline, not a rebuild target.
- GitHub is the source of truth; changes go through a development branch and review.
- Prefer simple HTML/CSS/JavaScript and minimal dependencies; preserve existing React/Vite where practical.
- Do not assume source and deployed assets are identical until verified.

## Next verification
Confirm frontend entry points, API calls, Netlify deployment mapping, production branch/commit, and smoke tests before implementation.
