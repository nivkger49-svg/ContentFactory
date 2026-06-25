from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    load_dotenv = None


def _publishing_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_env() -> None:
    env_path = _publishing_root() / ".env"
    if env_path.exists() and load_dotenv is not None:
        load_dotenv(env_path)


@dataclass(frozen=True)
class Config:
    publishing_root: Path
    contentfactory_root: Path
    ready_videos_dir: Path
    ready_carousels_dir: Path
    video_meta_json: Path
    default_language: str
    publish_mode: str
    posting_interval_hours: int
    max_posts_per_day: int
    planner_batch_size: int
    timezone: str
    daily_posting_slots: Tuple[str, ...]
    target_platforms: Tuple[str, ...]
    zernio_api_key: Optional[str]
    zernio_profile_id: Optional[str]
    vercel_blob_token: Optional[str]
    vercel_blob_store_id: Optional[str]
    vercel_blob_api_url: str
    blob_buffer_max_bytes: int
    blob_cleanup_interval_days: int
    blob_retention_days: int
    comment_base_url: str
    comment_utm_source: str
    comment_utm_medium: str
    comment_utm_campaign: str
    comment_log_file: Path
    state_file: Path
    queue_file: Path
    log_file: Path

    @property
    def is_draft_mode(self) -> bool:
        return self.publish_mode == "draft"


def load_config() -> Config:
    _load_env()
    publishing_root = _publishing_root()

    contentfactory_root = Path(
        os.getenv("CONTENTFACTORY_ROOT", "/Users/mister/Documents/ContentFactory")
    ).expanduser()
    ready_videos_dir = Path(
        os.getenv(
            "READY_VIDEOS_DIR",
            str(contentfactory_root / "Видео_готовые_с_субтитрами"),
        )
    ).expanduser()
    ready_carousels_dir = Path(
        os.getenv(
            "READY_CAROUSELS_DIR",
            str(contentfactory_root / "Карусели_готовые"),
        )
    ).expanduser()
    video_meta_json = Path(
        os.getenv("VIDEO_META_JSON", str(contentfactory_root / "video_meta.json"))
    ).expanduser()

    publish_mode = os.getenv("PUBLISH_MODE", "draft").strip().lower() or "draft"
    if publish_mode not in {"draft", "schedule", "publish"}:
        raise ValueError(
            "PUBLISH_MODE must be one of: draft, schedule, publish"
        )

    interval_raw = os.getenv("POSTING_INTERVAL_HOURS", "6")
    max_per_day_raw = os.getenv("MAX_POSTS_PER_DAY", "3")
    target_platforms = tuple(
        platform.strip().lower()
        for platform in os.getenv("TARGET_PLATFORMS", "instagram,tiktok").split(",")
        if platform.strip()
    )
    daily_posting_slots = tuple(
        slot.strip()
        for slot in os.getenv("DAILY_POSTING_SLOTS", "10:00,18:00").split(",")
        if slot.strip()
    )

    data_dir = publishing_root / "data"

    return Config(
        publishing_root=publishing_root,
        contentfactory_root=contentfactory_root,
        ready_videos_dir=ready_videos_dir,
        ready_carousels_dir=ready_carousels_dir,
        video_meta_json=video_meta_json,
        default_language=os.getenv("DEFAULT_LANGUAGE", "uk").strip() or "uk",
        publish_mode=publish_mode,
        posting_interval_hours=int(interval_raw),
        max_posts_per_day=int(max_per_day_raw),
        planner_batch_size=int(os.getenv("PLANNER_BATCH_SIZE", "5")),
        timezone=os.getenv("TIMEZONE", "Europe/Bucharest").strip()
        or "Europe/Bucharest",
        daily_posting_slots=daily_posting_slots,
        target_platforms=target_platforms,
        zernio_api_key=os.getenv("ZERNIO_API_KEY") or None,
        zernio_profile_id=os.getenv("ZERNIO_PROFILE_ID") or None,
        vercel_blob_token=(
            os.getenv("VERCEL_BLOB_TOKEN")
            or os.getenv("BLOB_READ_WRITE_TOKEN_READ_WRITE_TOKEN")
            or None
        ),
        vercel_blob_store_id=(
            os.getenv("BLOB_STORE_ID")
            or os.getenv("BLOB_READ_WRITE_TOKEN_STORE_ID")
            or None
        ),
        vercel_blob_api_url=(
            os.getenv("VERCEL_BLOB_API_URL", "https://vercel.com/api/blob").strip()
            or "https://vercel.com/api/blob"
        ),
        blob_buffer_max_bytes=int(
            os.getenv("BLOB_BUFFER_MAX_BYTES", str(1024 * 1024 * 1024))
        ),
        blob_cleanup_interval_days=int(
            os.getenv("BLOB_CLEANUP_INTERVAL_DAYS", "2")
        ),
        blob_retention_days=int(os.getenv("BLOB_RETENTION_DAYS", "2")),
        comment_base_url=(
            os.getenv(
                "COMMENT_BASE_URL",
                "https://mamabezkriku.com/public/vash-profil/",
            ).strip()
            or "https://mamabezkriku.com/public/vash-profil/"
        ),
        comment_utm_source=os.getenv("COMMENT_UTM_SOURCE", "facebook").strip() or "facebook",
        comment_utm_medium=os.getenv("COMMENT_UTM_MEDIUM", "comment").strip() or "comment",
        comment_utm_campaign=os.getenv("COMMENT_UTM_CAMPAIGN", "organic").strip() or "organic",
        comment_log_file=data_dir / "published-comments.json",
        state_file=data_dir / "publishing-state.json",
        queue_file=data_dir / "publishing-queue.json",
        log_file=data_dir / "published-log.json",
    )
