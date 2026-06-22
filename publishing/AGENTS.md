# AGENTS.md

## Purpose

This file defines mandatory instructions for any coding agent working on the
isolated Zernio publishing module inside:

- `/Users/mister/Documents/ContentFactory/publishing`

The goal of this layer is:

1. detect new ready `.mp4` videos
2. generate unique Ukrainian captions with a bio-link CTA
3. upload large videos through Vercel Blob when needed
4. create scheduled Zernio posts in planner batches

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
- `PUBLISH_MODE=schedule`
- `PLANNER_BATCH_SIZE=5`
- `MAX_POSTS_PER_DAY=2`
- `DAILY_POSTING_SLOTS=08:00,18:00`

Large video upload requires one of:

- `VERCEL_BLOB_TOKEN`
- `BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN`

The agent must treat the second name as an accepted alias for the first.

## Planner Behavior Rule

- Every new `.mp4` in `../Видео_готовые_с_субтитрами/` must enter the queue.
- Only the next 5 queued videos should be sent to planner in one run.
- Schedule only 2 posts per day.
- Captions must be in Ukrainian.
- Every caption must contain a CTA that sends the user to the profile bio link.
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
- CTA must still point to the profile bio link, but it should feel like a
  natural continuation of the text rather than a hard abrupt ad line.
- If metadata is weak, the agent should prefer a simple emotionally true text
  over padded generic motivational phrasing.

## Upload Rule

- Videos over 4MB cannot use Zernio direct upload.
- Large `.mp4` uploads must go through Vercel Blob via the SDK large upload flow.
- If a valid Blob token is missing, the agent must stop and report the blocker.

## Platform Rule

- The currently validated connected target is Instagram account `neirokidapp`.
- TikTok is not currently validated in this profile and must not be assumed to
  work unless explicitly confirmed by the agent from live account data.

## State Rule

The agent must use these files as operational state:

- `data/publishing-state.json`
- `data/publishing-queue.json`
- `data/published-log.json`

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
