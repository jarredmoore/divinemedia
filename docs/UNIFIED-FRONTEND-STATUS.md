# Unified frontend integration

The candidate lives on feat/unified-frontend (PR #15), stacked on the existing native plugin branch. Production Git and the published frontend remain unchanged.

Review preview: https://6af2333621fcf813417c819a--mediaproduction.netlify.app/?theme=code-black (source 026b334dfb23320f255e0eb44cbc73304cd7a202). This draft uses the existing AVideo accounts and library; account actions on it persist to the real backend. No public test accounts or media were created.

Implemented: same-origin native sessions, sign-in, CAPTCHA, account creation/recovery and email verification; frontend playback and embeds; sharing, comments, reactions, account favorites, watch later, playlist management and ordering; categories/channels; notifications; creator uploads, video metadata, native Encoder queue controls and Live studio settings.

The JSON adapter uses installed native permissions and handlers. No replacement account or media database is introduced. Session and gateway credentials never become frontend configuration. A rejected CSRF login is tested to leave authentication unchanged.

Verification:

- 18 frontend boundary/media/theme tests and 15 existing backend tests pass.
- Browser fixture journey passes at 1440, 390 and 320 pixels, including browser back/forward, without native HTML embeds or backend navigation links. This is a mocked UI contract, not a production authenticated journey.
- The isolated off-VM recovery rehearsal passes native login/session rotation, comments/reactions, playlist ownership, creator grants, upload finalization/cancellation, Encoder ownership, recovery token replay rejection and email verification. All 52 original restored media hashes remain unchanged. Disposable accounts and uploads exist only in the rehearsal.
- HTML redirect mapping is tested but activation remains disabled pending preview verification and cutover review. Private native administration and native processing remain intact.

The restricted JSON adapter is installed with verified private off-VM before/after snapshots. All 54 current media hashes, catalog rows, Encoder queue, creator permissions, native sources and container uptimes were preserved. A live anonymous preview check loaded 18 catalog items and passed 14 mobile route checks, cookie flags, cross-site/CSRF refusal and the backend gateway guard. Public HTML redirects remain disabled, and the native head hook is not deployed.

Limits before full cutover: a real authenticated preview journey still needs review with an existing account; large-file uploads have not been load-tested; native Encoder queue creation/ownership is proven, but conversion and output delivery need a new isolated worker rehearsal. The adapter deliberately does not launch the global Encoder queue, retry old jobs, or touch existing videos/thumbnails. Live studio configuration is integrated; this change does not start a public broadcast. Public playlist discovery, comment replies/editing and the remaining configured plugin interfaces need completion before claiming full AVideo parity.

Recovery: the API installer refuses changed staged/native sources, existing adapters and unexpected keys. It verifies a private off-VM backup before installation, snapshots its own files/key, compares catalog/media/permissions/queue and container uptimes, and rolls back only its additions on failure. Never restore the whole database to undo frontend work. The previous published Netlify deploy remains 6af1fcdf8e188044e7207f35.
