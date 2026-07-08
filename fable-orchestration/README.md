# Fable 5 오케스트레이션 가이드

> Fable 5는 지휘만, 실행은 Opus 4.8, 잡무는 Haiku 4.5 —
> 그리고 이 역할 분리를 권고가 아니라 **물리 차단**으로 강제하는 4계층 구성.

- 가이드 웹 페이지: [`index.html`](index.html)
- 바로 설치 가능한 설정 파일: [`setup/`](setup/) (`bash setup/install.sh` 한 번이면 끝)

## 도입

Claude Fable 5는 현재 가장 똑똑한 모델이면서 가장 비싼 모델입니다. 입력 100만 토큰당 10달러, 출력 100만 토큰당 50달러로 Opus 4.8의 두 배입니다. 그래서 Fable 5에게 보일러플레이트 작성, 테스트 실행, 파일 검색 같은 실행 작업을 시키면 비싼 토큰이 싼 일에 녹아 없어집니다.

해결 방향은 명확합니다. Fable 5는 계획, 작업 분배, 중요한 결정, 결과 종합 같은 판단만 맡고, 실제 손발은 하위 모델이 움직이면 됩니다. 무거운 추론은 Opus 4.8이 최대 추론 예산으로 처리하고, 명령 실행이나 로그 확인 같은 잡무는 Haiku 4.5가 처리하는 구조입니다.

그런데 대부분의 셋업이 여기서 한 가지를 놓칩니다. CLAUDE.md에 "Fable은 지휘만 하고 구현은 위임한다"라고 적는 것만으로는 부족합니다. 이 지침은 어디까지나 권고라서, 모델이 마음만 먹으면 직접 코드를 고칠 수 있기 때문입니다. 토큰을 실제로 아끼려면 말로 설득하는 단계를 넘어 물리적으로 막아야 합니다.

이 가이드는 그 전체 구조를 다룹니다. 지침 선언, 서브에이전트 역할 배정, 모델 리매핑, 그리고 훅 기반 강제 게이트까지 4계층을 쌓고, 마지막에 이 모든 것을 명령 하나로 켜고 끄는 스위치로 묶습니다. 실제 환경에서 차단이 작동하는지 검증한 결과도 함께 싣습니다.

### 이 가이드에서 얻는 것

1. **Fable 5 지휘 + Opus 4.8 실행 + Haiku 4.5 잡무의 3단 역할 분리** — 비싼 모델이 싼 일을 하지 않게 만드는 기본 구도
2. **CLAUDE.md 권고를 물리 차단으로 바꾸는 PreToolUse 강제 게이트** — 메인 에이전트의 직접 코드 수정을 턴당 2개 파일로 제한
3. **서브에이전트는 차단하지 않는 안전한 게이트 설계** — 훅 페이로드의 `agent_id` 필드로 메인과 서브를 구분
4. **`fable on/off` 명령 하나로 전체 설정을 켜고 끄는 스위치 구조** — 설정 본체는 한 폴더, 각 설정 파일에는 얇은 로딩 코드만

## 전체 구조 훑어보기

본격적인 설치에 들어가기 전에 구조부터 잡겠습니다. 각 계층이 무엇을 담당하는지 알아야 문제가 생겼을 때 어디를 봐야 하는지 판단할 수 있기 때문입니다.

| 계층 | 파일 | 역할 |
|------|------|------|
| 선언 | `~/.claude/fable/fable.md` | 오케스트레이션 지침. CLAUDE.md가 임포트해서 세션에 로드 |
| 역할 배정 | `~/.claude/fable/agents/` | deep-reasoner(Opus 4.8, 심층 추론)와 runner(Haiku 4.5, 잡무) 정의 |
| 모델 리매핑 | `~/.claude/fable/env.sh` | Sonnet으로 지정된 서브에이전트를 Opus 4.8로 승격하는 환경변수 주입 |
| 강제 장치 | `~/.claude/fable/hooks/orchestration-gate.py` | 메인 에이전트의 직접 코드 수정을 물리적으로 제한하는 PreToolUse 훅 |

이 구조의 핵심 설계 원칙은 **설정 본체와 로딩 코드의 분리**입니다. 실제 내용은 전부 `~/.claude/fable/` 한 폴더에만 있고, Claude Code가 읽는 설정 파일에는 그 폴더를 가리키는 얇은 로딩 코드 한 줄씩만 들어갑니다. 켜고 끌 때는 설정 파일을 전혀 건드리지 않고 폴더 안의 심링크 하나만 바꿉니다. 덕분에 나중에 완전히 제거하고 싶어도 로딩 코드 몇 줄만 지우면 끝납니다.

### 설정 본체 구조

```
~/.claude/fable
├── fable.md              # 오케스트레이션 지침 (on일 때 로드)
├── empty.md              # 빈 파일 (off일 때 로드)
├── active.md             # 심링크: fable.md <-> empty.md 를 오감
├── env.sh                # claude 래퍼 함수 + Sonnet->Opus 리매핑
├── agents
│   ├── deep-reasoner.md  # Opus 4.8, 추론 예산 최대
│   └── runner.md         # Haiku 4.5, 잡무 전담
├── hooks
│   └── orchestration-gate.py  # PreToolUse 강제 게이트
└── state/                # 게이트가 쓰는 턴별 카운터 (자동 생성)
```

로딩 코드는 네 군데에 한 번씩만 설치합니다.

| 위치 | 로딩 코드 | 담당 계층 |
|------|-----------|-----------|
| `~/.claude/CLAUDE.md` 끝 | `@/home/사용자명/.claude/fable/active.md` 한 줄 | 선언 |
| `~/.claude/agents/` | 에이전트 파일 심링크 2개 | 역할 배정 |
| `~/.bashrc` | `source ~/.claude/fable/env.sh` 한 줄 | 모델 리매핑 |
| `~/.claude/settings.json` | PreToolUse 훅 등록 블록 | 강제 장치 |

## 시작 전 준비

아래 조건만 갖추면 이 가이드를 그대로 따라갈 수 있습니다. 전체 과정은 WSL 터미널 기준입니다.

- [ ] Windows + WSL 환경에 Claude Code 최신 버전 설치
- [ ] Fable 5를 쓸 수 있는 구독 플랜 (Pro, Max, Team, Enterprise)
- [ ] WSL에 python3 설치 (게이트 훅 스크립트 실행용)
- [ ] `~/.local/bin`이 PATH에 포함되어 있는지 확인

준비 확인은 터미널에서 바로 할 수 있습니다.

```console
$ claude --version
$ python3 --version
Python 3.12.3
$ echo $PATH | grep -o '.local/bin'
.local/bin
```

## 1단계: 오케스트레이션 지침과 스위치

첫 단계에서는 Fable 5에게 줄 지휘 지침을 파일로 만들고, 그 지침을 켜고 끄는 스위치 구조를 세웁니다. 이 단계만 끝나도 "지휘만 하고 위임하라"는 선언 계층이 작동합니다.

먼저 설정 본체 폴더를 만들고 지침 파일을 작성합니다.

```console
$ mkdir -p ~/.claude/fable/agents ~/.claude/fable/hooks
```

지침 파일에는 역할 정의, 라우팅 기준, 직접 처리 허용 범위를 담습니다. 직접 처리 범위를 명시하는 부분이 중요합니다. 작은 작업까지 전부 위임하면 오히려 왕복 비용이 더 커지기 때문입니다.

**`~/.claude/fable/fable.md`** → 전문은 [`setup/fable.md`](setup/fable.md)

이 지침을 CLAUDE.md에 직접 붙여넣지 않는 이유가 스위치 구조의 핵심입니다. 대신 빈 파일 하나와 심링크 하나를 추가로 만듭니다.

```console
$ echo '<!-- fable off -->' > ~/.claude/fable/empty.md
$ ln -sfn ~/.claude/fable/fable.md ~/.claude/fable/active.md
$ readlink ~/.claude/fable/active.md
/home/사용자명/.claude/fable/fable.md
```

그리고 `~/.claude/CLAUDE.md` 맨 끝에 임포트 한 줄만 추가합니다. Claude Code는 CLAUDE.md 안의 `@경로` 문법으로 다른 파일을 함께 로드합니다.

```markdown
<!-- fable-loader: 토글은 fable on/off, 이 줄은 그대로 둡니다 -->
@/home/사용자명/.claude/fable/active.md
```

이제 CLAUDE.md는 항상 active.md를 로드하지만, 그 심링크가 어디를 가리키느냐에 따라 내용이 달라집니다. fable.md를 가리키면 지침이 로드되고, empty.md를 가리키면 아무것도 로드되지 않습니다. 켜고 끌 때 CLAUDE.md를 건드릴 필요가 없어지는 구조입니다.

이 심링크 전환을 매번 손으로 하지 않도록 토글 명령을 만듭니다. `~/.local/bin/fable`로 저장하고 실행 권한을 주면 어느 터미널에서든 `fable on`, `fable off`, `fable status`로 조작할 수 있습니다. 설정 파일은 전혀 건드리지 않고 상태 파일과 심링크만 전환하며, status는 로딩 코드 4종의 설치 여부까지 한 번에 점검합니다.

**`~/.local/bin/fable`** → 전문은 [`setup/bin/fable`](setup/bin/fable)

## 2단계: 서브에이전트 역할 배정

두 번째 단계에서는 Fable 5가 위임할 대상을 만듭니다. Claude Code는 `~/.claude/agents/` 폴더의 마크다운 파일을 커스텀 서브에이전트로 인식하고, 파일 상단의 frontmatter로 모델과 도구를 지정할 수 있습니다.

먼저 무거운 추론 전담인 **deep-reasoner**입니다. 어려운 문제를 풀어서 실행 지침으로 돌려주는 역할이라 Opus 4.8에 추론 예산을 최대로 줍니다. → [`setup/agents/deep-reasoner.md`](setup/agents/deep-reasoner.md)

다음은 잡무 전담인 **runner**입니다. 판단이 필요 없는 명령 실행과 조회만 맡기 때문에 Haiku 4.5로 충분하고, 도구도 읽기 계열로만 제한합니다. → [`setup/agents/runner.md`](setup/agents/runner.md)

frontmatter에서 자주 쓰는 필드는 아래와 같습니다.

| 필드 | 값 예시 | 설명 |
|------|---------|------|
| `name` | `deep-reasoner` | 에이전트 이름. 지침에서 이 이름으로 라우팅 |
| `description` | 위임 기준 설명 | 메인 에이전트가 언제 위임할지 판단하는 근거 |
| `model` | `claude-opus-4-8` | 이 에이전트가 사용할 모델. 생략하면 세션 모델 상속 |
| `effort` | `max`, `low` | 추론 예산. 생략하면 세션 설정 상속 |
| `tools` | `Bash, Read, Grep, Glob` | 허용 도구 목록. 생략하면 전체 도구 |

두 파일을 본체 폴더에 두고, 에이전트 폴더에는 심링크만 겁니다. 스위치 구조의 원칙대로 실제 내용은 한 곳에만 두기 위해서입니다.

```console
$ ln -sfn ~/.claude/fable/agents/deep-reasoner.md ~/.claude/agents/deep-reasoner.md
$ ln -sfn ~/.claude/fable/agents/runner.md ~/.claude/agents/runner.md
$ ls -la ~/.claude/agents/
deep-reasoner.md -> /home/사용자명/.claude/fable/agents/deep-reasoner.md
runner.md -> /home/사용자명/.claude/fable/agents/runner.md
```

## 3단계: Sonnet 요청을 Opus로 리매핑

세 번째 단계는 선택 사항이지만, 실행 품질을 Opus 4.8로 끌어올리고 싶다면 필요합니다. oh-my-claudecode 같은 오케스트레이션 플러그인의 실행 에이전트 다수가 frontmatter에 `model: sonnet`으로 고정되어 있는데, Claude Code는 `ANTHROPIC_DEFAULT_SONNET_MODEL` 환경변수로 이 sonnet 등급이 실제로 어떤 모델을 가리킬지 바꿀 수 있습니다.

문제는 이 환경변수를 어디에 두느냐입니다. `.bashrc`에 그냥 export하면 스위치를 꺼도 계속 적용됩니다. 그래서 스위치 상태를 실행 시점마다 읽는 래퍼 함수로 만듭니다. → [`setup/env.sh`](setup/env.sh)

`.bashrc` 맨 끝에 로딩 한 줄을 추가하면 설치가 끝납니다.

```bash
# fable 오케스트레이션 스위치 로더
[ -f "$HOME/.claude/fable/env.sh" ] && . "$HOME/.claude/fable/env.sh"
```

이제 터미널에서 claude를 치는 순간마다 래퍼가 스위치 상태를 확인하고, on일 때만 환경변수를 주입합니다. 이미 열려 있는 터미널에는 `source ~/.bashrc`를 한 번 실행해 줍니다.

> **ℹ️ Sonnet을 유지하고 싶다면**
> 실행 품질보다 비용이 우선이라면 이 단계를 건너뛰면 됩니다. 그 경우 sonnet 고정 에이전트는 그대로 Sonnet으로 실행되고, 나머지 계층(지침·역할 배정·강제 게이트)은 동일하게 작동합니다. 반대로 이 리매핑을 적용하면 실행은 Opus 4.8, 잡무는 Haiku 4.5로 Sonnet 등급을 건너뛰는 구성이 됩니다.

## 4단계: 강제 게이트 — 권고를 물리 차단으로

마지막 계층이 이 가이드의 핵심입니다. 앞의 세 단계는 전부 권고입니다. 지침이 로드되어 있어도 모델이 스스로 판단해서 직접 코드를 고치는 일은 언제든 일어날 수 있습니다. 이걸 막는 장치가 PreToolUse 훅입니다.

PreToolUse 훅은 Claude Code가 도구를 실행하기 직전에 호출되는 스크립트입니다. 스크립트가 종료 코드 2로 끝나면 그 도구 호출이 차단되고, stderr에 적은 메시지가 모델에게 전달됩니다. 게이트의 규칙은 다음과 같습니다.

- 메인 에이전트는 한 턴에 코드 파일을 2개까지만 직접 수정할 수 있습니다. 3개째부터 차단되고, 위임하라는 지시가 모델에게 돌아갑니다.
- 같은 파일을 다시 고치는 것은 개수에 세지 않습니다. 마크다운, JSON, YAML 같은 설정·문서 파일도 제한하지 않습니다.
- Bash로 코드 파일을 고치는 우회 경로(`sed -i`, `perl -i`, 리다이렉트, `tee`)는 개수와 무관하게 차단합니다.
- 스위치가 off면 모든 검사를 건너뛰고 통과시킵니다.

### 서브에이전트를 구분하는 방법

게이트 설계에서 가장 조심해야 할 부분이 서브에이전트 처리입니다. PreToolUse 훅은 서브에이전트의 도구 호출에도 발화되기 때문에, 구분 없이 차단하면 위임받은 실행 에이전트까지 막혀서 오케스트레이션 전체가 죽습니다.

다행히 공식적으로 지원되는 구분 방법이 있습니다. 훅이 서브에이전트 안에서 발화되면 stdin으로 들어오는 JSON에 `agent_id`와 `agent_type` 필드가 추가됩니다. 메인 에이전트의 호출에는 이 필드가 없습니다. 실제 페이로드를 비교하면 차이가 명확합니다.

```jsonc
// 메인 에이전트의 Write 호출 - agent 필드 없음
{
  "session_id": "75f02f85-...",
  "prompt_id": "6d225c46-...",
  "tool_name": "Write",
  "tool_input": { "file_path": "/project/a.ts" }
}

// 서브에이전트의 Write 호출 - agent_id, agent_type 존재
{
  "session_id": "75f02f85-...",
  "prompt_id": "6d225c46-...",
  "agent_id": "a513e1e15cbfd1608",
  "agent_type": "general-purpose",
  "tool_name": "Write",
  "tool_input": { "file_path": "/project/b.ts" }
}
```

`prompt_id`도 함께 눈여겨볼 필드입니다. 사용자가 프롬프트를 보낼 때마다 새 값이 부여되기 때문에, 이 값이 바뀌면 "새 턴이 시작됐다"로 보고 파일 카운터를 리셋할 수 있습니다. 별도의 턴 감지 훅 없이 PreToolUse 훅 하나로 턴당 제한이 구현되는 이유입니다.

게이트 스크립트의 핵심 판별 로직은 아래와 같습니다.

```python
data = json.load(sys.stdin)
# 스위치가 off면 즉시 통과
if state != "on":
    allow()
# 서브에이전트는 게이트 대상이 아님 - 위임이 실행 경로다
if data.get("agent_id") or data.get("agent_type"):
    allow()
# 같은 턴(prompt_id)에서 수정한 코드 파일이 이미 2개면 차단
if len(gate["files"]) >= LIMIT:
    deny("추가 코드 수정은 서브에이전트에 위임하세요: ...")
```

전체 스크립트에는 코드 파일 확장자 판별, Bash 우회 패턴 감지, 턴 카운터 저장과 리셋, 오류 시 통과(fail-open) 처리까지 포함됩니다. → 전문은 [`setup/hooks/orchestration-gate.py`](setup/hooks/orchestration-gate.py)

스크립트를 `~/.claude/fable/hooks/orchestration-gate.py`로 저장하고 실행 권한을 준 다음, `~/.claude/settings.json`에 훅을 등록합니다. 이 등록은 로딩 코드라서 한 번만 하면 되고, 이후 켜고 끄는 것은 스크립트 안의 스위치 확인이 처리합니다. → 등록 블록은 [`setup/settings.hooks.example.json`](setup/settings.hooks.example.json)

## 실제로 차단되는지 검증하기

강제 게이트는 만들어놓는 것보다 실제로 차단되는지 증명하는 것이 중요합니다. 규칙을 적는 것과 규칙을 어겼을 때 실제로 막히는 것은 다른 문제이기 때문입니다.

| 지침만 있을 때 | 강제 게이트 적용 후 |
|----------------|---------------------|
| CLAUDE.md에 위임 지침이 로드되어 있어도 모델이 판단에 따라 코드 파일 3개, 4개를 직접 수정하는 일이 일어난다. 지침은 권고라서 어긴다고 막히지 않는다. | 3번째 코드 파일 수정 시도가 도구 호출 단계에서 차단되고, 모델은 위임 지시 메시지를 받는다. 파일은 디스크에 생성되지 않는다. 서브에이전트의 수정은 개수 제한 없이 통과한다. |

검증은 새 터미널에서 헤드리스 세션으로 진행합니다. 먼저 메인 에이전트에게 코드 파일 3개를 만들게 시키고, 이어서 같은 작업을 서브에이전트에게 위임시켜 결과를 비교합니다.

```console
$ claude -p "c1.ts, c2.ts, c3.ts 세 파일을 순서대로 생성해라. 차단되면 BLOCKED: 뒤에 사유를 출력하고 멈춰라."
BLOCKED: [fable 게이트] 이번 턴에 메인 에이전트가 직접 수정한 코드 파일이 이미 2개입니다
$ ls *.ts
c1.ts  c2.ts
$ claude -p "서브에이전트를 띄워서 d1.ts, d2.ts, d3.ts 세 파일을 생성하게 해라."
SUB_DONE
$ ls d*.ts
d1.ts  d2.ts  d3.ts
```

기대한 대로 메인 에이전트는 2개까지만 만들고 3개째에서 차단됐습니다. c3.ts는 디스크에 존재하지 않습니다. 반면 서브에이전트는 3개를 전부 만들었습니다. 위임 경로는 손상되지 않았다는 뜻입니다. 이 두 결과가 함께 확인되어야 게이트가 완성된 것입니다.

## 일상 사용법

설치가 끝나면 일상 조작은 명령 세 개가 전부입니다.

| 명령 | 동작 |
|------|------|
| `fable on` | 지침 로드 + 리매핑 + 게이트 활성. 다음 세션부터 적용 |
| `fable off` | 전부 비활성. 로딩 코드는 그대로 두고 심링크와 상태만 전환 |
| `fable status` | 현재 상태와 로딩 코드 4종의 설치 여부 점검 |

```console
$ fable status
Fable 오케스트레이션: ON
  active.md -> /home/사용자명/.claude/fable/fable.md
  [OK] @import   ~/.claude/CLAUDE.md
  [OK] env 래퍼  ~/.bashrc
  [OK] agents    ~/.claude/agents
  [OK] 게이트 훅 ~/.claude/settings.json
  [OK] 게이트 스크립트 ~/.claude/fable/hooks/orchestration-gate.py
```

> **⚠️ 적용 시점에 주의**
> CLAUDE.md와 훅은 세션 시작 시점에 로드됩니다. `fable on/off`를 실행해도 이미 떠 있는 세션에는 적용되지 않고, 다음에 새로 시작하는 세션부터 반영됩니다. env.sh의 래퍼 함수는 claude를 실행하는 순간마다 상태를 읽기 때문에 터미널을 새로 열 필요까지는 없습니다.

지휘자 모델 자체는 스위치가 건드리지 않습니다. Claude Code 안에서 `/model` 명령으로 Fable 5를 기본 모델로 저장해 두면, 그 위에 이 오케스트레이션 계층이 얹히는 구조입니다.

## 주의할 점

운영하면서 알아둬야 할 한계와 설계 의도를 정리합니다. 게이트를 과신하지 않고 쓰기 위해 필요한 내용입니다.

- 게이트는 완벽한 차단막이 아니라 **폭주 방지 장치**입니다. Bash 우회 패턴 감지는 `sed -i`, `perl -i`, 리다이렉트, `tee` 같은 대표 경로를 막지만, 이론상 다른 우회가 불가능하지는 않습니다. 그래서 지침에도 "Bash로 코드를 수정하지 않는다"를 함께 적어 운영 규칙과 물리 장치를 겹으로 둡니다.
- 게이트 스크립트는 오류가 나면 차단이 아니라 통과를 선택합니다(**fail-open**). 게이트 버그 하나가 모든 도구 호출을 막아 세션을 마비시키는 것보다, 그 턴을 놓치는 쪽이 낫다는 설계입니다.
- 제한 대상은 **코드 파일뿐**입니다. 마크다운 문서나 설정 파일 정리는 지휘자가 직접 해도 토큰 손해가 크지 않고, 이것까지 막으면 사소한 작업마다 왕복 비용이 생기기 때문입니다.
- 셸 래퍼를 거치지 않는 실행 경로(IDE 확장 등)에서는 3단계의 Sonnet 리매핑이 적용되지 않습니다. 지침에 "래퍼 없는 세션에서는 위임 시 model을 명시하라"는 문구를 넣어 보완합니다.
- 다른 플러그인의 훅과는 **충돌하지 않습니다**. Claude Code는 등록된 PreToolUse 훅을 전부 실행하고 그중 하나라도 차단하면 막는 구조라서, 조언을 주입하는 기존 훅과 차단 게이트가 나란히 작동합니다.
- 턴 경계 감지에 쓰는 `prompt_id` 필드는 Claude Code **v2.1.196 이상**에서 제공됩니다. 그 이전 버전에는 이 필드가 없어 턴마다 카운터가 리셋되지 않으므로, 게이트를 쓰기 전 `claude --version`으로 버전을 확인하는 편이 안전합니다.
