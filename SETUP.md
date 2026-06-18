# Setup Notes

These instructions now work for macOS/Linux as well as Windows. Use repository-relative paths if your clone lives somewhere else.

## FFmpeg

Install FFmpeg so both `ffmpeg` and `ffprobe` are available in your shell `PATH`.

macOS with Homebrew:

```bash
brew install ffmpeg
```

Windows options:

1. Install FFmpeg globally and add it to `PATH`, or
2. Download the essentials ZIP from https://www.gyan.dev/ffmpeg/builds/ and place it under `tools/ffmpeg`.

Expected local fallback on Windows:

```text
F:\ContentFactory	oolsfmpeginfmpeg.exe
F:\ContentFactory	oolsfmpeginfprobe.exe
```

## Database

Create the local SQLite database:

```bash
python3 scripts/init_db.py
python3 scripts/migrate_asset_priority.py
```

Useful commands:

```bash
python3 scripts/intake_assets.py assets
python3 scripts/add_idea.py "First test video" "topic" "hook"
python3 scripts/list_ideas.py
```

## Scene Audit

The ranker uses scene-level rows from `asset_scenes`. After intake, add at least one scene audit row for every asset you plan to rank:

```bash
python3 scripts/audit_asset.py add   --asset assets/raw/video/example.mp4   --start 0   --end 3.5   --role hook   --visual "Woman scrolling phone in bed"   --emotion curiosity   --themes "phone,scroll,night"   --score 4.2
```

Inspect audit rows:

```bash
python3 scripts/audit_asset.py list --asset assets/raw/video/example.mp4
```

## Local Audio Transcription

The repo includes `scripts/transcribe_audio.py`, but the local ASR environment is not stored in Git.

Recommended setup:

```bash
python3 -m venv tools/asr/.venv
tools/asr/.venv/bin/python -m pip install --upgrade pip
tools/asr/.venv/bin/python -m pip install faster-whisper
```

On Windows, use the `.venv\Scripts\python.exe` path instead.

Use it to create SRT/TXT from voiceovers:

```bash
tools/asr/.venv/bin/python scripts/transcribe_audio.py assets/voice/voice.mp3 --model small --language uk --subtitle-mode words
```

Models are downloaded on first use and cached under `tools/asr/models`.

Use Python 3.11 or 3.12 for this ASR environment. Older or newer versions may work for the rest of the repo, but ASR dependencies are most predictable on 3.11/3.12.

## API Keys

Copy `.env.example` to `.env`, then fill only the keys you need.

Tracked scripts currently require:

```text
PEXELS_API_KEY=
```

Documented for adjacent workflows, but not consumed directly by the tracked scripts in this repo:

```text
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
```

Never commit `.env`.

## Asset Selection

Before choosing final assets for a storyboard:

```bash
python3 scripts/pick_assets.py rank --role hook --themes "phone,scroll,curiosity" --batch ubt-001 --limit 10
```

After keeping a draft render:

```bash
python3 scripts/pick_assets.py record --storyboard batches/ubt-001/storyboard_example.json
```
