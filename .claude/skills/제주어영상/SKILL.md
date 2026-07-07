---
name: 제주어영상
description: 제주어(제주 방언) 영상 콘텐츠 제작 스킬. 유튜브 제주어 콘텐츠 조사, 제주어 대사 작성·검증, 애니메이션+합성음성 영상 렌더링(로컬), HeyGen 실사 영상용 프롬프트 준비까지 수행. 사용자가 제주어 영상, 삼춘 대화 영상, 카드뉴스 영상 제작을 요청할 때 사용.
---

# 제주어 영상 제작 스킬

탐라그라운드(@tamnaground) 제주어 콘텐츠용 세로형 영상을 만든다.

## 브랜드 규칙

- 규격: 1080x1920 (9:16 쇼츠/릴스), 30fps, H.264 MP4 + AAC
- 핸들 `@tamnaground`를 항상 화면에 표시, 마무리 문구는 "제주어, 같이 지켜요 — 탐라그라운드"
- 카드뉴스 팔레트: 크림 `#F5EDDF`, 주황 `#E8622D`, 노랑 `#FFCC5C`/`#F7C873`, 초록 `#2F7A3D`/`#BCD9A0`, 파랑 `#1D5BB8`/`#2563AC`, 분홍 `#F2A9C4`, 글자 `#3E3226`. 6잎 꽃 모티프와 점선 테두리 사용 (card_1~5.png 참고)
- 완성물은 `샘플영상/`에, 조사 자료는 `첨부자료/`에 저장하고 지정 브랜치에 커밋한다

## 1단계 — 자료 조사

`첨부자료/제주어_유튜브_콘텐츠.md`를 먼저 읽는다 (뭐랭하맨, Wikitongues 'Hyun speaking Jejueo', CNA 다큐, GO! Billy Korean, KBS제주/JIBS 등 정리됨). 새 주제면 WebSearch로 보강하고 문서를 갱신한다.

## 2단계 — 제주어 대사 작성

검증된 문형만 사용한다 (근거: 나무위키 제주 방언/문법, 제주도청 제주어 사전, 디지털제주문화대전):

- 진행상: `-암져/-엄져` (오람져 = 오고 있네), `-암신고` (오람신고 = 오는 걸까)
- 어휘: 하영(많이), 무사(왜), 기여(맞아/그래), 혼저(어서), 고장(꽃), 질(길), 어신디(없는데), 게메마씸(글쎄 말이에요), 폭싹 속았수다(수고하셨습니다), 혼저옵서예(어서 오세요)
- 청유: `-읍주` (들어갑주 = 들어갑시다)
- 항상 표준어 번역을 병기한다 (말풍선=제주어, 하단 자막=표준어)
- **실존 인물(유튜버·해녀 삼춘 등) 목소리 클로닝은 본인 동의 없이는 금지.** "유튜브 콘텐츠 학습"은 표현·말투 반영으로 해석한다

## 3단계 — 애니메이션 영상 (로컬 렌더링 파이프라인)

참고 구현: `샘플영상/scene.html`(카드뉴스형), `샘플영상/build_audio.py` + `build_scene.py` + `mix_audio.py`(대화형). 대사만 바꾸면 재생성 가능.

### 환경 준비 (원격 세션마다 필요)

```bash
apt-get install -y espeak-ng   # 한국어 TTS (오프라인, 기계음)
curl -sSL -o NotoSansKR.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"  # 한글 폰트 없음 주의
```

- ffmpeg (libx264+aac): `/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (없으면 `pip install imageio-ffmpeg`)
- Playwright chromium은 사전 설치됨. `require('/opt/node22/lib/node_modules/playwright')` 사용
- **네트워크 제약**: gTTS(구글)·edge-tts(MS)는 프록시가 차단함. HTTPS 인증서 오류 시 `cat /root/.ccr/ca-bundle.crt >> $(python3 -c 'import certifi; print(certifi.where())')`

### 파이프라인 순서

1. `build_audio.py`: espeak-ng로 대사별 wav 생성 (할망 `-p 75 -s 125`, 하르방 `-p 25 -s 115`), 길이 측정 → `timeline.json`
2. `build_scene.py`: timeline 기반으로 scene.html 생성 (말풍선·자막·입모양 애니메이션 딜레이 자동 계산)
3. 렌더링: Playwright로 페이지 열고 `window.seek(ms)`(`document.getAnimations()` 전부 pause 후 currentTime 설정)로 프레임별 스크린샷 → `frames/f%04d.png`
4. `mix_audio.py`: 빗소리 등 앰비언스 + 대사 오프셋 믹싱 → mix.wav
5. 인코딩: `ffmpeg -framerate 30 -i frames/f%04d.png -i mix.wav -c:v libx264 -crf 21 -pix_fmt yuv420p -c:a aac -movflags +faststart out.mp4`

### 함정 (실제로 겪은 버그)

- 퇴장 애니메이션은 `fill: forwards`로 (`both`로 하면 backwards-fill 때문에 시작부터 모든 요소가 보임)
- 프리뷰 프레임을 장면당 1장씩 뽑아 Read로 눈검사 후 전체 렌더링할 것
- ffmpeg 한 명령에 `-ss ... -i ... out1.png -ss ... -i ... out2.png` 식 다중 추출 금지 (둘 다 첫 입력에서 뽑힘)

## 4단계 — 실사(포토리얼) 영상: HeyGen

- **이 CLI 세션에서는 HeyGen compose/render가 정책상 차단됨.** 실사 생성은 사용자가 claude.ai 웹/데스크톱 채팅에서 해야 한다
- `첨부자료/실사영상_제작패키지.md`의 생성 프롬프트를 주제에 맞게 갱신해서 사용자에게 전달한다
- 이 세션에서 가능한 것: `mcp__HyperFrames_by_HeyGen__list_projects` / `get_project_status` / `get_render_status`로 진행 상황 조회, 완성된 MP4 URL 확보 후 저장소에 정리

## 마무리

- 산출물과 제작 스크립트를 지정 브랜치에 커밋·푸시
- SendUserFile(display: render)로 MP4를 사용자에게 바로 전달
- 음성이 기계음(espeak)일 때는 그 한계를 사용자에게 명시하고, 성우 녹음/고품질 TTS 음원으로 교체 가능함을 안내
