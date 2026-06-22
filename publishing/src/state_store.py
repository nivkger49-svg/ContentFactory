from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _default_payload(path: Path) -> Any:
    if path.name == "publishing-state.json":
        return {}
    return []


def load_json(path: Path) -> Any:
    if not path.exists():
        return _default_payload(path)

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return _default_payload(path)
    return json.loads(raw)


def save_json(path: Path, payload: Any) -> None:
    _ensure_parent(path)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def load_state(path: Path) -> Dict[str, Dict[str, Any]]:
    data = load_json(path)
    return data if isinstance(data, dict) else {}


def save_state(path: Path, state: Dict[str, Dict[str, Any]]) -> None:
    save_json(path, state)


def load_queue(path: Path) -> List[Dict[str, Any]]:
    data = load_json(path)
    return data if isinstance(data, list) else []


def save_queue(path: Path, queue: List[Dict[str, Any]]) -> None:
    save_json(path, queue)


def append_log(path: Path, item: Dict[str, Any]) -> None:
    log = load_queue(path)
    log.append(item)
    save_queue(path, log)
