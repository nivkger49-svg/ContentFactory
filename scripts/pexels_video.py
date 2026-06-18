from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "pexels"
DOWNLOAD_ROOT = ROOT / "assets" / "raw" / "video" / "pexels"
API_BASE = "https://api.pexels.com/v1/videos/search"


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def api_key() -> str:
    load_env()
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key:
        raise SystemExit("PEXELS_API_KEY is missing. Add it to F:\\ContentFactory\\.env or environment variables.")
    return key


def request_json(url: str) -> tuple[dict, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key(),
            "Accept": "application/json",
            "User-Agent": "ContentFactory/1.0 (+local workflow)",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        headers = {k: v for k, v in response.headers.items()}
        return json.loads(response.read().decode("utf-8")), headers


def slugify(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9а-яА-ЯіІїЇєЄґҐ_-]+", "-", text, flags=re.UNICODE)
    safe = re.sub(r"-+", "-", safe).strip("-").lower()
    return safe[:80] or "pexels"


def best_file(video: dict, prefer: str = "vertical") -> dict:
    files = video.get("video_files") or []
    if not files:
        return {}

    def score(item: dict) -> tuple[int, int, int]:
        width = int(item.get("width") or 0)
        height = int(item.get("height") or 0)
        vertical_bonus = 1 if prefer == "vertical" and height >= width else 0
        return vertical_bonus, height, width

    return max(files, key=score)


def flatten_video(video: dict) -> dict[str, str]:
    selected = best_file(video)
    user = video.get("user") or {}
    return {
        "id": str(video.get("id", "")),
        "url": video.get("url", ""),
        "duration": str(video.get("duration", "")),
        "width": str(video.get("width", "")),
        "height": str(video.get("height", "")),
        "author": user.get("name", ""),
        "author_url": user.get("url", ""),
        "selected_width": str(selected.get("width", "")),
        "selected_height": str(selected.get("height", "")),
        "selected_quality": str(selected.get("quality", "")),
        "selected_file_type": str(selected.get("file_type", "")),
        "download_url": selected.get("link", ""),
    }


def search(args: argparse.Namespace) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    params = {
        "query": args.query,
        "orientation": args.orientation,
        "per_page": str(args.per_page),
        "page": str(args.page),
    }
    if args.min_duration is not None:
        params["min_duration"] = str(args.min_duration)
    if args.max_duration is not None:
        params["max_duration"] = str(args.max_duration)

    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    data, headers = request_json(url)
    videos = data.get("videos") or []
    rows = [flatten_video(video) for video in videos]

    stem = args.output_stem or f"{date.today().isoformat()}_{slugify(args.query)}"
    json_path = REPORT_DIR / f"{stem}.json"
    csv_path = REPORT_DIR / f"{stem}.csv"

    payload = {
        "query": args.query,
        "request_url": url,
        "ratelimit_limit": headers.get("X-Ratelimit-Limit", ""),
        "ratelimit_remaining": headers.get("X-Ratelimit-Remaining", ""),
        "ratelimit_reset": headers.get("X-Ratelimit-Reset", ""),
        "response": data,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "id",
        "url",
        "duration",
        "width",
        "height",
        "author",
        "author_url",
        "selected_width",
        "selected_height",
        "selected_quality",
        "selected_file_type",
        "download_url",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"results={len(rows)}")
    print(f"csv={csv_path}")
    print(f"json={json_path}")
    if headers.get("X-Ratelimit-Remaining"):
        print(f"pexels_remaining={headers.get('X-Ratelimit-Remaining')}")


def load_results(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    videos = data.get("response", {}).get("videos") or []
    return videos


def download(args: argparse.Namespace) -> None:
    result_path = Path(args.results_json).resolve()
    wanted = {item.strip() for item in args.ids.split(",") if item.strip()}
    if not wanted:
        raise SystemExit("Pass one or more Pexels IDs with --ids, for example --ids 123,456")

    videos = [video for video in load_results(result_path) if str(video.get("id")) in wanted]
    if not videos:
        raise SystemExit("No matching IDs found in the search JSON.")

    target_dir = DOWNLOAD_ROOT / date.today().isoformat()
    target_dir.mkdir(parents=True, exist_ok=True)

    for video in videos:
        selected = best_file(video)
        link = selected.get("link")
        if not link:
            print(f"skip id={video.get('id')} no download link")
            continue
        ext = ".mp4"
        file_type = selected.get("file_type") or ""
        if "/" in file_type:
            ext = "." + file_type.split("/")[-1].replace("quicktime", "mov")
        video_id = str(video.get("id"))
        width = selected.get("width", "")
        height = selected.get("height", "")
        filename = f"pexels_{video_id}_{width}x{height}{ext}"
        out_path = target_dir / filename

        request = urllib.request.Request(link, headers={"User-Agent": "ContentFactory/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            out_path.write_bytes(response.read())

        meta = {
            "source": "pexels",
            "pexels_id": video_id,
            "pexels_url": video.get("url", ""),
            "author": (video.get("user") or {}).get("name", ""),
            "author_url": (video.get("user") or {}).get("url", ""),
            "license_status": "pexels_license",
            "search_results_json": str(result_path),
            "download_url": link,
            "selected_file": selected,
            "raw_video": video,
            "next_step": "Run intake_assets.py and scene analysis before final render use.",
        }
        out_path.with_suffix(out_path.suffix + ".json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"downloaded={out_path}")
        print(f"metadata={out_path.with_suffix(out_path.suffix + '.json')}")

    print("Next: run intake_assets.py, then analyze scenes before using these clips in a final render.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search and selectively download Pexels videos for ContentFactory.")
    sub = parser.add_subparsers(dest="command", required=True)

    search_parser = sub.add_parser("search", help="Search Pexels videos and save shortlist files.")
    search_parser.add_argument("query")
    search_parser.add_argument("--orientation", default="portrait", choices=["landscape", "portrait", "square"])
    search_parser.add_argument("--per-page", type=int, default=12)
    search_parser.add_argument("--page", type=int, default=1)
    search_parser.add_argument("--min-duration", type=int, default=None)
    search_parser.add_argument("--max-duration", type=int, default=30)
    search_parser.add_argument("--output-stem", default=None)
    search_parser.set_defaults(func=search)

    download_parser = sub.add_parser("download", help="Download selected IDs from a saved search JSON.")
    download_parser.add_argument("--results-json", required=True)
    download_parser.add_argument("--ids", required=True)
    download_parser.set_defaults(func=download)

    args = parser.parse_args()
    try:
        args.func(args)
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"Pexels HTTP error {exc.code}: {exc.read().decode('utf-8', errors='replace')}\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
