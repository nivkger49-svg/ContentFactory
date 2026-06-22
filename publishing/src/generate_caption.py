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
        return f"{base_cta} {bio_cta}"
    return bio_cta


def generate_caption(meta: VideoMeta) -> str:
    seed = f"{meta.file}|{meta.title}|{meta.angle}|{meta.hook}"
    parts: List[str] = []

    hook = _clean_text(meta.hook or meta.voiceover.splitlines()[0] if meta.voiceover else "")
    if hook:
        parts.append(_add_emoji(hook, seed, "hook"))
    else:
        parts.append(_add_emoji(_pick(OPENERS, seed, "fallback-open"), seed, "fallback-open"))

    opener = _pick(OPENERS, seed, "open")
    if opener not in parts:
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
