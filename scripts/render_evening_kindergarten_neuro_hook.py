from __future__ import annotations

import json
from pathlib import Path

import render_evening_kindergarten_long as base


OUTPUT_BASE = "neirokid_evening_kindergarten_neuro_hook_v3"
BATCH = "neirokid_evening_kindergarten_neuro_hook_v3"

NEURO_SOURCE = "assets/raw/video/наработки/01_без_субтитров/6F149C84-2FD8-41EA-99C1-12137B0D3346.MP4"


CAPTIONS = [
    (0.00, 1.15, "ЦЕ НЕ\\N{\\c&H0000E8FF&}НЕСЛУХНЯНІСТЬ"),
    (1.15, 2.55, "ДИТИНА\\NПЕРЕВАНТАЖЕНА"),
    (2.55, 4.20, "МЕНЕ НАЛЯКАЛА\\NНЕ ІСТЕРИКА"),
    (4.20, 6.10, "ЦЕ ПОВТОРЮВАЛОСЬ\\N{\\c&H0000E8FF&}ЩОВЕЧОРА"),
    (6.10, 8.35, "О 5 ВЕЧОРА\\NВСЕ ЩЕ ДОБРЕ"),
    (8.35, 10.20, "А ПОТІМ...\\N{\\c&H0000E8FF&}КНОПКА"),
    (10.20, 12.20, "СЛЬОЗИ\\NКРИК\\NЗЛІСТЬ"),
    (12.20, 14.35, "ЧЕРЕЗ\\NДРІБНИЦІ"),
    (14.35, 16.25, "Я НЕ РОЗУМІЛА\\N{\\c&H0000E8FF&}ЧОМУ"),
    (16.25, 18.60, "Я ВЖЕ\\NВСЕ\\NПЕРЕПРОБУВАЛА"),
    (18.60, 20.55, "ВІДВОЛІКАЛА\\NДАВАЛА ПЕРЕКУС"),
    (20.55, 22.60, "МУЛЬТИКИ\\NІГРИ\\NДОМОВЛЯННЯ"),
    (22.60, 24.30, "ДОПОМАГАЛО\\NНА КІЛЬКА ХВИЛИН"),
    (24.30, 26.10, "{\\c&H0000E8FF&}НЕ\\NПРАЦЮЄ"),
    (26.10, 28.25, "ІНША МАМА\\NОПИСАЛА\\NМОЮ ДИТИНУ"),
    (28.25, 30.25, "Я НЕ ОДНА\\NТАКА"),
    (30.25, 32.45, "ПРОБЛЕМА\\NНЕ В ХАРАКТЕРІ"),
    (32.45, 34.50, "НЕРВОВА СИСТЕМА\\N{\\c&H0000E8FF&}ПЕРЕВАНТАЖЕНА"),
    (34.50, 37.10, "САДОК\\NШУМ\\NЕМОЦІЇ"),
    (37.10, 39.50, "НОВІ\\NВРАЖЕННЯ"),
    (39.50, 41.80, "МОЗОК\\NНЕ СПРАВЛЯЄТЬСЯ"),
    (41.80, 44.10, "СПОЧАТКУ\\N{\\c&H0000E8FF&}ТІЛО"),
    (44.10, 46.35, "ПОТІМ\\NСЛОВА"),
    (46.35, 48.75, "КОРОТКЕ\\NОПИТУВАННЯ"),
    (48.75, 51.20, "ПЛАН\\NПІД СТАН\\NДИТИНИ"),
    (51.20, 53.45, "ПРОСТІ\\NНЕЙРОВПРАВИ"),
    (53.45, 56.10, "КІЛЬКА ХВИЛИН\\NНА ДЕНЬ"),
    (56.10, 59.20, "ЗМІНИ\\NПРИЙШЛИ\\NШВИДКО"),
    (59.20, 62.20, "ЗА ТИЖДЕНЬ\\NВЕЧОРИ СТАЛИ\\NСПОКІЙНІШІ"),
    (62.20, 66.20, "Я НАРЕШТІ\\NЗРОЗУМІЛА\\NСВОЮ ДИТИНУ"),
    (66.20, 72.20, "ЯКЩО ВПІЗНАЛИ\\NСЕБЕ"),
    (72.20, 80.90, "ПРОЙДІТЬ\\NКОРОТКЕ\\NОПИТУВАННЯ"),
]


NEURO_SEGMENTS = [
    {"source": NEURO_SOURCE, "ss": ss, "dur": 1.60, "mode": "cover", "role": "neuro"}
    for ss in [
        0.25,
        2.15,
        4.05,
        5.95,
        7.85,
        9.75,
        11.65,
        13.55,
        15.45,
        17.35,
        19.25,
        21.15,
        23.05,
        24.95,
        26.85,
        28.75,
        30.65,
        32.55,
        34.45,
        36.35,
        38.25,
        40.15,
        42.05,
        43.95,
        45.85,
        47.75,
        49.65,
        51.55,
        53.45,
        55.35,
        57.25,
        59.15,
        61.05,
    ]
]


INTERFACE_SEGMENTS = [
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov", "ss": 0.7, "dur": 1.60, "mode": "contain", "role": "interface"},
    {"source": "assets/raw/video/наработки/03_интерфейс/квиз.MP4", "ss": 0.8, "dur": 1.60, "mode": "contain", "role": "interface"},
    {"source": "assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-55-24_1.mov", "ss": 0.8, "dur": 1.60, "mode": "contain", "role": "interface"},
    {"source": "assets/raw/video/наработки/03_интерфейс/интерфейс.MP4", "ss": 1.0, "dur": 1.60, "mode": "contain", "role": "interface"},
    {"source": "assets/raw/video/наработки/03_интерфейс/онбординг.MP4", "ss": 1.0, "dur": 1.60, "mode": "contain", "role": "interface"},
]


CUTAWAY_SEGMENTS = [
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_12760968_2160x3840.mp4", "ss": 0.8, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 0.4, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 1.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 1.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505952_2160x3840.mp4", "ss": 0.8, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 0.25, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_12760968_2160x3840.mp4", "ss": 3.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 2.4, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 3.2, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 3.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505952_2160x3840.mp4", "ss": 3.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 3.0, "dur": 1.55, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 1.8, "dur": 1.55, "mode": "cover", "role": "cutaway"},
]


SEGMENTS = (
    NEURO_SEGMENTS[:10]
    + CUTAWAY_SEGMENTS[:3]
    + NEURO_SEGMENTS[10:18]
    + CUTAWAY_SEGMENTS[3:6]
    + NEURO_SEGMENTS[18:25]
    + INTERFACE_SEGMENTS
    + NEURO_SEGMENTS[25:]
    + CUTAWAY_SEGMENTS[6:]
)


def write_mix_report() -> None:
    totals: dict[str, float] = {}
    for segment in SEGMENTS:
        totals[str(segment["role"])] = totals.get(str(segment["role"]), 0.0) + float(segment["dur"])

    total = sum(totals.values())
    report = {
        "batch": BATCH,
        "total_visual_seconds": round(total, 2),
        "mix_seconds": {key: round(value, 2) for key, value in totals.items()},
        "mix_percent": {key: round(value / total * 100, 1) for key, value in totals.items()},
        "rules": {
            "hook": "first seconds use the boy-at-table/wall neuro exercise source",
            "neuro": "more than 60 percent",
            "interface": "about 10 percent",
            "cutaways": "safe Ukraine-context cutaways only; no shтовкати AI/Spanish clips and no mismatched casting",
        },
    }
    path = base.OUT_DIR / f"{OUTPUT_BASE}_mix_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"mix_report={path}")


def main() -> None:
    base.OUTPUT_BASE = OUTPUT_BASE
    base.BATCH = BATCH
    base.CAPTIONS = CAPTIONS
    base.SEGMENTS = SEGMENTS
    base.main()
    write_mix_report()


if __name__ == "__main__":
    main()
