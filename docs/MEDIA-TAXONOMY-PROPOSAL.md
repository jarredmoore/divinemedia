# Divine Media taxonomy proposal

Status: review draft, November 19, 2026. No category, content assignment or URL changes have been applied.

Use a small creator-facing category tree, plus independent metadata fields for work type, format and genre. There is no single category list shared by every streaming/distribution service. The portable part is a stable internal vocabulary with explicit mappings to each destination.

## Standards and their roles

| Reference | Use in Divine Media | What it does not determine |
| --- | --- | --- |
| U.S. Copyright Office work types | Describe the kind of work and distinguish rights in recordings, compositions, audiovisual work, writing and artwork | Genre, navigation, ownership or permission to stream |
| Schema.org CreativeWork and MediaObject types | Public semantic metadata: work, creator, genre, language, license, recording and encoding relationships | A universal genre list or legal registration decision |
| DDEX | A later music-distribution exchange mapping for recordings, releases, parties and rights data | A replacement for the full site taxonomy; mapping is not certification or a completed delivery integration |
| PBCore | Audiovisual cataloging and the separation of an intellectual asset from its technical instantiations | A consumer streaming genre taxonomy |

A music composition and a sound recording are distinct works. A music video is an audiovisual work even when it contains a recording and a composition. One upload can therefore have several related works/rights records. Do not infer copyright ownership from a file type, genre, uploader identity or YouTube channel.

## Preserve the current structure

Existing IDs and paths stay unchanged:

- Media (#1)
  - Audio (#4)
    - Music (#3)
      - Hip Hop (#7)
      - Rhythm and Blues (#2; preserve the existing `rythem-and-blues` slug until any approved migration provides an alias)
  - Video (#5)
    - Film (#6)

Keep this working tree for now. Suggested future navigation additions, subject to review:

| Existing family | Additional creator-facing collections |
| --- | --- |
| Audio | Podcasts; Audiobooks; Spoken Word; Radio Programs; Sound Design |
| Video | Television; Music Videos; Short-form; Interviews & Talk; Recorded Performances; Educational; Promotional |
| New Image branch | Photography; Artwork & Illustration; Graphics; Covers & Thumbnails |
| New Documents branch | Articles; Scripts; Lyrics; Scores; Production Documents |

These are discovery collections. They do not replace the structured semantic fields below. A television documentary, for example, can have collection Television, format Episode and genre Documentary without duplicating a large category subtree.

## Creator fields and semantic mappings

| Creator choice | Internal meaning | Schema.org direction | Copyright Office work-type direction |
| --- | --- | --- | --- |
| Song / music recording | Recorded performance/master | MusicRecording, with an AudioObject for the encoding; recordingOf links a MusicComposition when known | Sound recording; underlying composition is separately identified |
| Musical composition / lyrics | Underlying musical work | MusicComposition; lyrics/lyricist when applicable | Performing arts/musical composition; choose the actual filing based on the submitted work |
| Album / EP / single release | Release grouping; not the audio file itself | MusicAlbum and its recordings | Identify the actual works and any applicable registration option, not an automatic category-to-filing conversion |
| Film / music video | Audiovisual work | Movie where appropriate, plus VideoObject for the encoding; otherwise VideoObject/CreativeWork | Motion picture or other audiovisual work |
| TV program / episode / series | Program and episode relationships | TVSeries / TVEpisode plus VideoObject | Audiovisual work for the recorded program |
| Podcast / interview | Series/episode and its recording | PodcastSeries / PodcastEpisode with AudioObject or VideoObject | Sound recording or audiovisual work; scripts may have separate authorship |
| Radio program | Program/series and audio recording | RadioSeries / RadioEpisode with AudioObject | Recording and any underlying authored work are assessed separately |
| Photograph / artwork | Visual work and its image encoding | Photograph / VisualArtwork with ImageObject | Visual arts/photograph, as appropriate |
| Article / document | Written work and document encoding | Article or DigitalDocument | Literary work, where applicable |
| Recorded live performance | An event and its fixed recording | Event / MusicEvent / BroadcastEvent related to the appropriate recorded work | Classify the fixed recording and underlying works; Live itself is not a rights class |

Schema.org has overlapping types, so mappings may be combinations rather than one exclusive type. Use a precise subtype only when creator-supplied facts support it.

## Separate facets rather than deeper paths

- **Media family:** audio, video, image, document. Derive from the actual file/asset, not the title.
- **Work type:** recording, composition, audiovisual work, visual work, written work. Keep related works separate.
- **Format:** track, album, episode, series, feature, short, clip, music video, interview, tutorial, commercial, still image, document. It is possible to have more than one descriptive format.
- **Genre:** Hip Hop, Rhythm and Blues, Documentary, Comedy, Drama, etc. Use stable concept IDs, display names and aliases. Avoid assuming a genre has an exact equivalent at every distributor.
- **Subjects/keywords:** optional search labels; the new native Keywords group can serve this purpose, not as a substitute for all semantic fields.
- **Delivery:** on demand, live, scheduled/linear, catch-up; embed versus hosted is an asset/source property. Live, YouTube and MP4 are not genres.
- **Technical metadata:** MIME type, container/codec, duration, dimensions, aspect ratio, bytes, audio channels/sample rate and caption availability, from media inspection where possible.
- **Contributors and rights:** creator, performer, composer, lyricist, producer, director, publisher, copyright holder, license, territories and license dates. A contributor role does not imply ownership.

Use BCP 47 language tags, ISO 8601 dates/durations and ISO 3166 territory codes. Keep internal file sizes numeric in bytes; serialize to a destination's expected representation. Accept optional assigned identifiers such as ISRC for recordings, ISWC for compositions, UPC/EAN for releases and EIDR for audiovisual works where appropriate. Never invent an industry identifier.

## Cross-platform mapping design

Store a versioned record for each concept: stable internal ID, label, definition, aliases, parent concepts, standard mappings, destination mappings, version and provenance. External mappings must record whether they are exact, broader, narrower or approximate. Destination-specific code lists remain adapters: changing one distributor's list must not rename native categories or force every creator to recategorize content.

Separate the work from its encodings: one recording may have an original upload, MP3, HLS output, cover art and an external embed. They remain related assets of the same work. Keep private/license/internal metadata out of public JSON-LD; export only information intended for public discovery.

## Review and migration sequence

1. Approve terminology and a small initial set of work types/formats/genres.
2. Inventory current category assignments and preserve all IDs, slugs and share links.
3. Add optional fields through native models/plugins where they fit. Do not overload permission/monetization tag groups or create a parallel content database just for navigation.
4. Treat mappings from current categories as suggestions. Audio → Music → Hip Hop can suggest a genre, but does not prove every item is a particular work type or establish rights.
5. Let creators review their own classifications. Add public Schema.org output only after validation and visibility checks.
6. Validate mapping adapters for the actual distributors selected later. DDEX implementation, registration submissions and delivery to streaming services are separate projects.

## Sources reviewed

- [Copyright Office registration portal](https://www.copyright.gov/registration/)
- [Performing arts registration](https://www.copyright.gov/registration/performing-arts/)
- [Motion pictures and audiovisual works](https://www.copyright.gov/registration/motion-pictures/)
- [Schema.org CreativeWork](https://schema.org/CreativeWork), [VideoObject](https://schema.org/VideoObject), [AudioObject](https://schema.org/AudioObject)
- [MusicRecording](https://schema.org/MusicRecording), including recordingOf and isrcCode; [MusicComposition](https://schema.org/MusicComposition), including iswcCode and lyrics
- [DDEX standards](https://ddex.net/standards/)
- [PBCore](https://pbcore.org/) and its [data model](https://pbcore.org/data-model)
