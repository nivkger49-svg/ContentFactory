# AGENTS.md

## Purpose

This file defines mandatory instructions for any coding agent working on the
isolated Zernio publishing module inside:

- `/Users/mister/Documents/ContentFactory/publishing`

The goal of this layer is:

1. detect new ready `.mp4` videos
2. detect new prepared carousel folders
2. generate unique Ukrainian captions with a bio-link CTA
3. upload large media through Vercel Blob when needed
4. create scheduled Zernio posts in planner batches
5. attach Instagram first comments with unique UTM links at post creation time
6. generate tracked reel comment records after publication

This module should be understood and referred to as:

- `ContentFactory Zernio Publishing Module`

## Isolation Rule

Agents must work only inside:

- `/Users/mister/Documents/ContentFactory/publishing`

Agents must not modify:

- `/Users/mister/Documents/New project`
- `/Users/mister/Documents/neirokid-ads-agent`
- NeiroKid website frontend/backend
- unrelated ContentFactory render scripts unless explicitly requested

## Mandatory Reading

Before changing or running this flow, the agent must read:

- [README.md](/Users/mister/Documents/ContentFactory/publishing/README.md)
- [PLANNER_FLOW_RULES.md](/Users/mister/Documents/ContentFactory/publishing/PLANNER_FLOW_RULES.md)

The agent must not assume the planner flow from memory.

If the module was downloaded from git by a new agent, these files are the
required entry point and should be enough to start safely.

## Runtime Rule

Use the dedicated Python 3.12 environment for real planner work:

- `/Users/mister/Documents/ContentFactory/publishing/.venv-py312`

Do not rely on the system `python3` for Zernio/Blob planner execution, because
the system interpreter on this machine is Python 3.9 and the current SDK stack
was validated with Python 3.12.

## Environment Rule

Planner execution requires these local env values in:

- `/Users/mister/Documents/ContentFactory/publishing/.env`

Required:

- `ZERNIO_API_KEY`
- `ZERNIO_PROFILE_ID`
- `READY_CAROUSELS_DIR`
- `PUBLISH_MODE=schedule`
- `PLANNER_BATCH_SIZE=5`
- `MAX_POSTS_PER_DAY=2`
- `DAILY_POSTING_SLOTS=08:00,18:00`

Large video upload requires one of:

- `VERCEL_BLOB_TOKEN`
- `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN`
- optional explicit store id:
  - `BLOB_STORE_ID`
- Blob buffer controls:
  - `BLOB_BUFFER_MAX_BYTES=1073741824`
  - `BLOB_CLEANUP_INTERVAL_DAYS=2`
  - `BLOB_RETENTION_DAYS=2`

The agent must treat the second name as an accepted alias for the first.

## Planner Behavior Rule

- Every new `.mp4` in `../Видео_готовые_с_субтитрами/` must enter the queue.
- Every new valid carousel folder in `../Карусели_готовые/` must enter the same queue.
- Only the next 5 queued videos should be sent to planner in one run.
- The queue may contain both `reel` and `carousel` entries.
- Schedule only 2 posts per day.
- Captions must be in Ukrainian.
- Every caption must end with the current message CTA, not a profile-bio CTA.
- Caption wording should vary across videos.
- Remaining queued videos must stay in queue for the next run.

## Text Generation Rule

- Caption text must sound human, warm, and alive rather than templated.
- The meaning should not repeat from reel to reel; do not recycle the same core
  message with only minor wording changes.
- Text should talk to a parent, not mechanically describe the footage.
- Each caption should carry one clear useful idea:
  - reframe the child's behavior
  - reduce guilt
  - explain overload simply
  - point to a practical next step
- Use a small amount of emoji for rhythm, not decoration overload.
- Default target:
  - `1` emoji near the opening hook
  - optional second emoji only if it improves rhythm
  - avoid emoji spam and avoid putting emoji on every paragraph
- Standard CTA direction:
  the user should be prompted to write `опитування` or `додаток`.
- Preferred standard CTA family:
  `Хочете, щоб застосунок підібрав вправи саме під вашу дитину? 🌿 Напишіть «опитування» або «додаток».`
- CTA should still feel like a natural continuation of the text rather than a
  hard abrupt ad line.
- If metadata is weak, the agent should prefer a simple emotionally true text
  over padded generic motivational phrasing.

## Upload Rule

- Videos over 4MB cannot use Zernio direct upload.
- Carousel images over 4MB cannot use Zernio direct upload either.
- Large `.mp4` uploads must go through Vercel Blob via the SDK large upload flow.
- If a valid Blob token is missing, the agent must stop and report the blocker.

## Blob Buffer Rule

- Vercel Blob in this module is a temporary upload buffer, not permanent
  storage.
- Target active buffer size is `1 GB`.
- The worker must attempt cleanup every `2` days.
- Deletion rule:
  keep Blob media until at least `2` days after:
  - `scheduled_for` for scheduled posts
  - `published_at` for immediate publish runs
  - or `uploaded_at` when upload succeeded but post creation failed
- The worker must never delete Blob media for future scheduled posts.
- The worker must only delete Blob URLs that were tracked by this module under
  `_blob_buffer`.
- The worker must not scan the entire Blob store and must not delete unrelated
  Blob assets that were not created by this flow.
- Before a live upload, the worker should check projected active Blob usage.
- If the next upload would overflow the `1 GB` limit, the worker should force a
  cleanup pass first.
- If usage would still exceed the limit after cleanup, the worker must stop
  rather than risk breaking future scheduled media.
- Manual cleanup command:
  `./.venv-py312/bin/python scripts/cleanup_blob_buffer.py --force`

## Carousel Rule

- Carousel posts are image-only.
- Each carousel must contain between `2` and `10` images.
- Supported slide formats:
  - `jpg`
  - `jpeg`
  - `png`
  - `webp`
- Preferred structure:
  - one folder per carousel
  - `carousel.json` or `manifest.json`
  - `images/` subfolder with ordered slides
- If no slide list is declared in the manifest, the worker will infer images
  from the folder.
- Instagram carousel posts may use long human captions.
- TikTok carousel posts must not reuse the long Instagram caption as-is.
- For TikTok photo carousels, the short text should stay within about `90`
  characters because TikTok uses it like a slideshow title.
- The module must send TikTok carousel text through platform-specific
  `customContent`.
- Preferred manifest fields for TikTok-specific copy:
  - `tiktok_caption_override`
  - `tiktok_title`
  - `tiktok_hook`

## Platform Rule

- The currently validated connected targets are:
  - Instagram `neirokidapp`
  - TikTok `aineirokid`
- The default live flow should target both connected accounts unless the user
  explicitly requests otherwise.
- Exception:
  carousel posts require a TikTok-specific short text flow; if that short text
  is missing or broken, do not blindly send the Instagram caption to TikTok.
- Instagram-specific comment rule:
  all new and future scheduled Instagram posts must carry the quiz CTA as
  `platformSpecificData.firstComment` during `posts.create` or `posts.update`.
- TikTok note:
  the current validated SDK model does not expose `firstComment` for TikTok, so
  do not assume the same mechanism exists there.

## State Rule

The agent must use these files as operational state:

- `data/publishing-state.json`
- `data/publishing-queue.json`
- `data/published-log.json`
- `data/published-comments.json`

Instagram first-comment retrofit state may also be stored inside
`publishing-state.json` under:

- `instagram_first_comment`
- `instagram_first_comment_reference_at`

The agent must not manually wipe or rewrite historical records unless explicitly
requested.

## Execution Rule

For real planner submission, the agent should use:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
./.venv-py312/bin/python scripts/schedule_all.py
```

For preview only:

```bash
cd /Users/mister/Documents/ContentFactory/publishing
python3 scripts/dry_run.py
```

## Failure Rule

- Do not mark a video as scheduled unless Zernio confirmed post creation.
- If a run partially succeeds, keep unsent items in queue.
- If an API/SDK response shape changes, update the adapter layer in `src/`
  rather than working around it manually.
- If the console output crashes after successful scheduling, verify state/log
  before retrying planner submission.
- If reel comment publishing is unsupported for the live platform payload, the
  agent must still save the generated UTM link and comment text for manual
  posting/pinning instead of silently dropping tracking.
- If a post is not yet published and is still editable, the agent must prefer
  `platformSpecificData.firstComment` over any manual fallback path for
  Instagram.
- The sync flow must backfill both:
  - scheduled reels with `scheduled_comment_prepared`
  - old published reels with `manual_pin_required`

## First Comment Rule

- Instagram first comment is not a separate top-level field in this module.
- It must be passed per platform under:
  `platforms[].platformSpecificData.firstComment`
- For reels, the same Instagram platform object may also carry reel-specific
  options; firstComment remains nested inside that same
  `platformSpecificData` object.
- The first comment text must use the tracked quiz URL with unique UTM params.
- The module must generate the Instagram first comment before post creation so
  the comment can be attached during `posts.create`.
- For already-created future Instagram posts in planner, the agent should use:
  `./.venv-py312/bin/python scripts/retrofit_instagram_first_comments.py`
- This retrofit path applies only to future scheduled Instagram posts.
- Already published posts are not fixed by this mechanism.
