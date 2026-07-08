#!/usr/bin/env bash
# fable 오케스트레이션 설치 스크립트
#
# 가이드의 1~4단계를 그대로 수행한다:
#   본체 복사(~/.claude/fable) → 스위치 구조 → CLAUDE.md 임포트 →
#   에이전트 심링크 → .bashrc 로더 → settings.json 게이트 훅 등록 → fable 토글 설치
#
# 여러 번 실행해도 안전(멱등). 기존 settings.json 은 백업 후 hooks 만 병합한다.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
FABLE_DIR="$HOME/.claude/fable"

command -v python3 >/dev/null || { echo "python3가 필요합니다." >&2; exit 1; }

# 1. 본체 복사 + 스위치 구조
mkdir -p "$FABLE_DIR/agents" "$FABLE_DIR/hooks" "$HOME/.claude/agents" "$HOME/.local/bin"
cp "$SRC/fable.md" "$SRC/empty.md" "$SRC/env.sh" "$FABLE_DIR/"
cp "$SRC/agents/deep-reasoner.md" "$SRC/agents/runner.md" "$FABLE_DIR/agents/"
cp "$SRC/hooks/orchestration-gate.py" "$FABLE_DIR/hooks/"
chmod +x "$FABLE_DIR/hooks/orchestration-gate.py"
[ -e "$FABLE_DIR/active.md" ] || ln -sfn "$FABLE_DIR/fable.md" "$FABLE_DIR/active.md"

# 2. CLAUDE.md 임포트 (로딩 코드 1)
touch "$HOME/.claude/CLAUDE.md"
if ! grep -q 'fable/active.md' "$HOME/.claude/CLAUDE.md"; then
  printf '\n<!-- fable-loader: 토글은 fable on/off, 이 줄은 그대로 둡니다 -->\n@%s/active.md\n' "$FABLE_DIR" >> "$HOME/.claude/CLAUDE.md"
fi

# 3. 에이전트 심링크 (로딩 코드 2)
ln -sfn "$FABLE_DIR/agents/deep-reasoner.md" "$HOME/.claude/agents/deep-reasoner.md"
ln -sfn "$FABLE_DIR/agents/runner.md" "$HOME/.claude/agents/runner.md"

# 4. .bashrc 로더 (로딩 코드 3)
if ! grep -q 'fable/env.sh' "$HOME/.bashrc" 2>/dev/null; then
  printf '\n# fable 오케스트레이션 스위치 로더\n[ -f "$HOME/.claude/fable/env.sh" ] && . "$HOME/.claude/fable/env.sh"\n' >> "$HOME/.bashrc"
fi

# 5. settings.json 게이트 훅 병합 (로딩 코드 4)
python3 - "$HOME/.claude/settings.json" "$FABLE_DIR/hooks/orchestration-gate.py" <<'PY'
import json, os, shutil, sys
path, gate = sys.argv[1], sys.argv[2]
settings = {}
if os.path.exists(path):
    shutil.copy(path, path + ".bak")
    with open(path) as f:
        settings = json.load(f)
entry = {
    "matcher": "Write|Edit|NotebookEdit|MultiEdit|Bash",
    "hooks": [{"type": "command", "command": gate}],
}
pre = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any("orchestration-gate" in h.get("command", "")
           for e in pre for h in e.get("hooks", [])):
    pre.append(entry)
with open(path, "w") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
PY

# 6. fable 토글 설치 + 켜기
cp "$SRC/bin/fable" "$HOME/.local/bin/fable"
chmod +x "$HOME/.local/bin/fable"
"$HOME/.local/bin/fable" on
"$HOME/.local/bin/fable" status

echo
echo "설치 완료. 새 터미널(또는 source ~/.bashrc) 후 다음 claude 세션부터 적용됩니다."
