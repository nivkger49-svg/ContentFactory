from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from config import Config
from logger import get_logger


logger = get_logger("contentfactory-publishing.blob-buffer")

STATE_KEY = "_blob_buffer"
STATE_VERSION = 1


def _now(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone)).replace(microsecond=0)


def _now_iso(timezone: str) -> str:
    return _now(timezone).isoformat()


def _parse_iso(value: object) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _normalize_store_id(raw_value: str) -> str:
    value = raw_value.strip()
    if value.startswith("store_"):
        return value[len("store_") :]
    return value


def _extract_store_id_from_token(token: str) -> Optional[str]:
    parts = token.strip().split("_")
    if len(parts) >= 4 and parts[3]:
        return _normalize_store_id(parts[3])
    return None


def _is_vercel_blob_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and "vercel-storage.com" in parsed.netloc


class BlobBufferManager:
    def __init__(self, config: Config, state: Dict[str, Dict[str, Any]]) -> None:
        self.config = config
        self.state = state

    def ensure_capacity_for_upload(self, asset_paths: Iterable[Path]) -> None:
        candidate_sizes = [
            path.stat().st_size
            for path in asset_paths
            if path.exists() and path.is_file()
        ]
        if not candidate_sizes:
            return

        projected_size = self.get_active_bytes() + sum(candidate_sizes)
        if projected_size <= self.config.blob_buffer_max_bytes:
            return

        logger.warning(
            "Blob buffer projected usage %s bytes exceeds limit %s bytes. Forcing cleanup.",
            projected_size,
            self.config.blob_buffer_max_bytes,
        )
        self.cleanup_if_due(force=True)

        projected_size = self.get_active_bytes() + sum(candidate_sizes)
        if projected_size > self.config.blob_buffer_max_bytes:
            raise RuntimeError(
                "Blob buffer limit would be exceeded even after cleanup. "
                "Wait for old media to age out, trigger cleanup later, or increase "
                "BLOB_BUFFER_MAX_BYTES."
            )

    def record_uploaded_media(
        self,
        owner_file: str,
        source_paths: Iterable[Path],
        media_items: List[Dict[str, str]],
        content_type: str,
    ) -> None:
        source_path_list = list(source_paths)
        now_iso = _now_iso(self.config.timezone)
        items = self._items()

        for media_item, source_path in zip(media_items, source_path_list):
            media_url = str(media_item.get("url") or "").strip()
            if not media_url or not _is_vercel_blob_url(media_url):
                continue

            existing = items.get(media_url, {})
            items[media_url] = {
                **existing,
                "url": media_url,
                "size_bytes": source_path.stat().st_size if source_path.exists() else int(existing.get("size_bytes") or 0),
                "source_path": str(source_path),
                "content_type": content_type,
                "media_type": str(media_item.get("type") or ""),
                "owner_file": owner_file,
                "owner_status": str(existing.get("owner_status") or "uploaded"),
                "uploaded_at": str(existing.get("uploaded_at") or now_iso),
                "last_seen_at": now_iso,
                "scheduled_for": existing.get("scheduled_for"),
                "published_at": existing.get("published_at"),
                "deleted_at": existing.get("deleted_at"),
                "delete_attempts": int(existing.get("delete_attempts") or 0),
                "delete_error": existing.get("delete_error"),
            }

    def refresh_owner_state(self, owner_file: str, owner_state: Dict[str, Any]) -> None:
        media_urls = owner_state.get("media_urls") or []
        items = self._items()
        now_iso = _now_iso(self.config.timezone)

        for raw_url in media_urls:
            media_url = str(raw_url or "").strip()
            if not media_url:
                continue

            existing = items.get(media_url, {"url": media_url})
            published_at = existing.get("published_at")
            status = str(owner_state.get("status") or existing.get("owner_status") or "")
            if status == "published_now" and not published_at:
                published_at = now_iso

            items[media_url] = {
                **existing,
                "url": media_url,
                "owner_file": owner_file,
                "owner_status": status,
                "scheduled_for": owner_state.get("scheduled_for") or existing.get("scheduled_for"),
                "published_at": published_at,
                "last_seen_at": now_iso,
                "deleted_at": existing.get("deleted_at"),
                "delete_attempts": int(existing.get("delete_attempts") or 0),
                "delete_error": existing.get("delete_error"),
            }

    def cleanup_if_due(self, force: bool = False) -> Dict[str, Any]:
        if not self.config.vercel_blob_token:
            return {"status": "skipped", "reason": "missing_blob_token"}

        bucket = self._bucket()
        now = _now(self.config.timezone)
        last_cleanup_at = _parse_iso(bucket.get("last_cleanup_at"))
        interval = timedelta(days=self.config.blob_cleanup_interval_days)

        if (
            not force
            and last_cleanup_at is not None
            and now < last_cleanup_at + interval
        ):
            return {
                "status": "skipped",
                "reason": "cleanup_not_due",
                "next_cleanup_after": (last_cleanup_at + interval).isoformat(),
            }

        deleted_urls: List[str] = []
        skipped_urls: List[str] = []
        failed_urls: List[Dict[str, str]] = []

        for media_url, item in list(self._items().items()):
            if item.get("deleted_at"):
                continue

            if not self._is_deletion_due(item, now):
                skipped_urls.append(media_url)
                continue

            try:
                self._delete_urls([media_url])
            except FileNotFoundError:
                logger.info("Blob already missing during cleanup: %s", media_url)
            except RuntimeError as exc:
                item["delete_attempts"] = int(item.get("delete_attempts") or 0) + 1
                item["delete_error"] = str(exc)
                failed_urls.append({"url": media_url, "error": str(exc)})
                continue

            item["deleted_at"] = now.isoformat()
            item["delete_error"] = None
            item["delete_attempts"] = int(item.get("delete_attempts") or 0) + 1
            deleted_urls.append(media_url)

        bucket["version"] = STATE_VERSION
        bucket["last_cleanup_at"] = now.isoformat()
        bucket["last_cleanup_summary"] = {
            "deleted_count": len(deleted_urls),
            "skipped_count": len(skipped_urls),
            "failed_count": len(failed_urls),
            "active_bytes": self.get_active_bytes(),
        }

        return {
            "status": "ok",
            "deleted_urls": deleted_urls,
            "skipped_urls": skipped_urls,
            "failed_urls": failed_urls,
            "active_bytes": self.get_active_bytes(),
        }

    def get_active_bytes(self) -> int:
        total = 0
        for item in self._items().values():
            if item.get("deleted_at"):
                continue
            total += int(item.get("size_bytes") or 0)
        return total

    def get_status(self) -> Dict[str, Any]:
        bucket = self._bucket()
        active_items = [
            item
            for item in self._items().values()
            if not item.get("deleted_at")
        ]
        return {
            "limit_bytes": self.config.blob_buffer_max_bytes,
            "active_bytes": self.get_active_bytes(),
            "active_items": len(active_items),
            "last_cleanup_at": bucket.get("last_cleanup_at"),
            "cleanup_interval_days": self.config.blob_cleanup_interval_days,
            "retention_days": self.config.blob_retention_days,
        }

    def _is_deletion_due(self, item: Dict[str, Any], now: datetime) -> bool:
        status = str(item.get("owner_status") or "").strip().lower()
        if status == "queued":
            return False

        reference_at = (
            _parse_iso(item.get("published_at"))
            or _parse_iso(item.get("scheduled_for"))
            or _parse_iso(item.get("uploaded_at"))
        )
        if reference_at is None:
            return False

        expires_at = reference_at + timedelta(days=self.config.blob_retention_days)
        if status == "scheduled" and reference_at > now:
            return False
        return now >= expires_at

    def _bucket(self) -> Dict[str, Any]:
        bucket = self.state.get(STATE_KEY)
        if isinstance(bucket, dict):
            bucket.setdefault("version", STATE_VERSION)
            bucket.setdefault("items", {})
            return bucket

        bucket = {
            "version": STATE_VERSION,
            "items": {},
        }
        self.state[STATE_KEY] = bucket
        return bucket

    def _items(self) -> Dict[str, Dict[str, Any]]:
        bucket = self._bucket()
        items = bucket.get("items")
        if isinstance(items, dict):
            return items

        bucket["items"] = {}
        return bucket["items"]

    def _delete_urls(self, urls: List[str]) -> None:
        if not urls:
            return

        payload = self._api_request(
            "/delete",
            method="POST",
            payload={"urls": urls},
        )
        if payload is None:
            return

    def _api_request(
        self,
        path: str,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        token = self.config.vercel_blob_token
        if not token:
            raise RuntimeError("Missing Vercel Blob token.")

        store_id = (
            self.config.vercel_blob_store_id
            or _extract_store_id_from_token(token)
        )
        if not store_id:
            raise RuntimeError(
                "Could not resolve Blob store id. Set BLOB_STORE_ID or BLOB_READ_WRITE_TOKEN_STORE_ID."
            )

        url = self.config.vercel_blob_api_url.rstrip("/") + path
        if query:
            url = f"{url}?{urlencode(query)}"

        body = None
        headers = {
            "authorization": f"Bearer {token}",
            "x-vercel-blob-store-id": _normalize_store_id(store_id),
            "x-api-version": "12",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["content-type"] = "application/json"

        request = Request(url, data=body, method=method, headers=headers)

        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8").strip()
        except HTTPError as exc:
            response_text = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404:
                raise FileNotFoundError(url) from exc
            raise RuntimeError(
                f"Blob API {method} {path} failed with HTTP {exc.code}: {response_text}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Blob API request failed: {exc}") from exc

        if not raw:
            return None
        return json.loads(raw)
