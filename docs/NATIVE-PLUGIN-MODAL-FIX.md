# Native plugin Configure dialogs

The shared glass skin applied backdrop blur to panels containing Bootstrap 3 dialogs. This created stacking contexts beneath the body-level backdrop and blocked pointer input.

The skin now disables blur on modal ancestors, including dynamically inserted dialogs. Native forms, nodes, handlers, and save behavior remain intact. A CSS selector and a JavaScript class fallback cover browsers without `:has`. Shared asset versions advance to `34-glass-2`.

Validation: 19 backend tests pass. The browser fixture reproduces the original failure and verifies editable settings, close/Escape, dynamic dialogs, and unchanged form nodes at 1440, 390, and 320 pixels; the narrowest case disables `:has` to exercise the fallback. The fixture uses synthetic settings and native Bootstrap 3.4.1/jQuery assets.

Applied only three shared presentation files on Azure. Private before/after backups were verified off-VM. Media/artwork hashes, catalog, Encoder queue, protected native handlers, and container uptimes remained unchanged. Live head routing hooks were preserved. Rollback state: `/srv/divinemedia/backups/native-popup-20043530ddcc`.

Separately, the requested YouTubeAPI primary server-side key was configured after a private settings backup. Google returned HTTP 403 with `quotaExceeded`. No credentials are stored in this repository. This does not resolve the separate yt-dlp import challenge.
