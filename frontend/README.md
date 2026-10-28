# Divine Media — Discover UI v0.1

A modern, responsive React + Vite frontend. It is a **visual prototype**, not yet connected to AVideo. Media thumbnails are remote Unsplash images; content titles and creators are illustrative. No login, uploads, purchases or live streams are enabled.

## Local run

Install Node.js 20.19+ or 22.12+ and run:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL shown by Vite (typically http://localhost:5173). This is a **separate app** from the AVideo backend on https://localhost.

## Netlify

Set Base directory to `frontend`, Build command to `npm run build`, Publish directory to `dist` (relative to base). Deploy branch `divine-media-2`. The included netlify.toml supports SPA routes.

## Next

Verify AVideo's API and embeds before connecting real data. Public Netlify users cannot reach your local-only AVideo server.
