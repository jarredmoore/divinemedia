# AVideo upstream dependency and maintenance policy

Official upstream source: https://github.com/WWBN/AVideo
Publisher: WWBN. Upstream default branch: master (verified 2026-11-01).
Official website cited by current upstream README: https://streamphp.com/
Upstream documentation: https://github.com/WWBN/AVideo/wiki
Releases: https://github.com/WWBN/AVideo/releases

## Project architecture
- AVideo is the **upstream video backend** for Divine Media, not the custom DCG public Watch frontend.
- DCG Watch frontend source: jarredmoore/divinemedia, frontend/ on divine-media-2 and dev/divine-media-3.1.
- The platform publishes via the self-hosted AVideo service at https://media.divinecreativegroup.com/ with Encoder at /Encoder/.
- The public viewer is https://watch.divinecreativegroup.com/.
- Upload, posters/thumbnails and playback were confirmed working by the owner on 2026-11-01.

## Do not conflate
- WWBN/AVideo upstream source code with the DCG-maintained frontend repository.
- GitHub upstream master with the actual version installed on Azure; this version is **not verified**.
- Encoder's upstream repository/version with AVideo's root repository without verifying exact deployed versions.

## Safe upgrade procedure
1. Record exact running AVideo commit/tag, plugin list and dependencies on Azure. Never guess from upstream HEAD.
2. Check upstream release notes, changelog and breaking changes for the target version.
3. Back up persistent videos, application config and databases, and document a restore test.
4. Test on a separately isolated staging environment, including upload, encode queue, poster/thumbnail generation, playback, API response and Watch frontend.
5. Compare existing site customization with upstream before updating.
6. Deploy only with explicit approval, a maintenance window and documented rollback.
7. Do not automatically pull upstream master into the running server or change thumbnails/encoder during frontend UI work.

## Working baseline
Previous Upload repair backup: /srv/divinemedia/backups/upload-restore-20261101T220406Z
Do not store credentials, database dumps or video assets in Git.

## Follow-up
- Verify deployed AVideo version and remote/repository origin.
- Identify separate Encoder upstream and installed version if future backend maintenance requires it.
- Track upstream changes as advisory only until scoped, backed up and approved.
