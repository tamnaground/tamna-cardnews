# 데이터

## 제주어_어휘.json — 검증된 제주어 어휘 사전 (콘텐츠의 단일 소스)

카드뉴스·영상 대사에 쓰는 모든 제주어 표현의 정본. **`verified: true`인 항목만 콘텐츠에 사용한다.**

### 스키마

- `sources` (최상위): 출처 키 → URL 맵. 항목의 `sources`는 이 키를 참조한다 (URL이 바뀌면 여기 한 곳만 수정).
- `entries[]`:
  - `jeju`: 대표 표기 (제주도청 사전 표기 우선). 어미는 하이픈 유지 (예: `-암져/-엄져`)
  - `std`: 표준어 뜻
  - `type`: `명사 | 동사 | 형용사 | 부사 | 감탄사 | 어미 | 관용구`
  - `variants`: 이형 표기 (아래아 ㆍ 표기 포함 — 대표 표기는 현대 한글로)
  - `example_jeju` / `example_std`: 예문 쌍 (필수)
  - `sources`: 출처 키 목록. **1개 이상 있어야 `verified: true` 가능**
  - `verified`: 출처 확인 여부. false면 콘텐츠 사용 금지
  - `used_in`: 이 표현이 실제 쓰인 산출물 경로 목록

### 등록 규칙

새 어휘는 WebSearch로 출처(제주도청 사전, 나무위키 제주 방언/문법, 디지털제주문화대전)를 확인한 뒤 여기 등록하고 나서 콘텐츠에 사용한다.

### 검증 원라이너

```bash
python3 -c "
import json; d = json.load(open('데이터/제주어_어휘.json'))
bad = [e['jeju'] for e in d['entries'] if e['verified'] and not e['sources']]
missing = [e['jeju'] for e in d['entries'] if not (e.get('example_jeju') and e.get('example_std'))]
assert not bad, f'출처 없는 verified 항목: {bad}'
assert not missing, f'예문 없는 항목: {missing}'
print(len(d['entries']), '개 항목 OK')"
```
