# Divine Media backup and recovery

This runbook implements the owner's authorization to create a fresh off-VM backup and rehearse recovery after the 3.3 audit found that the November 1 backup was stale. It does not authorize production releases or Upload/Encoder repairs.

## Storage and access

- Resource group: `rg-divinemedia-backups`, Central US.
- Account: `stdmbackup983066`, StorageV2, Standard LRS.
- Container: `verified-backups`; public blob access and shared-key access disabled.
- HTTPS required, minimum TLS 1.2, Azure-managed blob encryption enabled.
- Blob versioning plus 30-day blob and container soft deletion enabled. Soft deletion is not an immutable retention lock or automatic expiration policy.
- VM system-assigned managed identity has Storage Blob Data Contributor at this container's scope only. Scripts obtain short-lived tokens from the VM metadata service in memory; they use no account keys, SAS URLs or printed tokens.
- This is off-VM protection in the same Azure region, not a geographically separate disaster-recovery environment.

The one-off backup and restore exercise does not install an unattended scheduler. Do not mistake the presence of this storage account for a recurring backup policy.

## Backup set

Prefix: `verified-20261107T050456Z`.

The primary set captures both transactional database dumps, the application tree including videos, Encoder and compose configuration, host support configuration, private container-recovery metadata, media inventories and a checksum manifest. All 27 main database tables and seven Encoder tables report InnoDB. Dumps use single transactions, quick streaming, routines/events/triggers and no live table lock. Each database has its own snapshot; this is not an atomic VM-wide disk snapshot.

All 52 MP3/MP4 files (640,912,565 bytes) had identical before/after inventories during capture, and all archived media bytes matched their expected SHA-256 hashes. The main database had 16 video rows. Primary objects total 1,010,082,660 bytes, approximately 963 MiB.

An additional runtime set captures the active container's Apache, PHP and SSL configuration. This is necessary because Apache's virtual-host configuration was generated inside the live container rather than stored entirely in the application bind mount. Its separate `runtime-manifest.json` records checksums. Both runtime objects were downloaded and checksum-verified after upload.

The image recovery set uses `images-manifest.json` and preserves all five exact images referenced by the recovery metadata. The compressed archive and manifest total 925,466,922 bytes; image configuration digests match the recorded IDs. The complete primary/runtime/image set is 19 objects totaling 1,935,869,019 bytes. All 19 objects were downloaded separately from Blob Storage and checksum-verified. Never publish these private image/configuration archives; they can contain operational secrets.

All backup/configuration data remains outside Git. Local backup paths are root-only under `/srv/divinemedia/backups`.

## Tools and manual sequence

The scripts in `ops/divinemedia` target this specific installed stack, container names and storage account. They run as root on the VM with Python 3.12+, Docker, tar and gzip. They are manual tools; reviewing or merging the PR does not execute them on Azure.

From a private checkout of the scripts on the VM:

```sh
sudo bash ops/divinemedia/create-backup.sh
sudo python3 ops/divinemedia/blob-roundtrip.py
sudo bash ops/divinemedia/capture-runtime.sh
sudo bash ops/divinemedia/capture-images.sh
sudo python3 ops/divinemedia/rehearse-restore.py
sudo bash ops/divinemedia/finalize-backup.sh
```

The first step writes `.latest-verification-backup` only after successful local validation. Upload/download tools read that pointer and use a unique prefix. A separate `.latest-roundtrip-backup` points to the downloaded restore source. The runtime, image and verification supplements share that prefix and have independent manifests. The finalization step checks the original media against the backup inventory, records live container health and uploads the aggregate recovery report without raw logs or credentials.

The helper refuses single objects above 4 GiB; larger catalogs need staged block uploads or another verified transfer client. It was verified against the current approximately 1 GiB application and 0.9 GiB image archives.

The upload uses create-only object requests. Do not rerun an upload blindly over an existing prefix; an existing object causes failure rather than replacement. Inspect any interrupted run privately and use a fresh backup prefix if needed. Do not delete old verified backups to resolve an upload error.

The tools check every downloaded object's SHA-256 against the source manifest. They do not print credentials, SQL data, configuration contents or signed URLs. Private diagnostic files can contain sensitive operational details and must remain private.

## Rehearsal design

Recovery uses the downloaded off-VM copy, never the live application/database volumes. Archive paths and links are validated before extraction. Original numeric ownership and permission bits are preserved for the trusted, checksum-verified files; generic safe-extraction defaults otherwise remove directory permissions needed by the application.

Both databases run in temporary containers on a dedicated internal Docker network with no public ports or external route. Scratch data uses tmpfs, and the restored application uses a newly extracted private directory. The web container bypasses the normal production entrypoint, avoiding cron/encoder startup. Captured Apache/PHP/SSL configuration and the recovered environment restore the web runtime. Database credentials remain in private files/process memory.

Temporary database containers are each limited to 0.5 CPU and 768 MiB RAM; the web container to 0.5 CPU and 1 GiB; the cache to 0.25 CPU and 64 MiB. All scratch containers, network and extracted files are removed after the test, including failed tests. Reports contain counts and status, not data records.

A bare replacement host also needs Docker and the private image archive loaded before launching the recovered stack. Do not run a restored stack with production callbacks or external network access until its site URLs, identities, queue behavior and isolation have been reviewed. A successful isolated read test does not verify a live DNS cutover, upload, encoding, thumbnail processing, live streaming, SMTP or external integrations.

## Verified rehearsal result

The completed exercise restored from the Blob-downloaded copy and passed:

| Check | Result |
| --- | --- |
| Downloaded primary, runtime and image hashes | Match source manifests |
| Main / Encoder database table checks | Pass; 27 / seven restored tables |
| Recovered video records | 16, matching the fresh backup manifest |
| Recovered media | All 52 MP3/MP4 SHA-256 checks pass |
| Recovery image archive | Five exact image configuration IDs verified |
| Captured Apache configuration | Pass |
| Recovered PHP runtime connections to both databases | Pass |
| Isolated web request | HTTP 200; rendered response passes fatal-error check |
| Isolated static media range | HTTP 206 |
| Scratch containers, network and extracted files | Removed |

The rehearsal revealed two recovery requirements now represented in the scripts: preserve active container-generated web configuration, and preserve the trusted archive's directory ownership/modes. The isolated stack also needs its cache service. Earlier incomplete attempts were cleaned up; only the completed passing run establishes the web/range result.

Final verification rehashed all 52 original MP3/MP4 files and confirmed unchanged bytes. Original containers remained running/healthy, with no remaining rehearsal containers. The aggregate verification report and its manifest were uploaded as two additional objects and downloaded with matching checksums (21 objects total).

The exact image archive is now off-VM, but no replacement Azure VM was provisioned and no cold-host Docker import, public DNS cutover or production deployment was performed. These remain separate operations. Upload, encoding, thumbnail jobs and live-stream behavior were not tested.

## Cost and rollback boundaries

This storage account has usage-based storage/request charges. A few GiB of one-off backup data should be well below $1/month at ordinary Hot LRS storage rates, plus request charges; this is an estimate, not a billed quote. Version history, future backup sets, retention and transfer can increase costs. No additional always-on VM was provisioned.

The new identity and role grant do not restart application services. Rollback means revoking only the backup-container role assignment and, if otherwise unused, removing the newly added VM identity. Retain the storage account and verified backup data until another recoverable copy exists; deleting the account/resource group can defeat the intended protection. No rollback or resource deletion was performed during this exercise.
