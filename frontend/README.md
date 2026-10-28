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

## Divine Media 2.5 — feed refresh and verified local playback

- The confirmed AVideo video #1 remains in Watch even when a curated JSON feed is configured, unless the feed already contains that same `watchUrl`.
- The frontend checks the configured JSON feed at startup and every 60 seconds while the page is visible. This is **feed polling, not yet automatic AVideo catalog synchronization**.
- The verified local watch page opens inside the Divine Media modal as an iframe; an **Open in AVideo** fallback remains available.
- To sync new AVideo uploads automatically, a server-side adapter must first be connected to verified AVideo endpoints and publish the normalized JSON feed. Never expose AVideo database credentials or admin tokens in Vite environment variables.
- `https://localhost` works only on the machine hosting AVideo. Public deployment requires a publicly reachable HTTPS backend.

## Divine Media 2.6 — local AVideo catalog API (experimental)

The Vite **development server** now proxies `/avideo-local/...` to `https://localhost/...`. This avoids browser CORS problems with local AVideo and accepts the self-signed certificate **only in the local development proxy**. No credentials are stored.

1. In AVideo admin, enable the **API** plugin if installed: Admin → Plugins → API.
2. While Vite is running, visit `http://localhost:5173/avideo-local/plugin/API/get.json.php?APIName=video&rowCount=10`. Expect JSON with `response.rows`. If the API plugin is unavailable, existing content continues working.
3. The frontend requests the public video list every 60 seconds, merges it with the optional curated feed, and keeps the known first video. API response field names and URL accessibility must be checked against your actual installation. This is not yet a verified end-to-end sync.
4. The proxy is **development only**. Netlify requires a public HTTPS AVideo host and a production-safe API proxy. Never commit API secrets or user credentials.
