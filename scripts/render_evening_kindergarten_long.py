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
OUTPUT_BASE = "neirokid_evening_kindergarten_long_hook"
BATCH = "neirokid_evening_kindergarten_long_hook"


CAPTIONS = [
    (0.00, 1.15, "ВСІ\\NДИВИЛИСЯ\\N{\\c&H0000E8FF&}НА НАС"),
    (1.15, 2.55, "МЕНЕ НАЛЯКАЛА\\NНЕ ІСТЕРИКА"),
    (2.55, 4.20, "ЦЕ ПОВТОРЮВАЛОСЬ\\N{\\c&H0000E8FF&}ЩОВЕЧОРА"),
    (4.20, 6.10, "НІБИ\\NЗА РОЗКЛАДОМ"),
    (6.10, 8.35, "О 5 ВЕЧОРА\\NВСЕ ЩЕ ДОБРЕ"),
    (8.35, 10.20, "А ПОТІМ...\\N{\\c&H0000E8FF&}КНОПКА"),
    (10.20, 12.20, "СЛЬОЗИ\\NКРИК\\NЗЛІСТЬ"),
    (12.20, 14.35, "ЧЕРЕЗ\\NДРІБНИЦІ"),
    (14.35, 16.25, "Я НЕ РОЗУМІЛА\\N{\\c&H0000E8FF&}ЧОМУ"),
    (16.25, 18.60, "Я ВЖЕ\\NВСЕ\\NПЕРЕПРОБУВАЛА"),
    (18.60, 20.55, "ВІДВОЛІКАЛА\\NДАВАЛА ПЕРЕКУС"),
    (20.55, 22.60, "МУЛЬТИКИ\\NІГРИ\\NДОМОВЛЯННЯ"),
    (22.60, 24.30, "ДОПОМАГАЛО\\NНА КІЛЬКА ХВИЛИН"),
    (24.30, 26.10, "{\\c&H0000E8FF&}НЕ\\NПРАЦЮЄ"),
    (26.10, 28.25, "ІНША МАМА\\NОПИСАЛА\\NМОЮ ДИТИНУ"),
    (28.25, 30.25, "Я НЕ ОДНА\\NТАКА"),
    (30.25, 32.45, "Я НАМАГАЛАСЯ\\NВИПРАВИТИ\\NПОВЕДІНКУ"),
    (32.45, 34.50, "АЛЕ ПРОБЛЕМА\\NНЕ В ПОВЕДІНЦІ"),
    (34.50, 37.10, "НЕРВОВА СИСТЕМА\\N{\\c&H0000E8FF&}ПЕРЕВАНТАЖЕНА"),
    (37.10, 39.50, "САДОК\\NШУМ\\NЕМОЦІЇ"),
    (39.50, 41.80, "НОВІ\\NВРАЖЕННЯ"),
    (41.80, 44.10, "МОЗОК\\NНЕ СПРАВЛЯЄТЬСЯ"),
    (44.10, 46.35, "Я ПРОЙШЛА\\NКОРОТКЕ\\NОПИТУВАННЯ"),
    (46.35, 48.75, "ОТРИМАЛА ПЛАН\\NПІД СТАН ДИТИНИ"),
    (48.75, 51.20, "ПОЧАЛИ\\NЗ ПРОСТИХ\\NНЕЙРОВПРАВ"),
    (51.20, 53.45, "КІЛЬКА ХВИЛИН\\NНА ДЕНЬ"),
    (53.45, 56.10, "ЗМІНИ\\NПРИЙШЛИ\\NШВИДКО"),
    (56.10, 59.20, "ЗА ТИЖДЕНЬ\\NВЕЧОРИ СТАЛИ\\NСПОКІЙНІШІ"),
    (59.20, 62.20, "Я ПЕРЕСТАЛА\\NГАДАТИ"),
    (62.20, 66.20, "Я НАРЕШТІ\\NЗРОЗУМІЛА\\NСВОЮ ДИТИНУ"),
    (66.20, 72.20, "ЯКЩО ВПІЗНАЛИ\\NСЕБЕ"),
    (72.20, 80.90, "ПРОЙДІТЬ\\NКОРОТКЕ\\NОПИТУВАННЯ"),
]


SEGMENTS = [
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.0, "dur": 1.35, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 2.35, "dur": 1.30, "mode": "cover"},
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 0.25, "dur": 1.25, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/штовкати.mp4", "ss": 0.5, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 0.2, "dur": 1.55, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8033559_2160x3840.mp4", "ss": 1.0, "dur": 1.50, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 1.2, "dur": 1.55, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 1.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 1.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505903_2160x3840.mp4", "ss": 1.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7676991_1080x1920.mp4", "ss": 0.5, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 2.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 2.4, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 1.0, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук1.mp4", "ss": 2.0, "dur": 1.55, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk1.png"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук картки.mp4", "ss": 1.4, "dur": 1.55, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/otzyv6.JPG"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 4.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 4.6, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 4.3, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8502737_1080x1920.mp4", "ss": 0.7, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8524155_1080x1920.mp4", "ss": 0.8, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_12760968_2160x3840.mp4", "ss": 0.8, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505952_2160x3840.mp4", "ss": 0.8, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov", "ss": 0.7, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 0.8, "dur": 1.60, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-55-24_1.mov", "ss": 0.8, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/интерфейс.MP4", "ss": 1.0, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 3.2, "dur": 1.60, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-10_1.mov", "ss": 0.8, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/хом.MP4", "ss": 1.0, "dur": 1.60, "mode": "contain"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук2.mp4", "ss": 1.6, "dur": 1.55, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk4.png"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 6.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 6.2, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-48_1.mov", "ss": 0.7, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-58-29_1.mov", "ss": 0.7, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-59-29_1.mov", "ss": 0.6, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук.mov", "ss": 0.5, "dur": 1.55, "mode": "cover", "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/otzyv6.JPG"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 7.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/хом.MP4", "ss": 5.0, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 7.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 7.2, "dur": 1.40, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8033559_2160x3840.mp4", "ss": 4.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 5.6, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 4.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/онбординг.MP4", "ss": 1.0, "dur": 1.60, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 5.0, "dur": 1.60, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-53-55_1.mov", "ss": 0.6, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 8.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 8.0, "dur": 1.45, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/хом.MP4", "ss": 8.5, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-59-29_1.mov", "ss": 3.0, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/наработки/03_интерфейс/интерфейс.MP4", "ss": 4.0, "dur": 1.55, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8670995_2160x4096.mp4", "ss": 9.0, "dur": 1.55, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 9.0, "dur": 1.55, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 10.0, "dur": 1.45, "mode": "cover"},
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


def escape_ass_text(text: str) -> str:
    return text.replace("\\N", "\n").replace("\\", r"\\").replace("\n", r"\N")


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
Style: Hook,Arial,86,&H00FFFFFF,&H000000FF,&H00101010,&H00000000,1,0,0,0,100,100,0,0,1,7,0,5,80,80,0,1
Style: Main,Arial,74,&H00FFFFFF,&H000000FF,&H00101010,&H00000000,1,0,0,0,100,100,0,0,1,6,0,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for index, (start, end, text) in enumerate(CAPTIONS):
        style = "Hook" if index < 4 else "Main"
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{escape_ass_text(text)}")
    return header + "\n".join(events) + "\n"


def build_filter(mode: str) -> str:
    if mode == "contain":
        return "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p"
    return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def render_segment(ffmpeg: str, temp_dir: Path, index: int, spec: dict[str, object]) -> Path:
    src = ROOT / str(spec["source"])
    out = temp_dir / f"segment_{index:02d}.mp4"
    dur = float(spec["dur"])
    cmd = [ffmpeg, "-y", "-ss", str(spec.get("ss", 0)), "-t", f"{dur}", "-i", str(src)]
    overlay_source = spec.get("overlay_source")
    if overlay_source:
        overlay_path = ROOT / str(overlay_source)
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", str(overlay_path)]
        filter_complex = (
            f"[0:v]{build_filter(str(spec.get('mode', 'cover')))}[bg];"
            "[1:v]scale=500:-2:force_original_aspect_ratio=decrease,format=rgba,"
            "colorchannelmixer=aa=0.96[card];"
            "[bg][card]overlay=W-w-36:135"
        )
        cmd += ["-an", "-filter_complex", filter_complex]
    else:
        cmd += ["-an", "-vf", build_filter(str(spec.get("mode", "cover")))]
    cmd += ["-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", str(out)]
    run(cmd)
    return out


def write_storyboard(path: Path, audio_path: Path, draft_path: Path, subs_path: Path) -> None:
    scenes = []
    cursor = 0.0
    for index, seg in enumerate(SEGMENTS):
        dur = float(seg["dur"])
        role = "hook" if index < 4 else "body"
        scenes.append({"vo": f"{cursor:.2f}-{cursor + dur:.2f}", "role": role, "path": str(seg["source"]), "ss": float(seg.get("ss", 0)), "t": dur})
        cursor += dur
    data = {
        "batch": BATCH,
        "variant": "V02_long_voice",
        "subtitle_mode": "semantic_hormozi_blocks",
        "asset_selection": "manual",
        "voice": str(audio_path.relative_to(ROOT)),
        "subs": str(subs_path.relative_to(ROOT)),
        "draft": str(draft_path.relative_to(ROOT)),
        "total_visual_seconds": round(cursor, 2),
        "scenes": scenes,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ffmpeg = resolve_binary("ffmpeg")
    audio_path = resolve_voice_file(VOICE_DEFAULT)
    temp_dir = TEMP_ROOT / f"{OUTPUT_BASE}_build"
    batch_dir = ROOT / "batches" / BATCH
    subs_dir = batch_dir / "subs"
    ass_path = subs_dir / f"{OUTPUT_BASE}_bullets.ass"
    storyboard_path = batch_dir / f"storyboard_{OUTPUT_BASE}.json"
    draft_path = OUT_DIR / f"{OUTPUT_BASE}.mp4"
    bullets_path = OUT_DIR / f"{OUTPUT_BASE}_bullets.mp4"

    temp_dir.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    subs_dir.mkdir(parents=True, exist_ok=True)

    paths = [render_segment(ffmpeg, temp_dir, idx, seg) for idx, seg in enumerate(SEGMENTS, start=1)]
    concat_list = temp_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8")

    sped_audio = temp_dir / "voice_sped.m4a"
    run([ffmpeg, "-y", "-i", str(audio_path), "-filter:a", f"atempo={AUDIO_SPEED}", "-c:a", "aac", str(sped_audio)])

    stitched = temp_dir / "video_only.mp4"
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(stitched)])
    run([ffmpeg, "-y", "-i", str(stitched), "-i", str(sped_audio), "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(draft_path)])

    ass_path.write_text(build_ass(), encoding="utf-8")
    write_storyboard(storyboard_path, audio_path, draft_path, ass_path)
    run([
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
    ])

    manifest = OUT_DIR / f"{OUTPUT_BASE}_manifest.json"
    manifest.write_text(json.dumps({"draft": str(draft_path), "bullets": str(bullets_path), "storyboard": str(storyboard_path), "subs": str(ass_path)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"draft={draft_path}")
    print(f"bullets={bullets_path}")
    print(f"manifest={manifest}")


if __name__ == "__main__":
    main()
