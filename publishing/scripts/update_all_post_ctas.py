from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config import load_config
from generate_caption import generate_caption, generate_tiktok_carousel_caption
from read_video_meta import get_video_meta, load_carousel_meta, load_global_meta
from zernio_client import ZernioClient


EDITABLE_STATUSES = {"draft", "scheduled", "failed", "partial"}


def _hash_caption(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _post_status(post: dict) -> str:
    raw = str(post.get("status") or "").strip()
    if "." in raw:
        raw = raw.split(".")[-1]
    return raw.lower()


def _resolve_instagram_caption(file_name: str, cfg, global_meta: dict) -> str:
    carousel_dir = cfg.ready_carousels_dir / file_name
    if carousel_dir.exists() and carousel_dir.is_dir():
        meta, _ = load_carousel_meta(carousel_dir, cfg.default_language)
        return generate_caption(meta)

    video_path = cfg.ready_videos_dir / file_name
    meta = get_video_meta(video_path, global_meta, cfg.default_language)
    return generate_caption(meta)


def _resolve_tiktok_caption(file_name: str, cfg) -> str:
    carousel_dir = cfg.ready_carousels_dir / file_name
    if carousel_dir.exists() and carousel_dir.is_dir():
        meta, _ = load_carousel_meta(carousel_dir, cfg.default_language)
        return generate_tiktok_carousel_caption(meta)
    return ""


def main() -> None:
    cfg = load_config()
    client = ZernioClient(cfg)
    sdk = client._sdk()
    state_path = cfg.state_file
    state = json.loads(state_path.read_text(encoding="utf-8"))
    global_meta = load_global_meta(cfg.video_meta_json)

    results: list[dict[str, str]] = []

    for file_name, record in state.items():
        instagram_post_id = str(record.get("zernio_post_id") or "").strip()
        tiktok_post_id = str(record.get("tiktok_zernio_post_id") or "").strip()

        instagram_caption = ""
        tiktok_caption = ""
        if instagram_post_id:
            instagram_caption = _resolve_instagram_caption(file_name, cfg, global_meta)
        if tiktok_post_id:
            tiktok_caption = _resolve_tiktok_caption(file_name, cfg)

        if instagram_post_id:
            row = {
                "file": file_name,
                "platform": "instagram",
                "post_id": instagram_post_id,
            }
            try:
                post = client.get_post(instagram_post_id)
                status = _post_status(post)
                row["status"] = status
                if status in EDITABLE_STATUSES:
                    sdk.posts.update(instagram_post_id, content=instagram_caption)
                    record["current_caption"] = instagram_caption
                    record["caption_hash"] = _hash_caption(instagram_caption)
                    row["result"] = "updated"
                else:
                    row["result"] = "skipped_not_editable"
            except Exception as exc:
                row["status"] = "lookup_failed"
                row["result"] = "skipped_error"
                row["error"] = str(exc)
            results.append(row)

        if tiktok_post_id:
            row = {
                "file": file_name,
                "platform": "tiktok",
                "post_id": tiktok_post_id,
            }
            try:
                post = client.get_post(tiktok_post_id)
                status = _post_status(post)
                row["status"] = status
                if tiktok_caption and status in EDITABLE_STATUSES:
                    sdk.posts.update(tiktok_post_id, content=tiktok_caption)
                    record["tiktok_current_caption"] = tiktok_caption
                    record["tiktok_caption_hash"] = _hash_caption(tiktok_caption)
                    row["result"] = "updated"
                elif not tiktok_caption:
                    row["result"] = "skipped_no_tiktok_caption"
                else:
                    row["result"] = "skipped_not_editable"
            except Exception as exc:
                row["status"] = "lookup_failed"
                row["result"] = "skipped_error"
                row["error"] = str(exc)
            results.append(row)

    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
