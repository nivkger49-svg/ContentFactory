# Planner Flow Rules

These rules define how the isolated `ContentFactory/publishing` layer must work
with the Zernio planner.

## Mandatory Entry Point

- Any future agent working on this flow must first read:
  - `AGENTS.md`
  - `README.md`
  - this file

## Scope

- Work only inside `/Users/mister/Documents/ContentFactory/publishing`.
- Read ready videos only from:
  `/Users/mister/Documents/ContentFactory/Видео_готовые_с_субтитрами`
- Do not touch website repositories, NeiroKid frontend/backend, or other
  projects.

## Source of Truth

- A video is eligible when a new `.mp4` appears in the ready videos folder.
- Metadata is resolved in this order:
  1. `VIDEO_META_JSON`
  2. matching sidecar `*.creative.json`
- A video already marked as `scheduled`, `published`, or `published_now` in
  `publishing-state.json` must not be queued again.

## Queue Rules

- Every new `.mp4` must automatically enter the publishing flow.
- `publishing-queue.json` is the working queue for unsent videos.
- Existing queued items must refresh their generated caption on every new run,
  so the queue always reflects the latest caption rules.
- The queue is persistent. If only part of the queue is sent to the planner,
  the rest stays queued for the next run.

## Planner Window

- Send only the next `5` queued videos into the planner at a time.
- This is controlled by `PLANNER_BATCH_SIZE=5`.
- Remaining queued videos wait for the next planner run.
- When new `.mp4` files appear later, they must join the same queue
  automatically without manual intervention.

## Posting Cadence

- Plan `2` videos per day.
- Default local posting slots:
  1. `08:00`
  2. `18:00`
- This is controlled by:
  - `MAX_POSTS_PER_DAY=2`
  - `DAILY_POSTING_SLOTS=08:00,18:00`
- Scheduling should always fill the next available slot while respecting the
  daily limit.
- In current planner output this corresponds to UTC times:
  - `07:00:00+00:00`
  - `15:00:00+00:00`
  while timezone remains `Europe/Bucharest`.

## Caption Rules

- Each planned video must have a unique Ukrainian caption.
- Captions should use metadata such as title, hook, pain, angle, offer, and
  voiceover when available.
- Every caption must end with a CTA that points users to the link in the
  profile bio.
- CTA wording should vary across videos, but the action must remain the same:
  go to the profile bio link.
- Hashtags may remain consistent if needed, but the main descriptive text and
  CTA should not be duplicated across the planner window.
- Captions must be written for people, not as a dry visual description of the
  reel.
- The central meaning should not repeat across reels. Vary the takeaway:
  guilt, overload, regulation, support, first step, understanding, calm, daily
  routine, emotional safety, or practical relief.
- Each caption should feel specific and emotionally believable.
- Use a small amount of emoji for rhythm:
  - usually one emoji near the first line
  - sometimes a second emoji if it genuinely improves the pacing
  - never turn the caption into emoji-heavy copy
- Avoid overly generic filler such as empty reassurance without a concrete
  parent insight.

## Planner Mode

- Default safe mode is `draft`.
- Real planner submission uses `PUBLISH_MODE=schedule`.
- Immediate posting uses `PUBLISH_MODE=publish`, but should not be used for the
  normal planner flow.
- Real planner execution should use:
  - `/Users/mister/Documents/ContentFactory/publishing/.venv-py312/bin/python`
- Normal agent behavior for planner work:
  1. scan queue
  2. refresh captions
  3. plan next 5
  4. send them to Zernio as scheduled posts

## Large Video Upload Rule

- Zernio direct upload works only for files up to `4MB`.
- Most real `.mp4` videos in this project are larger than that.
- For large files, the agent must use the SDK large upload flow via
  `VERCEL_BLOB_TOKEN`.
- `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN` is accepted as an alias source for
  the same token.
- If `VERCEL_BLOB_TOKEN` is missing, the agent must stop before planner
  submission and report that large-file upload is blocked.
- The SDK also requires the Python package `vercel` in the active environment.

## Required Environment

- `ZERNIO_API_KEY`
- `ZERNIO_PROFILE_ID`
- `VERCEL_BLOB_TOKEN` for large videos
- or `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN` as an accepted alias for the same token
- `PUBLISH_MODE=schedule`
- `PLANNER_BATCH_SIZE=5`
- `MAX_POSTS_PER_DAY=2`
- `DAILY_POSTING_SLOTS=08:00,18:00`
- `TIMEZONE=Europe/Bucharest`

## Validated Runtime

- Use Python 3.12 from:
  `/Users/mister/Documents/ContentFactory/publishing/.venv-py312`
- The system Python 3.9 is not the validated runtime for the live planner flow.

## Validated Platform Target

- The currently validated connected social account is Instagram:
  - username: `neirokidapp`
  - profile id: `6a3807977183d73693c67dae`
- TikTok is not currently validated in the live profile and must not be assumed
  available without a fresh check.

## State Files

- `data/publishing-state.json`
  stores per-file status, hashes, scheduled time, and external ids
- `data/publishing-queue.json`
  stores queued items waiting for planner submission
- `data/published-log.json`
  stores append-only planner/publish history

## Standard Agent Runbook

1. Read `.env` and verify `ZERNIO_API_KEY`, `ZERNIO_PROFILE_ID`, and
   `VERCEL_BLOB_TOKEN`.
2. If `VERCEL_BLOB_TOKEN` is empty, check
   `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN`.
3. Use the Python 3.12 venv for live planner commands.
4. Verify planner mode is `schedule`.
5. Scan the ready videos folder for new `.mp4` files.
6. Resolve metadata from `video_meta.json` or `*.creative.json`.
7. Refresh queued captions so current CTA rules apply.
8. Build the next planner window of `5` videos.
9. Schedule only `2` videos per day into the next available planner slots.
10. Upload media through Zernio.
11. If file size exceeds `4MB`, switch to large upload using Blob token.
12. Create scheduled Zernio posts, not immediate publishes.
13. Update `publishing-state.json`, `publishing-queue.json`, and
    `published-log.json`.
14. Verify the scheduled items were recorded in state/log.

## Canonical Commands

Dry preview:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
python3 scripts/dry_run.py
```

Live planner batch:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
./.venv-py312/bin/python scripts/schedule_all.py
```

Single immediate publish:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
./.venv-py312/bin/python scripts/publish_next.py --mode publish
```

## Known SDK/Adapter Facts

- The current Zernio SDK returns many responses as Pydantic models, not plain
  dicts.
- Account objects use `field_id` in several places instead of `id`.
- Post creation must use `media_items`, not `media_urls`.
- Large uploads require the `vercel` Python package in the venv.
- If the scheduling script prints a serialization error after scheduling work,
  verify state/log before retrying because post creation may already have
  succeeded.

## Writing Quality Check

Before sending a planner batch, the agent should quickly sanity-check:

1. Would this read naturally in a reel caption?
2. Is it talking to a parent rather than narrating the video?
3. Is the core meaning different from nearby queued reels?
4. Is there practical value or emotional relief in the text?
5. Are emojis present but restrained?

## Failure Handling

- If planner submission fails before a video is scheduled, keep the video in the
  queue.
- Do not mark a video as `scheduled` unless Zernio confirms post creation.
- If upload is blocked by missing large-file token, do not remove the item from
  the queue.
- If only some of the 5 videos succeed, preserve the remaining unsent items for
  the next run.
- If an SDK field shape changes, fix the adapter in `src/zernio_client.py` or
  `src/publish_worker.py` instead of editing state by hand.
