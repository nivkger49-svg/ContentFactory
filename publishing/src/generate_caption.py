from __future__ import annotations

import hashlib
from typing import List

from read_video_meta import VideoMeta


CTA_MAP = {
    "LEARN_MORE": "Переходьте за посиланням у шапці профілю, щоб пройти коротке опитування і отримати персональні рекомендації.",
    "SIGN_UP": "Зайдіть у шапку профілю та пройдіть коротке опитування, щоб отримати персональний план вправ.",
    "GET_STARTED": "Відкрийте посилання в шапці профілю та отримайте персональні вправи для вашої дитини.",
}

EMOJI_BEATS = ["✨", "🤍", "🌿", "💛", "🫶", "🌙"]

OPENERS = [
    "Іноді одна хвилина показує більше, ніж цілий день пояснень.",
    "За зовнішнім хаосом часто стоїть не впертість, а перевантаження.",
    "Батькам важко не тому, що вони роблять щось не так, а тому що сигнал дитини легко пропустити.",
    "Такі моменти виснажують, особливо коли здається, що все сталося раптово.",
]

BRIDGES = [
    "Саме тому важливо дивитися не лише на поведінку, а й на стан нервової системи.",
    "У таких історіях ключове питання не \"чому вона так поводиться\", а \"що зараз перевантажує її систему\".",
    "Коли ми бачимо причину глибше, з'являється більше спокою і менше безсилля.",
    "Розуміння причини дає батькам не почуття провини, а наступний конкретний крок.",
]

CLOSERS = [
    "Маленькі нейровправи можуть стати тим м'яким способом повернути більше регуляції в день.",
    "Короткі вправи через рух і гру часто допомагають дитині м'якше переключатися та менше зриватися.",
    "Поступова щоденна підтримка дає дитині більше опори, а дорослим більше передбачуваності.",
    "Коли вправи підібрані під стан дитини, вдома стає трохи спокійніше вже з перших кроків.",
]

HASHTAGS = [
    "#нейровправи",
    "#розвитокдитини",
    "#маминапідтримка",
    "#сенсорнарегуляція",
    "#дитячіемоції",
    "#neirokid",
]

BIO_CTA_VARIANTS = [
    "Перейдіть за посиланням у шапці профілю, щоб отримати персональні рекомендації саме для вашої дитини.",
    "Посилання в шапці профілю допоможе вам пройти коротке опитування та підібрати вправи під стан дитини.",
    "Зайдіть у шапку профілю та отримайте підбірку вправ, яка відповідає саме вашій ситуації.",
    "У шапці профілю є коротке опитування, після якого ви отримаєте персональний маршрут підтримки для дитини.",
    "Тисніть на посилання в шапці профілю, щоб отримати вправи та рекомендації під потреби вашої дитини.",
]

CTA_FOLLOWUP_VARIANTS = [
    "Там ви зможете пройти коротке опитування й отримати персональні рекомендації.",
    "Там на вас чекає коротке опитування і персональний маршрут підтримки.",
    "Саме там можна швидко підібрати вправи під вашу ситуацію.",
]

TIKTOK_SHORT_CTA = "Посилання в шапці профілю."
TIKTOK_MAX_PHOTO_TITLE_CHARS = 90


def _pick(options: List[str], seed: str, salt: str) -> str:
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def _clean_text(value: str) -> str:
    return " ".join(value.split()).strip()


def _add_emoji(text: str, seed: str, salt: str) -> str:
    if not text:
        return text
    emoji = _pick(EMOJI_BEATS, seed, salt)
    return f"{emoji} {text}"


def _resolve_cta(meta: VideoMeta) -> str:
    seed = f"{meta.file}|{meta.title}|{meta.angle}|{meta.hook}|cta"
    bio_cta = _pick(BIO_CTA_VARIANTS, seed, "bio-cta")
    if meta.cta in CTA_MAP:
        return bio_cta
    if meta.cta:
        base_cta = _clean_text(meta.cta)
        lower_cta = base_cta.lower()
        if "шап" in lower_cta and "проф" in lower_cta:
            followup = _pick(CTA_FOLLOWUP_VARIANTS, seed, "cta-followup")
            return f"{base_cta.rstrip('.')} — {followup}"
        return f"{base_cta} {bio_cta}"
    return bio_cta


def _normalize_multiline_text(value: str) -> str:
    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    return "\n\n".join(lines)


def _truncate_for_tiktok(text: str) -> str:
    compact = _clean_text(text)
    if len(compact) <= TIKTOK_MAX_PHOTO_TITLE_CHARS:
        return compact

    clipped = compact[: TIKTOK_MAX_PHOTO_TITLE_CHARS - 1].rstrip(" ,.-")
    return f"{clipped}…"


def generate_tiktok_carousel_caption(meta: VideoMeta) -> str:
    override = _clean_text(str(meta.raw.get("tiktok_caption_override") or ""))
    if override:
        return _truncate_for_tiktok(override)

    explicit_short = _clean_text(str(meta.raw.get("tiktok_title") or ""))
    if explicit_short:
        return _truncate_for_tiktok(explicit_short)

    opening = _clean_text(
        str(
            meta.raw.get("tiktok_hook")
            or meta.hook
            or meta.title
            or meta.pain
            or meta.angle
            or ""
        )
    )
    if opening and opening.lower().startswith("01_"):
        opening = ""
    if not opening:
        opening = "Підтримка для дитини починається з розуміння."

    candidate = f"{opening} {TIKTOK_SHORT_CTA}".strip()
    if len(_clean_text(candidate)) <= TIKTOK_MAX_PHOTO_TITLE_CHARS:
        return _clean_text(candidate)

    compact_cta = _clean_text(TIKTOK_SHORT_CTA)
    available_for_opening = TIKTOK_MAX_PHOTO_TITLE_CHARS - len(compact_cta) - 1
    if opening and available_for_opening > 12:
        shortened_opening = _truncate_for_tiktok(opening[:available_for_opening].rstrip())
        combined = _clean_text(f"{shortened_opening} {compact_cta}")
        if len(combined) <= TIKTOK_MAX_PHOTO_TITLE_CHARS:
            return combined

    fallback_parts = [part for part in [opening, _clean_text(meta.title), TIKTOK_SHORT_CTA] if part]
    for part in fallback_parts:
        if len(part) <= TIKTOK_MAX_PHOTO_TITLE_CHARS:
            return _truncate_for_tiktok(part)

    return _truncate_for_tiktok(f"{opening} {TIKTOK_SHORT_CTA}")


def generate_caption(meta: VideoMeta) -> str:
    override = _normalize_multiline_text(str(meta.raw.get("caption_override") or ""))
    if override:
        return override

    seed = f"{meta.file}|{meta.title}|{meta.angle}|{meta.hook}"
    parts: List[str] = []

    opening_line = _clean_text(
        meta.hook or (meta.voiceover.splitlines()[0] if meta.voiceover else "")
    )
    if not opening_line:
        opening_line = _pick(OPENERS, seed, "fallback-open")

    parts.append(_add_emoji(opening_line, seed, "hook"))

    opener = _pick(OPENERS, seed, "open")
    if _clean_text(opener) != _clean_text(opening_line):
        parts.append(opener)

    if meta.pain:
        parts.append(f"Це про { _clean_text(meta.pain) }.")

    if meta.angle:
        parts.append(_clean_text(meta.angle).rstrip(".") + ".")

    parts.append(_pick(BRIDGES, seed, "bridge"))

    if meta.offer:
        parts.append(
            f"{_clean_text(meta.offer).rstrip('.')} допомагають підтримати дитину без тиску і зайвого перевантаження."
        )
    else:
        parts.append(_pick(CLOSERS, seed, "close"))

    parts.append(_resolve_cta(meta))
    parts.append(" ".join(HASHTAGS))

    return "\n\n".join(parts)
