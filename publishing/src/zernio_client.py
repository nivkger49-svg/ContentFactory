from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from config import Config
from logger import get_logger


logger = get_logger("contentfactory-publishing.zernio")


def _payload_get(payload: object, *keys: str) -> Optional[str]:
    for key in keys:
        if isinstance(payload, dict):
            value = payload.get(key)
        else:
            value = getattr(payload, key, None)
        if value:
            return str(value)
    return None


def _payload_list(payload: object, key: str) -> List[Dict[str, object]]:
    if isinstance(payload, dict):
        value = payload.get(key, [])
    else:
        value = getattr(payload, key, [])
    return value if isinstance(value, list) else []


def _item_get(item: object, key: str, default: object = None) -> object:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _normalize_platform(value: object) -> str:
    text = str(value or "").strip().lower()
    if "." in text:
        text = text.split(".")[-1]
    return text


def _extract_profile_id(value: object) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, str):
        if "field_id=" in value:
            marker = "field_id='"
            start = value.find(marker)
            if start != -1:
                start += len(marker)
                end = value.find("'", start)
                if end != -1:
                    return value[start:end]
        return value
    direct = _item_get(value, "id") or _item_get(value, "field_id")
    return str(direct) if direct else None


class ZernioClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._client = None

    def _sdk(self):
        if self._client is not None:
            return self._client
        if not self.config.zernio_api_key:
            raise RuntimeError("ZERNIO_API_KEY is required for schedule/publish modes.")
        try:
            from zernio import Zernio
        except ImportError as exc:
            raise RuntimeError(
                "zernio-sdk is not installed. Run `pip install -e .` inside publishing/."
            ) from exc

        self._client = Zernio(api_key=self.config.zernio_api_key)
        return self._client

    def _list_accounts(self) -> List[Dict[str, object]]:
        client = self._sdk()
        resource = getattr(client, "accounts")

        if hasattr(resource, "list"):
            payload = resource.list()
        elif hasattr(resource, "list_accounts"):
            payload = resource.list_accounts()
        else:
            raise RuntimeError("Unsupported Zernio SDK version: accounts list method missing.")

        accounts = _payload_list(payload, "accounts")
        if not isinstance(accounts, list):
            raise RuntimeError("Unexpected Zernio accounts payload.")
        return accounts

    def get_target_platforms(self) -> List[Dict[str, str]]:
        accounts = self._list_accounts()
        results: List[Dict[str, str]] = []

        for platform in self.config.target_platforms:
            matched = self._find_account(accounts, platform, self.config.zernio_profile_id)
            if matched:
                results.append(
                    {
                        "platform": platform,
                        "accountId": matched["id"],
                    }
                )

        if not results:
            raise RuntimeError(
                "No connected Instagram/TikTok accounts were found for the configured Zernio profile."
            )
        return results

    def _find_account(
        self,
        accounts: List[Dict[str, object]],
        platform: str,
        profile_id: Optional[str],
    ) -> Optional[Dict[str, str]]:
        for account in accounts:
            account_platform = _normalize_platform(_item_get(account, "platform", ""))
            if account_platform != platform:
                continue

            if profile_id:
                raw_profile = (
                    _item_get(account, "profileId")
                    or _item_get(account, "profile_id")
                    or _item_get(account, "profile")
                    or {}
                )
                raw_profile_id = _extract_profile_id(raw_profile)
                if raw_profile_id and str(raw_profile_id) != profile_id:
                    continue

            account_id = (
                _item_get(account, "id")
                or _item_get(account, "_id")
                or _item_get(account, "field_id")
            )
            if account_id:
                return {"id": str(account_id)}
        return None

    def upload_media(self, video_path: Path) -> str:
        logger.info("Uploading media to Zernio: %s", video_path.name)
        if video_path.stat().st_size > 4 * 1024 * 1024:
            if not self.config.vercel_blob_token:
                raise RuntimeError(
                    "Large video upload requires VERCEL_BLOB_TOKEN in publishing/.env."
                )
            payload = self._sdk().media.upload_large(
                str(video_path),
                vercel_token=self.config.vercel_blob_token,
            )
        else:
            payload = self._sdk().media.upload(str(video_path))

        media_url = _payload_get(payload, "publicUrl", "url", "downloadUrl")
        if not media_url:
            raise RuntimeError("Zernio media upload did not return a public URL.")
        return str(media_url)

    def create_post(
        self,
        caption: str,
        media_url: str,
        title: str,
        scheduled_for: Optional[str],
        publish_now: bool,
    ) -> Dict[str, object]:
        platforms = self.get_target_platforms()
        for platform in platforms:
            if platform["platform"] == "youtube":
                platform["youtubeTitle"] = title

        payload = {
            "content": caption,
            "media_items": [
                {
                    "type": "video",
                    "url": media_url,
                }
            ],
            "platforms": platforms,
            "timezone": self.config.timezone,
        }
        if publish_now:
            payload["publish_now"] = True
        elif scheduled_for:
            payload["scheduled_for"] = scheduled_for
        else:
            raise RuntimeError("A scheduled_for value is required when publish_now is False.")

        logger.info(
            "Creating Zernio post for %s platforms in %s mode.",
            len(platforms),
            "publish" if publish_now else "schedule",
        )
        return self._sdk().posts.create(**payload)
