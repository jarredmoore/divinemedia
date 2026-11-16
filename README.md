# Divine Media

**Watch. Listen. Create.**

Divine Media is Divine Creative Group’s platform for publishing and discovering independent video and audio—films, performances, episodes, and creator releases. This repository contains the platform’s source code, frontend development, and operational documentation.

The viewing experience uses React and Vite. AVideo manages the media catalog, creator accounts, uploads, and publishing, with Encoder handling media preparation.

## Explore the platform

| Destination | Purpose |
| --- | --- |
| [Watch](https://divinemedia.us/) | Public viewing and listening experience |
| [Media](https://media.divinemedia.us/) | Branded entrance and media platform |
| [Creator upload](https://media.divinemedia.us/upload) | Direct upload for authorized creators; sign-in required |
| [Encoder](https://media.divinemedia.us/Encoder/) | Connect a media account, upload source files, and follow processing |

The previous Watch hostname redirects to `divinemedia.us`. Existing media URLs remain supported; creator sign-in and Encoder entry pages move to the new media hostname.

## How it fits together

| Component | Technology | Delivery |
| --- | --- | --- |
| Watch frontend | React 19, Vite 6, lucide-react | Netlify previews and production |
| Media platform | AVideo, PHP, Apache, MariaDB | Azure VM and Docker |
| Encoder | AVideo Encoder and FFmpeg | Azure backend |
| Source and review | GitHub branches and pull requests | This repository |

Published media stays in AVideo’s catalog. The frontend presents that catalog and plays its published media sources. Creator authentication, upload permissions, encoding, and thumbnail processing remain with the backend.

## Development and deployment

- **Repository homepage:** `master`. This branch contains the historical backend source and this overview.
- **Active integration branch:** [`dev/divine-media-3.1`](https://github.com/jarredmoore/divinemedia/tree/dev/divine-media-3.1). Current Watch frontend work starts here.
- **Production branch:** `production/divine-media`. Changes or merges require explicit approval.
- **Feature work:** small, reversible changes on separate branches, reviewed through pull requests.

GitHub is the source of truth. Netlify handles frontend previews and production delivery; Azure hosts AVideo and Encoder. A merged pull request and a deployed release are separate steps—verify the deployed source and rollback reference for each service.

Existing videos and thumbnail processing must be preserved. Backend changes need a verified backup, a scoped deployment plan, and a rollback path. Keep credentials and private runtime configuration out of commits, frontend bundles, and logs.

### Run the Watch frontend locally

Use Node.js 22 and npm. The frontend lives on the development branch, rather than the repository homepage branch.

```sh
git clone https://github.com/jarredmoore/divinemedia.git
cd divinemedia
git switch dev/divine-media-3.1
cd frontend
npm install
npm run dev
```

Build and inspect the production frontend locally:

```sh
npm run build
npm run preview
```

Validate API responses, media playback, navigation, and mobile layouts in a frontend preview before production promotion.

## Requirements

### Current Divine Media stack

| Area | Requirements |
| --- | --- |
| Frontend development | Node.js 22, npm, React 19, Vite 6, and a modern browser |
| Backend hosting | Linux, Docker, Apache 2.x with `mod_rewrite`, PHP with the extensions required by the deployed AVideo version, and MariaDB/MySQL-compatible databases |
| Media preparation | AVideo Encoder, FFmpeg/FFprobe, temporary working storage, and access to the media platform |
| Public delivery | HTTPS endpoints for the frontend, media platform, and Encoder |
| Operations | Persistent media/database storage, off-VM backups, restore verification, and deployment rollback references |

The November 7, 2026 backend audit verified PHP 8.5.4, MariaDB 13.0.2, and FFmpeg 8.0.1 in the deployed containers. These are observed runtime versions, not a claim that the older repository Dockerfile reproduces the current installation. Check the deployed configuration and version-specific AVideo requirements before backend work.

### Historical upstream server requirements

The original README listed these minimums. They are retained for historical reference; use the current Divine Media stack above for ongoing work.

- PHP 5.6+
- MySQL 5.0+
- Apache web server 2.x (with mod_rewrite enabled)

See the [AVideo administrator manual](https://github.com/WWBN/AVideo/wiki/Admin-manual) and [Encoder repository](https://github.com/WWBN/AVideo-Encoder) for upstream installation guidance.

## Version history

### Divine Media

| Version / milestone | Status and scope |
| --- | --- |
| **3.3 — Viewer foundation released** | Canonical domains, audio/player fixes, branded media entrance and creator workspace, plus selectable Default and Code Black viewing themes. Production promotion was approved and completed through PR #11. Broader native account/plugin integration continues separately in PR #12. |
| **3.1 — Development baseline, November 1, 2026** | Established `dev/divine-media-3.1` from the existing Divine Media frontend work. Upload, thumbnail display, and playback were confirmed working as the baseline for the Watch redesign. |
| **2.x — Earlier frontend foundation** | Existing Watch development on `divine-media-2`, carried forward into the 3.1 integration branch. |

Current work and implementation details:

- [Audio discovery and playback — PR #2](https://github.com/jarredmoore/divinemedia/pull/2)
- [Azure audit — PR #3](https://github.com/jarredmoore/divinemedia/pull/3)
- [Backup and recovery tooling — PR #4](https://github.com/jarredmoore/divinemedia/pull/4)
- [Branded entrance and login — PR #5](https://github.com/jarredmoore/divinemedia/pull/5)
- [Creator workspace — PR #6](https://github.com/jarredmoore/divinemedia/pull/6)
- [Canonical domains and integrated 3.3 foundation — PR #8](https://github.com/jarredmoore/divinemedia/pull/8)
- [Code Black viewing theme — PR #10](https://github.com/jarredmoore/divinemedia/pull/10)
- [Approved production release — PR #11](https://github.com/jarredmoore/divinemedia/pull/11)
- [Native feature activation and free/paid plugin audit — PR #12](https://github.com/jarredmoore/divinemedia/pull/12)

Project references on the integration branch: [Project charter](https://github.com/jarredmoore/divinemedia/blob/dev/divine-media-3.1/PROJECT.md), [experience direction](https://github.com/jarredmoore/divinemedia/blob/dev/divine-media-3.1/EXPERIENCE_DIRECTION.md), and [changelog](https://github.com/jarredmoore/divinemedia/blob/dev/divine-media-3.1/CHANGELOG.md). These documents describe their recorded baseline; the linked pull requests contain subsequent work.

### AVideo upstream history

The release notes below are preserved from the original README. These are **AVideo versions**, separate from Divine Media’s version numbers. References to an “upcoming version” describe the historical upstream roadmap.

<details>
<summary>Expand the original AVideo release notes (5.6 through 3.4.1)</summary>

# In the upcoming version (already in the code on the master branch)
- Better support for Nginx and Microsofts IIS (experimental)

# Version 5.6
- Google analytics per user

# Version 5.5
- Bugfixes & improvements
- Introduce new video-types (linkVideo and linkAudio)
- LiveLinks-Plugin

# Version 5.4
- Wavesurfer-visualisation for audio
- Add dynamic /help-page (also useful for admins)
- Embeded videos from youtube are in a native player now (allow plugins for it)
- New options in advancedcustomised-plugin (minify js, disable add + share-button, disable the above player)
- Backend-work and tons of fixes for it
- Better translations (de,es,us,tr)
- Import videos from filesystem

# Version 5.3
- User now can Verify Emails and Choose the Channel Name

# Version 5.2
- Subscribers now can choose to not be notified from new videos (Need the Notification Plugin)

# Version 5.01
- Category now can have a parent category (enables subcategories)
- Direct upload and various plugins supports audio
- Type for categories

# Version 5.0
- Allow Download and disable youtubeupload on configuration menu
- Category Description
- Category Next Video Order

# Version 4.9
- Increase SMTP fields space to be able to store largers passwords

# Version 4.8
- Add preferred videos that will randomly appear on first page

# Version 4.7
- Add Channels Browser
- Add User about field, to be used in their channels

# Version 4.6
- Improve comments system.
- like/dislike comments
- reply comments

# Version 4.5
- Set Upload permition for specific users

# Version 4.4
- Next video set-able
- Play List Sortable

# Version 4.3
In this version registered users need the AVideo administrator to grant them permission to transmit streams

# Version 4.2
In this version you can embed Youtube and Vimeo Links

# What is new on this version 4.0?
Since version 4.x+ we separate the streamer website from the encoder website, so that we can distribute the application on different servers.
- The Streamer site, is the main front end and has as main function to attend the visitors of the site, through a layout based on the youtube experience, you can host the streamer site in any common internet host can host it (Windows or Linux).
- The Encoder site, will be better than the original encoder, the new encoder will be in charge of managing a media encoding queue. You can Donwload the encoder here: https://github.com/WWBN/AVideo-Encoder. but to install it you will need ssh access to your server, usually only VPS servers give you that kind of access, that code uses commands that use the Linux shell and consume more CPU.
- I will have to install the encoder and the streamer?
No. We will be providing a public encoder, we will build the encoder in such a way that several streamers can use the same encoder. We are also providing source code for this, so you can install it internally and manage your own encoding priority.

<div align="center">
<img src="https://platform.avideo.com/website/assets/151/images/chalkboard.png">
<a href="https://github.com/WWBN/AVideo-Encoder" target="_blank">Download Encoder</a>
</div>

# Older version
If you want the old version with Streamer and Encoder together (Version 3.4.1) download it <a href="https://github.com/WWBN/AVideo/releases/tag/3.4.1">here</a>


</details>

## Upstream acknowledgments and licensing

Divine Media builds on [AVideo](https://github.com/WWBN/AVideo) and [AVideo Encoder](https://github.com/WWBN/AVideo-Encoder), developed by WWBN and the upstream community. AVideo was formerly known as YouPHPTube; legacy names remain in parts of the codebase.

AVideo is a trademark of World Wide Broadcast Network, Inc. Existing copyright, trademark, and third-party license notices remain applicable. See the repository’s [LICENSE](LICENSE) and [upstream licensing information](https://platform.avideo.com/AVideo_OpenSource).
