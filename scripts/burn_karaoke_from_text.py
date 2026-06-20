from __future__ import annotations

import argparse
import math
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def resolve_ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def resolve_ffprobe(ffmpeg_bin: str) -> str:
    ffmpeg_path = Path(ffmpeg_bin)
    sibling = ffmpeg_path.with_name("ffprobe")
    if sibling.exists():
        return str(sibling)
    return "ffprobe"


def ffprobe_duration(ffprobe_bin: str, path: Path) -> float:
    result = subprocess.run(
        [
            ffprobe_bin,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def ass_time(seconds: float) -> str:
    total_cs = max(0, int(round(seconds * 100)))
    hours = total_cs // 360000
    minutes = (total_cs % 360000) // 6000
    secs = (total_cs % 6000) // 100
    centis = total_cs % 100
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def normalize_subtitle_text(text: str) -> str:
    replacements = {
        "💛": "",
        "👇": "↓",
    }
    normalized = text
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return " ".join(normalized.split())


def split_into_blocks(text: str, max_words: int = 3, max_chars: int = 18) -> list[str]:
    normalized = normalize_subtitle_text(text)
    if not normalized:
        return []

    phrase_parts = re.findall(r"[^.!?,;:]+[.!?,;:]?", normalized)
    blocks: list[str] = []

    for phrase in phrase_parts:
        words = phrase.strip().split()
        if not words:
            continue
        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word]).strip()
            if current and (len(current) >= max_words or len(candidate) > max_chars):
                blocks.append(" ".join(current).strip())
                current = [word]
            else:
                current.append(word)
        if current:
            blocks.append(" ".join(current).strip())

    return [block for block in blocks if block]


def build_windows(lines: list[str], total_duration: float) -> list[tuple[float, float, str]]:
    clean_lines: list[str] = []
    for line in lines:
        clean_lines.extend(split_into_blocks(line.strip()))
    total_chars = sum(max(8, len(line.replace(" ", ""))) for line in clean_lines)
    lead_in = 0.15
    gap = 0.08
    available = max(1.0, total_duration - lead_in - gap * max(0, len(clean_lines) - 1))
    cursor = lead_in
    windows: list[tuple[float, float, str]] = []
    for index, line in enumerate(clean_lines):
        weight = max(8, len(line.replace(" ", "")))
        line_duration = available * weight / total_chars
        end = total_duration if index == len(clean_lines) - 1 else min(total_duration, cursor + line_duration)
        windows.append((cursor, end, line))
        cursor = end + gap
    return windows


def word_k_tags(text: str, start: float, end: float) -> str:
    words = text.split()
    if not words:
        return ""
    total_cs = max(1, int(round((end - start) * 100)))
    weights = [max(1, len(word.strip(".,!?…—-–:;\"'()"))) for word in words]
    total_weight = sum(weights)
    raw = [total_cs * weight / total_weight for weight in weights]
    cents = [max(1, int(math.floor(value))) for value in raw]
    diff = total_cs - sum(cents)
    index = 0
    while diff != 0 and cents:
        pos = index % len(cents)
        if diff > 0:
            cents[pos] += 1
            diff -= 1
        elif cents[pos] > 1:
            cents[pos] -= 1
            diff += 1
        index += 1
    return "".join(f"{{\\k{centis}}}{escape_ass(word)} " for centis, word in zip(cents, words)).strip()


def build_ass(lines: list[str], total_duration: float) -> str:
    windows = build_windows(lines, total_duration)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Arial,74,&H00FFFFFF,&H0000D7FF,&H00101010,&H5A000000,1,0,0,0,100,100,0,0,1,5,1,2,80,80,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for start, end, line in windows:
        events.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Karaoke,,0,0,0,,{word_k_tags(line, start, end)}"
        )
    return header + "\n".join(events) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate karaoke ASS from text and burn it into video.")
    parser.add_argument("--video", required=True, help="Input video path")
    parser.add_argument("--text-file", required=True, help="Narration text file")
    parser.add_argument("--output", required=True, help="Output video path")
    parser.add_argument("--ass-output", required=False, help="Optional ASS output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ffmpeg_bin = resolve_ffmpeg()
    ffprobe_bin = resolve_ffprobe(ffmpeg_bin)

    video = Path(args.video).resolve()
    text_file = Path(args.text_file).resolve()
    output = Path(args.output).resolve()
    ass_output = Path(args.ass_output).resolve() if args.ass_output else output.with_suffix(".ass")

    if not video.exists():
        raise SystemExit(f"Video not found: {video}")
    if not text_file.exists():
        raise SystemExit(f"Text file not found: {text_file}")

    lines = text_file.read_text(encoding="utf-8").splitlines()
    total_duration = ffprobe_duration(ffprobe_bin, video)
    ass_output.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    ass_output.write_text(build_ass(lines, total_duration), encoding="utf-8")

    subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(video),
            "-vf",
            f"subtitles={ass_output}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )
    print(output)


if __name__ == "__main__":
    main()
