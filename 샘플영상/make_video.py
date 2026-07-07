"""원커맨드 영상 빌드: python3 make_video.py"""
import json
import os
import shutil
import subprocess
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd):
    print('>>>', ' '.join(cmd))
    subprocess.run(cmd, check=True)


assert shutil.which('espeak-ng'), 'espeak-ng 미설치: apt-get install -y espeak-ng'
assert os.path.exists('NotoSansKR.ttf'), 'NotoSansKR.ttf 없음: SKILL.md 환경 준비 참고'

run([sys.executable, 'build_audio.py'])
run([sys.executable, 'build_scene.py'])
shutil.rmtree('frames', ignore_errors=True)  # 이전 렌더 잔여 프레임이 남으면 ffmpeg가 옛 프레임을 이어 붙인다
run(['node', 'render.js', 'scene_generated.html', '30'])
run([sys.executable, 'mix_audio.py'])
run([FFMPEG, '-y', '-framerate', '30', '-i', 'frames/f%04d.png', '-i', 'mix.wav',
     '-c:v', 'libx264', '-crf', '21', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-shortest', '-movflags', '+faststart', 'out.mp4'])

total = json.load(open('timeline.json'))['total']
print(f'완료: out.mp4 (예상 길이 {total:.1f}s)')
