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

## Folder Layout

- `assets/raw/video`: source video clips
- `assets/raw/images`: source images
- `assets/raw/site-recordings`: owned screen recordings
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

## Core Rule

Do not store heavy media, secrets, SQLite data, or user-specific campaign materials in Git.
