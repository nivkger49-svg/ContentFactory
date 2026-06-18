from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _ffmpeg import resolve_binary
from _voice import resolve_voice_file

ROOT = Path(__file__).resolve().parents[1]
INPUT_VIDEO = ROOT / "outputs" / "drafts" / "neirokid_evening_overload_draft_v6.mp4"
OUTPUT_VIDEO = ROOT / "outputs" / "drafts" / "neirokid_evening_overload_draft_v6_bullets.mp4"
BATCH_DIR = ROOT / "batches" / "neirokid_evening_overload_v6"
SUBS_DIR = BATCH_DIR / "subs"
ASS_PATH = SUBS_DIR / "evening_overload_bullets.ass"
STORYBOARD_PATH = BATCH_DIR / "storyboard_evening_overload_bullets.json"
DEFAULT_AUDIO_PATH = ROOT / "assets" / "voice" / "До вечора.mp3"

CUES = [
    (0.00, 2.20, "До вечора все змінювалось"),
    (2.20, 4.20, "Зранку ще спокійно"),
    (4.20, 6.20, "А потім хаос"),
    (6.20, 8.60, "Дратується без причини"),
    (8.60, 10.90, "Плаче через дрібниці"),
    (10.90, 13.20, "Не хоче слухати"),
    (13.20, 15.90, "Я не розуміла чому"),
    (15.90, 18.50, "Відволікання не працює"),
    (18.50, 21.10, "Лише на кілька хвилин"),
    (21.10, 23.80, "До вечора перевантаження"),
    (23.80, 26.10, "Шум. Люди. Садок."),
    (26.10, 28.50, "Емоцій занадто багато"),
    (28.50, 31.30, "Мозок не справляється"),
    (31.30, 34.10, "Почали нейровправи"),
    (34.10, 36.80, "Через рух і гру"),
    (36.80, 39.40, "7-10 хвилин на день"),
    (39.40, 42.40, "Спочатку тіло"),
    (42.40, 45.10, "Потім спокій"),
    (45.10, 47.90, "Менше зривів"),
    (47.90, 50.60, "Більше спокою"),
    (50.60, 56.40, "Пройди коротке опитування"),
]


def ass_time(seconds: float) -> str:
    total_cs = max(0, int(round(seconds * 100)))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def build_ass() -> str:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Bullet,Arial,66,&H00FFFFFF,&H000000FF,&H0010121A,&H6E000000,1,0,0,0,100,100,0,0,1,4,0,8,80,80,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for start, end, text in CUES:
        events.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Bullet,,0,0,0,,{escape_ass(text)}"
        )
    return header + "\n".join(events) + "\n"


def write_storyboard(audio_path: Path) -> None:
    storyboard = {
        "batch": "neirokid_evening_overload_v6",
        "variant": "V01_bullets_top_safe",
        "subtitle_mode": "bullets",
        "asset_selection": "manual",
        "voice": str(audio_path.relative_to(ROOT)),
        "subs": str(ASS_PATH.relative_to(ROOT)),
        "source_video": str(INPUT_VIDEO.relative_to(ROOT)),
        "scene_count": len(CUES),
    }
    STORYBOARD_PATH.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if not INPUT_VIDEO.exists():
        raise SystemExit(f"Input video not found: {INPUT_VIDEO}")

    ffmpeg = resolve_binary("ffmpeg")
    audio_path = resolve_voice_file(DEFAULT_AUDIO_PATH)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    SUBS_DIR.mkdir(parents=True, exist_ok=True)
    ASS_PATH.write_text(build_ass(), encoding="utf-8")
    write_storyboard(audio_path)

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(INPUT_VIDEO),
            "-vf",
            f"subtitles={ASS_PATH}",
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
            str(OUTPUT_VIDEO),
        ],
        check=True,
    )
    print(OUTPUT_VIDEO)


if __name__ == "__main__":
    main()
