# ContentFactory Zernio Publishing Module

This folder contains an isolated Zernio publishing module for ContentFactory
reels and carousels. It does not modify the existing render pipeline, website
code, or other repositories. The module scans ready `.mp4` files and prepared
carousel folders, resolves metadata, generates Ukrainian captions, uploads
large media through Vercel Blob when needed, and then schedules or publishes
posts through the official Zernio Python SDK.

Default planner behavior:

- every new `.mp4` is added to the publishing flow automatically
- every new valid carousel folder is added to the publishing flow automatically
- the next 5 queued videos are pushed into the planner window
- scheduling uses 2 posts per day by default
- captions always include a CTA that asks people to write `опитування` or `додаток`
- captions should feel human, useful, and varied in meaning
- captions may use a small amount of emoji for rhythm, but not heavily
- TikTok carousel posts use a separate short text flow from Instagram
- Instagram posts can carry a tracked quiz CTA in the first comment through
  `platformSpecificData.firstComment`

## Quick Start

1. Open this module only:
   `/Users/mister/Documents/ContentFactory/publishing`
2. Read:
   - `AGENTS.md`
   - `PLANNER_FLOW_RULES.md`
   - this `README.md`
3. Use the validated Python 3.12 environment:
   - `./.venv-py312/bin/python`
4. Confirm local `.env` contains:
   - `ZERNIO_API_KEY`
   - `ZERNIO_PROFILE_ID`
   - `VERCEL_BLOB_TOKEN` or
     `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN`
   - `BLOB_BUFFER_MAX_BYTES=1073741824`
   - `BLOB_CLEANUP_INTERVAL_DAYS=2`
   - `BLOB_RETENTION_DAYS=2`
5. Run either:
   - preview: `python3 scripts/dry_run.py`
   - live planner batch:
     `./.venv-py312/bin/python scripts/schedule_all.py`

## First Run Checklist

- Confirm git root is `ContentFactory`
- Confirm you are not working in `New project` or `neirokid-ads-agent`
- Confirm `.env` exists locally and is not staged
- Confirm `PUBLISH_MODE=schedule` for planner work
- Confirm `DAILY_POSTING_SLOTS=08:00,18:00`
- Confirm the Blob token is available for videos over 4MB
- Confirm Blob buffer limit is `1073741824` bytes unless intentionally changed
- Confirm the active target platform is actually connected in Zernio
- Confirm carousel posts contain only images and between 2 and 10 slides
- Confirm TikTok carousel text stays within the short-title limit

## Known Live Setup

- Module name: `ContentFactory Zernio Publishing Module`
- Validated runtime:
- `publishing/.venv-py312`
- Validated connected platform:
  - Instagram `neirokidapp`
- First comment mechanism:
  - Instagram `platformSpecificData.firstComment`
- Current planner cadence:
  - `08:00` and `18:00` Bucharest time
- Queue policy:
  - next `5` videos at a time
- Posting density:
  - `2` videos per day

## Common Failure Cases

- Missing Blob token:
  large videos cannot upload, planner run must stop
- Wrong Python runtime:
  system Python 3.9 is not the validated live runtime
- SDK response shape mismatch:
  fix adapter code in `src/zernio_client.py` or `src/publish_worker.py`
- Connected account mismatch:
  do not assume TikTok exists unless the live Zernio account list confirms it
- Old duplicate scheduled post:
  inspect live scheduled posts before bulk rescheduling

## Isolation Rules

- Work only inside `ContentFactory/publishing/`.
- Read source videos from `../Видео_готовые_с_субтитрами/`.
- Read source carousels from `../Карусели_готовые/`.
- Read metadata from `../video_meta.json` when available.
- Fall back to per-video `*.creative.json` files next to the videos.
- Fall back to per-carousel `carousel.json`, `manifest.json`, or
  `<folder-name>.creative.json`.
- Keep API secrets in `.env`, never in code or committed files.

## Folder Layout

```text
publishing/
  AGENTS.md
  .env.example
  PLANNER_FLOW_RULES.md
  pyproject.toml
  README.md
  data/
    published-comments.json
    published-log.json
    publishing-queue.json
    publishing-state.json
  scripts/
    cleanup_blob_buffer.py
    dry_run.py
    publish_next.py
    retrofit_instagram_first_comments.py
    schedule_all.py
    sync_reel_comments.py
  src/
    __init__.py
    blob_buffer.py
    config.py
    generate_caption.py
    logger.py
    pinned_comment.py
    publish_worker.py
    read_video_meta.py
    scan_ready_carousels.py
    scan_ready_videos.py
    scheduler.py
    state_store.py
    zernio_client.py
```

## Setup

1. Use the dedicated Python 3.12 virtual environment for live planner work.
2. Install the package in editable mode.
3. Copy `.env.example` to `.env`.
4. Fill in `ZERNIO_API_KEY` and confirm the correct `ZERNIO_PROFILE_ID`.
5. If your videos are larger than 4MB, also add `VERCEL_BLOB_TOKEN`.
6. Install the `vercel` package in the same venv for Blob upload support.
7. Current validated planner slots are `08:00` and `18:00` in `Europe/Bucharest`.
8. Add comment UTM env values if you want default tracked reel comments:
   - `COMMENT_BASE_URL`
   - `COMMENT_UTM_SOURCE=facebook`
   - `COMMENT_UTM_MEDIUM=comment`
   - `COMMENT_UTM_CAMPAIGN=organic`

```bash
cd /Users/mister/Documents/ContentFactory/publishing
/Users/mister/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m venv .venv-py312
source .venv-py312/bin/activate
pip install -e .
pip install vercel
cp .env.example .env
```

## Agent Rules

Planner-specific agent rules are documented in
[AGENTS.md](/Users/mister/Documents/ContentFactory/publishing/AGENTS.md) and
[PLANNER_FLOW_RULES.md](/Users/mister/Documents/ContentFactory/publishing/PLANNER_FLOW_RULES.md).
These files are the operational playbook for how new videos enter the queue,
how the next 5 videos are sent to the Zernio planner, how 2-per-day scheduling
works, which Python runtime must be used, and when Blob upload is mandatory.

## Metadata Sources

The publisher tries sources in this order:

1. `VIDEO_META_JSON` if it exists and contains an array of video records.
2. `<video-name>.creative.json` next to each `.mp4`.
3. `carousel.json`, `manifest.json`, or `<folder-name>.creative.json` inside a
   carousel folder.

Supported metadata fields are normalized from either source:

- `file`
- `title`
- `voiceover`
- `angle`
- `cta`
- `hook`
- `offer`
- `pain`
- `language`

For carousels, the manifest can also contain:

- `slides`
- `images`
- `tiktok_caption_override`
- `tiktok_title`
- `tiktok_hook`

Each slide can be either a string path like `images/01.jpg` or an object with
`file`, `path`, `image`, or `image_file`.

## How To Add A Carousel

Create one folder per carousel inside:

- `/Users/mister/Documents/ContentFactory/Карусели_готовые`

Recommended structure:

```text
Карусели_готовые/
  sensory-overload-signs/
    carousel.json
    images/
      01.jpg
      02.jpg
      03.jpg
```

Example `carousel.json`:

```json
{
  "file": "sensory-overload-signs",
  "title": "5 ознак перевантаження нервової системи",
  "hook": "Іноді дитина не вередує, а вже перевантажена.",
  "angle": "коли вдома багато зривів і батькам важко зрозуміти причину",
  "pain": "після звичайного дня дитина різко зривається, а мама відчуває безсилля",
  "offer": "пояснення стану дитини і м'які нейровправи для щоденної підтримки",
  "cta": "Перейдіть у шапку профілю",
  "tiktok_caption_override": "Дитина не вередує навмисно. Часто причина глибша. Посилання в шапці профілю.",
  "language": "uk",
  "slides": [
    "images/01.jpg",
    "images/02.jpg",
    "images/03.jpg"
  ]
}
```

Carousel rules:

- only image slides are supported
- minimum `2` slides
- maximum `10` slides
- supported file types: `jpg`, `jpeg`, `png`, `webp`
- if `slides` is omitted, the worker will infer images from `images/` or the
  carousel root folder
- each new carousel folder enters the same planner queue as reels

## TikTok Carousel Rule

TikTok photo carousels do not use the same long caption flow as Instagram.
In live Zernio/TikTok behavior, the slideshow text acts like a short photo
title and must stay within roughly `90` characters.

Because of that, this module uses:

- full `caption` for Instagram
- short TikTok-only `customContent` for carousel posts

Resolution order for TikTok carousel text:

1. `tiktok_caption_override`
2. `tiktok_title`
3. `tiktok_hook`

## Instagram First Comment Rule

This module now treats Instagram first comment as part of the normal publishing
payload, not as a separate afterthought.

Implementation rule:

- first comment must be sent inside:
  `platforms[].platformSpecificData.firstComment`
- this applies to new Instagram reels and carousel posts created by this module
- the first comment text is generated from the quiz link template with unique
  UTM parameters
- the first comment is generated before post creation so the same text can be
  attached at `posts.create` time and also stored locally for traceability

Current scope:

- supported through this flow for Instagram
- not currently supported through the same field for TikTok

For already-created future Instagram planner posts, run:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
./.venv-py312/bin/python scripts/retrofit_instagram_first_comments.py
```

This retrofits `firstComment` into future scheduled Instagram posts that were
created before the rule was added.

Limit:

- already published posts are not fixed by this retrofit path
4. fallback derived from `hook` or `title`

If no explicit TikTok short text is provided, the module generates one
automatically and trims it to the safe limit.

## Blob Buffer Rule

This module now treats Vercel Blob as a temporary media buffer, not permanent
storage for planner assets.

- active Blob buffer limit: `1 GB`
- cleanup cadence: every `2` days
- retention rule: keep scheduled/published Blob media for `2` days after the
  reference time, then delete it
- reference time:
  - `scheduled_for` for scheduled planner items
  - `published_at` for immediate publish runs
  - fallback `uploaded_at` if post creation failed after upload

Safe behavior:

- future scheduled posts are not deleted early
- before every live upload, the worker checks projected Blob usage
- if the next upload would push the buffer above `1 GB`, the worker forces a
  cleanup pass
- if the buffer is still above limit after cleanup, the live run stops instead
  of silently overflowing temporary storage

Tracked Blob records are stored inside `data/publishing-state.json` under the
reserved `_blob_buffer` key.

Safety boundary:

- cleanup only touches Blob URLs that this publishing module itself tracked
- it does not scan the whole Blob store and does not delete unrelated assets

Manual cleanup command:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
./.venv-py312/bin/python scripts/cleanup_blob_buffer.py --force
```

## Modes

- `draft`: do not call Zernio, only prepare queue items and captions.
- `schedule`: upload media and create scheduled Zernio posts.
- `publish`: upload media and publish immediately.

## Commands

Dry run:

```bash
python3 scripts/dry_run.py
```

Schedule the next 5 queued videos using env defaults:

```bash
./.venv-py312/bin/python scripts/schedule_all.py
```

Publish the next queued video immediately:

```bash
./.venv-py312/bin/python scripts/publish_next.py
```

Sync scheduled and published reel comments and UTM records:

```bash
./.venv-py312/bin/python scripts/sync_reel_comments.py
```

Override mode for one command:

```bash
./.venv-py312/bin/python scripts/schedule_all.py --mode schedule
./.venv-py312/bin/python scripts/publish_next.py --mode publish
```

## State Files

- `publishing-state.json`: per-video state, caption hash, timestamps, external ids.
- `publishing-queue.json`: pending queue created by scans or dry runs.
- `published-log.json`: append-only history of scheduled or published items.
- `published-comments.json`: generated tracked reel comment records with UTM links.

Only the next planner window is scheduled at a time by default. Remaining reels
and carousels stay in `publishing-queue.json` and will be picked up
automatically on the next planning run, including newly added files.

## Zernio Notes

The integration uses the official Zernio Python SDK (`zernio-sdk`) and expects
connected Instagram/TikTok accounts inside the configured profile. By default,
the worker looks for `instagram` and `tiktok` accounts inside
`ZERNIO_PROFILE_ID`, but this can be overridden with `TARGET_PLATFORMS`.

The currently validated live connected targets are:

- Instagram `neirokidapp`
- TikTok `aineirokid`

The default live publishing flow should target both accounts.

Zernio direct upload works only for files up to 4MB. For normal `.mp4` video
publishing and large carousel images, add a `VERCEL_BLOB_TOKEN` so the worker
can call the SDK's large upload flow automatically. The env alias
`BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN` is also accepted.

## Reel Comment UTM Flow

For reels, the module now generates tracked follow-up comment records for both
scheduled and already published posts with:

- `utm_source=facebook`
- `utm_medium=comment`
- `utm_campaign=organic`
- unique `utm_content` per reel post

Comment base URL default:

- `https://mamabezkriku.com/public/vash-profil/`

Comment text template:

```text
💙 Не знаєте, які вправи підійдуть саме вашій дитині?

Пройдіть коротке опитування - додаток безкоштовно підбере вправи та ігри саме під вік і потреби вашої дитини.

👇 Почати можна тут:

{GENERATED_URL}
```

Important API constraint:

- The current Zernio SDK does not expose a proven direct `pin comment under reel`
  API.
- Scheduled reels receive prebuilt comment records with
  `status=scheduled_comment_prepared`.
- Already published reels receive fallback records with
  `status=manual_pin_required`.
- The module stores the final comment payload in `published-comments.json` even
  when comment publishing or pinning is unavailable.

## Safety

- `draft` mode is the default.
- If the API key is missing, API calls are blocked automatically.
- Files already marked as `scheduled` or `published` are skipped.
- The queue is idempotent per file name.
