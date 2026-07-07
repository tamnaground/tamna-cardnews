# PLAN: 영상 렌더링 원커맨드 파이프라인 (`make_video.py` + `render.js`)

> 우선순위: **1위 (가장 먼저 할 것)**
> 이유: 현재 영상 제작의 핵심 단계(프레임 캡처·인코딩)가 `.claude/skills/제주어영상/SKILL.md`의 3단계에 **문장으로만** 기술되어 있고 실행 가능한 스크립트가 없다. 매 영상마다 이 절차를 수작업으로 재구성해야 하며, `timeline.json`이 저장소에 없어서 신선한 클론에서는 `build_scene.py`·`mix_audio.py`가 즉시 실패한다. 이 계획이 완료되면 "명령 한 번 → MP4"가 되어 이후 모든 영상 작업의 비용이 극적으로 줄어든다.

## 목표

`샘플영상/` 디렉토리에서 명령 **한 번**(`python3 make_video.py`)으로 다음 전체 파이프라인이 실행되어 `out.mp4`(1080x1920, 30fps, H.264+AAC)가 생성되게 한다:

```
build_audio.py (espeak-ng TTS + timeline.json 생성)
  → build_scene.py (scene_generated.html 생성)
  → render.js (Playwright로 프레임별 스크린샷 → frames/f0001.png ...)
  → mix_audio.py (앰비언스+대사 믹싱 → mix.wav)
  → ffmpeg 인코딩 (frames + mix.wav → out.mp4)
```

## 수정/생성할 정확한 파일

| 파일 | 작업 |
|---|---|
| `샘플영상/render.js` | **신규 생성** — Playwright 프레임 캡처 스크립트 |
| `샘플영상/make_video.py` | **신규 생성** — 전체 파이프라인 오케스트레이터 |
| `샘플영상/build_scene.py` | **수정** — 출력 파일명을 `scene.html` → `scene_generated.html`로 변경 (185행 `with open('scene.html', 'w')`). 기존 커밋된 `scene.html`은 카드뉴스형 별도 샘플이므로 덮어쓰면 안 된다 |
| `.claude/skills/제주어영상/SKILL.md` | **수정** — "3단계 파이프라인 순서" 섹션(46~52행)을 `python3 make_video.py` 한 줄 안내로 교체하고, 수동 절차는 "내부 동작" 참고로 남긴다 |

## 단계별 작업 순서

### 1단계: 환경 준비 확인

```bash
cd 샘플영상
which espeak-ng || apt-get install -y espeak-ng
ls NotoSansKR.ttf || curl -sSL -o NotoSansKR.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"
ls /usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2 || pip install imageio-ffmpeg
node -e "require('/opt/node22/lib/node_modules/playwright')" && echo playwright-ok
```

### 2단계: `build_scene.py` 출력명 변경

185행 `with open('scene.html', 'w')` → `with open('scene_generated.html', 'w')`. 187행의 print 문구도 맞춰 수정.

### 3단계: `render.js` 작성

아래 요구사항을 정확히 지킨다:

```js
// 사용법: node render.js [scene_generated.html 경로] [fps]
const playwright = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const htmlPath = process.argv[2] || 'scene_generated.html';
  const fps = parseInt(process.argv[3] || '30', 10);
  const total = JSON.parse(fs.readFileSync('timeline.json', 'utf8')).total; // 초 단위
  const nFrames = Math.ceil(total * fps);
  const browser = await playwright.chromium.launch(); // 실패 시 executablePath: '/opt/pw-browsers/chromium' 로 재시도
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + require('path').resolve(htmlPath));
  await page.waitForTimeout(1500); // 폰트 로딩 대기
  fs.mkdirSync('frames', { recursive: true });
  for (let f = 0; f < nFrames; f++) {
    await page.evaluate(ms => window.seek(ms), (f / fps) * 1000);
    await page.screenshot({ path: `frames/f${String(f + 1).padStart(4, '0')}.png` });
    if (f % 60 === 0) console.log(`frame ${f}/${nFrames}`);
  }
  await browser.close();
})();
```

- 페이지·브라우저를 **프레임마다 새로 열지 말 것** (한 페이지 재사용, 위 구조 그대로).
- `window.seek(ms)`는 이미 `build_scene.py`가 생성하는 HTML에 정의돼 있다 (`document.getAnimations()` 전부 pause 후 `currentTime` 설정).

### 4단계: `make_video.py` 작성

```python
"""원커맨드 영상 빌드: python3 make_video.py"""
import subprocess, sys, os, shutil, json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd):
    print('>>>', ' '.join(cmd)); subprocess.run(cmd, check=True)

# 사전 점검 (실패 시 명확한 한국어 에러로 즉시 중단)
assert shutil.which('espeak-ng'), 'espeak-ng 미설치: apt-get install -y espeak-ng'
assert os.path.exists('NotoSansKR.ttf'), 'NotoSansKR.ttf 없음: SKILL.md 환경 준비 참고'

run([sys.executable, 'build_audio.py'])
run([sys.executable, 'build_scene.py'])
shutil.rmtree('frames', ignore_errors=True)   # 이전 렌더 잔여 프레임 제거 (필수)
run(['node', 'render.js', 'scene_generated.html', '30'])
run([sys.executable, 'mix_audio.py'])
run([FFMPEG, '-y', '-framerate', '30', '-i', 'frames/f%04d.png', '-i', 'mix.wav',
     '-c:v', 'libx264', '-crf', '21', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-shortest', '-movflags', '+faststart', 'out.mp4'])
total = json.load(open('timeline.json'))['total']
print(f'완료: out.mp4 (예상 길이 {total:.1f}s)')
```

### 5단계: 미리보기 검사 후 전체 실행

전체 렌더 전에 프레임 3장만 뽑아 눈검사한다 (SKILL.md의 함정 항목 준수):

```bash
node -e "…"  # render.js를 f=0, 중간, 마지막 3프레임만 돌리도록 임시 인자를 주거나,
# 간단히: 전체 실행 후 frames/f0001.png, 중간, 마지막 프레임을 Read 도구로 열어 확인
```

### 6단계: SKILL.md 갱신, 커밋

`git add 샘플영상/render.js 샘플영상/make_video.py 샘플영상/build_scene.py .claude/skills/제주어영상/SKILL.md` 후 커밋. **frames/, *.wav, timeline.json, out.mp4, scene_generated.html은 커밋하지 않는다** (PLAN-readme-housekeeping.md의 .gitignore 참고).

## 성능이 낮은 모델이 놓치기 쉬운 엣지 케이스

1. **기존 `scene.html`을 덮어쓰는 사고**: 저장소에 커밋된 `샘플영상/scene.html`은 build_scene.py의 출력이 **아니라** 카드뉴스형 영상의 별도 수제 샘플이다 (배경이 `#000`이고 `.scene` 클래스 구조가 다름). build_scene.py를 그대로 실행하면 이 파일이 파괴된다. 반드시 출력명을 `scene_generated.html`로 바꾼 뒤 실행할 것.
2. **`timeline.json` 부재**: 신선한 클론에는 timeline.json이 없다. `build_audio.py`를 먼저 실행하지 않고 `build_scene.py`나 `mix_audio.py`를 실행하면 `FileNotFoundError`. make_video.py의 실행 순서가 이를 보장한다.
3. **espeak-ng 한국어 발음 실패**: espeak-ng가 없거나 `-v ko` 보이스가 없으면 subprocess가 실패한다. 사전 점검 assert를 생략하지 말 것.
4. **폰트 로딩 레이스**: `page.goto` 직후 바로 스크린샷을 찍으면 첫 수십 프레임이 폰트 없는 두부(□) 글자로 렌더링된다. `waitForTimeout(1500)` 또는 `document.fonts.ready` 대기를 반드시 넣을 것.
5. **잔여 프레임 오염**: 이전 렌더가 더 길었다면 frames/에 낡은 f0xxx.png가 남아 ffmpeg가 옛 프레임을 이어 붙인다. 렌더 전 `frames/` 삭제가 필수.
6. **`-shortest` 누락**: mix.wav와 프레임 수 길이가 미세하게 다르면 영상 끝에 검은 화면이나 무음 꼬리가 생긴다. ffmpeg에 `-shortest`를 넣을 것.
7. **음수 animation-delay와 seek**: 빗방울은 음수 delay로 이미 낙하 중 상태에서 시작한다. `window.seek`이 `document.getAnimations()`를 pause하고 currentTime을 설정하는 현재 구현은 이를 올바르게 처리하므로, seek 구현을 "다시 작성"하지 말고 생성된 것을 그대로 쓸 것.
8. **chromium 실행 경로**: `playwright.chromium.launch()`가 실행 파일을 못 찾으면 `{ executablePath: '/opt/pw-browsers/chromium' }` 옵션으로 재시도한다. `playwright install`을 실행하면 안 된다 (환경 정책).

## 완료 기준 (사용자가 직접 검증)

```bash
cd 샘플영상 && python3 make_video.py
```

1. 위 명령 한 번으로 에러 없이 `out.mp4`가 생성된다.
2. `ffprobe`(또는 `FFMPEG -i out.mp4`)로 확인: 해상도 1080x1920, 30fps, h264 + aac.
3. 영상 길이가 `timeline.json`의 `total` 값 ±0.3초 이내.
4. 영상을 재생하면: 인트로 카드 → 6개 말풍선이 순서대로 등장/퇴장 → 하단 표준어 자막 동기화 → 아웃트로 "제주어, 같이 지켜요 — 탐라그라운드" 표시. 시작부터 모든 요소가 겹쳐 보이는 현상(backwards-fill 버그)이 없어야 한다.
5. `git status`에서 커밋된 산출물은 render.js, make_video.py, build_scene.py 수정분, SKILL.md 수정분 뿐이어야 한다.
6. 기존 `샘플영상/scene.html`이 `git diff`에서 변경되지 않았어야 한다.
