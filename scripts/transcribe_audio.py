from __future__ import annotations

import argparse
import os
from pathlib import Path

from faster_whisper import WhisperModel


ROOT = Path(__file__).resolve().parents[1]
MODEL_CACHE = ROOT / "tools" / "asr" / "models"


def srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path: Path, segments) -> None:
    lines: list[str] = []
    for index, segment in enumerate(segments, start=1):
        text = " ".join(segment.text.strip().split())
        if not text:
            continue
        lines.append(str(index))
        lines.append(f"{srt_time(segment.start)} --> {srt_time(segment.end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_txt(path: Path, segments) -> None:
    text = "\n".join(" ".join(s.text.strip().split()) for s in segments if s.text.strip())
    path.write_text(text + "\n", encoding="utf-8")


def word_chunks(segments, max_seconds: float, max_chars: int):
    chunks = []
    current_words: list[str] = []
    start: float | None = None
    end: float | None = None

    def flush():
        nonlocal current_words, start, end
        if current_words and start is not None and end is not None:
            chunks.append({"start": start, "end": end, "text": " ".join(current_words)})
        current_words = []
        start = None
        end = None

    for segment in segments:
        words = getattr(segment, "words", None) or []
        if not words:
            text = " ".join(segment.text.strip().split())
            if text:
                chunks.append({"start": segment.start, "end": segment.end, "text": text})
            continue
        for word in words:
            token = word.word.strip()
            if not token:
                continue
            if start is None:
                start = word.start
            current_words.append(token)
            end = word.end
            text_now = " ".join(current_words)
            duration = (end or 0) - (start or 0)
            ends_sentence = token.endswith((".", "!", "?", "…", ":"))
            if duration >= max_seconds or len(text_now) >= max_chars or ends_sentence:
                flush()
    flush()
    return chunks


def write_chunk_srt(path: Path, chunks) -> None:
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        text = " ".join(chunk["text"].strip().split())
        if not text:
            continue
        lines.append(str(index))
        lines.append(f"{srt_time(chunk['start'])} --> {srt_time(chunk['end'])}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio to SRT/TXT with local faster-whisper.")
    parser.add_argument("audio", help="Path to mp3/wav/m4a audio file")
    parser.add_argument("--model", default="small", help="Whisper model: tiny, base, small, medium, large-v3, distil-large-v3")
    parser.add_argument("--language", default="uk", help="Language code, e.g. uk, ru, en. Use auto for detection.")
    parser.add_argument("--output-dir", default=None, help="Where to write SRT/TXT. Defaults to audio folder.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Use cpu by default.")
    parser.add_argument("--compute-type", default="int8", help="int8 is light for CPU; float16 for CUDA.")
    parser.add_argument("--subtitle-mode", default="words", choices=["words", "segments"], help="words creates short Reels-friendly cues.")
    parser.add_argument("--max-subtitle-seconds", type=float, default=2.4, help="Max cue duration in words mode.")
    parser.add_argument("--max-subtitle-chars", type=int, default=42, help="Max cue text length in words mode.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audio = Path(args.audio).resolve()
    if not audio.exists():
        raise SystemExit(f"Audio not found: {audio}")

    MODEL_CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(MODEL_CACHE))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(MODEL_CACHE / "hub"))

    out_dir = Path(args.output_dir).resolve() if args.output_dir else audio.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    srt_path = out_dir / f"{audio.stem}.srt"
    txt_path = out_dir / f"{audio.stem}.txt"

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
        download_root=str(MODEL_CACHE),
    )
    language = None if args.language.lower() == "auto" else args.language
    segments_iter, info = model.transcribe(
        str(audio),
        language=language,
        vad_filter=True,
        beam_size=5,
        word_timestamps=args.subtitle_mode == "words",
    )
    segments = list(segments_iter)

    if args.subtitle_mode == "words":
        chunks = word_chunks(segments, args.max_subtitle_seconds, args.max_subtitle_chars)
        write_chunk_srt(srt_path, chunks)
    else:
        write_srt(srt_path, segments)
    write_txt(txt_path, segments)

    print(f"audio={audio}")
    print(f"model={args.model}")
    print(f"language={info.language} probability={info.language_probability:.2f}")
    print(f"srt={srt_path}")
    print(f"txt={txt_path}")


if __name__ == "__main__":
    main()
