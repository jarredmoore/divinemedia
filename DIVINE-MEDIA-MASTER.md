# Divine Media — Master Project Guide
Updated: 2026-10-28 | Baseline: Divine Media 3.0 | Target: commercial launch during 2027

## Mission
Build a reusable independent-media publishing, discovery, distribution and monetization platform. Divine Creative Group (DCG) is the parent creative-technology brand; Divine Media is its cinematic media product. Preserve original concepts and source archives from approximately 2016–2019 until audited.

## Evidence and status
- **Verified locally by the project owner:** AVideo Docker backend uploads and encodes videos; API catalog returns titles, real thumbnails and video URLs; Divine Media plays videos; a second upload appeared automatically.
- **Implemented in development:** React/Vite frontend with Discover, Watch, Listen, Live, Creators and Library, featured programming, creator filtering, responsive design, local saved items and automatic AVideo catalog refresh.
- **Not yet verified as production-ready:** public AVideo hosting, authentication, payment processing, premium playback enforcement, creator onboarding, external YouTube/Spotify imports, full search-engine rendering, legal distribution rights, and analytics.
- **Repository:** jarredmoore/divinemedia. Development branch: divine-media-2. Preserve legacy master. Current frontend: frontend/. Do not rewrite or move it without an explicit migration plan.
- **Local environment:** AVideo via Docker at https://localhost; Vite development frontend at http://localhost:5173. These localhost URLs are not public deployment endpoints.

## Architectural decisions
1. Backend: keep AVideo/PHP and evaluate its plugin ecosystem for encoding, live streaming, channel administration, paid content and reporting. Inventory installed plugins and licensing before promising capabilities.
2. Frontend: framework-agnostic API contracts and semantic HTML/CSS/JS. React is the current working implementation, not a permanent requirement. Vue is a valid future client. No immediate rewrite.
3. Separate domain models from AVideo response formats through a small adapter. Shared media model should cover id, slug, title, description, poster, creator, type, visibility, availability and playback entitlement; do not expose private AVideo API/session metadata.
4. Protected media: require server-enforced entitlements and protected delivery URLs. Hiding a button or frontend route is not a paywall.
5. Content: support original uploads, licensed third-party media and permitted external embeds as different source types. Do not assume YouTube or Spotify streams can be downloaded, rehosted or resold.
6. Dependencies: prefer vanilla JS and CSS for portable components; use framework/build dependencies when they provide clear value. Preserve backwards compatibility during extraction.
7. SEO: public film, series, creator and event pages need crawlable server-rendered/prerendered HTML, unique metadata, canonicals, structured data, OG imagery, sitemap and accessible navigation. Keep gated playback separate from public editorial metadata.
8. Security/privacy: protect credentials, isolate public/private data, record minimum necessary consumption analytics, and document consent/retention.

## Brand relationship
DCG parent palette (recovered from the Divine Creative Master): background #09090C; panel #101015; surface #15151C; text #F7F5F2; muted #B7B4BD; orange #FF6A2A; gold #FFCC2F; magenta #EE3E9F.
Historic Root creative direction: yellow #FFD84D, red #E53935, blue #1FB6FF, midnight #0B0F1A, pink #FF4D8D, orange #FF8F1F, aqua #4DFFF3. Historical proposals are not newly approved brand standards.
Divine Media working cinematic sub-brand: cinema black #090B0F, panel #151A1D, lime #C4FA77, warm white #F7F5F2. Preserve the current lime accent and visual continuity. Suggested typography: Inter body; Manrope or Space Grotesk headlines. Keep authentic creator imagery, restrained motion, reduced-motion support and strong contrast.
CSS tokens: see packages/design-tokens/tokens.css. These are portable defaults; adoption in the existing app is a separate tested change.

## Proposed code organization (not yet implemented)
- apps/web-react: current interface after a planned, tested move from frontend/
- apps/web-vue: optional later client, only if justified
- apps/creator-portal: eventual creator workflow
- packages/media-core: framework-neutral media contracts
- packages/media-api: AVideo and other adapters
- packages/player: framework-neutral playback/access abstraction
- packages/design-tokens: portable CSS variables
- docs: architecture, branding, roadmap and legacy inventory
Do not create parallel apps prematurely. Keep a single functional frontend while extracting shared contracts.

## Proposed delivery roadmap
### Q4 2026 — Foundation
Inventory legacy code/design/research, audit AVideo plugin capabilities, preserve existing working branch, establish design tokens, API contracts, migration plan and test coverage.
### Q1 2027 — Production readiness
Public HTTPS hosting and storage, SEO-capable content pages, creator profiles, authenticated access, operational monitoring, backups and security review.
### Q2 2027 — Monetization pilot
Verify installed licensing/plugins; implement and test authorized playback, rentals/subscriptions, payment webhooks, refunds, content rights and analytics. Launch a limited creator pilot.
### H2 2027 — Launch and expansion
Curated public catalog, creator onboarding, film and live programming, customer support, reporting and reusable client deployments. Timing is a target, contingent on rights, testing and readiness.

## Immediate next actions
1. Audit the original master branch and legacy assets; do not overwrite.
2. Inventory the current AVideo plugin installation and distinguish free, licensed and missing modules.
3. Define stable media and creator schemas and playback entitlement boundaries.
4. Add a minimal automated build/smoke-test process before refactoring.
5. Integrate shared tokens into frontend incrementally without changing the approved look.
6. Plan public hosting and SEO page delivery before commercial launch.

## Change control
Mark every feature as Proposed, Implemented, Locally verified or Production verified. Record decisions in this file and keep secrets out of GitHub. Never conflate external embeds with owned/licensed paywalled media.
