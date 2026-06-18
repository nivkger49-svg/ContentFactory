from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _ffmpeg import resolve_binary
from _voice import resolve_voice_file

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "drafts"
TEMP_DIR = ROOT / "temp" / "evening_overload_build_v2"
DEFAULT_AUDIO = ROOT / "assets" / "voice" / "До вечора.mp3"
AUDIO_SPEED = 1.17

SEGMENTS = [
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 0.4, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.2, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/17867776878545728.mp4", "ss": 1.2, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/46D33E86-94C9-4E8C-BB5A-990D6214129F.MP4", "ss": 10.0, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/17844353067684790.mp4", "ss": 0.8, "dur": 1.9, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/6F149C84-2FD8-41EA-99C1-12137B0D3346.MP4", "ss": 8.0, "dur": 1.9, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/ScreenRecording_06-12-2026 10-57-48_1.mov", "ss": 0.9, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 1.0, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/ScreenRecording_06-12-2026 10-58-29_1.mov", "ss": 0.7, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505903_2160x3840.mp4", "ss": 0.8, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/ScreenRecording_06-12-2026 10-59-29_1.mov", "ss": 0.6, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505952_2160x3840.mp4", "ss": 0.8, "dur": 1.9, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-55-24_1.mov", "ss": 0.8, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7676991_1080x1920.mp4", "ss": 1.0, "dur": 1.9, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/интерфейс.MP4", "ss": 1.1, "dur": 1.8, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8098909_2160x3840.mp4", "ss": 1.2, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 3.2, "dur": 1.8, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394183_2160x3840.mp4", "ss": 2.0, "dur": 1.9, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/онбординг.MP4", "ss": 0.9, "dur": 1.7, "mode": "contain"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_8033559_2160x3840.mp4", "ss": 0.9, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук1.mp4", "ss": 2.0, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6168664_2160x4096.mp4", "ss": 0.8, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук картки.mp4", "ss": 1.4, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 0.7, "dur": 1.8, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук 3.mov", "ss": 0.6, "dur": 1.7, "mode": "cover"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov", "ss": 0.7, "dur": 1.6, "mode": "cover"},
    {
        "source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov",
        "ss": 2.4,
        "dur": 1.5,
        "mode": "cover",
        "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk1.png",
    },
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-10_1.mov", "ss": 0.8, "dur": 1.6, "mode": "cover"},
    {"source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук2.mp4", "ss": 0.3, "dur": 1.6, "mode": "cover"},
    {
        "source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук2.mp4",
        "ss": 1.6,
        "dur": 1.5,
        "mode": "cover",
        "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/vidguk4.png",
    },
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 0.8, "dur": 1.6, "mode": "contain"},
    {
        "source": "assets/raw/video/наработки/05_отзывы/видео/Відгук Нейробук.mov",
        "ss": 0.5,
        "dur": 1.6,
        "mode": "cover",
        "overlay_source": "assets/raw/video/наработки/05_отзывы/скрины/otzyv6.JPG",
    },
]


def build_filter(mode: str) -> str:
    if mode == "contain":
        return "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p"
    return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p"


def render_segment(ffmpeg: str, index: int, spec: dict[str, object]) -> Path:
    src = ROOT / str(spec["source"])
    out = TEMP_DIR / f"segment_{index:02d}.mp4"
    dur = float(spec["dur"])
    overlay_source = spec.get("overlay_source")
    cmd = [ffmpeg, "-y"]
    if src.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", str(src)]
    else:
        cmd += ["-ss", str(spec.get("ss", 0)), "-t", f"{dur}", "-i", str(src)]
    if overlay_source:
        overlay_path = ROOT / str(overlay_source)
        if overlay_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            cmd += ["-loop", "1", "-t", f"{dur}", "-i", str(overlay_path)]
        else:
            cmd += ["-ss", str(spec.get("overlay_ss", 0)), "-t", f"{dur}", "-i", str(overlay_path)]
        filter_complex = (
            f"[0:v]{build_filter(str(spec.get('mode', 'cover')))}[bg];"
            "[1:v]scale=420:-2:force_original_aspect_ratio=decrease,"
            "pad=456:280:(ow-iw)/2:(oh-ih)/2:white,"
            "format=rgba,"
            "colorchannelmixer=aa=0.98[card];"
            "[bg][card]overlay=W-w-36:H-h-220"
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
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ]
        subprocess.run(cmd, check=True)
        return out
    cmd += [
        "-an",
        "-vf", build_filter(str(spec.get("mode", "cover"))),
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return out


def main() -> None:
    ffmpeg = resolve_binary("ffmpeg")
    audio = resolve_voice_file(DEFAULT_AUDIO)
    if not audio.exists():
        raise SystemExit(f"Audio not found: {audio}")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    segment_paths = [render_segment(ffmpeg, idx, spec) for idx, spec in enumerate(SEGMENTS, start=1)]

    concat_list = TEMP_DIR / "concat.txt"
    concat_list.write_text("".join([f"file '{p.as_posix()}'\n" for p in segment_paths]), encoding="utf-8")

    sped_audio = TEMP_DIR / "voice_sped.m4a"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(audio), "-filter:a", f"atempo={AUDIO_SPEED}", "-c:a", "aac", str(sped_audio)],
        check=True,
    )

    stitched = TEMP_DIR / "video_only.mp4"
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(stitched)], check=True)

    final_path = OUT_DIR / "neirokid_evening_overload_draft_v5.mp4"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(stitched), "-i", str(sped_audio), "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(final_path)],
        check=True,
    )

    manifest = {
        "audio": audio.name,
        "audio_speed": AUDIO_SPEED,
        "segments": SEGMENTS,
        "output": str(final_path),
        "local_segment_count": sum(1 for s in SEGMENTS if "/pexels/" not in str(s["source"])),
        "pexels_segment_count": sum(1 for s in SEGMENTS if "/pexels/" in str(s["source"])),
    }
    (TEMP_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(final_path)


if __name__ == "__main__":
    main()
