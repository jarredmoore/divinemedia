# Branded routes and URL continuity

The public addresses are **https://divinemedia.us** for Watch/Listen and **https://media.divinemedia.us** for media accounts, library, channels, categories, uploads and Encoder. The work adds one shared presentation layer around native HTML pages, preserving the native forms, permissions, processing and media.

## Coverage

| Route / view | Treatment |
| --- | --- |
| Watch / Listen | Existing Default and Code Black themes; links and embeds carry the active theme. |
| Media `/` and `/?theme=...` | Branded entrance. A theme query no longer falls through to the default gallery. |
| `/user`, protected-account redirects | Existing branded login, with the shared palette and theme selector. |
| `/signUp` | Native registration form in the branded shell; dark panels/footer and corrected mobile row widths. |
| `/view/` | Native media library with branded navigation and palette. |
| `/cat/default`, other category/error views | Shared branded shell; native category lookup and unavailable-content messages remain authoritative. |
| `/view/channels.php`, `/channel/admin` | Branded channel browsing/profile, with corrected mobile gallery width. |
| `/upload` | Existing creator workspace or branded sign-in, depending on native permissions. |
| `/Encoder/`, `/Encoder/view/index.php` | Existing creator workspace; shared Encoder head carries the same palette and preference. |
| Notifications | Native UserNotifications content receives the shared palette; embedded views do not gain a duplicate site header. |
| Video/audio embeds | Native player and access controls remain intact; palette is applied without an extra navigation bar. |
| Administrative destinations | Permissions remain native. `/categories` is the categories **manager**, not the public category browser; guests keep their native access/error flow. |
| API, media files, password-recovery handler and upload callbacks | Native response formats and behavior are retained; these are not HTML entry pages. |

The account menu's old subscriptions-manager shortcut led guests to an administrative permission error. It now offers the verified **Browse channels** page. Channel following and account actions stay inside the native platform.

## One selected theme across the two sites

Theme precedence is: an explicitly valid URL choice, then the shared preference cookie, then older host-local storage, then Default. `cold-black` remains an accepted alias for Code Black. The public selector labels remain **Default** and **Code Black**.

The non-secret `dm_view_theme` cookie uses the `divinemedia.us` domain, root path, HTTPS and SameSite=Lax. It stores only the visual preference. Native authentication/session cookies are unchanged; this does not create a second login system or transfer account credentials. URL handoff also works from Netlify previews, which cannot set the production domain's cookie.

The HTML head sets the palette before the body paints. The critical tags use AVideo Layout's `doNotSepareteTag` convention so Layout does not move them to the footer. Existing branded login/creator headers are reused. Generic native pages gain one Divine Media header. Embedded, popup and compact views retain their intended header behavior.

## Canonical URLs and compatibility

New navigation uses only the `.us` hosts. Legacy browser GET/HEAD entry paths redirect to `media.divinemedia.us`; allowlisted public query options are preserved, while credential-bearing query options are discarded. The earlier auth-entry redirect policy remains in place.

Existing video/audio files, API requests, embedded-player compatibility paths and POST handlers remain supported on the legacy host. This deliberate compatibility does not generate old-domain public navigation. Do not replace every legacy hostname string in configuration, signed URLs or historical documentation indiscriminately.

## Deployment and recovery

The source changes are five leased native files: `.htaccess`, `view/include/head.php`, Encoder's `view/index.header.php` and `view/localEncoder.php`, and the branded landing head. The five new assets live in `/srv/divinemedia/app/divine-shell`. These files are persistent in the existing app/Encoder bind mounts. Apache and containers are not restarted, and no SQL configuration or processing job is changed.

The isolated recovery test validated 11 HTML entries, legacy-browser redirects, both-host byte ranges, API responses, native PHP syntax, and exact rollback/reapply. That restore uses the established 16-record/52-file baseline plus current configuration and presentation. The live deployment separately preserved all **54 current media hashes**, catalog fields, Encoder queue, 11 protected native source/config files and every container uptime. Configuration supplements are not a new full media/database backup.

Private before/after configuration archives have off-VM roundtrip hash verification. The initial snapshot is `/srv/divinemedia/backups/route-shell-0ac6faa36d`. A subsequent CSS-only channel-width refinement and asset-cache version bump has its own verified archives. The standalone Local Encoder launcher subsequently received a head-only include, covering all three standalone Encoder documents without executing the launcher. The final combined rollback snapshot is `/srv/divinemedia/backups/encoder-shell-ad8bbacb46/recovery`: use the route installer's lease-checked rollback against that snapshot to restore the original five native files and remove the owned shell assets. Later source/asset edits block rollback rather than being overwritten. No whole-database restore is needed.

The production Git branch is not modified by this work. Frontend delivery uses the existing workflow of promoting a verified Netlify draft from committed Git source, with the previous published deploy retained for rollback. Repository and deployment provenance are recorded with the verification evidence.

## Verification scope

Frontend unit checks cover URL trust and theme precedence/handoff; backend tests cover source leases and rollback. Anonymous browser checks exercise Watch → Encoder → Watch → signup, both theme choices, server-side cookie/prepaint behavior, canonical links, one header per HTML view, embedded-player framing and responsive layouts. Non-GET requests are blocked in browser verification. No real sign-in, registration, CAPTCHA submission, upload or encode is performed. Staff-only authenticated views are not claimed as manually tested; they share the native rendering hooks when used.

Media artwork, CAPTCHA imagery, other content images and third-party widgets can contain white pixels. The cleanup targets default white application surfaces, not the contents of uploaded media. Upstream attribution is retained.

Evidence: [initial public-route audit](ROUTES-BEFORE-AUDIT.json), [isolated stage](ROUTES-STAGE-VERIFICATION.json), [live backend preservation](ROUTES-BACKEND-VERIFICATION.json).

Live frontend publication: Netlify deploy `6af0f784f9b38d200ae0b693`, from frontend source `9004b733`; previous deploy `6aefc9b7bac75e020823b88a`. Backend implementation is committed through `29e08ba6`. Production Git remains `5067877dbd56bcd769812f42b46b15576848753f`.

Final live checks passed 33 route/viewport combinations at 1440, 390 and 320 pixels, and native controls/audio playback at six widths. Evidence: [live route checks](ROUTES-PRODUCTION-BROWSER-VERIFICATION.json), [native controls](ROUTES-NATIVE-CONTROLS-VERIFICATION.json), [frontend publication](ROUTES-FRONTEND-PUBLICATION.json), [legacy redirects](ROUTES-LEGACY-URL-VERIFICATION.json), [CSS refinement](ROUTES-CSS-REFINEMENT.json), [standalone Encoder extension](ROUTES-ENCODER-EXTENSION.json). The screenshots in `previews/routes-*` show the actual published media site.
