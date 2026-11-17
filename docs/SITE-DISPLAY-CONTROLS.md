# Site-wide display controls

The Display button appears in both frontend navigation themes, creator/account workspaces, video players (including embeds), and the listening room. Site fullscreen targets the document so navigation and overlays remain usable; Safari can fall back to native video fullscreen when document fullscreen is unavailable.

AirPlay uses the browser’s native media picker where supported. Google Cast uses Google’s official Sender SDK and default media receiver, loaded only after opening the Display menu in a compatible Chromium browser. The receiver loads the active permission-checked program URL, resumes VOD position, and local playback pauses only after the receiver accepts the media. Decorative background loops are excluded. HLS uses its original HTTPS manifest rather than a browser-only MediaSource blob. No custom receiver, paid AVideo module, backend route or public account change is required for this implementation.

Whole-tab or whole-screen mirroring is selected through the browser’s Cast tab command or the device’s Screen Mirroring controls. The website cannot open those system mirroring selectors on every platform. The display menu explains this distinction and disables media casting until program media is open.

Receiver access to the source, codec support and network discovery determine whether a particular video can play remotely. Browser API calls and receiver interactions have been simulated in automated checks; a physical AirPlay device and Chromecast still need testing. Do not interpret the presence of the button as proof of hardware connectivity.

Verification: 27 frontend unit tests; complete existing isolated frontend browser interactions; AirPlay/Cast/fullscreen API doubles; menu bounds at 320px/390px; both themes at 320px/390px/1440px; creator overlay control; production build. No real account mutations or physical receiver connections were made by these checks.

This feature is prepared on a feature branch and review preview, not published to production. The reported user-specific sign-in rejection remains separate and unresolved.
