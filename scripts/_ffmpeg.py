from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_BIN = ROOT / "tools" / "ffmpeg" / "bin"


def project_bin(name: str) -> Path:
    exe = ".exe" if __import__("os").name == "nt" else ""
    return TOOLS_BIN / f"{name}{exe}"


def resolve_binary(name: str) -> str:
    local = project_bin(name)
    if local.exists():
        return str(local)
    found = shutil.which(name)
    if found:
        return found
    alt = shutil.which(f"{name}.exe")
    if alt:
        return alt
    expected = local if __import__("os").name == "nt" else Path(f"<PATH or {local}>")
    raise FileNotFoundError(f"{name} not found. Install it into PATH or place it at {expected}.")
