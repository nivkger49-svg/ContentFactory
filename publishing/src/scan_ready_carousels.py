from __future__ import annotations

from pathlib import Path
from typing import Dict, List


ACTIVE_STATUSES = {"queued", "scheduled", "published", "published_now"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MANIFEST_NAMES = {"carousel.json", "manifest.json"}


def _has_images(carousel_dir: Path) -> bool:
    image_roots = [carousel_dir / "images", carousel_dir]
    for root in image_roots:
        if not root.exists() or not root.is_dir():
            continue
        for path in root.iterdir():
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                return True
    return False


def _has_manifest(carousel_dir: Path) -> bool:
    for name in MANIFEST_NAMES:
        if (carousel_dir / name).exists():
            return True
    return False


def scan_ready_carousels(
    ready_carousels_dir: Path,
    state: Dict[str, dict],
) -> List[Path]:
    if not ready_carousels_dir.exists():
        return []

    ready: List[Path] = []
    for path in sorted(ready_carousels_dir.iterdir()):
        if not path.is_dir():
            continue

        current_state = state.get(path.name, {})
        status = str(current_state.get("status", "")).strip().lower()
        if status in ACTIVE_STATUSES:
            continue

        if not _has_manifest(path) and not _has_images(path):
            continue

        ready.append(path)
    return ready
