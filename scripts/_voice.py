from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "assets" / "voice"
DOTENV_PATH = ROOT / ".env"


def load_dotenv(path: Path = DOTENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")


def _coerce_path(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def resolve_voice_file(default: Path | None = None) -> Path:
    load_dotenv()

    explicit = os.environ.get("CONTENTFACTORY_VOICE_FILE", "").strip()
    if explicit:
        candidate = _coerce_path(explicit)
        if candidate.exists():
            return candidate

    preferred = VOICE_DIR / "voice.mp3"
    if preferred.exists():
        return preferred

    if default and default.exists():
        return default

    newest = sorted(VOICE_DIR.glob("*.mp3"), key=lambda path: path.stat().st_mtime, reverse=True)
    if newest:
        return newest[0]

    return preferred if default is None else default
