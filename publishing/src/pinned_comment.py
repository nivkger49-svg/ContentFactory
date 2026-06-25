from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any, Dict, Optional
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from config import Config


COMMENT_TEMPLATE = """💙 Не знаєте, які вправи підійдуть саме вашій дитині?

Пройдіть коротке опитування - додаток безкоштовно підбере вправи та ігри саме під вік і потреби вашої дитини.

👇 Почати можна тут:

{url}"""


@dataclass(frozen=True)
class GeneratedComment:
    video_id: str
    platform: str
    post_id: str
    utm_content: str
    full_url: str
    text: str
    reference_at: str
    status: str
    scheduled_for: Optional[str] = None
    published_at: Optional[str] = None
    comment_id: Optional[str] = None
    pinned: bool = False
    manual_pin_required: bool = True
    pin_supported: bool = False
    reason: Optional[str] = None
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None


def build_unique_utm_content(
    *,
    video_id: str,
    platform: str,
    post_id: str,
    reference_at: str,
) -> str:
    dt = datetime.fromisoformat(str(reference_at).replace("Z", "+00:00"))
    timestamp = dt.astimezone(ZoneInfo("Europe/Bucharest")).strftime("%Y%m%d_%H%M%S")
    digest = sha256(f"{video_id}|{platform}|{reference_at}".encode("utf-8")).hexdigest()[:6]
    normalized_platform = (platform or "platform").strip().lower()
    return f"{normalized_platform}_reel_{timestamp}_{digest}"


def build_comment_url(config: Config, utm_content: str) -> str:
    query = urlencode(
        {
            "utm_source": config.comment_utm_source,
            "utm_medium": config.comment_utm_medium,
            "utm_campaign": config.comment_utm_campaign,
            "utm_content": utm_content,
        }
    )
    return f"{config.comment_base_url.rstrip('/')}/?{query}"


def render_comment_text(url: str) -> str:
    return COMMENT_TEMPLATE.format(url=url)


def build_planned_comment_text(
    *,
    config: Config,
    video_id: str,
    platform: str,
    reference_at: str,
) -> str:
    utm_content = build_unique_utm_content(
        video_id=video_id,
        platform=platform,
        post_id="",
        reference_at=reference_at,
    )
    url = build_comment_url(config, utm_content)
    return render_comment_text(url)


def build_generated_comment(
    *,
    config: Config,
    video_id: str,
    platform: str,
    post_id: str,
    reference_at: str,
    status: str,
    scheduled_for: Optional[str] = None,
    published_at: Optional[str] = None,
    reason: Optional[str] = None,
    comment_id: Optional[str] = None,
    pinned: bool = False,
    manual_pin_required: bool = True,
    pin_supported: bool = False,
    platform_post_id: Optional[str] = None,
    platform_post_url: Optional[str] = None,
) -> GeneratedComment:
    utm_content = build_unique_utm_content(
        video_id=video_id,
        platform=platform,
        post_id=post_id,
        reference_at=reference_at,
    )
    full_url = build_comment_url(config, utm_content)
    text = render_comment_text(full_url)
    return GeneratedComment(
        video_id=video_id,
        platform=platform,
        post_id=post_id,
        utm_content=utm_content,
        full_url=full_url,
        text=text,
        reference_at=reference_at,
        status=status,
        scheduled_for=scheduled_for,
        published_at=published_at,
        comment_id=comment_id,
        pinned=pinned,
        manual_pin_required=manual_pin_required,
        pin_supported=pin_supported,
        reason=reason,
        platform_post_id=platform_post_id,
        platform_post_url=platform_post_url,
    )


def comment_to_record(comment: GeneratedComment) -> Dict[str, Any]:
    return {
        "video_id": comment.video_id,
        "platform": comment.platform,
        "post_id": comment.post_id,
        "utm_content": comment.utm_content,
        "full_url": comment.full_url,
        "text": comment.text,
        "reference_at": comment.reference_at,
        "scheduled_for": comment.scheduled_for,
        "published_at": comment.published_at,
        "status": comment.status,
        "comment_id": comment.comment_id,
        "pinned": comment.pinned,
        "manual_pin_required": comment.manual_pin_required,
        "pin_supported": comment.pin_supported,
        "reason": comment.reason,
        "platform_post_id": comment.platform_post_id,
        "platform_post_url": comment.platform_post_url,
    }
