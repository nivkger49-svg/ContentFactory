from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _ffmpeg import resolve_binary
from _voice import resolve_voice_file

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'outputs' / 'drafts'
TEMP_ROOT = ROOT / 'temp'
VOICE_DEFAULT = ROOT / 'assets' / 'voice' / 'voice.mp3'
AUDIO_SPEED = 1.04
OUTPUT_BASE = 'neirokid_potential_yoga_v1'
BATCH = 'neirokid_potential_yoga_v1'

CAPTIONS = [
    (0.00, 1.60, 'Я НЕ ХОЧУ'),
    (1.60, 3.80, 'ПРОСТО\\NСПОКІЙНУ\\NДИТИНУ'),
    (3.80, 6.60, 'Я ХОЧУ\\NЩОБ ВОНА\\NРОЗКРИЛА ПОТЕНЦІАЛ'),
    (6.60, 9.10, 'САМЕ ТОМУ\\NМИ ПОЧАЛИ\\NНЕЙРОВПРАВИ'),
    (9.10, 11.10, 'НЕ ЧЕРЕЗ\\NПРОБЛЕМИ'),
    (11.10, 14.40, 'МОЗОК ДИТИНИ\\NЗАРАЗ РОЗВИВАЄТЬСЯ\\NНАЙШВИДШЕ'),
    (14.40, 16.60, 'І КОЖЕН ДЕНЬ\\NМАЄ\\NЗНАЧЕННЯ'),
    (16.60, 19.10, 'СПОЧАТКУ\\NЦЕ БУЛА\\NГРА'),
    (19.10, 21.90, 'АЛЕ ПОТІМ\\NЯ ПОБАЧИЛА\\NЗМІНИ'),
    (21.90, 24.10, 'ДОВШЕ\\NТРИМАЄ\\NУВАГУ'),
    (24.10, 26.20, 'ШВИДШЕ\\NЗАПАМʼЯТОВУЄ'),
    (26.20, 29.10, 'ЛЕГШЕ\\NСПРАВЛЯЄТЬСЯ\\NЗ НОВИМ'),
    (29.10, 31.80, 'САМЕ ТОМУ\\NМИ ОБРАЛИ\\NНЕЙРОКІД'),
    (31.80, 34.40, 'У ДОДАТКУ\\NВСЕ ЗІБРАНО'),
    (34.40, 37.40, 'УВАГА\\NКОНЦЕНТРАЦІЯ\\NНЕЙРОВПРАВИ'),
    (37.40, 40.40, 'ЙОГА\\NКООРДИНАЦІЯ\\NСАМОКОНТРОЛЬ'),
    (40.40, 43.70, 'КАРТКИ ЕМОЦІЙ\\NЩОБ ДИТИНА\\NРОЗУМІЛА СЕБЕ'),
    (43.70, 46.60, 'ВПРАВИ\\NПІД РІЗНІ\\NСТАНИ ДИТИНИ'),
    (46.60, 49.60, 'НЕ ПОТРІБНО\\NГАДАТИ\\NЩО ПІДІЙДЕ'),
    (49.60, 52.30, 'ПРОЙДИ\\NКОРОТКЕ\\NОПИТУВАННЯ'),
    (52.30, 57.80, 'І ОТРИМАЙ\\NВПРАВИ КАРТКИ\\NТА РЕКОМЕНДАЦІЇ'),
]

SEGMENTS = [
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044903_1080x1920_crop1080x1920.mp4', 'ss': 1.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952685_2160x3840_crop1080x1920.mp4', 'ss': 6.4, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952692_2160x3840_crop1080x1920.mp4', 'ss': 1.5, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952520_2160x3840_crop1080x1920.mp4', 'ss': 2.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044834_1080x1920_crop1080x1920.mp4', 'ss': 4.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044903_1080x1920_crop1080x1920.mp4', 'ss': 5.2, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov', 'ss': 0.4, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-59-29_1.mov', 'ss': 0.4, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952685_2160x3840_crop1080x1920.mp4', 'ss': 1.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952692_2160x3840_crop1080x1920.mp4', 'ss': 5.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044834_1080x1920_crop1080x1920.mp4', 'ss': 10.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-53-55_1.mov', 'ss': 0.2, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/квиз.MP4', 'ss': 0.8, 'dur': 1.55, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-55-24_1.mov', 'ss': 0.5, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044903_1080x1920_crop1080x1920.mp4', 'ss': 7.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952520_2160x3840_crop1080x1920.mp4', 'ss': 6.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/интерфейс.MP4', 'ss': 0.8, 'dur': 1.60, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-10_1.mov', 'ss': 0.7, 'dur': 1.50, 'mode': 'contain'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952685_2160x3840_crop1080x1920.mp4', 'ss': 8.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952692_2160x3840_crop1080x1920.mp4', 'ss': 7.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044903_1080x1920_crop1080x1920.mp4', 'ss': 2.8, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/онбординг.MP4', 'ss': 0.8, 'dur': 1.60, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/квиз.MP4', 'ss': 3.2, 'dur': 1.55, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-48_1.mov', 'ss': 0.4, 'dur': 1.50, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-58-29_1.mov', 'ss': 0.3, 'dur': 1.50, 'mode': 'contain'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044834_1080x1920_crop1080x1920.mp4', 'ss': 14.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952520_2160x3840_crop1080x1920.mp4', 'ss': 8.0, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/интерфейс.MP4', 'ss': 2.5, 'dur': 1.55, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-59-29_1.mov', 'ss': 2.7, 'dur': 1.50, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952685_2160x3840_crop1080x1920.mp4', 'ss': 4.5, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/квиз.MP4', 'ss': 5.0, 'dur': 1.55, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/онбординг.MP4', 'ss': 3.8, 'dur': 1.55, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-54-51_1.mov', 'ss': 2.6, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_8044903_1080x1920_crop1080x1920.mp4', 'ss': 0.3, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-12-2026 10-57-10_1.mov', 'ss': 2.0, 'dur': 1.50, 'mode': 'contain'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/ScreenRecording_06-09-2026 10-53-55_1.mov', 'ss': 2.4, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/pexels/2026-06-19/cropped_1080x1920/pexels_6952692_2160x3840_crop1080x1920.mp4', 'ss': 3.3, 'dur': 1.45, 'mode': 'cover'},
    {'source': 'assets/raw/video/наработки/03_интерфейс/интерфейс.MP4', 'ss': 4.3, 'dur': 1.55, 'mode': 'contain'},
]

def ass_time(seconds: float) -> str:
    total_cs = max(0, int(round(seconds * 100)))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'


def escape_ass_text(text: str) -> str:
    return text.replace('\\N', '\n').replace('\\', r'\\\\').replace('\n', r'\\N')


def build_ass() -> str:
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Arial,76,&H00FFFFFF,&H000000FF,&H00101010,&H00000000,1,0,0,0,100,100,0,0,1,6,0,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = [f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Main,,0,0,0,,{escape_ass_text(text)}' for start, end, text in CAPTIONS]
    return header + '\n'.join(events) + '\n'


def build_filter(mode: str) -> str:
    if mode == 'contain':
        return 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p'
    return 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p'


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def render_segment(ffmpeg: str, temp_dir: Path, index: int, spec: dict[str, object]) -> Path:
    src = ROOT / str(spec['source'])
    out = temp_dir / f'segment_{index:02d}.mp4'
    dur = float(spec['dur'])
    cmd = [ffmpeg, '-y', '-ss', str(spec.get('ss', 0)), '-t', f'{dur}', '-i', str(src), '-an', '-vf', build_filter(str(spec.get('mode', 'cover'))), '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', str(out)]
    run(cmd)
    return out


def write_storyboard(path: Path, audio_path: Path, draft_path: Path, subs_path: Path) -> None:
    scenes = []
    cursor = 0.0
    for index, seg in enumerate(SEGMENTS):
        dur = float(seg['dur'])
        role = 'hook' if index < 4 else 'body'
        scenes.append({'vo': f'{cursor:.2f}-{cursor + dur:.2f}', 'role': role, 'path': str(seg['source']), 'ss': float(seg.get('ss', 0)), 't': dur})
        cursor += dur
    data = {
        'batch': BATCH,
        'variant': 'V01_potential_yoga_ui_mix',
        'subtitle_mode': 'semantic_hormozi_blocks',
        'asset_selection': 'manual',
        'voice': str(audio_path.relative_to(ROOT)),
        'subs': str(subs_path.relative_to(ROOT)),
        'draft': str(draft_path.relative_to(ROOT)),
        'total_visual_seconds': round(cursor, 2),
        'scenes': scenes,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> None:
    ffmpeg = resolve_binary('ffmpeg')
    audio_path = resolve_voice_file(VOICE_DEFAULT)
    temp_dir = TEMP_ROOT / f'{OUTPUT_BASE}_build'
    batch_dir = ROOT / 'batches' / BATCH
    subs_dir = batch_dir / 'subs'
    ass_path = subs_dir / f'{OUTPUT_BASE}_bullets.ass'
    storyboard_path = batch_dir / f'storyboard_{OUTPUT_BASE}.json'
    draft_path = OUT_DIR / f'{OUTPUT_BASE}.mp4'
    bullets_path = OUT_DIR / f'{OUTPUT_BASE}_bullets.mp4'

    temp_dir.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    subs_dir.mkdir(parents=True, exist_ok=True)

    paths = [render_segment(ffmpeg, temp_dir, idx, seg) for idx, seg in enumerate(SEGMENTS, start=1)]
    concat_list = temp_dir / 'concat.txt'
    concat_list.write_text(''.join(f"file '{p.as_posix()}'\n" for p in paths), encoding='utf-8')

    sped_audio = temp_dir / 'voice_sped.m4a'
    run([ffmpeg, '-y', '-i', str(audio_path), '-filter:a', f'atempo={AUDIO_SPEED}', '-c:a', 'aac', str(sped_audio)])

    stitched = temp_dir / 'video_only.mp4'
    run([ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_list), '-c', 'copy', str(stitched)])
    run([ffmpeg, '-y', '-i', str(stitched), '-i', str(sped_audio), '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', str(draft_path)])

    ass_path.write_text(build_ass(), encoding='utf-8')
    write_storyboard(storyboard_path, audio_path, draft_path, ass_path)
    run([ffmpeg, '-y', '-i', str(draft_path), '-vf', f'subtitles={ass_path}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-c:a', 'copy', '-movflags', '+faststart', str(bullets_path)])

    manifest = OUT_DIR / f'{OUTPUT_BASE}_manifest.json'
    manifest.write_text(json.dumps({'draft': str(draft_path), 'bullets': str(bullets_path), 'storyboard': str(storyboard_path), 'subs': str(ass_path)}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'draft={draft_path}')
    print(f'bullets={bullets_path}')
    print(f'manifest={manifest}')


if __name__ == '__main__':
    main()
