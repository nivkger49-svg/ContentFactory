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
- captions always include a CTA that sends people to the profile bio link
- captions should feel human, useful, and varied in meaning
- captions may use a small amount of emoji for rhythm, but not heavily
- TikTok carousel posts use a separate short text flow from Instagram

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
- Confirm the active target platform is actually connected in Zernio
- Confirm carousel posts contain only images and between 2 and 10 slides
- Confirm TikTok carousel text stays within the short-title limit

## Known Live Setup

- Module name: `ContentFactory Zernio Publishing Module`
- Validated runtime:
  - `publishing/.venv-py312`
- Validated connected platform:
  - Instagram `neirokidapp`
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
    published-log.json
    publishing-queue.json
    publishing-state.json
  scripts/
    dry_run.py
    publish_next.py
    schedule_all.py
  src/
    __init__.py
    config.py
    generate_caption.py
    logger.py
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
4. fallback derived from `hook` or `title`

If no explicit TikTok short text is provided, the module generates one
automatically and trims it to the safe limit.

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

Override mode for one command:

```bash
./.venv-py312/bin/python scripts/schedule_all.py --mode schedule
./.venv-py312/bin/python scripts/publish_next.py --mode publish
```

## State Files

- `publishing-state.json`: per-video state, caption hash, timestamps, external ids.
- `publishing-queue.json`: pending queue created by scans or dry runs.
- `published-log.json`: append-only history of scheduled or published items.

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

## Safety

- `draft` mode is the default.
- If the API key is missing, API calls are blocked automatically.
- Files already marked as `scheduled` or `published` are skipped.
- The queue is idempotent per file name.
