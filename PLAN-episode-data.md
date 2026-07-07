# PLAN: 대사·장면 데이터 외부화 (`episodes/*.json`) + build_scene.py CSS 버그 수정

> 우선순위: **2위**
> 이유: 현재 새 에피소드를 만들려면 파이썬 코드 3곳을 직접 수정해야 한다 — 대사는 `build_audio.py`의 `LINES` 상수에, 인트로/아웃트로 문구는 `build_scene.py`의 HTML 문자열 안에 하드코딩돼 있다. 데이터 파일 하나만 바꾸면 새 영상이 나오는 구조로 만들면, 이후 콘텐츠 생산이 "JSON 작성"으로 단순해진다. 또한 `build_scene.py`에 실제 CSS 버그가 있어 함께 고친다.

## 목표

1. 에피소드(대사, 화자, 목소리 파라미터, 인트로/아웃트로 문구)를 `샘플영상/episodes/<이름>.json` 파일로 분리한다.
2. `build_audio.py`, `build_scene.py`가 명령 인자로 에피소드 파일을 받게 한다: `python3 build_audio.py episodes/rainy_day.json`
3. **버그 수정**: `build_scene.py` 101행의 `border-radius:ars 999px; border-radius:999px;` — 앞쪽 `border-radius:ars 999px;`는 잘못 들어간 무효 CSS이므로 삭제한다 (뒤의 유효한 선언 덕분에 지금은 우연히 동작 중).
4. 하단 자막의 `white-space:nowrap` 오버플로 문제를 해결한다 (긴 표준어 자막이 1080px 화면을 벗어남).

## 수정/생성할 정확한 파일

| 파일 | 작업 |
|---|---|
| `샘플영상/episodes/rainy_day.json` | **신규 생성** — 기존 하드코딩 데이터를 그대로 옮김 |
| `샘플영상/build_audio.py` | **수정** — 7행 `VOICES`, 9~16행 `LINES`, 18~20행 `INTRO/GAP/OUTRO` 상수를 에피소드 JSON 로딩으로 교체 |
| `샘플영상/build_scene.py` | **수정** — 101행 CSS 버그 삭제, 161~162행 인트로/아웃트로 문구를 JSON에서 로딩, 자막 오버플로 수정, 대사 텍스트 HTML 이스케이프 |
| `샘플영상/make_video.py` | **수정** (PLAN-render-pipeline 완료 후) — `python3 make_video.py episodes/rainy_day.json`처럼 에피소드 인자를 하위 스크립트에 전달 |
| `.claude/skills/제주어영상/SKILL.md` | **수정** — 3단계에 "새 영상 = episodes/에 JSON 추가" 절차 반영 |

## 단계별 작업 순서

### 1단계: 에피소드 스키마 정의 및 `episodes/rainy_day.json` 생성

```json
{
  "id": "rainy_day",
  "intro": { "title": "비 오는 날,<br>제주 삼춘들", "subtitle": "제주어로 듣는 일상 대화", "duration": 3.2 },
  "outro": { "duration": 4.5 },
  "gap": 1.15,
  "speakers": {
    "halmang": { "espeak": ["-p", "75", "-s", "125"], "side": "left" },
    "harbang": { "espeak": ["-p", "25", "-s", "115"], "side": "right" }
  },
  "lines": [
    { "speaker": "halmang", "jeju": "아이고, 비 하영 오람져.", "std": "아이고, 비가 많이 오네." },
    { "speaker": "harbang", "jeju": "기여, 무사 영 오람신고.", "std": "그러게, 왜 이렇게 오는 걸까." },
    { "speaker": "halmang", "jeju": "우산도 어신디 큰일 났져.", "std": "우산도 없는데 큰일이네." },
    { "speaker": "harbang", "jeju": "밭디 물 들카부덴 걱정이여.", "std": "밭에 물 들까 봐 걱정이야." },
    { "speaker": "halmang", "jeju": "게메마씸, 비 그치민 고장 하영 피키여.", "std": "글쎄 말이야, 비 그치면 꽃이 많이 필 거야." },
    { "speaker": "harbang", "jeju": "혼저 안네 들어갑주.", "std": "어서 안에 들어가자." }
  ]
}
```

아웃트로 문구("제주어, 같이 지켜요 / 탐라그라운드 / @tamnaground")는 **브랜드 고정 문구이므로 JSON에 넣지 말고** build_scene.py에 남긴다 (SKILL.md 브랜드 규칙).

### 2단계: `build_audio.py` 수정

- 파일 상단에 추가:
  ```python
  import sys
  EP = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'episodes/rainy_day.json'))
  ```
- `VOICES` → `{k: tuple(v['espeak']) for k, v in EP['speakers'].items()}`
- `LINES` → `[(L['speaker'], L['jeju'], L['std']) for L in EP['lines']]`
- `INTRO, GAP, OUTRO` → `EP['intro']['duration'], EP['gap'], EP['outro']['duration']`
- timeline.json 출력에 `"episode": EP['id']`와 `"intro_title": ..., "intro_subtitle": ...` 필드를 추가해 build_scene.py가 timeline.json만 읽어도 되게 한다 (build_scene.py가 JSON 두 개를 읽는 것보다 단순).

### 3단계: `build_scene.py` 수정

- **버그 수정 (101행)**: `border-radius:ars 999px; border-radius:999px;` → `border-radius:999px;`
- 161행의 하드코딩 인트로 문구를 timeline.json의 `intro_title`/`intro_subtitle`로 교체.
- **자막 오버플로 수정 (101행 `.subtitle`)**: `white-space:nowrap` 제거하고 다음으로 교체:
  ```css
  max-width: 960px; text-align: center; word-break: keep-all; white-space: normal;
  ```
- **HTML 이스케이프**: 22행과 25행에서 `L["jeju"]`, `L["std"]`를 그대로 f-string에 넣고 있다. `import html` 후 `html.escape(...)`로 감쌀 것 (대사에 `<`, `&`, 따옴표가 들어가면 HTML이 깨진다).
- 화자 side 판정 18행 `side = 'left' if spk == 'halmang' else 'right'` → speakers 딕셔너리의 `side` 값 사용 (timeline.json에 speakers 정보도 포함시킬 것).

### 4단계: 회귀 검증

기존과 동일한 출력이 나오는지 확인:

```bash
cd 샘플영상
python3 build_audio.py episodes/rainy_day.json
python3 build_scene.py
grep -c "bubble left\|bubble right" scene_generated.html   # 말풍선 6개
grep "border-radius:ars" scene_generated.html; echo "exit=$? (1이어야 정상)"
```

### 5단계: 새 에피소드로 실전 검증

`episodes/test_sunny.json`을 임시로 만들어 (대사 2줄이면 충분) 파이프라인이 코드 수정 없이 도는지 확인 후, 임시 파일은 삭제하고 커밋.

## 성능이 낮은 모델이 놓치기 쉬운 엣지 케이스

1. **`ars` 버그를 "이미 유효하니까" 방치**: CSS는 무효 선언을 조용히 무시하므로 지금 화면은 정상이다. 하지만 이는 명백한 오타 잔재이고, 뒤 선언을 지우는 리팩터링 시 자막 모서리가 각지게 되는 지뢰다. 반드시 앞쪽 무효 선언을 삭제할 것.
2. **espeak 인자와 셸 이스케이프**: 대사에 작은따옴표·쉼표가 있어도 `subprocess.run(리스트)` 형태라 안전하다. 이를 `shell=True` 문자열로 "개선"하지 말 것 — 대사 텍스트가 셸 인젝션 표면이 된다.
3. **말줄임표·물음표만 있는 대사**: espeak-ng가 무음에 가까운 wav를 만들면 `dur`이 0.1초 미만이 되어 말풍선이 깜빡하고 사라진다. `dur = max(dur, 0.8)` 하한을 build_audio.py에 넣을 것.
4. **화자가 2명이 아닌 에피소드**: `talk_anims = {'halmang': [], 'harbang': []}`처럼 화자명이 하드코딩된 곳이 build_scene.py에 3곳 있다 (11~12행, 30~33행, 캐릭터 SVG). 화자 키를 `EP['speakers']` 기반으로 만들되, **캐릭터 SVG는 halmang/harbang 2종만 존재하므로** 스키마 검증에서 "speakers 키는 halmang, harbang만 허용"을 assert로 강제하는 것이 이번 범위에서 올바른 처리다 (새 캐릭터 추가는 별도 작업).
5. **`<br>`이 포함된 intro_title**: html.escape를 인트로 제목에까지 일괄 적용하면 의도된 `<br>` 줄바꿈이 `&lt;br&gt;`로 보인다. **대사(jeju/std)만 이스케이프하고 인트로 문구는 이스케이프하지 않는다**고 명시적으로 구분할 것.
6. **JSON 인코딩**: 에피소드 파일은 반드시 UTF-8로 저장하고, 저장 시 `ensure_ascii=False`. 아래아(ㆍ) 등 옛한글 문자가 들어갈 수 있다.
7. **timeline.json 스키마 변경의 파급**: `mix_audio.py`도 timeline.json을 읽는다 (5행). 필드를 추가하는 것은 안전하지만 기존 필드(`total`, `outro_start`, `lines[].start/dur/i`)의 이름·의미를 바꾸면 mix_audio.py가 깨진다. 기존 필드는 절대 변경하지 말 것.

## 완료 기준 (사용자가 직접 검증)

1. `git grep -n "LINES = \[" 샘플영상/build_audio.py` 결과가 비어 있다 (대사 하드코딩 제거됨).
2. `grep -n "border-radius:ars" 샘플영상/build_scene.py` 결과가 비어 있다 (버그 수정됨).
3. `python3 -c "import json; json.load(open('샘플영상/episodes/rainy_day.json'))"`이 에러 없이 통과한다.
4. 대사 2줄짜리 새 JSON을 만들어 `python3 make_video.py episodes/새파일.json` 실행 시 **파이썬 파일을 한 줄도 수정하지 않고** 새 영상이 나온다.
5. 기존 rainy_day.json으로 만든 영상이 기존 `제주삼춘_비오는날_대화.mp4`와 동일한 대사·순서·자막을 보여준다.
6. 표준어 자막에 40자짜리 긴 문장을 넣어도 자막이 화면 밖으로 잘리지 않고 2줄로 줄바꿈된다.
