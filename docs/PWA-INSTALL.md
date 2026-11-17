# Divine Media app installation

The frontend now owns its PWA manifest at `/manifest.webmanifest`, with a stable `/` app identity, a standalone start URL, black theme and background, 192px/512px icons, a maskable icon and a 180px Apple touch icon. The black-and-gold D mark reuses the current frontend wordmark geometry; its vector source is `frontend/public/icons/divine-mark.svg`. The same artwork is the favicon.

Both navigation themes have a gold Install action, and the main catalog has a branded installation card. Mobile navigation keeps the theme chooser alongside an additional labelled Install action. A native browser install prompt is used only after a click when the browser supplies it. Otherwise a focused dialog explains browser installation, iPhone/iPad Safari Share → Add to Home Screen, and Safari on Mac Add to Dock. Accepted/dismissed choices are handled; standalone launches and appinstalled events hide installation controls. No automatic popup is shown.

The service worker stores only the generic offline page and public 192px/512px icons. API, account, login, mutation, media and cross-origin requests are not cached or intercepted. Navigations stay network-first; a network failure shows a generic reconnect page rather than old account content. Only this app’s old offline-cache versions are removed. `/sw.js` and the manifest have revalidation headers. Streaming and account features require the internet.

Verification covers 29 frontend tests, a production build, existing isolated player/account/creator interactions, both themes at 1440/390/320px, simulated native install choices, iPhone guidance, standalone suppression, and a real service worker/offline fallback on localhost. No real user installation, login, account mutation or device Cast connection was performed. The native install experience and icon on actual devices remain owner testing. Existing installed shortcuts can retain old OS-cached artwork until re-added.

User explicitly authorized production publication of this change. The separate user-specific login issue remains unresolved; no account or backend settings are changed by the PWA implementation.
