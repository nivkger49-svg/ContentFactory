from __future__ import annotations

import json
import render_evening_kindergarten_long as base

OUTPUT_BASE = "neirokid_oral_sensory_hook_v1"
BATCH = "neirokid_oral_sensory_hook_v1"

# Keep the spoken pacing natural; the user explicitly asked to avoid over-speeding the voice.
base.AUDIO_SPEED = 1.05

CAPTIONS = [
    (3.30, 5.10, "ПЕРЕСТАНЬ\\NМЕНЕ\\NКУСАТИ"),
    (5.10, 7.20, "ЦЕ\\NБОЛЯЧЕ"),
    (7.20, 9.50, "Я ГОВОРИЛА\\NЦЕ\\NМАЙЖЕ ЩОДНЯ"),
    (9.50, 11.80, "ВІН\\NГРИЗ\\NФУТБОЛКИ"),
    (11.80, 14.10, "КУСАВ\\NМЕНЕ\\NЗА РУКУ"),
    (14.10, 16.40, "ЛИЗАВ СТІЛ\\NІ ТЯГНУВ\\NВСЕ ДО РОТА"),
    (16.40, 18.70, "Я ДУМАЛА\\NЦЕ ПРОСТО\\NЗВИЧКА"),
    (18.70, 20.90, "АЛЕ ПОТІМ\\NДІЗНАЛАСЯ\\NВАЖЛИВЕ"),
    (20.90, 23.60, "МОЗОК\\NШУКАЄ\\NВІДЧУТТЯ"),
    (23.60, 26.20, "КОЛИ ЇХ\\NНЕ ВИСТАЧАЄ\\NТІЛУ"),
    (26.20, 28.90, "САМЕ ТОМУ\\NДІТИ\\NГРИЗУТЬ"),
    (28.90, 31.10, "КУСАЮТЬ\\NШТОВХАЮТЬСЯ\\NСТРИБАЮТЬ"),
    (31.10, 33.50, "ПОСТІЙНО\\NКРУТЯТЬСЯ"),
    (33.50, 36.00, "ТАК НЕРВОВА\\NСИСТЕМА\\NЗАСПОКОЮЄТЬСЯ"),
    (36.00, 38.70, "ЗАБОРОНЯТИ\\NЦЕ\\NБЕЗГЛУЗДО"),
    (38.70, 41.20, "МОЗКУ ВСЕ ОДНО\\NПОТРІБНІ\\NЦІ ВІДЧУТТЯ"),
    (41.20, 43.80, "ЇХ ТРЕБА\\NДАТИ\\NБЕЗПЕЧНО"),
    (43.80, 46.40, "САМЕ ДЛЯ ЦЬОГО\\NМИ ПОЧАЛИ\\NНЕЙРОВПРАВИ"),
    (46.40, 49.30, "РУХ\\NБАЛАНС\\NНАТИСКАННЯ"),
    (49.30, 52.10, "КООРДИНАЦІЯ\\NІ РОБОТА\\NТІЛА"),
    (52.10, 55.00, "ДИТИНА ОТРИМУЄ\\NТЕ, ЧОГО\\NНЕ ВИСТАЧАЛО"),
    (55.00, 58.10, "І ПОТРЕБА\\NКУСАТИ\\NСТАЄ МЕНШОЮ"),
    (58.10, 61.00, "ГРИЗТИ\\NШУКАТИ\\NСТИМУЛЯЦІЮ"),
    (61.00, 63.80, "МИ ПРОЙШЛИ\\NКОРОТКЕ\\NОПИТУВАННЯ"),
    (63.80, 66.70, "ОТРИМАЛИ\\NВПРАВИ САМЕ\\NПІД СТАН ДИТИНИ"),
    (66.70, 70.20, "КІЛЬКА\\NХВИЛИН\\NНА ДЕНЬ"),
    (70.20, 73.70, "І МИ\\NПОБАЧИЛИ\\NЗМІНИ"),
    (73.70, 79.90, "ПРОЙДІТЬ\\NКОРОТКЕ\\NОПИТУВАННЯ"),
]

NEURO_SEGMENTS = [
    {"source": "assets/raw/video/наработки/01_без_субтитров/6F149C84-2FD8-41EA-99C1-12137B0D3346.MP4", "ss": ss, "dur": 1.65, "mode": "cover", "role": "neuro"}
    for ss in [
        0.8, 1.8, 2.7, 3.7, 4.6, 5.6, 6.5, 8.4, 10.3, 12.2, 14.1, 16.0, 17.9, 19.8, 21.7,
        23.6, 25.5, 27.4, 29.3, 31.2, 33.1, 35.0, 36.9, 38.8, 40.7, 42.6, 44.5,
        46.4, 48.3, 50.2, 52.1, 54.0, 55.9, 57.8, 59.7, 61.3, 62.8,
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
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18440166544189606.mp4", "ss": 0.9, "dur": 1.20, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/02_украинские_субтитры/18592189384022677.mp4", "ss": 2.0, "dur": 1.20, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/наработки/01_без_субтитров/башня.mp4", "ss": 1.7, "dur": 1.20, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 0.4, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 1.0, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505917_2160x3840.mp4", "ss": 1.0, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7505952_2160x3840.mp4", "ss": 0.8, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_12760968_2160x3840.mp4", "ss": 0.8, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_6174922_2160x4096.mp4", "ss": 2.4, "dur": 1.45, "mode": "cover", "role": "cutaway"},
    {"source": "assets/raw/video/pexels/2026-06-18/pexels_7394191_2160x3840.mp4", "ss": 3.2, "dur": 1.45, "mode": "cover", "role": "cutaway"},
]

SEGMENTS = (
    CUTAWAY_SEGMENTS[:3]
    + NEURO_SEGMENTS[:9]
    + CUTAWAY_SEGMENTS[3:5]
    + NEURO_SEGMENTS[9:18]
    + INTERFACE_SEGMENTS
    + NEURO_SEGMENTS[18:27]
    + CUTAWAY_SEGMENTS[5:8]
    + NEURO_SEGMENTS[27:]
    + CUTAWAY_SEGMENTS[8:]
)


def write_mix_report() -> None:
    totals: dict[str, float] = {}
    for segment in SEGMENTS:
        role = str(segment["role"])
        totals[role] = totals.get(role, 0.0) + float(segment["dur"])
    total = sum(totals.values())
    report = {
        "batch": BATCH,
        "total_visual_seconds": round(total, 2),
        "mix_seconds": {key: round(value, 2) for key, value in totals.items()},
        "mix_percent": {key: round(value / total * 100, 1) for key, value in totals.items()},
        "rules": {
            "hook": "oral-sensory hook first: licking glass, then toy-to-tv, then body-chaos impact",
            "neuro": "majority neuro exercises",
            "interface": "about 10 percent",
            "cutaways": "safe Ukraine-context cutaways only",
        },
    }
    path = base.OUT_DIR / f"{OUTPUT_BASE}_mix_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"mix_report={path}")


def main() -> None:
    base.OUTPUT_BASE = OUTPUT_BASE
    base.BATCH = BATCH
    base.CAPTIONS = CAPTIONS
    base.SEGMENTS = list(SEGMENTS)
    base.main()
    write_mix_report()


if __name__ == "__main__":
    main()
