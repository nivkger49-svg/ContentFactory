from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
CAROUSEL_MANIFEST_NAMES = ("carousel.json", "manifest.json")


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
        or payload.get("id")
        or payload.get("slug")
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


def _find_carousel_manifest(carousel_dir: Path) -> Optional[Path]:
    for name in CAROUSEL_MANIFEST_NAMES:
        candidate = carousel_dir / name
        if candidate.exists():
            return candidate

    custom_sidecar = carousel_dir / f"{carousel_dir.name}.creative.json"
    if custom_sidecar.exists():
        return custom_sidecar
    return None


def _resolve_slide_path(base_dir: Path, raw_value: str) -> Path:
    candidate = Path(str(raw_value))
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def _extract_slide_file(slide: Any) -> Optional[str]:
    if isinstance(slide, str):
        return slide
    if not isinstance(slide, dict):
        return None
    for key in ("file", "path", "image", "image_file", "url"):
        value = slide.get(key)
        if value:
            return str(value)
    return None


def _infer_carousel_images(carousel_dir: Path) -> List[Path]:
    image_root = carousel_dir / "images"
    search_roots = [image_root, carousel_dir] if image_root.exists() else [carousel_dir]
    image_paths: List[Path] = []
    for root in search_roots:
        for path in sorted(root.iterdir()):
            if not path.is_file():
                continue
            if path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            image_paths.append(path.resolve())
    return image_paths


def load_carousel_meta(
    carousel_dir: Path,
    default_language: str,
) -> tuple[VideoMeta, List[Path]]:
    manifest_path = _find_carousel_manifest(carousel_dir)
    payload: Dict[str, Any] = {}

    if manifest_path:
        raw_payload = _read_json(manifest_path)
        if not isinstance(raw_payload, dict):
            raise ValueError(f"Expected an object in {manifest_path}")
        payload = dict(raw_payload)

    payload.setdefault("file", carousel_dir.name)
    payload.setdefault("title", carousel_dir.name.replace("_", " ").strip())
    payload.setdefault("language", default_language)

    meta = normalize_meta(payload)
    if meta is None:
        meta = VideoMeta(
            file=carousel_dir.name,
            title=carousel_dir.name.replace("_", " ").strip(),
            language=default_language,
        )

    slides = payload.get("slides") or payload.get("images") or []
    image_paths: List[Path] = []
    if isinstance(slides, list) and slides:
        for slide in slides:
            slide_file = _extract_slide_file(slide)
            if not slide_file:
                continue
            image_paths.append(_resolve_slide_path(carousel_dir, slide_file))
    else:
        image_paths = _infer_carousel_images(carousel_dir)

    image_paths = [path for path in image_paths if path.exists() and path.is_file()]
    if len(image_paths) < 2:
        raise ValueError(
            f"Carousel {carousel_dir.name} must contain at least 2 images."
        )
    if len(image_paths) > 10:
        raise ValueError(
            f"Carousel {carousel_dir.name} exceeds Instagram limit of 10 images."
        )

    return meta, image_paths
