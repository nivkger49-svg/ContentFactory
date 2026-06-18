from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from _voice import ROOT, VOICE_DIR, load_dotenv


DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a voiceover with ElevenLabs, save it into assets/voice, then optionally transcribe it."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Literal script text to synthesize.")
    group.add_argument("--text-file", help="Path to a UTF-8 text file with the script.")
    parser.add_argument(
        "--output-name",
        default="voice.mp3",
        help="Output audio filename inside assets/voice unless --output-path is used. Default: voice.mp3",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Absolute or repo-relative output audio path. Overrides --output-name.",
    )
    parser.add_argument("--voice-id", default=None, help="Override ELEVENLABS_VOICE_ID for this run.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="ElevenLabs model ID.")
    parser.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT, help="ElevenLabs output format.")
    parser.add_argument("--language", default="uk", help="Language code to send to ElevenLabs. Default: uk")
    parser.add_argument("--stability", type=float, default=0.45, help="Voice stability 0..1")
    parser.add_argument("--similarity-boost", type=float, default=0.8, help="Similarity boost 0..1")
    parser.add_argument("--style", type=float, default=0.0, help="Style exaggeration 0..1")
    parser.add_argument("--speaker-boost", action="store_true", help="Enable speaker boost")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for more consistent output")
    parser.add_argument("--no-transcribe", action="store_true", help="Skip local SRT/TXT generation")
    parser.add_argument("--asr-model", default="small", help="Whisper model for local SRT generation")
    parser.add_argument("--subtitle-mode", default="words", choices=["words", "segments"])
    parser.add_argument("--max-subtitle-seconds", type=float, default=2.4)
    parser.add_argument("--max-subtitle-chars", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting the output mp3")
    return parser.parse_args()


def read_text(args: argparse.Namespace) -> tuple[str, str]:
    if args.text is not None:
        return args.text.strip(), "inline"

    source_path = Path(args.text_file).expanduser()
    if not source_path.is_absolute():
        source_path = (ROOT / source_path).resolve()
    if not source_path.exists():
        raise SystemExit(f"Script text file not found: {source_path}")
    return source_path.read_text(encoding="utf-8").strip(), str(source_path)


def resolve_output_path(args: argparse.Namespace) -> Path:
    if args.output_path:
        path = Path(args.output_path).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        return path
    return VOICE_DIR / args.output_name


def ensure_env() -> tuple[str, str]:
    load_dotenv()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY is empty in .env")
    if not voice_id:
        raise SystemExit("ELEVENLABS_VOICE_ID is empty in .env")
    return api_key, voice_id


def synthesize(
    *,
    text: str,
    api_key: str,
    voice_id: str,
    model_id: str,
    output_format: str,
    language: str,
    stability: float,
    similarity_boost: float,
    style: float,
    speaker_boost: bool,
    seed: int | None,
) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={output_format}"
    payload: dict[str, object] = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": speaker_boost,
        },
    }
    if language:
        payload["language_code"] = language
    if seed is not None:
        payload["seed"] = seed

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"ElevenLabs HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"ElevenLabs request failed: {exc.reason}") from exc


def write_source_text(audio_path: Path, text: str) -> Path:
    source_path = audio_path.with_suffix(".source.txt")
    source_path.write_text(text.strip() + "\n", encoding="utf-8")
    return source_path


def find_asr_python() -> str | None:
    candidates = [
        ROOT / "tools" / "asr" / ".venv" / "bin" / "python",
        ROOT / "tools" / "asr" / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    if shutil.which(sys.executable):
        return sys.executable
    return None


def run_transcription(args: argparse.Namespace, audio_path: Path) -> None:
    asr_python = find_asr_python()
    if not asr_python:
        print("warning=local ASR python not found; mp3 generated but SRT/TXT skipped")
        return

    cmd = [
        asr_python,
        str(ROOT / "scripts" / "transcribe_audio.py"),
        str(audio_path),
        "--model",
        args.asr_model,
        "--language",
        args.language or "uk",
        "--subtitle-mode",
        args.subtitle_mode,
        "--max-subtitle-seconds",
        str(args.max_subtitle_seconds),
        "--max-subtitle-chars",
        str(args.max_subtitle_chars),
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"warning=audio generated but local transcription failed (exit {exc.returncode})")


def main() -> None:
    args = parse_args()
    text, text_source = read_text(args)
    if not text:
        raise SystemExit("Voice script is empty")

    audio_path = resolve_output_path(args)
    if audio_path.suffix.lower() != ".mp3":
        raise SystemExit("Output file must end with .mp3")
    if audio_path.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists: {audio_path}. Use --overwrite to replace it.")

    api_key, env_voice_id = ensure_env()
    voice_id = args.voice_id or env_voice_id

    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_bytes = synthesize(
        text=text,
        api_key=api_key,
        voice_id=voice_id,
        model_id=args.model_id,
        output_format=args.output_format,
        language=args.language,
        stability=args.stability,
        similarity_boost=args.similarity_boost,
        style=args.style,
        speaker_boost=args.speaker_boost,
        seed=args.seed,
    )
    audio_path.write_bytes(audio_bytes)
    source_path = write_source_text(audio_path, text)

    if not args.no_transcribe:
        run_transcription(args, audio_path)

    print(f"audio={audio_path}")
    print(f"source={source_path}")
    print(f"text_source={text_source}")
    print(f"voice_id={voice_id}")
    print(f"model_id={args.model_id}")


if __name__ == "__main__":
    main()
