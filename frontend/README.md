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

## Divine Media 2.3 — curated media bridge

The frontend can now read an optional curated JSON feed, with no invented AVideo API calls.

1. Copy `public/media.example.json` to `public/media.json` and edit the entries. The example file is **not loaded automatically**.
2. Add real, permissioned public HTTPS media URLs in `videoUrl` or `audioUrl`, or use same-origin paths for locally served media. Do not enter passwords, session tokens or private URLs.
3. Restart Vite if you change environment variables; otherwise refresh the page. If `media.json` is absent or invalid, the existing sample cards remain.
4. For a remote feed, set `VITE_MEDIA_FEED_URL` in `.env.local` (do not commit secrets). The remote endpoint must allow browser CORS.
5. AVideo's real catalog API, authentication, thumbnail URLs, signed playback and live stream capabilities must be verified before building an adapter.

The Library now persists **in this browser only** via localStorage; it is not synchronized to AVideo accounts. Direct video/audio controls work only when a valid accessible media URL is configured. Sample player controls are demonstrative and do not produce sound.
