# Generation Workflow

This is the durable creative workflow. Use it before every serious render.

<<<<<<< HEAD
=======

## Project Boundary Rule

This ContentFactory project is isolated.

Work only inside:

- `/Users/mister/Documents/ContentFactory`

Never use `/Users/mister/Documents/New project` for ContentFactory sources, temp files, overlays, subtitles, renders, or exports.

Never modify the NeiroKid project while doing ContentFactory work unless the user explicitly switches tasks.

>>>>>>> 3e268fc (Add isolated ContentFactory workflow and render tooling)
Primary rendering spec for NeiroKid creatives:

- `reports/neirokid-video-rendering-requirements-v1.md`

If a generation choice conflicts with that rendering spec, follow the rendering spec.

## Core Order

1. Define script, hook, angle, CTA, target emotion, and target style.
2. Split the script into scenes or beats.
3. Search the local DB first.
4. If local assets are stale or missing, search Pexels.
5. Download only shortlisted Pexels clips.
6. Analyze and import new clips into the DB before final render.
7. Build a storyboard from indexed assets.
8. Render a draft.
9. Check the draft visually.
10. Record storyboard usage in the DB.
11. After publishing, record metrics and lessons.

## Default Style Variants

For one script, generate up to three visual lanes:

- `premium_mystic`: darker, polished, chart/planet/premium visuals.
- `quiz_product`: product-led, phone/site/quiz flow, clearer CTA.
- `emotional`: pain, loneliness, reflection, relationship or money stress.

Do not make all styles use the same opening visual pattern.

## NeiroKid Render Rule

For NeiroKid videos, do not treat visuals as decorative support.

Every spoken line should be backed by a matching visual beat.

Required structure for NeiroKid:

- first 3 seconds must show problem, strong emotion, or conflict;
- first 3-5 seconds must make the viewer instantly recognize: `це про мою дитину`;
- include the emotional ladder: problem -> recognition -> hope -> solution -> result;
- include visible mom presence, visible child state, visible solution, and visible result;
- avoid neutral beauty footage as an opener.

Use the detailed percentages, block requirements, and final render checklist from `reports/neirokid-video-rendering-requirements-v1.md`.

Additional non-negotiables for NeiroKid:

- use Ukraine-market-believable casting and context;
- do not fake social proof by floating reviews over unrelated footage;
- avoid repeated shots and repeated clip reuse;
- keep the montage moving fast, usually around 1.0-2.2 seconds per shot.

## Asset Rules

- Hook scenes should almost always use fresh or very strong assets.
- If a scene is marked stale/gap, use Pexels or write a manual override reason.
- Do not reuse a recently used hook asset without a reason.
- Do not use fresh Pexels in a final render before audit/import.
- Record usage after a draft is kept.

## Screen Recording Rule

Screen recordings are product moments, not ordinary lifestyle footage.

Allowed modes:

- `fullscreen_contain`: fit the whole recording into 1080x1920.
- `fullscreen_crop_safe`: crop only if important UI remains visible.
- `phone_mock/product_frame`: place the screen recording in a designed product frame.

Avoid:

- aggressive `cover` crop;
- cutting off buttons, date pickers, headers, or key UI text;
- zooming interface elements until they feel accidental;
- placing subtitles directly over important UI.

Before using a screen recording scene, extract a preview frame from the exact timestamp and verify readability.

## Final Delivery Rule

A ContentFactory render is not considered complete until the final delivery contains both:

- final video: `video_name.mp4`
- metadata sidecar: `video_name.creative.json`

This is mandatory for all videos produced by the flow.

Required behavior:

- generate the final MP4
- generate the matching `.creative.json` sidecar
- place both files next to each other in the final output folder
- keep `source_video` inside the JSON exactly equal to the MP4 filename
- do not mark the render `READY`, `FINAL`, or delivered if the sidecar is missing

The sidecar exists so downstream analysis, registry import, hypothesis mapping, and archival do not rely on filename guessing or speech-to-text reconstruction.

## CTA Rule

Use dedicated CTA backgrounds from the DB:

- `asset_type=generated_cta_background`
- `role=cta_background`

Read tags before rendering:

- `template_name`
- `style`
- `safe_zone`
- `button_zone`
- `avoid_zone`
- `text_contrast`
- `cta_layout`
- `motion_recipe`

Text, button, arrow, glow, and pulse are added in render. They should not be baked into generated backgrounds.

Do not place large random rectangles over random video frames for CTA. Make the final card feel designed.

## Subtitle Rule

Use one clear subtitle mode:

- full karaoke/TikTok subtitles, or
- short bullet subtitles.

Do not mix full subtitles and bullet subtitles without a reason.

For the current NeiroKid production flow, keep the existing subtitle pipeline:

1. generate or update the final voiceover;
2. generate timing from that voiceover;
3. build `ASS` subtitles;
4. burn subtitles into the final MP4 through FFmpeg `subtitles=...`.

Do not invent a replacement subtitle flow without explicit user approval.
Do not switch to image overlays, manual frame painting, or alternate subtitle engines if the existing `ASS` flow can be restored.

For screen recordings, move subtitles away from important UI or reduce them to compact bullets.

For `9:16` NeiroKid renders, subtitle phrases must be split into short semantic blocks so they fit comfortably on screen:

- one screen = one short thought;
- prefer `2-4` words per block;
- do not leave long full-sentence subtitle lines unbroken;
- if a phrase does not fit cleanly, split it before rendering instead of shrinking the whole style.

If ElevenLabs or another voice tool does not provide SRT, use **local faster-whisper** (default — do not use paid/trial ASR):

```powershell
F:\ContentFactory\tools\asr\.venv\Scripts\python.exe F:\ContentFactory\scripts\transcribe_audio.py F:\ContentFactory\assets\voice\voice.mp3 --model small --language uk --subtitle-mode words --max-subtitle-seconds 2.4 --max-subtitle-chars 42
```

Outputs `voice.srt` + `voice.txt` beside the audio. Models cache: `F:\ContentFactory\tools\asr\models`.

Run ASR on **every new or changed** `assets/voice/*.mp3` before building bullet ASS. Use SRT timestamps as timing truth; review Ukrainian wording before render. See `.cursor/rules/local-asr.mdc`.

If the default system `ffmpeg` lacks subtitle support, keep the same flow and use an `ffmpeg` binary that includes `libass`. This is still the same production flow, not a new one.

For this local project, the subtitle burn step may use the `imageio_ffmpeg` bundled binary because it includes `libass`.

## Language Rule

All production creative copy is Ukrainian for this project.

Russian is fine only for internal discussion and planning. Ukrainian text must be checked for natural wording before render.

## FFmpeg Safe Effects

Use by default:

- hard cuts;
- `fadefast` or `dissolve`;
- light pan/zoom on stills;
- per-scene color correction;
- ASS outline/shadow subtitles;
- CTA glow or subtle button emphasis.

Use carefully:

- one `hblur` transition per video;
- vignette;
- stronger color treatments;
- product insert layouts.

Avoid by default:

- novelty wipes;
- pixelize/radial/squeeze transitions;
- heavy global filters;
- chromakey without approved assets.
