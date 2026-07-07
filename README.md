# 탐라 카드뉴스 (tamna-cardnews)

제주어(제주 방언) 보존 콘텐츠 저장소 — 카드뉴스와 세로형 쇼츠 영상을 만든다.
인스타그램/유튜브: **@tamnaground**

## 저장소 구조

```
card_1~5.png                      오늘의 제주어 '고장' 카드뉴스 원본 (레퍼런스, 덮어쓰기 금지)
카드뉴스/                          카드뉴스 자동 생성기
  ├─ words.json                   단어 세트 데이터 (여기만 수정하면 새 세트)
  ├─ build_cards.py               생성 실행 스크립트
  ├─ card_template.py             카드 레이아웃·팔레트 템플릿
  ├─ shoot.js                     Playwright 스크린샷
  └─ output/                      생성된 PNG (<세트id>_<n>.png)
샘플영상/                          영상 파이프라인 + 완성 영상
  ├─ episodes/                    에피소드(대사) JSON — 여기만 수정하면 새 영상
  ├─ make_video.py                원커맨드 빌드 (아래 참고)
  ├─ build_audio.py / build_scene.py / render.js / mix_audio.py
  ├─ scene.html                   카드뉴스형 영상 수제 샘플 (파이프라인 출력물 아님)
  └─ *.mp4                        완성 영상
데이터/
  └─ 제주어_어휘.json              검증된 제주어 어휘 사전 (콘텐츠의 단일 소스, 규칙: 데이터/README.md)
첨부자료/                          조사 자료·HeyGen 실사 영상 제작 패키지
.claude/skills/제주어영상/         제작 스킬 정본 (브랜드 규칙·파이프라인 상세)
PLAN-*.md                         실행 계획 문서
```

## 영상 만들기 (원커맨드)

```bash
cd 샘플영상 && python3 make_video.py episodes/rainy_day.json   # → out.mp4 (1080x1920, 30fps)
```

새 영상 = `샘플영상/episodes/`에 JSON 추가 (스키마: `episodes/rainy_day.json`). 파이썬 수정 불필요.

필요 환경 (원격 세션마다): `apt-get install -y espeak-ng`, `샘플영상/NotoSansKR.ttf` 다운로드, `pip install imageio-ffmpeg`. 상세와 함정 목록은 `.claude/skills/제주어영상/SKILL.md` 참고.

## 카드뉴스 만들기

```bash
python3 카드뉴스/build_cards.py 카드뉴스/words.json   # → 카드뉴스/output/<세트id>_<n>.png (1080x1350)
```

구성: 표지 + 단어당 [뜻 / 제주어 예문 / 표준어 예문] + 마무리. 단어 추가는 words.json의 `cards` 배열에만.

## 브랜드 규칙 (요약 — 정본은 `.claude/skills/제주어영상/SKILL.md`)

- 영상 1080x1920 30fps H.264+AAC / 카드 1080x1350
- 팔레트: 크림 `#F5EDDF`, 주황 `#E8622D`, 노랑 `#FFCC5C`, 초록 `#2F7A3D`, 파랑 `#1D5BB8`, 분홍 `#F2A9C4`, 글자 `#3E3226` + 6잎 꽃 모티프, 점선 테두리
- 마무리 문구: "제주어, 같이 지켜요 — 탐라그라운드" / 핸들 `@tamnaground` 상시 표시
- 제주어 어휘는 `데이터/제주어_어휘.json`의 `verified: true` 항목만 사용

## 산출물 명명 규칙

- 완성 영상: `샘플영상/<주제>_<형식>.mp4` (예: 제주삼춘_비오는날_대화.mp4). 작업 중 출력 `out.mp4`는 커밋하지 않고, 완성되면 한국어 제목으로 rename 후 커밋
- 카드뉴스: `카드뉴스/output/<세트id>_<n>.png`
- 중간 산출물(wav / frames / timeline.json / scene_generated.html)은 커밋하지 않는다 (.gitignore 처리됨)
- 팁: `git status`에서 한글 경로가 이스케이프되어 보이면 `git config core.quotepath false`

## 실행 계획 문서

`PLAN-*.md` 5건 (모두 구현 완료) — 우선순위 순서: render-pipeline → episode-data → cardnews-generator → jejueo-lexicon → readme-housekeeping
