from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class VideoMeta:
    file: str
    title: str
    voiceover: str = ""
    angle: str = ""
    cta: str = ""
    hook: str = ""
    offer: str = ""
    pain: str = ""
    language: str = "uk"
    raw: Dict[str, Any] = field(default_factory=dict)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_global_meta(meta_json_path: Path) -> Dict[str, VideoMeta]:
    if not meta_json_path.exists():
        return {}

    data = _read_json(meta_json_path)
    if not isinstance(data, list):
        raise ValueError(f"Expected an array in {meta_json_path}")

    records: Dict[str, VideoMeta] = {}
    for item in data:
        normalized = normalize_meta(item)
        if normalized:
            records[normalized.file] = normalized
    return records


def normalize_meta(payload: Dict[str, Any]) -> Optional[VideoMeta]:
    if not isinstance(payload, dict):
        return None

    file_name = (
        payload.get("file")
        or payload.get("source_video")
        or payload.get("video")
        or payload.get("filename")
    )
    if not file_name:
        return None

    voiceover = (
        payload.get("voiceover")
        or payload.get("voiceover_text")
        or payload.get("script")
        or ""
    )

    return VideoMeta(
        file=str(file_name),
        title=str(payload.get("title") or Path(str(file_name)).stem).strip(),
        voiceover=str(voiceover).strip(),
        angle=str(payload.get("angle") or "").strip(),
        cta=str(payload.get("cta") or "").strip(),
        hook=str(payload.get("hook") or "").strip(),
        offer=str(payload.get("offer") or "").strip(),
        pain=str(payload.get("pain") or "").strip(),
        language=str(payload.get("language") or "uk").strip() or "uk",
        raw=payload,
    )


def load_sidecar_meta(video_path: Path) -> Optional[VideoMeta]:
    sidecar_path = video_path.with_suffix(".creative.json")
    if not sidecar_path.exists():
        return None
    return normalize_meta(_read_json(sidecar_path))


def get_video_meta(
    video_path: Path,
    global_meta: Dict[str, VideoMeta],
    default_language: str,
) -> VideoMeta:
    file_name = video_path.name

    if file_name in global_meta:
        meta = global_meta[file_name]
    else:
        meta = load_sidecar_meta(video_path)

    if meta is None:
        return VideoMeta(
            file=file_name,
            title=video_path.stem.replace("_", " ").strip(),
            language=default_language,
        )

    if not meta.language:
        meta.language = default_language
    return meta


def resolve_video_meta_batch(
    video_paths: Iterable[Path],
    meta_json_path: Path,
    default_language: str,
) -> List[VideoMeta]:
    global_meta = load_global_meta(meta_json_path)
    return [
        get_video_meta(video_path, global_meta, default_language)
        for video_path in video_paths
    ]
