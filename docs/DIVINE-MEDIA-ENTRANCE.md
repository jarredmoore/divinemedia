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
