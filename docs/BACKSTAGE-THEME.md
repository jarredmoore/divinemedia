# Backstage theme preview

Status: published to production with owner approval through [PR #47](https://github.com/jarredmoore/divinemedia/pull/47). [Open Backstage](https://divinemedia.us/?theme=backstage); see [release evidence and rollback reference](BACKSTAGE-RELEASE.json).

Direction: an editorial music/film theme inspired by the expansive artwork, strong typography, black space and split feature layouts of [Duff McKagan’s site](https://duffmckagan.com/) and its [video page](https://duffmckagan.com/videos/hung-drawn-and-quartered-1424/). Divine Media retains its own mark, imagery, content and player/studio components. No reference-site assets or code are copied.

Select **Backstage** in the theme menu or use `?theme=backstage`. Cozy and Code Black remain separate choices. The new theme uses an image-led poster hero, a slow ticker, scroll parallax, an editorial featured panel and a three-column desktop catalog. Mobile uses two catalog columns and the existing compact navigation. Player interactions and creator workflows remain in the existing frontend.

Motion uses CSS and one scroll-triggered animation-frame handler; there are no new dependencies or automatic media downloads. The hero has a pause control and respects reduced motion, data saving and hidden tabs. An opaque dark surface remains usable without backdrop blur. Native administration links hand off to the existing Code Black skin; frontend routes retain Backstage.

Verification: 44 frontend tests and the Vite build pass. The Backstage browser fixture verifies 1440/390/320px layouts, no horizontal overflow, theme switching/persistence, player opening, creator upload access, reduced motion and pause behavior. The existing link-import browser regression also passes at desktop/mobile widths. Browser checks use synthetic records and do not upload or import real media.

Rollback: select either existing theme; remove the Backstage option/component/styles on its feature branch. This release changes the frontend theme only; the backend, media and accounts are unchanged.
