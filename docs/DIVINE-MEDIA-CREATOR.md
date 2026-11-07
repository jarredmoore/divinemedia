# Divine Media creator workspace

A shared black-and-gold presentation for the native direct uploader and Encoder. The two services retain their separate authentication and upload behavior. No upload, authentication, queue or thumbnail handler is replaced.

## Routes and behavior

- `/upload`: existing access rules, MP3/MP4/OGG guidance, server-generated limits, browse/drop controls, automatic upload, progress and cancellation.
- `/Encoder/`: existing site/account connection, source upload options, settings and processing queue.
- Tabs link between the existing routes. Embedded and `noNavbar` modes retain native presentation.
- Existing form nodes and listeners are moved together into a branded container, rather than rebuilt. Native form actions and hidden inputs remain untouched.
- Native account and language menus remain available. The landing page, login, videos and thumbnails are outside this installer’s scope.

## Reversible installation

`ops/divinemedia/apply-creator.py` patches only `view/mini-upload-form/index.php` and `.compose/encoder/view/index.php` with a shared include before `</body>`. It installs four assets under `divine-creator/`.

Run first without `--apply` to inspect the SHA plan. For installation, provide the source hashes verified in isolation with `--expected`. The installer refuses an existing theme directory, unexpected source or duplicate hooks. Use a private backup location outside the public app tree.

```sh
python3 apply-creator.py --root /srv/divinemedia/app \
  --assets /private/release/assets --backup-root /srv/divinemedia/backups \
  --expected /private/release/expected-source.json --apply
```

Keep the reported `rollback_snapshot`. Restore using:

```sh
python3 apply-creator.py --root /srv/divinemedia/app \
  --rollback /srv/divinemedia/backups/creator-TIMESTAMP
```

Rollback checks installed file hashes and refuses to overwrite later changes. Assets are readable under a restrictive deployment umask; snapshots remain private.

## Design previews

The Encoder preview uses the public connection form with native styles. Direct Upload previews use a representative form fixture pending isolated authenticated rendering. These previews are design evidence, not proof of successful media processing.

| Direct upload | Encoder connection |
| --- | --- |
| ![Direct upload desktop](previews/creator-upload-1440.png) | ![Encoder desktop](previews/creator-encoder-1440.png) |
| ![Direct upload mobile](previews/creator-upload-390.png) | ![Encoder mobile](previews/creator-encoder-390.png) |

## Validation

Local browser checks cover both pages at 1440px and 390px, horizontal overflow, original form identity, retained submit listeners and native input IDs. All network traffic is intercepted; no production upload is submitted. Installer tests cover exact rollback, restrictive umask, source leases and refusal to destroy later changes. The production direct-upload script also passes a browser check with mocked transport: browse triggers the existing input, file addition submits once, progress reaches 50%, cancellation aborts, and failure retains its error state. Actual upload/encoding jobs are excluded from visual validation.
