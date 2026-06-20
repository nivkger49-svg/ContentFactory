# Content Factory Template

A local short-form video production workflow for testing hooks, scripts, assets, renders, and performance loops.

This repository contains the system only: scripts, database schema, operating rules, and folder structure. Bring your own assets, API keys, hooks, scripts, voiceovers, and metrics.

## What This Repo Tracks

- `scripts/`: database, intake, Pexels, asset ranking, scene audit, and utility scripts
- `db/schema.sql`: SQLite schema
- `reports/`: generic operating protocols and schemas
- `.env.example`: API key template
- empty working folders via `.gitkeep`

## Start Here

Read these files first:

- `GENERATION_WORKFLOW.md`: how to make a video from script to render.
- `TECHNICAL_REFERENCE.md`: local paths, commands, DB, FFmpeg, Git safety.
- `CREATIVE_LESSONS.md`: practical lessons from previous renders.
- `BACKLOG.md`: next tasks and future ideas.
- `reports/factory-operating-protocol.md`: durable detailed operating protocol.

## What This Repo Does Not Track

- real videos, images, voiceovers, and downloaded Pexels assets
- `db/factory.sqlite`
- `.env`
- local tools such as FFmpeg and the ASR virtual environment
- rendered outputs
- temporary files
- campaign-specific batches and subtitles

## Final Creative Metadata Rule

For every final video produced by the flow, the output is not complete unless both files exist side by side:

- `video_name.mp4`
- `video_name.creative.json`

This rule is mandatory for all final renders.

Do not treat a render as finished if only the MP4 exists.

The `.creative.json` sidecar must be created for every final video so downstream systems can reliably read:

- hook
- pain
- angle
- offer
- CTA
- voiceover text
- production status

If the final video is moved, copied, or archived, move the `.creative.json` file with it.

## Folder Layout

- `assets/raw/video`: source video clips
- `assets/raw/images`: source images
- `assets/raw/site-recordings`: owned screen recordings
- `assets/overlays`: reusable overlay PNG assets for reviews, pricing, CTA, and UI inserts
- `assets/generated/images`: generated image assets
- `assets/voice`: narration exports and SRT files
- `batches`: per-video storyboards, subtitles, and working files
- `outputs/drafts`: draft renders
- `projects`: campaign/project notes
- `references`: swipe files and source references
- `reports`: generic process docs and reusable operating rules
- `temp`: disposable working files

## First Workflow

1. Copy `.env.example` to `.env` and add API keys you plan to use.
2. Install FFmpeg so `ffmpeg` and `ffprobe` are available in `PATH`, or place them under `tools/ffmpeg/bin`.
3. Optional but recommended: install local ASR under `tools/asr` for SRT generation from audio.
4. Run `python3 scripts/init_db.py` once to create `db/factory.sqlite`.
5. Put your own assets into `assets/`.
6. Run `python3 scripts/intake_assets.py assets` to index local media.
7. Add scene-level usefulness rows with `python3 scripts/audit_asset.py add ...`.
8. Build a storyboard and rank assets with `python3 scripts/pick_assets.py`.
9. Render drafts through FFmpeg.
10. Record storyboard usage and publish metrics.

## Voiceover Flow

For a simple local narration flow:

1. Put `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` into `.env`.
2. Write your script into a `.txt` file.
3. Run:

```bash
python3 scripts/generate_elevenlabs_voice.py --text-file projects/my-script.txt --overwrite
```

This writes:

- `assets/voice/voice.mp3`
- `assets/voice/voice.source.txt`
- `assets/voice/voice.srt`
- `assets/voice/voice.txt`

Current render scripts now prefer `assets/voice/voice.mp3` automatically, so the new voiceover can flow into the next render step without renaming old files by hand.

## Background Music Rule

When background music is used:

- the voiceover is always the primary audio layer
- the voiceover must sound clearly louder than the background bed
- background music is secondary and should sit around `12-20%` volume by default
- trim the chosen music bed to a clean reusable segment if needed, then loop it to cover the whole video
- the music must fill the whole ролик without overpowering speech
- mix audio so the voice stays foreground: raise voice first, lower music second
- for FFmpeg mixes, avoid reducing speech through automatic normalization; keep the voice readable after the final mix
- if there is any conflict, lower the music first and keep the voiceover readable

## Overlay Rule

When the instruction is to "insert an overlay on video", use assets from `assets/overlays` by default unless a render batch explicitly overrides them.

Default overlay placement rules:

- review overlays: small, placed in the upper area of frame, shown for `5-7` seconds, never as full-screen replacement cards
- CTA overlay: use one CTA card at the end of the video
- pricing overlay: can stay through most of the video, but must not cover subtitles
- subtitles keep priority in the lower area; overlays must be moved upward or to corners so captions remain readable
- if both subtitles and overlays are present, avoid stacking overlays in the bottom third

Current reusable overlay files:

- `assets/overlays/reviews/review-1.png`
- `assets/overlays/reviews/review-2.png`
- `assets/overlays/pricing/price-13-uah-day.png`
- `assets/overlays/cta/get-personal-plan.png`
- `assets/overlays/cta/pass-survey.png`

## Core Rule

Do not store heavy media, secrets, SQLite data, or user-specific campaign materials in Git.

Do not create a new workflow or replace the current workflow without explicit user approval.


## Project Isolation Rule

ContentFactory is a fully separate project and must live only in:

- `/Users/mister/Documents/ContentFactory`

Hard prohibitions:

- do not create or use any ContentFactory folder inside `/Users/mister/Documents/New project`
- do not read from, write to, or store renders in `/Users/mister/Documents/New project` for ContentFactory work
- do not move ContentFactory outputs into the main NeiroKid project
- do not modify the main NeiroKid project while working on ContentFactory unless the user explicitly asks for a separate NeiroKid task

All ContentFactory assets, voiceovers, subtitles, overlays, temp files, and final videos must stay inside `/Users/mister/Documents/ContentFactory`.

## Unified NeiroKid Flow

For NeiroKid renders, keep one stable production flow:

1. put or update the script text in `projects/*.txt`
2. generate the voiceover into `assets/voice/voice.mp3`
3. place source footage into `assets/raw/video`
4. place site recordings into `assets/raw/site-recordings`
5. place reusable PNG overlays into `assets/overlays`
6. state the render balance in plain language, for example:
   - more own footage
   - less Pexels
   - more interface
   - more quiz
   - one review overlay
   - CTA only at the end
7. assemble the visual edit
8. add background music quietly under the voiceover
9. generate `ASS` subtitles from the final voice/script timing
10. burn the `ASS` subtitles into the final MP4
11. place final exports into `готовые-видео/...`

Do not create a parallel or replacement flow without explicit user approval.
If subtitle burning fails in the default system `ffmpeg`, use an `ffmpeg` binary with `libass` support but keep the same `ASS -> subtitles burn -> final MP4` pipeline.

## Git Remote Rule

This project is pushed to its own dedicated GitHub repository:

- `https://github.com/nivkger49-svg/ContentFactory.git`

Do not publish ContentFactory changes through the main NeiroKid repository.
Push ContentFactory only from this standalone project repository.
