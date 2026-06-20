from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _ffmpeg import resolve_binary
from _voice import resolve_voice_file


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "drafts"
TEMP_ROOT = ROOT / "temp"
VOICE_DEFAULT = ROOT / "assets" / "voice" / "voice.mp3"
AUDIO_SPEED = 1.12

CUES = [
    (0.00, 2.70, "Мене налякала не істерика"),
    (2.70, 5.20, "Щовечора по колу"),
    (5.20, 8.20, "Після садка найважче"),
    (8.20, 11.00, "Сльози. Крик. Злість."),
    (11.00, 13.70, "Я не розуміла чому"),
    (13.70, 16.80, "Відволікання не працює"),
    (16.80, 19.80, "Лише на кілька хвилин"),
    (19.80, 22.60, "Інша мама. Та сама історія."),
    (22.60, 25.60, "Проблема не в поведінці"),
    (25.60, 28.80, "Нервова система перевантажена"),
    (28.80, 31.80, "Садок. Шум. Емоції."),
    (31.80, 34.60, "Мозок не справляється"),
    (34.60, 37.40, "Пройшла коротке опитування"),
    (37.40, 40.20, "План під стан дитини"),
    (40.20, 43.20, "Почали з нейровправ"),
    (43.20, 46.10, "Кілька хвилин на день"),
    (46.10, 49.20, "Зміни прийшли швидко"),
    (49.20, 52.20, "За тиждень спокійніше"),
    (52.20, 55.20, "Я перестала гадати"),
    (55.20, 58.50, "Почала розуміти дитину"),
    (58.50, 61.40, "Пройдіть коротке опитування"),
]


COMMON_SEGMENTS = [
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 1.0, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 1.6, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 1.2, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 1.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505903_2160x3840.mp4", "ss": 1.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 2.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 3.8, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук1.mp4", "ss": 2.0, "dur": 1.5, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk1.png"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук картки.mp4", "ss": 1.4, "dur": 1.5, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/otzyv6.JPG"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 4.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 4.6, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 4.3, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov", "ss": 0.7, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 0.8, "dur": 1.6, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-55-24_1.mov", "ss": 0.8, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/интерфейс.MP4", "ss": 1.0, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 3.2, "dur": 1.6, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-10_1.mov", "ss": 0.8, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/хом.MP4", "ss": 1.0, "dur": 1.6, "mode": "contain"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук2.mp4", "ss": 1.6, "dur": 1.5, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk4.png"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 6.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 6.2, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-48_1.mov", "ss": 0.7, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-58-29_1.mov", "ss": 0.7, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-59-29_1.mov", "ss": 0.6, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук.mov", "ss": 0.5, "dur": 1.5, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/otzyv6.JPG"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 7.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/хом.MP4", "ss": 5.0, "dur": 1.5, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 7.0, "dur": 1.5, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 7.2, "dur": 1.4, "mode": "cover"},
]


VARIANTS = {
    "tv_hook": {
        "output_base": "neirokid_evening_kindergarten_tv_hook",
        "batch": "neirokid_evening_kindergarten_tv_hook",
        "hook": [
            {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 0.2, "dur": 1.4, "mode": "cover"},
            {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 1.8, "dur": 1.3, "mode": "cover"},
            {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.6, "dur": 1.4, "mode": "cover"},
            {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 0.2, "dur": 1.4, "mode": "cover"},
        ],
    },
    "tower_hook": {
        "output_base": "neirokid_evening_kindergarten_tower_hook",
        "batch": "neirokid_evening_kindergarten_tower_hook",
        "hook": [
            {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.0, "dur": 1.5, "mode": "cover"},
            {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 2.3, "dur": 1.4, "mode": "cover"},
            {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 0.4, "dur": 1.3, "mode": "cover"},
            {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 0.3, "dur": 1.4, "mode": "cover"},
        ],
    },
}


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


def build_filter(mode: str) -> str:
    if mode == "contain":
        return "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p"
    return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p"


def render_segment(ffmpeg: str, temp_dir: Path, index: int, spec: dict[str, object]) -> Path:
    src = ROOT / str(spec["source"])
    out = temp_dir / f"segment_{index:02d}.mp4"
    dur = float(spec["dur"])
    overlay_source = spec.get("overlay_source")
    cmd = [ffmpeg, "-y"]
    if src.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", str(src)]
    else:
        cmd += ["-ss", str(spec.get("ss", 0)), "-t", f"{dur}", "-i", str(src)]
    if overlay_source:
        overlay_path = ROOT / str(overlay_source)
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", str(overlay_path)]
        filter_complex = (
            f"[0:v]{build_filter(str(spec.get('mode', 'cover')))}[bg];"
            "[1:v]scale=520:-2:force_original_aspect_ratio=decrease,format=rgba,"
            "colorchannelmixer=aa=0.97[card];"
            "[bg][card]overlay=W-w-36:120"
        )
        cmd += [
            "-an",
            "-filter_complex",
            filter_complex,
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ]
    else:
        cmd += [
            "-an",
            "-vf",
            build_filter(str(spec.get("mode", "cover"))),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ]
    subprocess.run(cmd, check=True)
    return out


def write_storyboard(path: Path, batch: str, audio_path: Path, draft_path: Path, subs_path: Path, segments: list[dict[str, object]]) -> None:
    scenes = []
    cursor = 0.0
    for index, seg in enumerate(segments):
        dur = float(seg["dur"])
        role = "hook" if index < 4 else "body"
        scenes.append(
            {
                "vo": f"{cursor:.2f}-{cursor + dur:.2f}",
                "role": role,
                "path": str(seg["source"]),
                "ss": float(seg.get("ss", 0)),
                "t": dur,
            }
        )
        cursor += dur

    data = {
        "batch": batch,
        "variant": "V01_dual_hook",
        "subtitle_mode": "bullets",
        "asset_selection": "manual",
        "voice": str(audio_path.relative_to(ROOT)),
        "subs": str(subs_path.relative_to(ROOT)),
        "draft": str(draft_path.relative_to(ROOT)),
        "scenes": scenes,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def render_variant(name: str, config: dict[str, object], ffmpeg: str, audio_path: Path) -> tuple[Path, Path]:
    output_base = str(config["output_base"])
    temp_dir = TEMP_ROOT / f"{output_base}_build"
    batch_dir = ROOT / "batches" / str(config["batch"])
    subs_dir = batch_dir / "subs"
    ass_path = subs_dir / f"{output_base}_bullets.ass"
    storyboard_path = batch_dir / f"storyboard_{output_base}.json"
    draft_path = OUT_DIR / f"{output_base}.mp4"
    bullets_path = OUT_DIR / f"{output_base}_bullets.mp4"

    temp_dir.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    subs_dir.mkdir(parents=True, exist_ok=True)

    segments = list(config["hook"]) + COMMON_SEGMENTS
    paths = [render_segment(ffmpeg, temp_dir, idx, seg) for idx, seg in enumerate(segments, start=1)]

    concat_list = temp_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8")

    sped_audio = temp_dir / "voice_sped.m4a"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(audio_path), "-filter:a", f"atempo={AUDIO_SPEED}", "-c:a", "aac", str(sped_audio)],
        check=True,
    )

    stitched = temp_dir / "video_only.mp4"
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(stitched)], check=True)

    subprocess.run(
        [ffmpeg, "-y", "-i", str(stitched), "-i", str(sped_audio), "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(draft_path)],
        check=True,
    )

    ass_path.write_text(build_ass(), encoding="utf-8")
    write_storyboard(storyboard_path, str(config["batch"]), audio_path, draft_path, ass_path, segments)

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(draft_path),
            "-vf",
            f"subtitles={ass_path}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "19",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(bullets_path),
        ],
        check=True,
    )
    return draft_path, bullets_path


def main() -> None:
    ffmpeg = resolve_binary("ffmpeg")
    audio_path = resolve_voice_file(VOICE_DEFAULT)
    if not audio_path.exists():
        raise SystemExit(f"Audio not found: {audio_path}")

    results = {}
    for name, config in VARIANTS.items():
        draft_path, bullets_path = render_variant(name, config, ffmpeg, audio_path)
        results[name] = {
            "draft": str(draft_path),
            "bullets": str(bullets_path),
        }
        print(f"{name}_draft={draft_path}")
        print(f"{name}_bullets={bullets_path}")

    manifest = ROOT / "outputs" / "drafts" / "evening_kindergarten_dual_manifest.json"
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest={manifest}")


if __name__ == "__main__":
    main()
