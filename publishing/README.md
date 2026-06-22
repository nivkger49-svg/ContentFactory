# ContentFactory Zernio Publishing Module

This folder contains an isolated Zernio publishing module for ContentFactory
videos. It does not modify the existing render pipeline, website code, or other
repositories. The module scans ready `.mp4` files, resolves metadata,
generates Ukrainian captions, uploads large videos through Vercel Blob when
needed, and then schedules or publishes posts through the official Zernio
Python SDK.

Default planner behavior:

- every new `.mp4` is added to the publishing flow automatically
- the next 5 queued videos are pushed into the planner window
- scheduling uses 2 posts per day by default
- captions always include a CTA that sends people to the profile bio link
- captions should feel human, useful, and varied in meaning
- captions may use a small amount of emoji for rhythm, but not heavily

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
- Read metadata from `../video_meta.json` when available.
- Fall back to per-video `*.creative.json` files next to the videos.
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

Only the next planner window is scheduled at a time by default. Remaining videos
stay in `publishing-queue.json` and will be picked up automatically on the next
planning run, including newly added files.

## Zernio Notes

The integration uses the official Zernio Python SDK (`zernio-sdk`) and expects
connected Instagram/TikTok accounts inside the configured profile. By default,
the worker looks for `instagram` and `tiktok` accounts inside
`ZERNIO_PROFILE_ID`, but this can be overridden with `TARGET_PLATFORMS`.

The currently validated live connected target is Instagram account
`neirokidapp`. TikTok should not be assumed live unless it is verified again.

Zernio direct upload works only for files up to 4MB. For normal `.mp4` video
publishing, add a `VERCEL_BLOB_TOKEN` so the worker can call the SDK's large
upload flow automatically. The env alias
`BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN` is also accepted.

## Safety

- `draft` mode is the default.
- If the API key is missing, API calls are blocked automatically.
- Files already marked as `scheduled` or `published` are skipped.
- The queue is idempotent per file name.
