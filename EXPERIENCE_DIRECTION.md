# Divine Media 2.0 — Experience Direction

## Product thesis
A single independent media destination combining:
- **Netflix:** cinematic visual storytelling and curated film/video collections.
- **YouTube:** creator channels, publishing, following and community.
- **Spotify:** audio-first listening, playlists, discovery and persistent playback.

These are interaction references, not copied visual assets or branding.

## Navigation
Discover · Watch · Listen · Live · Creators · Library

## Initial design system
- Dark graphite background, warm off-white typography, restrained accent color.
- Large artwork, uncluttered cards, generous spacing and subtle hover motion.
- Lucide icons, accessible labels, keyboard support and reduced-motion preference.
- Mobile-first responsive layouts with compact navigation.
- Editorial, cinematic hero rather than a dense video grid.

## Homepage v1
1. Feature hero with prominent Watch / Listen actions.
2. Continue Watching / Continue Listening (when authenticated and supported).
3. Featured films, performances and series.
4. Made for You / curated collections.
5. Independent creators and channels.
6. Live now / upcoming broadcasts.

## Key views
- **Watch:** immersive video player, creator information, next up, related content.
- **Listen:** album/episode art, audio playback, queue and playlists.
- **Creators:** channel header, media tabs, follow action and biography.
- **Library:** saved content, history and user playlists.
- **Studio:** uploads, metadata, moderation and analytics; AVideo administration remains authoritative until integrations are verified.

## Technical boundary
- Modern React/Vite/Tailwind frontend suitable for Netlify.
- Existing AVideo backend remains on local Docker for development.
- Do not invent AVideo endpoints. Audit documented API/embeds before wiring data.
- A local backend is not accessible to public Netlify visitors; production integration needs an HTTPS-reachable backend and secure authentication.
- Avoid promising Spotify-style music licensing or music catalogs without rights clearance.

## Implementation order
1. Static, responsive Discover page with sample content clearly marked.
2. Watch and Listen views with accessible player shells.
3. Verify AVideo API and cross-origin/auth behavior; connect real video data.
4. Creator pages, playlists and account flows.
5. Deploy frontend preview to Netlify, then plan backend staging.

## Acceptance criteria for first visual milestone
- Desktop and mobile navigation work.
- Artwork is responsive and doesn't cause layout shifts.
- Clear differentiation between video, audio and live content.
- No hardcoded private credentials or broken API assumptions.
- Legacy `master` remains untouched.
