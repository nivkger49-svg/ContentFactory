from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from config import Config, load_config
from generate_caption import generate_caption, generate_tiktok_carousel_caption
from logger import get_logger
from read_video_meta import (
    VideoMeta,
    load_carousel_meta,
    load_global_meta,
    resolve_video_meta_batch,
)
from scan_ready_carousels import scan_ready_carousels
from scan_ready_videos import scan_ready_videos
from scheduler import build_schedule
from state_store import append_log, load_queue, load_state, save_queue, save_state
from zernio_client import ZernioClient


logger = get_logger("contentfactory-publishing.worker")


def _response_get(payload: object, key: str, default: object = None) -> object:
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


@dataclass
class QueueItem:
    file: str
    content_type: str
    source_path: str
    title: str
    caption: str
    caption_hash: str
    language: str
    platform_content: Dict[str, str] = field(default_factory=dict)
    asset_paths: List[str] = field(default_factory=list)
    video_path: Optional[str] = None
    status: str = "queued"
    scheduled_for: Optional[str] = None


def _now_iso(timezone: str) -> str:
    return (
        datetime.now(ZoneInfo(timezone))
        .replace(microsecond=0)
        .isoformat()
    )


def _hash_caption(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PublishWorker:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or load_config()
        self.state = load_state(self.config.state_file)
        self.queue = load_queue(self.config.queue_file)
        self.client = ZernioClient(self.config)

    def scan_and_queue(self) -> List[Dict[str, object]]:
        self._refresh_existing_queue()
        ready_videos = scan_ready_videos(self.config.ready_videos_dir, self.state)
        metadata = resolve_video_meta_batch(
            ready_videos,
            self.config.video_meta_json,
            self.config.default_language,
        )

        existing_files = {item["file"] for item in self.queue}
        new_items: List[Dict[str, object]] = []

        for video_path, meta in zip(ready_videos, metadata):
            if video_path.name in existing_files:
                continue
            item = self._build_queue_item(video_path, meta)
            new_items.append(asdict(item))
            self.state[video_path.name] = {
                "status": "queued",
                "content_type": "reel",
                "queued_at": _now_iso(self.config.timezone),
                "caption_hash": item.caption_hash,
                "title": item.title,
            }

        ready_carousels = scan_ready_carousels(
            self.config.ready_carousels_dir,
            self.state,
        )
        for carousel_dir in ready_carousels:
            if carousel_dir.name in existing_files:
                continue
            meta, image_paths = load_carousel_meta(
                carousel_dir,
                self.config.default_language,
            )
            item = self._build_carousel_queue_item(carousel_dir, meta, image_paths)
            new_items.append(asdict(item))
            self.state[carousel_dir.name] = {
                "status": "queued",
                "content_type": "carousel",
                "queued_at": _now_iso(self.config.timezone),
                "caption_hash": item.caption_hash,
                "title": item.title,
            }

        if new_items:
            self.queue.extend(new_items)
            self._persist()

        logger.info("Queued %s new content items.", len(new_items))
        return new_items

    def plan_schedule(self) -> List[Dict[str, object]]:
        planning_candidates = self.queue[: self.config.planner_batch_size]
        scheduled = build_schedule(
            queue_items=planning_candidates,
            existing_log=load_queue(self.config.log_file),
            interval_hours=self.config.posting_interval_hours,
            max_posts_per_day=self.config.max_posts_per_day,
            timezone=self.config.timezone,
            daily_posting_slots=self.config.daily_posting_slots,
        )

        by_file = {item["file"]: item for item in scheduled}
        for queue_item in self.queue:
            updated = by_file.get(queue_item["file"])
            if not updated:
                continue
            queue_item["scheduled_for"] = updated["scheduled_for"]
            if self.state.get(queue_item["file"]):
                self.state[queue_item["file"]]["scheduled_for"] = updated["scheduled_for"]

        self._persist()
        return scheduled

    def schedule_all(self) -> List[Dict[str, object]]:
        if not self.queue:
            return []

        scheduled_items = self.plan_schedule()
        if self.config.publish_mode == "draft":
            logger.info("Draft mode active, Zernio schedule calls skipped.")
            return scheduled_items

        results: List[Dict[str, object]] = []
        for item in scheduled_items:
            if self.state.get(item["file"], {}).get("status") == "scheduled":
                continue
            results.append(self._send_item(item, publish_now=False))
        return results

    def publish_next(self) -> Optional[Dict[str, object]]:
        if not self.queue:
            return None

        item = self.queue[0]
        if self.config.publish_mode == "draft":
            logger.info("Draft mode active, Zernio publish call skipped.")
            return item

        return self._send_item(item, publish_now=True)

    def _send_item(self, item: Dict[str, object], publish_now: bool) -> Dict[str, object]:
        content_type = str(item.get("content_type") or "reel")
        media_items = self._upload_item_media(item, content_type)
        response = self.client.create_post(
            caption=str(item["caption"]),
            media_items=media_items,
            title=str(item["title"]),
            content_type=content_type,
            platform_content=item.get("platform_content") or {},
            scheduled_for=None if publish_now else str(item.get("scheduled_for")),
            publish_now=publish_now,
        )

        status = "published_now" if publish_now else "scheduled"
        post_payload = _response_get(response, "post", response)
        post_id = _response_get(post_payload, "id") or _response_get(post_payload, "_id")

        self.state[item["file"]] = {
            **self.state.get(item["file"], {}),
            "status": status,
            "content_type": content_type,
            "updated_at": _now_iso(self.config.timezone),
            "scheduled_for": item.get("scheduled_for"),
            "zernio_post_id": post_id,
            "media_url": media_items[0]["url"],
            "media_urls": [media_item["url"] for media_item in media_items],
        }

        append_log(
            self.config.log_file,
            {
                "file": item["file"],
                "title": item["title"],
                "status": status,
                "content_type": content_type,
                "scheduled_for": item.get("scheduled_for"),
                "published_at": _now_iso(self.config.timezone) if publish_now else None,
                "zernio_post_id": post_id,
                "media_url": media_items[0]["url"],
                "media_urls": [media_item["url"] for media_item in media_items],
            },
        )

        self.queue = [queued for queued in self.queue if queued["file"] != item["file"]]
        self._persist()
        return {"file": item["file"], "status": status, "response": response}

    def _build_queue_item(self, video_path: Path, meta: VideoMeta) -> QueueItem:
        caption = generate_caption(meta)
        return QueueItem(
            file=video_path.name,
            content_type="reel",
            source_path=str(video_path),
            platform_content={},
            asset_paths=[str(video_path)],
            video_path=str(video_path),
            title=meta.title,
            caption=caption,
            caption_hash=_hash_caption(caption),
            language=meta.language or self.config.default_language,
        )

    def _build_carousel_queue_item(
        self,
        carousel_dir: Path,
        meta: VideoMeta,
        image_paths: List[Path],
    ) -> QueueItem:
        caption = generate_caption(meta)
        tiktok_caption = generate_tiktok_carousel_caption(meta)
        return QueueItem(
            file=carousel_dir.name,
            content_type="carousel",
            source_path=str(carousel_dir),
            platform_content={"tiktok": tiktok_caption},
            asset_paths=[str(path) for path in image_paths],
            title=meta.title,
            caption=caption,
            caption_hash=_hash_caption(caption),
            language=meta.language or self.config.default_language,
        )

    def _upload_item_media(
        self,
        item: Dict[str, object],
        content_type: str,
    ) -> List[Dict[str, str]]:
        if content_type == "carousel":
            asset_paths = [Path(str(path)) for path in item.get("asset_paths") or []]
            if len(asset_paths) < 2:
                raise RuntimeError(
                    f"Carousel {item['file']} must contain at least 2 images."
                )
            return self.client.upload_media_batch(asset_paths, media_type="image")

        video_path_raw = item.get("video_path")
        if not video_path_raw:
            asset_paths = item.get("asset_paths") or []
            if not asset_paths:
                raise RuntimeError(f"Queue item {item['file']} has no media path.")
            video_path_raw = asset_paths[0]

        video_path = Path(str(video_path_raw))
        return [self.client.upload_media_item(video_path, media_type="video")]

    def _refresh_existing_queue(self) -> None:
        if not self.queue:
            return

        refreshed_queue: List[Dict[str, object]] = []
        global_meta_by_file = load_global_meta(self.config.video_meta_json)

        for queue_item in self.queue:
            content_type = str(queue_item.get("content_type") or "reel")
            scheduled_for = queue_item.get("scheduled_for")

            try:
                if content_type == "carousel":
                    carousel_dir = Path(
                        str(queue_item.get("source_path") or self.config.ready_carousels_dir / queue_item["file"])
                    )
                    meta, image_paths = load_carousel_meta(
                        carousel_dir,
                        self.config.default_language,
                    )
                    rebuilt = asdict(
                        self._build_carousel_queue_item(carousel_dir, meta, image_paths)
                    )
                else:
                    video_path = Path(
                        str(queue_item.get("video_path") or queue_item.get("source_path"))
                    )
                    meta = global_meta_by_file.get(video_path.name)
                    if meta is None:
                        resolved = resolve_video_meta_batch(
                            [video_path],
                            self.config.video_meta_json,
                            self.config.default_language,
                        )
                        meta = resolved[0]
                    rebuilt = asdict(self._build_queue_item(video_path, meta))
            except Exception as exc:
                logger.warning(
                    "Failed to refresh queued item %s, keeping previous version: %s",
                    queue_item.get("file"),
                    exc,
                )
                refreshed_queue.append(queue_item)
                continue

            rebuilt["scheduled_for"] = scheduled_for
            refreshed_queue.append(rebuilt)

            if self.state.get(rebuilt["file"]):
                self.state[rebuilt["file"]]["caption_hash"] = rebuilt["caption_hash"]
                self.state[rebuilt["file"]]["title"] = rebuilt["title"]
                self.state[rebuilt["file"]]["content_type"] = rebuilt["content_type"]

        self.queue = refreshed_queue
        self._persist()

    def _persist(self) -> None:
        save_state(self.config.state_file, self.state)
        save_queue(self.config.queue_file, self.queue)
