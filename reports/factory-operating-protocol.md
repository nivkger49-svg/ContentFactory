# Content Factory Operating Protocol

Last updated: 2026-06-17

This document is the durable workflow for the video factory. If the chat context is lost, start here.

For NeiroKid renders, the mandatory rendering spec is `reports/neirokid-video-rendering-requirements-v1.md`.

If a generation decision conflicts with a general creative preference, the NeiroKid rendering spec wins.

## Core Rule

Every creative render starts with asset selection, not with rendering.

Required order:

1. Define the script, hook, angle, CTA, and target emotion.
2. Search the local SQLite database for matching assets.
3. If local assets are not enough, search Pexels API for the missing scene types.
4. Download only shortlisted Pexels assets.
5. Analyze every new downloaded video before using it in a final render.
6. Import analysis into the database.
7. Build the shot plan from indexed assets.
8. Render the draft.
9. Save lessons and performance data after publication.

## Pexels Rule

Pexels is a fallback and expansion layer, not a blind bulk downloader.

Use Pexels when:

- the local library does not cover the needed emotion or scene;
- the current video repeats too many visuals from previous drafts;
- a script needs a specific scene, such as couple conflict, woman with phone, window fatigue, journaling, luxury planning, money stress, or mystical room atmosphere.

Do not:

- download large packs without creative need;
- use a fresh Pexels clip directly in a final render;
- assume a clip is useful before scene analysis.

## New Pexels Asset Intake

For every downloaded Pexels video:

1. Save it under a dedicated source folder, for example:

```text
F:\ContentFactory\assets\raw\video\pexels\YYYY-MM-DD
```

2. Preserve metadata when possible:

- Pexels video ID;
- author;
- URL;
- license/source;
- search query;
- download date;
- selected file quality.

3. Send the video to the analysis workflow before render use.
4. Add scene-level data to `asset_scenes`.
5. Mark useful tags:

- visible subject;
- action;
- emotion;
- topic fit;
- hook fit;
- safe text zones;
- possible role in video: hook, proof, bridge, CTA, background, insert.

## Agent Analysis Rule

Any externally sourced video that was not already audited must be analyzed before final render.

Minimum analysis:

- timeline segments with approximate timestamps;
- what happens in each segment;
- emotion and energy;
- whether it fits astrology/natal/relationship/money/self-analysis angles;
- whether the frame is safe for big subtitles;
- whether there are logos, watermarks, visible text, or distracting objects.

The final render should only use assets that are either:

- already in the database with enough scene notes; or
- newly analyzed and imported into the database during the current workflow.

## NeiroKid-Specific Render Gate

Before approving any NeiroKid storyboard or render, verify all of the following:

1. The first 3 seconds contain a visible problem, strong emotion, or conflict.
2. The first 3-5 seconds make the viewer feel: `це про мою дитину`.
3. At least one mom-focused emotional beat is present.
4. The child's state is visible, not just described.
5. The solution is shown on screen, not only mentioned in voiceover.
6. The result is shown on screen before the CTA or ending.

Minimum visual coverage targets for NeiroKid:

- real problem: at least 20%
- mom: at least 20%
- child: at least 30%
- solution: at least 20%
- result: at least 10%

Overlay rule for NeiroKid:

- one idea per overlay
- 2-6 words per overlay

If one of the required blocks is missing, the render is incomplete and should not pass final approval.

Strong hook disqualifiers:

- calm child play
- smiling mom without tension
- beautiful room shot
- app-first opening without problem context
- abstract cards before the real-life situation

Additional NeiroKid approval checks:

1. Casting and environment still feel believable for the Ukrainian audience.
2. Social proof appears as a real insert or dedicated review beat, not as a pasted overlay over unrelated footage.
3. The same clip or near-identical shot is not repeated without a deliberate reason.
4. The pacing stays quick enough that no beat feels static unless readability truly requires it.

## Visual Variety Rule

Before rendering, compare the planned shot list against recent videos.

Avoid repeating the same visual pattern unless it is intentional.

Check at least:

- first 3 seconds;
- dominant subject type;
- repeated phone footage;
- repeated natal chart footage;
- repeated journaling footage;
- repeated CTA style.

If the planned sequence looks too similar to the last one, search local DB first, then Pexels.

## Static Asset Rule

Static images are allowed only when they have a clear job in the storyboard.

Before opening folders manually, check the SQLite database and tags. Useful image roles include:

- `hook_background`
- `key_visual`
- `fullscreen_insert`
- `product_moment`
- `astro_overlay`
- `transition`
- CTA background

Good uses:

- final CTA screens;
- product explanation moments;
- site-native quiz/report visuals;
- planet/chart overlays;
- short visual reset between people clips;
- mood-setting opening cards when the hook needs a designed frame.

Avoid:

- using static images as generic filler;
- leaving a still image dead for several seconds;
- repeating the same generated CTA background across many drafts;
- covering a video frame with a large dim rectangle when a designed CTA screen would be cleaner.

Every static scene should have light motion or rhythm: slow pan, subtle zoom, overlay movement, glow, text timing, or a deliberate hard cut.

## Chromakey Rule

Chromakey is paused for normal production while the system is used mainly for personal/internal creatives.

Do not spend render time trying to force chromakey unless the asset is already approved as a phone mockup with a clean green phone screen. A person standing on a green background is not enough for product insertion.

Future chromakey assets should be marked separately and used only after a short 3-5 second test render.

## Asset Priority Rule

Use `scripts/pick_assets.py` before choosing final render assets when a storyboard is being built or revised.

Recommended flow:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py rank --role hook --themes "instagram,phone,scroll" --batch ubt-007 --limit 10
```

The ranker returns:

- `priority_score`
- `fit_score`
- `repeat_penalty`
- `variety_bonus`
- `decision`: `pick_local`, `stale`, or `gap`
- `pexels_recommended`

Rules:

- prefer high `priority_score`, not just high base `asset_scenes.score`;
- avoid assets with high repeat penalty unless manually locked for a reason;
- if decision is `gap` or `stale`, Pexels search is allowed;
- every downloaded Pexels video still needs intake and scene audit before final render;
- after a draft render, record storyboard usage so future renders can avoid repetition.

Record usage:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py record --storyboard F:\ContentFactory\batches\<batch>\storyboard_*.json
```

Storyboard format is documented in:

```text
F:\ContentFactory\reports\storyboard-schema.md
```

## CTA Rule

Final CTA should be designed as a deliberate final screen.

Preferred style:

- generated or branded background;
- no random video behind the CTA unless it directly supports the idea;
- large high-contrast text;
- local text backing only behind the words if needed;
- avoid large decorative rectangles until a polished template exists.
- prefer prepared generated/site backgrounds and product visuals over improvised full-frame dark overlays.

Default copy:

```text
ПОСИЛАННЯ В ОПИСІ
глянь свою карту прямо зараз
```

## Language Rule

All production creative text is Ukrainian. Russian can be used only in internal discussion and planning.

Ukrainian text must be checked for natural wording before render.

## Persistent Principle

The system should improve every time assets, hooks, scripts, and results are added.

Do not rely on chat memory for important rules. If a rule changes, update this document or a more specific report file.
