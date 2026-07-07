# PLAN: 카드뉴스 자동 생성기 (`카드뉴스/build_cards.py`)

> 우선순위: **3위**
> 이유: 이 저장소의 이름이 tamna-**cardnews**인데, 정작 카드뉴스(card_1~5.png)는 재생성 수단이 없는 정적 산출물이다. 새 "오늘의 제주어" 시리즈를 만들 때마다 디자인을 처음부터 다시 만들어야 한다. 영상 파이프라인에서 이미 검증된 기법(HTML 템플릿 + Playwright 스크린샷)을 재사용하면 적은 비용으로 카드뉴스 생산을 자동화할 수 있다.

## 목표

`카드뉴스/words.json`에 단어 데이터를 쓰면 `python3 카드뉴스/build_cards.py`가 브랜드 디자인이 적용된 **1080x1350 (4:5, 인스타그램 규격)** PNG 카드 세트를 `카드뉴스/output/`에 생성한다. 기존 card_1~5.png와 동일한 규격·팔레트·모티프(6잎 꽃, 점선 테두리, @tamnaground 핸들)를 따른다.

## 수정/생성할 정확한 파일

| 파일 | 작업 |
|---|---|
| `카드뉴스/words.json` | **신규 생성** — 카드 세트 데이터 (아래 스키마) |
| `카드뉴스/card_template.py` | **신규 생성** — 카드 1장의 HTML을 만드는 함수 모음 (표지/단어/마무리 3종 레이아웃) |
| `카드뉴스/build_cards.py` | **신규 생성** — words.json → HTML → Playwright 스크린샷 → PNG |
| `.claude/skills/제주어영상/SKILL.md` | **수정** — 브랜드 규칙 섹션에 카드뉴스 생성기 사용법 1줄 추가 |

**주의: 루트의 card_1.png ~ card_5.png는 절대 덮어쓰지 않는다.** 원본 레퍼런스로 보존하고, 새 산출물은 `카드뉴스/output/<세트id>_1.png` 형식으로 저장한다.

## 단계별 작업 순서

### 1단계: 기존 카드 분석

`Read` 도구로 루트의 card_1.png ~ card_5.png를 **한 장씩 열어 눈으로 확인**하고 다음을 기록한다: 각 장의 역할(표지/내용/마무리), 배경색, 제목 위치, 꽃 모티프 위치, 점선 테두리 여백, 핸들 표기 위치. 이 관찰이 템플릿 CSS의 근거가 된다.

### 2단계: `words.json` 스키마 정의

```json
{
  "set_id": "gojang",
  "cover": { "title": "오늘의 제주어", "word": "고장", "hint": "무슨 뜻일까요?" },
  "cards": [
    { "word": "고장", "meaning": "꽃", "example_jeju": "비 그치민 고장 하영 피키여.", "example_std": "비 그치면 꽃이 많이 필 거야.", "color": "orange" },
    { "word": "하영", "meaning": "많이", "example_jeju": "비 하영 오람져.", "example_std": "비가 많이 오네.", "color": "green" },
    { "word": "혼저", "meaning": "어서", "example_jeju": "혼저옵서예!", "example_std": "어서 오세요!", "color": "blue" }
  ],
  "outro": { "message": "제주어, 같이 지켜요", "brand": "탐라그라운드", "handle": "@tamnaground" }
}
```

`color`는 SKILL.md 브랜드 팔레트의 키를 참조한다. `card_template.py`에 팔레트를 상수로 정의:

```python
PALETTE = {
    'cream': '#F5EDDF', 'orange': '#E8622D', 'yellow': '#FFCC5C', 'yellow2': '#F7C873',
    'green': '#2F7A3D', 'green2': '#BCD9A0', 'blue': '#1D5BB8', 'blue2': '#2563AC',
    'pink': '#F2A9C4', 'text': '#3E3226',
}
```

### 3단계: `card_template.py` 작성

- 함수 3개: `cover_html(data)`, `word_html(card)`, `outro_html(data)` — 각각 완전한 `<!DOCTYPE html>` 문서 문자열 반환.
- 공통 요소: `html, body { width:1080px; height:1350px; }`, 크림 배경, 점선 테두리(`border: 14px dotted`, inset 약 44px — 기존 scene.html의 `.dots` 스타일 26~28행을 그대로 재사용), 6잎 꽃 모티프는 CSS 또는 인라인 SVG(원 6개를 60도 간격 회전 배치 + 중심 원), 하단에 `@tamnaground`.
- 폰트: `샘플영상/NotoSansKR.ttf`를 `@font-face`로 참조 (상대경로 주의 — build_cards.py에서 HTML을 임시 파일로 쓸 때 폰트의 **절대경로**를 삽입할 것).
- 모든 사용자 텍스트는 `html.escape()` 처리.

### 4단계: `build_cards.py` 작성

```python
"""python3 build_cards.py [words.json 경로] — 카드뉴스 PNG 세트 생성"""
```

1. words.json 로드 → 카드 HTML 목록 = [cover] + [각 word] + [outro]
2. 각 HTML을 `카드뉴스/tmp_card_<n>.html`로 저장
3. node 원라이너 또는 `카드뉴스/shoot.js`로 Playwright 실행: viewport 1080x1350, `page.goto(file://...)`, `document.fonts.ready` 대기 후 `page.screenshot({path: 'output/<set_id>_<n>.png'})`
4. 임시 html 삭제, 생성된 PNG 목록 출력

Playwright는 `require('/opt/node22/lib/node_modules/playwright')`로 로드하고, launch 실패 시 `executablePath: '/opt/pw-browsers/chromium'` 폴백 (PLAN-render-pipeline.md의 render.js와 동일 패턴 — render.js가 이미 있으면 브라우저 구동 코드를 복사해서 쓸 것).

### 5단계: 검증 및 커밋

기존 card_1~5.png의 단어("고장" 세트로 추정 — 1단계 관찰로 확정)로 words.json을 채워 생성한 뒤, 원본과 새 출력을 나란히 Read로 열어 디자인 일관성을 확인한다. `카드뉴스/` 스크립트·words.json·output PNG를 커밋한다 (tmp_*.html은 제외).

## 성능이 낮은 모델이 놓치기 쉬운 엣지 케이스

1. **루트 card_N.png 덮어쓰기**: 출력 경로를 대충 `card_{n}.png`로 잡으면 원본 레퍼런스가 파괴된다. 반드시 `카드뉴스/output/` 하위에 세트 id를 붙여 저장.
2. **한글 줄바꿈**: CSS 기본값은 한글을 음절 단위로 아무 데서나 자른다. 모든 텍스트 블록에 `word-break: keep-all; overflow-wrap: break-word;`를 지정해 어절 단위로 줄바꿈되게 할 것.
3. **긴 예문 오버플로**: 예문이 2줄을 넘으면 카드 밖으로 넘친다. 예문 컨테이너에 `max-height`와 함께, build_cards.py에서 `len(example_jeju) > 40`이면 경고를 출력하고 폰트 크기를 한 단계 줄이는 분기를 넣을 것.
4. **폰트 상대경로 깨짐**: HTML 임시 파일 위치 기준으로 `url('NotoSansKR.ttf')`를 쓰면 폰트를 못 찾아 두부 글자가 된다. `os.path.abspath('../샘플영상/NotoSansKR.ttf')`를 f-string으로 주입하고, 파일 존재를 assert할 것. 또한 스크린샷 전 `document.fonts.ready`를 반드시 await.
5. **가변 폰트 굵기**: NotoSansKR은 가변(wght 100~900) ttf다. `@font-face`에 `font-weight: 100 900;`을 선언하지 않으면 `font-weight: 800`이 굵게 렌더링되지 않는다 (기존 scene.html 6~10행 참고).
6. **viewport와 카드 규격 불일치**: 영상용 1080x1920을 복사해 오다가 viewport를 그대로 두면 카드 아래 565px가 빈 여백으로 찍힌다. 카드는 **1080x1350**이다 (기존 PNG 5장 모두 확인됨).
7. **색 대비**: 노랑(`#FFCC5C`) 배경에 흰 글자를 얹으면 읽히지 않는다. 밝은 배경(cream/yellow/yellow2/green2/pink)에는 `text` 색(`#3E3226`), 어두운 배경(orange/green/blue/blue2)에는 흰색을 쓰는 매핑을 card_template.py에 함수로 두고 임의 판단하지 말 것.

## 완료 기준 (사용자가 직접 검증)

1. `python3 카드뉴스/build_cards.py 카드뉴스/words.json` 한 번으로 `카드뉴스/output/`에 (표지 1 + 단어 N + 마무리 1)장의 PNG가 생성된다.
2. `file 카드뉴스/output/*.png` 결과가 전부 `1080 x 1350`이다.
3. PNG를 열었을 때: 크림 배경 + 점선 테두리 + 꽃 모티프 + @tamnaground 핸들이 모든 장에 있고, 마무리 장에 "제주어, 같이 지켜요"가 있다. 글자가 □로 깨진 곳이 없다.
4. words.json에 단어 1개를 추가하고 재실행하면 코드 수정 없이 카드가 1장 늘어난다.
5. 루트의 card_1.png~card_5.png가 `git status`에서 변경되지 않았다.
