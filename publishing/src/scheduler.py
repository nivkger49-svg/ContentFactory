from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple
from zoneinfo import ZoneInfo


def _parse_dt(value: str, timezone: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone))
    return parsed


def _parse_slots(slots: Tuple[str, ...]) -> List[Tuple[int, int]]:
    parsed: List[Tuple[int, int]] = []
    for slot in slots:
        hours, minutes = slot.split(":", 1)
        parsed.append((int(hours), int(minutes)))
    return sorted(parsed)


def _next_available_slot(
    earliest: datetime,
    scheduled_counts: Dict[str, int],
    max_posts_per_day: int,
    slot_times: List[Tuple[int, int]],
) -> datetime:
    candidate_date = earliest.date()

    while True:
        if scheduled_counts[candidate_date.isoformat()] >= max_posts_per_day:
            candidate_date = candidate_date + timedelta(days=1)
            continue

        for hour, minute in slot_times:
            slot_dt = earliest.replace(
                year=candidate_date.year,
                month=candidate_date.month,
                day=candidate_date.day,
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0,
            )
            if slot_dt >= earliest:
                return slot_dt

        candidate_date = candidate_date + timedelta(days=1)


def build_schedule(
    queue_items: Iterable[Dict[str, object]],
    existing_log: List[Dict[str, object]],
    interval_hours: int,
    max_posts_per_day: int,
    timezone: str,
    daily_posting_slots: Tuple[str, ...],
) -> List[Dict[str, object]]:
    tz = ZoneInfo(timezone)
    now = datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    earliest = now + timedelta(hours=1)
    slot_times = _parse_slots(daily_posting_slots)

    scheduled_counts = defaultdict(int)
    latest_taken = earliest

    for item in existing_log:
        scheduled_for = item.get("scheduled_for")
        if not scheduled_for:
            continue
        dt = _parse_dt(str(scheduled_for), timezone).astimezone(tz)
        scheduled_counts[dt.date().isoformat()] += 1
        if dt > latest_taken:
            latest_taken = dt

    current = latest_taken
    results: List[Dict[str, object]] = []

    for item in queue_items:
        candidate = current if current > earliest else earliest
        candidate = _next_available_slot(
            earliest=candidate,
            scheduled_counts=scheduled_counts,
            max_posts_per_day=max_posts_per_day,
            slot_times=slot_times,
        )
        scheduled_counts[candidate.date().isoformat()] += 1
        results.append(
            {
                **item,
                "scheduled_for": candidate.astimezone(ZoneInfo("UTC"))
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )
        current = candidate + timedelta(hours=max(interval_hours, 1))

    return results
