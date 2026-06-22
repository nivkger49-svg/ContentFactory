from __future__ import annotations

from pathlib import Path
from typing import Dict, List


ACTIVE_STATUSES = {"queued", "scheduled", "published", "published_now"}


def scan_ready_videos(
    ready_videos_dir: Path,
    state: Dict[str, dict],
) -> List[Path]:
    ready: List[Path] = []
    for path in sorted(ready_videos_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".mp4":
            continue

        current_state = state.get(path.name, {})
        status = str(current_state.get("status", "")).strip().lower()
        if status in ACTIVE_STATUSES:
            continue

        ready.append(path)
    return ready
