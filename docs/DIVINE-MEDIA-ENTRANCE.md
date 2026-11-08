# Divine Media branded entrance

The owner requested a branded public entrance and matching login on `media.divinecreativegroup.com`, preserving existing routes and authentication. This work uses the current black/gold Divine Media direction and keeps the React/Netlify frontend as the main viewing experience.

## Public experience

- Bare homepage: branded gateway with “Explore Divine Media” to the watch frontend and a discreet creator sign-in.
- Creator sign-in: the existing AVideo guest form, presented in a matching responsive shell. Fields, CAPTCHA, password recovery, registration, alternative sign-in controls and native handlers are retained.
- Successful entry from the gateway requests a same-origin redirect to `/view/`, the existing native media library. The library also remains directly accessible from the entrance footer.
- No authentication wall is added to public API, media, embeds or Encoder. Signup/profile/admin pages are not broadly rethemed in this change.

Assets live in `backend/divine-entrance`. They use system fonts and local SVG/CSS, with no new third-party assets or analytics. The landing page needs no JavaScript. Login JavaScript moves the existing form nodes rather than cloning/replacing them; it does not fetch, inspect, store or forward credentials.

## Integration and rollback

`ops/divinemedia/apply-entrance.py` is an explicit installer for the deployed AVideo tree. GitHub's legacy AVideo files differ from the currently running release, so the theme is packaged separately rather than replacing deployed core files with the repository's older copies.

The installer plans the exact before/after hashes, copies only the five owned theme assets and prepends a narrowly scoped root rewrite plus an additive guest-login template include. The original rewrite rules remain intact below it. Only GET/HEAD with an empty query and a bare `/` or `/index.php` path match; existing query routes fall through. A live apply must use the expected source hashes from the isolated test. A changed source or an existing entrance directory stops the install rather than overwriting it.

The only modified native files are `.htaccess` and `view/userLogin.php`; the authentication handler, server-level Apache configuration, Encoder, media and existing rewrite rules are unchanged.

Before writes, original hook files and the checksum plan are stored in a private timestamped rollback directory. Files are replaced atomically with original owner/mode retained. The public theme directory is explicitly 0755 and assets 0644 even when deployment uses a private 0077 umask; rollback snapshots stay private. On an installation exception, the original hook files are restored and new owned assets removed.

Rollback verifies that the installed files still match this release before restoring the exact originals and removing the owned theme directory. It refuses to overwrite later edits or remove unowned files. No service restart or database migration is required.

```sh
# Inspect a plan first. These are examples; use the verified release paths.
python3 ops/divinemedia/apply-entrance.py \
  --root /path/to/avideo --assets backend/divine-entrance \
  --backup-root /private/rollback-directory

# Apply only with the expected-source.json produced by isolated verification.
python3 ops/divinemedia/apply-entrance.py \
  --root /path/to/avideo --assets backend/divine-entrance \
  --backup-root /private/rollback-directory --expected /private/expected-source.json --apply

python3 ops/divinemedia/apply-entrance.py \
  --root /path/to/avideo --rollback /private/rollback-snapshot
```

The fresh off-VM backup and recovery procedure is separate from this release. Existing media files, Encoder, thumbnail jobs, authentication endpoints and deployment branches are not modified by the theme installer.

## Validation

Browser checks against the existing public native login verify desktop/mobile bounds at 320, 375, 768 and 1440 pixels, unchanged form-node identity, the original submission URL/field names, and CAPTCHA activation after a simulated login failure. Authentication requests in that browser test are intercepted; no credentials or password-reset requests are sent to the backend. The native login stays native; real-account authentication/SSO should be reviewed by the owner without sharing passwords.

Installer regression checks cover restrictive deployment permissions, source-change rejection, exact rollback and preservation of later edits. GitHub Actions runs PHP, JavaScript and Python syntax checks plus those installer checks.

Deployment requires PHP lint, isolated route-preservation tests, a rollback/reapply rehearsal, and a source-hash match against the live installation. Screenshots under `docs/previews` contain blank form fields and public UI only.

## Isolated verification result

The installer was applied to an isolated restore of the verified off-VM backup, with the restored application, cache, and both databases on an internal network. Bare `/` and `/index.php` rendered the new entrance. The native library, root query filters, Encoder, video embed, video page, audio page and login JSON route all retained their baseline HTTP 200 statuses. The public catalog retained 16 rows and MP3/MP4 byte-range requests returned HTTP 206.

The native guest login kept `#loginForm` and received only the theme asset include. The authentication handler checksum was unchanged. PHP lint passed. The installer then rolled back to the exact original source, restored the native homepage, removed its assets, and reapplied successfully against the same original hashes. Scratch containers, network and extracted files were removed after verification.

The release bundle's deployment plan is tied to the original `.htaccess` and login-template hashes. This is a presentation change, not a database, upload, encoding or thumbnail release.

## Live deployment

Applied November 7, 2026 at 8:02 a.m. America/Chicago (14:02 UTC), from feature commit `1e4b67346e7bc470719c381d99fc6358b36fb0b2`, release `76e475070ca5`. No development or production branch was merged.

Public HTTPS homepage and creator sign-in return HTTP 200. Live native library/query, Encoder, embed, audio/video page and login JSON checks retained HTTP 200. Catalog count remains 16; MP3/MP4 ranges return 206. The authentication handler checksum and all 52 original media hashes are unchanged. Original containers remain healthy; no services were restarted.

Check the login on canonical HTTPS: HTTP can return AVideo's wrapper without the form. This is not evidence that sign-in is unavailable. The final presentation uses a full-bleed opaque canvas to prevent native animated backgrounds from changing the branded appearance. Native dialogs and controls remain visible; embedded/popup authentication keeps its native presentation.

Current exact rollback snapshot: `/srv/divinemedia/backups/entrance-20261107T140202Z-a7d9e2`. The installed core and owned-asset hashes must still match that snapshot's plan before rollback. Real-account sign-in and SSO were not exercised; the owner can validate those using their usual credentials without sharing them.
