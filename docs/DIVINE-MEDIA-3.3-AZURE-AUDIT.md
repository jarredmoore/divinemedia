# Divine Media 3.3 — Azure audit

Status: read-only observations, not a backend release. Observed November 6, 2026, approximately 10:34–10:40 p.m. America/Chicago (November 7, 04:34–04:40 UTC). Metrics cover the preceding seven days. Billing is delayed and excludes unreported usage.

## Main conclusion

`vm-divinemedia-staging` serves the public backend: the DNS address for `media.divinecreativegroup.com` equals the VM's static public IP. Treat it as production-serving. Do not stop, resize, repurpose, or use it for experimental Upload/Encoder repairs just because its name says staging.

The current workload has substantial average CPU, memory, and disk-capacity headroom. The principal verified operations gap is backup protection: local archives exist, but this audit did not establish an automated, off-VM backup or tested restore. Establish those protections before changing the backend.

## Resource and capacity observations

The VM belongs to Microsoft Azure Sponsorship, resource group `RG-DIVINEMEDIA-STAGING`, Central US. Subscription identifiers, credentials, private configurations and database contents are intentionally omitted.

| Item | Observed |
| --- | --- |
| VM | `Standard_D2s_v5`: 2 vCPU, 8 GiB RAM; running, guest agent ready |
| OS | Ubuntu 24.04 LTS image |
| OS managed disk | 64 GiB Premium LRS; guest filesystem 61 GiB, 14 GiB used, 48 GiB available (22% used) |
| Media managed disk | 128 GiB Standard SSD LRS; mounted at `/srv/divinemedia`; filesystem 125 GiB, 2.1 GiB used, 117 GiB available (2% used) |
| Inodes | OS 3% used; media 1% used |
| Guest memory snapshot | 7,931 MiB total; 1,301 MiB used; 6,629 MiB available; no swap |
| Guest load | 0.15 / 0.14 / 0.10; uptime about nine days |
| Video directory | Approximately 624 MiB |
| Encoder directory | Approximately 39 MiB |
| Local backup directory | Approximately 147 MiB |
| Main / Encoder DB volume directories | Approximately 161 / 156 MiB; Docker volumes on the OS filesystem |

Seven-day Azure Monitor observations use 168 hourly buckets; maxima preserve shorter underlying samples and do not measure duration of saturation.

| Metric | Average / total | Highest or lowest observed |
| --- | --- | --- |
| CPU | Mean of hourly averages 1.25% | Peak sample 99.18%; highest hourly average 8.99% |
| Available memory | Mean approximately 6.54 GiB | Lowest sample approximately 5.96 GiB |
| Network out | 4.98 GB total | Includes application and other outbound traffic, not verified unique viewer traffic |
| Data disk IOPS consumption | Mean 0.03% | Peak 50% |
| Data disk bandwidth consumption | Mean 0.03% | Peak 52% |
| OS disk IOPS consumption | Mean 2.43% | Peak 100% |
| OS disk bandwidth consumption | Mean 0.48% | Peak 100% |
| VM availability | 1.0 for all returned hourly aggregates/minima | No unavailability in these returned metrics |

No sustained capacity shortage was demonstrated. Do not downsize solely on the average: uploads, encoding, backup compression and OS/database I/O need separate workload profiling. The CPU peak's highest hourly bucket began November 3 at 01:34 UTC; this audit does not attribute it to a particular job.

## Service and network map

- Docker and cron active; host nginx, Apache, MySQL and MariaDB inactive. Web and database services run inside containers.
- `app-avideo-1`: healthy; Apache/PHP, AVideo and embedded Encoder directory; binds host ports 80, 443, 2053 and 3000.
- `app-database-1`: healthy; main DB; container-only port 3306.
- `app-database_encoder-1`: healthy; Encoder DB; container-only port 3306.
- `app-live-1`: healthy at observation; binds 1935, 8080 and 8443.
- `app-memcached-1`: running; container-only port 11211.
- AVideo application, videos, Encoder, HLS and certificate paths are under `/srv/divinemedia/app`. Main and Encoder database volumes are under `/var/lib/docker/volumes` on the OS filesystem. A media-disk-only backup would not automatically capture both live databases.
- The NIC NSG's listed custom rules allow public inbound 80/443 and SSH from one `/32` source. Other bound ports are not permitted by those listed custom rules. This is not a complete effective-route/firewall penetration test.
- Both the public AVideo root and `/Encoder/` return HTTP 200. Reachability is not upload or encoding success.

## Backup findings

- No Recovery Services vaults, Data Protection backup vaults, disk snapshots or Azure Storage accounts were returned in the inspected subscription. This does not exclude protection in another account/subscription or an external provider.
- Local November 1 files include `avideo.sql.gz`, `encoder.sql.gz`, `videos.tar.gz` and `config.tar.gz`; their gzip integrity checks pass. That establishes compressed-file integrity, not application consistency, completeness, encryption, recovery objectives or restore success.
- A local `upload-restore-20261101T220406Z` directory exists and matches the earlier project reference. Its name alone is not restore-test evidence.
- Searches of the standard host cron paths and timer names found certificate renewal and OS package backups, but no identifiable application-backup schedule. Container schedules and external automation have not been exhaustively audited.
- There are 31 MP3/MP4 files with filesystem modification timestamps after November 1 (checked against November 2 00:00 UTC). The November 1 archive set is therefore not demonstrated to cover the current media state; timestamp comparison is not a content-level backup diff.
- No off-VM copy, retention policy, restore rehearsal or recovery time objective was established.

Priority: propose consistent database dumps plus media/config backups to separate protected storage, with retention and a restore rehearsal on an isolated host. Do not create or change backup jobs under this audit. Database credentials and configuration archives must never go into GitHub.

## Actual usage costs

Cost Management query: resource-group-filtered ActualCost / PreTaxCost, MonthToDate, grouped daily by resource type, currency USD. Recorded rows cover November 1–6, with November 6 incomplete.

| Resource type | Recorded month-to-date |
| --- | ---: |
| VM compute | $15.23 |
| Managed disks | $3.97 |
| Public IP | $0.72 |
| Total | $19.91 |

November 1–5 complete-day mean is $3.38/day, or approximately $101.40 for a 30-day month at the same usage. This is a run-rate estimate, not an Azure forecast or invoice. Sponsorship credit/balance, tax, future bandwidth, backup storage, and other subscriptions are not included. No sponsorship expiry or remaining credit was verified. A second always-on environment of comparable size would add broadly comparable compute/disk/IP usage, plus backup and transfer costs; price a concrete design before provisioning.

## Separate Upload / Encoder investigation

No upload, encode, thumbnail request, queue action or media modification was performed.

- Installed runtime reports PHP 8.5.4 CLI and FFmpeg 8.0.1. Compatibility with the deployed AVideo/Encoder release is not yet established.
- Encoder index and `objects/functions.php` pass PHP syntax checks; the Encoder directory exists. No FFmpeg process was present at observation. These findings do not establish queue health or successful conversion.
- Apache PHP configuration directives specify `upload_max_filesize=10G`, `post_max_size=10G`, `max_execution_time=7200`, `max_input_time=60`, and `memory_limit=512M`. These are inspected directives, not an effective browser request test; per-directory/application/proxy limits may also apply.
- CLI defaults instead report 2 MiB upload / 8 MiB POST limits. Those CLI values are **not evidence that web uploads are capped at 2 MiB**.
- Encoder log metadata shows last modification November 3 at 02:18 UTC. Log contents, credentials and user data are not copied into this report.
- A phrase-count scan of the historical Encoder log found zero occurrences of ten common failure strings (including conversion failed, permission denied and connection refused). This narrow scan is not a complete error audit and cannot establish successful jobs or current queue health.
- Exact application revisions, queue-state counts, authenticated upload behavior, callback delivery and successful output verification remain open. Public HTTP 200 and healthy containers cannot resolve those questions.

Next investigation should capture a specific failed-upload timestamp/error from the owner, inspect narrowly relevant sanitized log events and application revisions, and compare PHP/FFmpeg compatibility and callback configuration. Any controlled test upload or repair belongs on isolated staging first and requires a defined test asset, verified backups and rollback. Existing videos and thumbnail processing remain outside the repair scope unless separately approved.

## Staging recommendation and priorities

1. **Protect the current backend.** Verify a recoverable off-VM backup containing both databases, application configuration and media, then rehearse restore independently. Treat the current host as production-serving.
2. **Use Netlify previews for frontend-only work.** A second AVideo VM is not needed merely for React layout, catalog adapters or player changes that read the existing public API.
3. **Use isolated, on-demand backend staging for Upload/Encoder work.** Prefer a separate VM, disks, databases, hostname and credentials, restoring an authorized backup or a minimal test catalog. Start from the current 2-vCPU/8-GiB runtime for comparable behavior, then measure. Avoid cloned outbound callbacks, production queues, emails and thumbnail jobs. Do not point test uploads at the current host.
4. **Measure and cap staging cost before provisioning.** Choose an explicit budget, runtime schedule and retention. Deallocation can stop compute billing but leaves disk and some network charges. No deallocation or budget configuration was performed.
5. **Add monitoring in a separately reviewed change.** Alert on disk space, backup age/failure, sustained CPU/memory pressure and HTTP/service health. Keep encoding and backup I/O peaks in capacity decisions.

## Method and limits

Used Azure CLI list/show, Cost Management query POST (a read query), Azure Monitor metrics, public DNS/HTTP reads and Azure VM Run Command with read-only guest inspection scripts. Run Command uses Azure's guest execution mechanism and can leave platform execution records; application settings/services were not changed. No resource resize, stop, provisioning, registration, network rule change, database mutation, upload, encoding job or thumbnail operation was requested.

The VM diagnostic-settings read failed with an Azure message requesting `Microsoft.Insights` provider registration; provider metadata confirms `NotRegistered`. No provider registration was attempted. Metrics reads succeeded. Therefore diagnostic-setting configuration remains unverified rather than assumed absent.

Raw audit evidence stays in the cloud workspace outside Git. This report contains summarized observations only. The frontend feature PR is independent; this document does not authorize any production deployment or backend change.
