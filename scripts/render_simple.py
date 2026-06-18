from pathlib import Path
import subprocess
import sys

from _ffmpeg import resolve_binary

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "outputs" / "drafts"


def main():
    try:
        ffmpeg = resolve_binary("ffmpeg")
    except FileNotFoundError as exc:
        print(exc)
        raise SystemExit(1)

    if len(sys.argv) < 3:
        print("Usage: python scripts/render_simple.py input_video_or_image output_name.mp4 [audio_file]")
        raise SystemExit(2)

    source = Path(sys.argv[1]).resolve()
    output = DRAFTS / sys.argv[2]
    audio = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None

    if not source.exists():
        print(f"Source not found: {source}")
        raise SystemExit(1)
    if audio and not audio.exists():
        print(f"Audio not found: {audio}")
        raise SystemExit(1)

    DRAFTS.mkdir(parents=True, exist_ok=True)

    if audio:
        cmd = [
            ffmpeg, "-y",
            "-stream_loop", "-1", "-i", str(source),
            "-i", str(audio),
            "-t", "30",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest",
            str(output),
        ]
    else:
        cmd = [
            ffmpeg, "-y",
            "-i", str(source),
            "-t", "30",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(output),
        ]

    subprocess.run(cmd, check=True)
    print(f"Draft rendered: {output}")


if __name__ == "__main__":
    main()
