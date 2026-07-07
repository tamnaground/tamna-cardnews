# PLAN: README 작성 + .gitignore + 저장소 구조 정리

> 우선순위: **5위**
> 이유: 저장소에 README가 전혀 없어 처음 온 사람(또는 새 세션의 AI)이 파일 구조·파이프라인·브랜드 규칙을 알 방법이 `.claude/skills/` 내부 파일뿐이다. 또한 .gitignore가 없어서 파이프라인을 한 번 돌리면 중간 산출물(wav, 프레임 PNG 수백 장, timeline.json)이 `git status`를 오염시키고, 실수로 커밋하면 저장소가 수십 MB씩 불어난다. 다른 4개 계획이 만들어낼 산출물이 깨끗하게 관리되기 위한 기반 작업이지만, 다른 계획을 막지는 않으므로 5위다. (단, **다른 계획 착수 전에 .gitignore 부분만 먼저 해 두면 좋다** — 10분 작업이다.)

## 목표

1. 저장소 루트에 `README.md`를 만들어 구조·제작 파이프라인·브랜드 규칙·산출물 목록을 한눈에 보이게 한다.
2. `.gitignore`로 중간 산출물이 절대 커밋되지 않게 한다.
3. 산출물 명명 규칙을 정해 README에 기록한다.

## 수정/생성할 정확한 파일

| 파일 | 작업 |
|---|---|
| `README.md` | **신규 생성** (루트) |
| `.gitignore` | **신규 생성** (루트) |

기존 파일 이동·삭제는 이번 범위에서 하지 않는다 (한글 디렉토리명 변경은 커밋 이력·스킬 문서 경로를 모두 건드리는 별도 결정사항).

## 단계별 작업 순서

### 1단계: `.gitignore` 작성

```gitignore
# 영상 파이프라인 중간 산출물 (make_video.py가 재생성)
샘플영상/line*_raw.wav
샘플영상/line*.wav
샘플영상/timeline.json
샘플영상/mix.wav
샘플영상/frames/
샘플영상/scene_generated.html
샘플영상/out.mp4

# 카드뉴스 임시 파일
카드뉴스/tmp_card_*.html

# 세션마다 다운로드하는 폰트
샘플영상/NotoSansKR.ttf

# 파이썬
__pycache__/
*.pyc
```

주의: `샘플영상/*.mp4` 전체를 ignore하면 **완성 샘플 2편(제주삼춘_비오는날_대화.mp4, 오늘의제주어_고장_샘플.mp4)이 이미 추적 중이므로 혼란만 생긴다**. 완성본은 커밋 대상이므로 `out.mp4`(작업 중 출력)만 ignore하고, 완성되면 한국어 제목으로 rename 후 커밋하는 규칙을 README에 적는다.

### 2단계: `README.md` 작성

아래 구성을 그대로 따른다 (전체 80~120줄 분량):

```markdown
# 탐라 카드뉴스 (tamna-cardnews)

제주어(제주 방언) 보존 콘텐츠 저장소 — 카드뉴스와 세로형 쇼츠 영상을 만든다.
인스타그램/유튜브: @tamnaground

## 저장소 구조
(디렉토리 트리 + 한 줄 설명: card_1~5.png, 샘플영상/, 첨부자료/, 데이터/, 카드뉴스/, .claude/skills/)

## 영상 만들기 (원커맨드)
cd 샘플영상 && python3 make_video.py episodes/rainy_day.json
필요 환경: espeak-ng, NotoSansKR.ttf, Playwright chromium — 자세한 준비는 .claude/skills/제주어영상/SKILL.md 참고

## 카드뉴스 만들기
python3 카드뉴스/build_cards.py 카드뉴스/words.json

## 브랜드 규칙 (요약)
- 영상 1080x1920 30fps / 카드 1080x1350
- 팔레트: 크림 #F5EDDF, 주황 #E8622D, 노랑 #FFCC5C, 초록 #2F7A3D, 파랑 #1D5BB8, 분홍 #F2A9C4, 글자 #3E3226
- 마무리 문구: "제주어, 같이 지켜요 — 탐라그라운드" / 핸들 @tamnaground 상시 표시
- 제주어 어휘는 데이터/제주어_어휘.json의 verified 항목만 사용

## 산출물 명명 규칙
- 완성 영상: 샘플영상/<주제>_<형식>.mp4 (예: 제주삼춘_비오는날_대화.mp4)
- 카드뉴스: 카드뉴스/output/<세트id>_<n>.png
- 중간 산출물(wav/frames/timeline.json)은 커밋하지 않는다 (.gitignore 처리됨)

## 실행 계획 문서
PLAN-*.md 5건 — 우선순위 순서: render-pipeline → episode-data → cardnews-generator → jejueo-lexicon → readme-housekeeping
```

README 내용 중 아직 존재하지 않는 파일(make_video.py, 카드뉴스/, 데이터/)은 해당 PLAN이 완료되기 전이라면 "(예정 — PLAN-xxx.md 참고)"를 붙여 거짓 문서가 되지 않게 한다. **다른 PLAN이 모두 완료된 뒤 이 계획을 실행하는 경우에는 예정 표기 없이 실제 상태를 기술한다.**

### 3단계: 정합성 확인 후 커밋

README에 적은 모든 경로가 실제 존재하는지(또는 예정 표기가 붙었는지) 확인하고, `git add README.md .gitignore` 커밋.

## 성능이 낮은 모델이 놓치기 쉬운 엣지 케이스

1. **이미 추적 중인 파일은 .gitignore로 안 빠진다**: 만약 timeline.json 등이 이미 커밋된 상태라면 .gitignore에 추가해도 계속 추적된다. `git ls-files 샘플영상/`으로 현재 추적 목록을 먼저 확인하고, 추적 중인 중간 산출물이 있으면 `git rm --cached <파일>`로 인덱스에서만 제거할 것 (현재 확인 기준으로는 py 3개, scene.html, mp4 2개만 추적 중이라 해당 없음 — 그래도 확인은 할 것).
2. **`샘플영상/*.wav`로 뭉뚱그리기**: 나중에 성우 녹음이나 CC 라이선스 음원(빗소리 등)을 저장소에 넣을 수 있다. 패턴은 파이프라인이 생성하는 이름(`line*.wav`, `mix.wav`)으로 좁게 잡을 것.
3. **한글 경로와 git 출력**: `git status`가 한글 경로를 `"\354\203\230..."` 식으로 이스케이프해 보여줄 수 있다. 정상이며, 보기 불편하면 `git config core.quotepath false`를 README 팁으로 적어 둘 것 (전역 설정 변경은 하지 말 것).
4. **README와 SKILL.md의 중복·불일치**: 브랜드 규칙을 두 곳에 전부 복사하면 곧 어긋난다. README에는 **요약만** 적고 "정본은 .claude/skills/제주어영상/SKILL.md"라고 명시할 것.
5. **거짓 문서화**: 아직 없는 명령(make_video.py 등)을 현재형으로 적으면 다음 실행자가 그대로 실행하다 실패한다. 2단계의 "(예정)" 규칙을 지킬 것.

## 완료 기준 (사용자가 직접 검증)

1. 루트에 README.md와 .gitignore가 존재한다.
2. 영상 파이프라인을 한 번 완주한 직후 `git status --porcelain`이 **빈 출력**이다 (중간 산출물이 전부 ignore됨).
3. `git check-ignore 샘플영상/mix.wav 샘플영상/timeline.json 샘플영상/frames/f0001.png` 가 세 경로 모두 출력한다.
4. `git check-ignore 샘플영상/제주삼춘_비오는날_대화.mp4` 는 **아무것도 출력하지 않는다** (완성본은 ignore 대상이 아님).
5. README의 모든 파일 경로가 실제 존재하거나 "(예정 — PLAN 참조)" 표기가 붙어 있다.
6. 제주어를 모르는 사람이 README만 읽고 "영상 만들기" 명령을 복사해 실행할 수 있다.
