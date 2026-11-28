# Planet Derrty archive restoration

Private review of the owner's April/May 2009 Flash work and the supplied `planetderrty/songs` collection. This folder contains only the modern review-player source and metadata preparation tool. Original SWFs, MP3s, source manifests and emulator binaries stay outside Git and outside Netlify production.

## Local review

Prepare `tracks.json` with Python 3 and FFprobe:

```sh
python tools/planetderrty/prepare.py /path/to/review/original/songs /path/to/review
```

Copy `index.html`, `player.css` and `player.js` into that review directory. Serve it over localhost with `python -m http.server 4177 --bind 127.0.0.1 --directory /path/to/review`. Open `http://127.0.0.1:4177/`. Do not serve the private audio directory on a public interface.

## Recovery findings

- 31 MP3 files; 154,237,846 bytes; approximately 121.5 minutes. Source bytes are unchanged, with SHA-256 verification.
- Preserve the 28-song XML order, then append the three additional files. The original XML contains bare ampersands; parsing repairs apply only to a working text copy.
- Embedded MP3 tags supply titles, artists, album, year, track, genre and other available fields. Preserve all tags, technical stream metadata, legacy XML values, filename and hash. The XML repeatedly assigns four sets of credits to unrelated tracks; it is not reliable title/artist authority.
- `ThisGoesOut.mp3` is about 6.4 seconds and requires review before release. None of the MP3s contains attached cover artwork.
- April's 1.8 MB `derrtyplayer.swf` renders the blue City Free/St. Lunatics scene. May's 112 KB player renders the DJ-console design. The supplied `planetderrty.swf` is only 54 bytes. External media and historical navigation may be unavailable.
- Ruffle 0.8.0 runs unchanged SWF bytes in an isolated review wrapper; this is emulation, not Adobe Flash. The tested May build renders but has not demonstrated working XML/audio playback. Do not call it fully restored. Ruffle is loaded only for the original view, never the production homepage.
- The modern HTML audio player supports play/pause, previous/next, seek, volume, search, native metadata review, mobile layouts and reduced motion. It is a design/reference implementation, not a second production media catalog.

## Import and privacy

The owner selected **private for review**. Native imports must be inactive/private under the existing owner account, in a private native playlist, with download/share disabled. Never publish a new public audio route or static copy of the private tracks. Keep import hash-to-record mappings outside Git. Preserve existing files, playlists and thumbnails. A rerun must verify existing private imports and reuse their IDs, not duplicate records or change public content.

The native import retains tags and conflicting XML provenance in each record's description. Playlist order is distinct from the embedded album track number. The short source remains private and flagged. No fabricated release dates, composers, ISRCs, publishers or ownership claims are added.

## Verified review import

On November 27, 2026, all 31 files were imported as new native audio records under existing owner 1, status `i` (inactive/private), with download/share disabled. Native private playlist **372**, **Planet Derrty — Private Archive Review**, contains all 31 in the recovered order. Each original and stored MP3 was SHA-256 verified during import. Existing media and encoding/thumbnail queues were not modified. Use the signed-in frontend **Your playlists** or **Your media** to review; this branch does not deploy a public archive route.

The private local bundle includes unchanged SWFs, source audio, the original-review wrapper, Ruffle runtime/licenses and the modern player. Binary/audio artifacts are deliberately excluded from this repository. Recorded original views show rendering through emulation, not proof of legacy playlist playback.

## Hosted review page

`https://divinemedia.us/planet-derrty` presents the modern console design publicly; listening and archive metadata require the existing owner's sign-in. The page reuses the same platform account UI, private media-session grant, native creator catalog and origin authorization gate. There are no static MP3s or private metadata manifests in the frontend build. Only the original-design recording and its poster are public display assets.

Playback repair: the first import placed MP3s in the storage root, while this installed AVideo resolves them from `<filename>/<filename>.mp3`. The 31 new private records were repaired by copying hash-verified original bytes into their exact native paths and clearing only their source caches. Private status and playlist membership remain unchanged; existing media was not moved or modified.

### Production tracklist correction

The hosted page now checks permission on the private archive playlist, then reads its 31 known imported records through the existing authorized creator-record endpoint in batches of four. It no longer depends on the generic creator listing returning inactive drafts. The metadata decoder handles numeric HTML entities and named dash entities from native descriptions. No audio permissions, media files, Encoder jobs or speaker/turntable layout are changed by this frontend correction.

## Managed channel presentation

The owner chose a managed collection under the existing account, not a separate creator login. `/channel/planet-derrty` is the canonical frontend presentation; `/planet-derrty` remains a working alias. The profile appears in Creators and the channel directory. A shared presentation registry holds the public profile and references the existing private native playlist/records. It does not rename the DivineCreative native channel, transfer ownership, create a native user, invent follower counts, or grant public media access.

The page includes Music, Collection and About sections, the existing speakers/turntable player, and an owner-only entry to the existing media manager. Native AVideo remains authoritative for ownership, media and access. This first managed profile retains the approved recovered-record selection; automatic playlist membership editing/synchronization is not introduced by this visual setup.

Native terminology and the administrator/artist model are defined in [AVIDEO-CREATOR-CHANNEL-MODEL.md](../../docs/AVIDEO-CREATOR-CHANNEL-MODEL.md). The managed presentation is not an additional native user channel; independent artist login must use native AVideo user records and permissions. DivineCreative remains the managing administrator, and Murphy Lee is the first artist selected for that next integration.
