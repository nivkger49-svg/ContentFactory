from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _voice import ROOT


SCRIPTS = {
    "voice": ROOT / "scripts" / "generate_elevenlabs_voice.py",
    "fresh": ROOT / "scripts" / "render_evening_overload_fresh.py",
    "draft": ROOT / "scripts" / "render_evening_overload_draft.py",
    "bullets": ROOT / "scripts" / "burn_evening_overload_bullets.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ContentFactory pipeline: script text -> ElevenLabs voice -> SRT/TXT -> render -> optional bullet subtitles."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Literal script text to synthesize before render.")
    group.add_argument("--text-file", help="UTF-8 text file to synthesize before render.")
    parser.add_argument("--render", choices=["fresh", "draft"], default="fresh", help="Which base render recipe to run.")
    parser.add_argument(
        "--captions",
        choices=["none", "bullets"],
        default="bullets",
        help="Whether to leave the base render alone or create the bullet-caption version after render.",
    )
    parser.add_argument("--output-name", default="voice.mp3", help="Voice filename inside assets/voice.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting the current voice mp3.")
    parser.add_argument("--language", default="uk", help="Voice and ASR language. Default: uk")
    parser.add_argument("--voice-id", default=None, help="Optional ElevenLabs voice override for this run.")
    parser.add_argument("--model-id", default=None, help="Optional ElevenLabs model override for this run.")
    parser.add_argument("--stability", type=float, default=None, help="Optional ElevenLabs stability override.")
    parser.add_argument("--similarity-boost", type=float, default=None, help="Optional ElevenLabs similarity boost override.")
    parser.add_argument("--style", type=float, default=None, help="Optional ElevenLabs style override.")
    parser.add_argument("--speaker-boost", action="store_true", help="Enable ElevenLabs speaker boost.")
    parser.add_argument("--seed", type=int, default=None, help="Optional ElevenLabs seed.")
    parser.add_argument("--asr-model", default="small", help="Whisper model for automatic SRT generation.")
    parser.add_argument("--subtitle-mode", choices=["words", "segments"], default="words")
    parser.add_argument("--max-subtitle-seconds", type=float, default=2.4)
    parser.add_argument("--max-subtitle-chars", type=int, default=42)
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_voice_command(args: argparse.Namespace) -> list[str]:
    cmd = [sys.executable, str(SCRIPTS["voice"])]
    if args.text is not None:
        cmd += ["--text", args.text]
    else:
        cmd += ["--text-file", args.text_file]
    cmd += [
        "--output-name",
        args.output_name,
        "--language",
        args.language,
        "--asr-model",
        args.asr_model,
        "--subtitle-mode",
        args.subtitle_mode,
        "--max-subtitle-seconds",
        str(args.max_subtitle_seconds),
        "--max-subtitle-chars",
        str(args.max_subtitle_chars),
    ]
    if args.overwrite:
        cmd.append("--overwrite")
    if args.voice_id:
        cmd += ["--voice-id", args.voice_id]
    if args.model_id:
        cmd += ["--model-id", args.model_id]
    if args.stability is not None:
        cmd += ["--stability", str(args.stability)]
    if args.similarity_boost is not None:
        cmd += ["--similarity-boost", str(args.similarity_boost)]
    if args.style is not None:
        cmd += ["--style", str(args.style)]
    if args.speaker_boost:
        cmd.append("--speaker-boost")
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    return cmd


def main() -> None:
    args = parse_args()

    voice_cmd = build_voice_command(args)
    render_cmd = [sys.executable, str(SCRIPTS[args.render])]

    print("step=voice")
    run(voice_cmd)

    print(f"step=render recipe={args.render}")
    run(render_cmd)

    if args.captions == "bullets":
        print("step=captions mode=bullets")
        run([sys.executable, str(SCRIPTS["bullets"])])

    print(f"done render={args.render} captions={args.captions}")


if __name__ == "__main__":
    main()
