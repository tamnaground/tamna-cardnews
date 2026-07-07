"""Synthesize the episode's Jeju dialogue with espeak-ng and compute the timeline.

사용법: python3 build_audio.py [episodes/<이름>.json]
"""
import json
import os
import subprocess
import sys
import wave

os.chdir(os.path.dirname(os.path.abspath(__file__)))

EP = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'episodes/rainy_day.json'))
# 캐릭터 SVG가 halmang/harbang 2종만 존재한다 (build_scene.py 참고)
assert set(EP['speakers']) <= {'halmang', 'harbang'}, \
    f"지원하지 않는 화자: {set(EP['speakers']) - {'halmang', 'harbang'}}"

FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

INTRO = EP['intro']['duration']
GAP = EP['gap']
OUTRO = EP['outro']['duration']

timeline = []
t = INTRO
for i, L in enumerate(EP['lines']):
    spk = L['speaker']
    raw = f'line{i}_raw.wav'
    out = f'line{i}.wav'
    args = ['espeak-ng', '-v', 'ko'] + list(EP['speakers'][spk]['espeak']) + ['-w', raw, L['jeju']]
    subprocess.run(args, check=True)
    # resample to 44100 mono 16-bit
    subprocess.run([FFMPEG, '-y', '-i', raw, '-ar', '44100', '-ac', '1', out],
                   check=True, capture_output=True)
    with wave.open(out) as w:
        dur = w.getnframes() / w.getframerate()
    dur = max(dur, 0.8)  # 초단문·무음에 가까운 대사도 말풍선이 읽힐 시간은 확보
    timeline.append({'i': i, 'speaker': spk, 'jeju': L['jeju'], 'std': L['std'],
                     'start': round(t, 3), 'dur': round(dur, 3)})
    t += dur + GAP

total = t - GAP + OUTRO
meta = {'episode': EP['id'],
        'intro': INTRO, 'intro_title': EP['intro']['title'], 'intro_subtitle': EP['intro']['subtitle'],
        'speakers': {k: {'side': v['side']} for k, v in EP['speakers'].items()},
        'outro_start': round(t - GAP + 0.9, 3), 'total': round(total + 0.001, 3), 'lines': timeline}
with open('timeline.json', 'w') as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False, indent=1))
