# Technical Reference

This file is the practical map of the local ContentFactory installation.

## Local Paths

- Project root: repository root
- SQLite DB: `db/factory.sqlite`
- DB schema: `db/schema.sql`
- FFmpeg: `ffmpeg` from `PATH`, or `tools/ffmpeg/bin/ffmpeg(.exe)`
- FFprobe: `ffprobe` from `PATH`, or `tools/ffmpeg/bin/ffprobe(.exe)`
- Assets: `assets`
- Batches/storyboards/subtitles: `batches`
- Draft renders: `outputs/drafts`
- Temporary render scripts/previews: `temp`

## Important Scripts

- `scripts/init_db.py`: create the local SQLite DB from schema.
- `scripts/migrate_asset_priority.py`: re-apply schema changes to an existing DB.
- `scripts/intake_assets.py`: index local media into the DB.
- `scripts/audit_asset.py`: add or inspect scene-level audit rows used by the ranker.
- `scripts/pexels_video.py`: search/download Pexels videos.
- `scripts/generate_elevenlabs_voice.py`: create `assets/voice/*.mp3` from script text via ElevenLabs and then run local transcription.
- `scripts/pick_assets.py`: rank assets, plan missing scenes, record storyboard usage.
- `scripts/transcribe_audio.py`: create local SRT/TXT from audio with faster-whisper.
- `scripts/add_idea.py` and `scripts/list_ideas.py`: simple idea helpers.

## Setup Commands

Create or refresh DB:

```bash
python3 scripts/init_db.py
python3 scripts/migrate_asset_priority.py
```

Index assets:

```bash
python3 scripts/intake_assets.py assets
```

Add a scene audit row:

```bash
python3 scripts/audit_asset.py add   --asset assets/raw/video/example.mp4   --role hook   --visual "Woman reacts to phone result"   --emotion shock   --themes "phone,reaction,quiz"   --score 4.5
```

Rank local assets for a scene:

```bash
python3 scripts/pick_assets.py rank --role hook --themes "phone,scroll,curiosity" --batch ubt-001 --limit 10
```

Record usage after keeping a draft:

```bash
python3 scripts/pick_assets.py record --storyboard batches/ubt-001/storyboard_example.json
```

Search Pexels:

```bash
python3 scripts/pexels_video.py search "woman phone astrology" --orientation portrait --per-page 10
```

Generate a voiceover from text and auto-create local SRT/TXT:

```bash
python3 scripts/generate_elevenlabs_voice.py --text-file projects/my-script.txt --overwrite
```

Transcribe audio locally:

```bash
tools/asr/.venv/bin/python scripts/transcribe_audio.py assets/voice/voice.mp3 --model small --language uk
```

Recommended for current Ukrainian voiceovers:

```bash
tools/asr/.venv/bin/python scripts/transcribe_audio.py assets/voice/voice.mp3 --model small --language uk --subtitle-mode words --max-subtitle-seconds 2.4 --max-subtitle-chars 42
```

On Windows, use the `.venv\Scripts\python.exe` path instead.

## Git Safety

This repo is separate from the website repo.

Git should track only the system: scripts, schema, generic docs, and empty folders. Do not commit:

- `.env`
- `db/factory.sqlite`
- `assets`
- `outputs`
- `batches`
- `temp`
- `tools`
- campaign-specific private materials

## Keys

Local keys live in `.env`.

Currently used by tracked scripts:

```text
PEXELS_API_KEY=
```

Reserved for adjacent workflows:

```text
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
```

Optional render override:

```text
CONTENTFACTORY_VOICE_FILE=
```

If set, render scripts use that audio file first. Otherwise they prefer `assets/voice/voice.mp3`, then fall back to older hardcoded files, then the newest mp3 in `assets/voice`.

Never commit `.env`.
