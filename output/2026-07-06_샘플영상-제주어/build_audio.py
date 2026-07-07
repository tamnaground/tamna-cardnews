"""Synthesize the Jeju dialogue lines with espeak-ng and compute the timeline."""
import json, subprocess, wave, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# speaker: (voice pitch, speed) — halmang higher/softer, harbang lower/slower
VOICES = {'halmang': ('-p', '75', '-s', '125'), 'harbang': ('-p', '25', '-s', '115')}

LINES = [
    ('halmang', '아이고, 비 하영 오람져.',      '아이고, 비가 많이 오네.'),
    ('harbang', '기여, 무사 영 오람신고.',       '그러게, 왜 이렇게 오는 걸까.'),
    ('halmang', '우산도 어신디 큰일 났져.',      '우산도 없는데 큰일이네.'),
    ('harbang', '밭디 물 들카부덴 걱정이여.',    '밭에 물 들까 봐 걱정이야.'),
    ('halmang', '게메마씸, 비 그치민 고장 하영 피키여.', '글쎄 말이야, 비 그치면 꽃이 많이 필 거야.'),
    ('harbang', '혼저 안네 들어갑주.',           '어서 안에 들어가자.'),
]

INTRO = 3.2      # title card before dialogue
GAP = 1.15       # pause between lines
OUTRO = 4.5      # end card after last line

timeline = []
t = INTRO
for i, (spk, jeju, std) in enumerate(LINES):
    raw = f'line{i}_raw.wav'
    out = f'line{i}.wav'
    args = ['espeak-ng', '-v', 'ko'] + list(VOICES[spk]) + ['-w', raw, jeju]
    subprocess.run(args, check=True)
    # resample to 44100 mono 16-bit
    subprocess.run(['/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2',
                    '-y', '-i', raw, '-ar', '44100', '-ac', '1', out],
                   check=True, capture_output=True)
    with wave.open(out) as w:
        dur = w.getnframes() / w.getframerate()
    timeline.append({'i': i, 'speaker': spk, 'jeju': jeju, 'std': std,
                     'start': round(t, 3), 'dur': round(dur, 3)})
    t += dur + GAP

total = t - GAP + OUTRO
meta = {'intro': INTRO, 'outro_start': round(t - GAP + 0.9, 3), 'total': round(total + 0.001, 3), 'lines': timeline}
with open('timeline.json', 'w') as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False, indent=1))
