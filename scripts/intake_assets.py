from __future__ import annotations

from pathlib import Path
import argparse
import mimetypes
import sqlite3
import subprocess
import json

from _ffmpeg import resolve_binary

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "factory.sqlite"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def probe_video(path: Path) -> dict[str, str]:
    try:
        ffprobe = resolve_binary("ffprobe")
    except FileNotFoundError:
        return {}
    try:
        raw = subprocess.check_output([
            ffprobe, "-v", "error",
            "-show_entries", "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate",
            "-of", "json", str(path)
        ], text=True, stderr=subprocess.DEVNULL)
        data = json.loads(raw)
        video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
        width = int(video.get("width") or 0)
        height = int(video.get("height") or 0)
        duration = float(data.get("format", {}).get("duration") or 0)
        fps = video.get("r_frame_rate", "")
        orientation = "vertical" if height > width else "horizontal" if width > height else "square"
        return {
            "duration": f"{duration:.2f}",
            "width": str(width),
            "height": str(height),
            "fps": fps,
            "video_codec": video.get("codec_name", ""),
            "audio": str(audio is not None),
            "audio_codec": audio.get("codec_name", "") if audio else "",
            "orientation": orientation,
        }
    except Exception:
        return {}


def classify(path: Path, explicit_kind: str | None) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    if explicit_kind:
        kind = explicit_kind
    elif suffix in VIDEO_EXTS:
        kind = "stock_video"
    elif suffix in IMAGE_EXTS:
        kind = "raw_image"
    else:
        kind = "file"

    path_text = rel(path)
    if "assets/generated" in path_text:
        if suffix in IMAGE_EXTS:
            return "generated_image", "user_generated_image", "ai_generated_review"
        return kind, "user_generated", "needs_review"
    if "site-recordings" in path_text:
        return "site_master_recording", "site_recording", "owned_site_recording"
    if "assets/raw/video" in path_text:
        return "stock_video", "pexels", "pexels_license"
    if "assets/raw/images" in path_text:
        return "raw_image", "user_import_raw_image", "needs_source_check"
    return kind, "user_import", "needs_source_check"


def main():
    parser = argparse.ArgumentParser(description="Incrementally import new media assets into the content factory database.")
    parser.add_argument("paths", nargs="*", default=[str(ROOT / "assets")])
    parser.add_argument("--kind", default=None, help="Optional asset_type override")
    args = parser.parse_args()

    roots = [Path(p).resolve() for p in args.paths]
    files: list[Path] = []
    for base in roots:
        if base.is_file():
            files.append(base)
        elif base.exists():
            files.extend(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in (IMAGE_EXTS | VIDEO_EXTS))

    files_added = 0
    files_updated = 0
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for path in sorted(files):
            asset_type, source, license_status = classify(path, args.kind)
            meta = probe_video(path) if path.suffix.lower() in VIDEO_EXTS else {}
            mime = mimetypes.guess_type(path.name)[0] or "unknown"
            notes_parts = [f"mime={mime}", f"bytes={path.stat().st_size}"]
            notes_parts.extend(f"{k}={v}" for k, v in meta.items() if v != "")
            if asset_type == "site_master_recording":
                notes_parts.append("MASTER SCREEN RECORDING. needs_trim=true. Exclude start/stop UI before render.")
            notes = "; ".join(notes_parts)
            existing = conn.execute("SELECT id FROM assets WHERE path = ?", (rel(path),)).fetchone()
            conn.execute(
                """
                INSERT INTO assets(path, asset_type, source, license_status, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                  asset_type=excluded.asset_type,
                  source=excluded.source,
                  license_status=excluded.license_status,
                  notes=excluded.notes
                """,
                (rel(path), asset_type, source, license_status, notes),
            )
            if existing:
                files_updated += 1
            else:
                files_added += 1
        conn.execute(
            "INSERT INTO asset_intake_runs(root_path, asset_kind, files_seen, files_added, files_updated, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (", ".join(str(p) for p in roots), args.kind or "auto", len(files), files_added, files_updated, "incremental import"),
        )
    print(f"seen={len(files)} added={files_added} updated={files_updated}")


if __name__ == "__main__":
    main()
