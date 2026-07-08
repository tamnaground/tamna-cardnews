#!/usr/bin/env python3
# ~/.claude/fable/hooks/orchestration-gate.py — fable 강제 게이트 (PreToolUse)
#
# 메인 에이전트가 한 턴(prompt_id)에 코드 파일을 2개까지만 직접 수정하게 허용하고,
# 3개째부터 차단하며 위임 지시를 돌려준다. Bash 를 통한 코드 파일 수정은 항상 차단.
# 서브에이전트(payload 에 agent_id/agent_type 존재)는 전부 통과 — 위임이 실행 경로다.
#
# fable off 상태(~/.claude/.fable-state != on)면 즉시 통과. 등록은 settings.json 에
# 1회(로딩 코드), 동작 여부는 스위치가 지배한다.
# 오류 시 fail-open(통과) — 게이트 버그가 세션을 마비시키지 않게 한다.
import json
import os
import re
import sys
import time

LIMIT = 2
STATE_FILE = os.path.expanduser("~/.claude/.fable-state")
GATE_STATE_DIR = os.path.expanduser("~/.claude/fable/state")
CODE_EXTS = {
    "ts", "tsx", "js", "jsx", "mjs", "cjs", "py", "go", "rs", "java", "kt",
    "kts", "swift", "c", "h", "cc", "cpp", "hpp", "cs", "rb", "php", "vue",
    "svelte", "astro", "css", "scss", "sass", "less", "html", "sh", "bash",
    "zsh", "sql", "lua", "dart", "scala", "ex", "exs", "zig", "ipynb",
}
EXT_RE = "|".join(sorted(CODE_EXTS))


def allow():
    sys.exit(0)


def deny(msg):
    sys.stderr.write(msg)
    sys.exit(2)


def is_code(path):
    return path.rsplit(".", 1)[-1].lower() in CODE_EXTS if "." in path else False


def main():
    try:
        state = open(STATE_FILE).read().strip()
    except OSError:
        state = "off"
    if state != "on":
        allow()
    data = json.load(sys.stdin)
    if data.get("agent_id") or data.get("agent_type"):
        allow()  # 서브에이전트는 게이트 대상이 아님
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    if tool == "Bash":
        cmd = tool_input.get("command", "")
        writes_inplace = re.search(r"\b(sed|perl)\s+[^|;&]*-\w*i", cmd)
        writes_redirect = re.search(
            r"(?:>>?|\btee\b(?:\s+-\w+)*)\s*['\"]?[^\s'\"|;&<>]+\.(?:%s)\b" % EXT_RE, cmd
        )
        touches_code = re.search(r"\.(?:%s)\b" % EXT_RE, cmd)
        if writes_redirect or (writes_inplace and touches_code):
            deny(
                "[fable 게이트] 메인 에이전트는 Bash로 코드 파일을 수정할 수 없습니다. "
                "코드 수정은 Edit/Write 도구(턴당 %d개 파일까지)를 쓰거나 서브에이전트에 위임하세요: "
                "일반 구현·수정 → 실행 에이전트(Opus), 심층 추론·설계 → deep-reasoner, 단순 잡무 → runner." % LIMIT
            )
        allow()
    if tool not in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        allow()
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path or not is_code(path):
        allow()  # 설정·문서 등 비코드 파일은 직접 수정 허용
    session = re.sub(r"[^a-zA-Z0-9-]", "", data.get("session_id", "nosession"))
    prompt = data.get("prompt_id", "")
    os.makedirs(GATE_STATE_DIR, exist_ok=True)
    gate_file = os.path.join(GATE_STATE_DIR, session + ".json")
    gate = {"prompt_id": prompt, "files": []}
    try:
        saved = json.load(open(gate_file))
        if saved.get("prompt_id") == prompt:
            gate = saved
        else:  # 새 턴 — 카운터 리셋 + 오래된 세션 상태 정리
            now = time.time()
            for fn in os.listdir(GATE_STATE_DIR):
                p = os.path.join(GATE_STATE_DIR, fn)
                if now - os.path.getmtime(p) > 86400:
                    os.remove(p)
    except (OSError, ValueError):
        pass
    if path in gate["files"]:
        allow()  # 같은 파일 재수정은 개수에 안 침
    if len(gate["files"]) < LIMIT:
        gate["files"].append(path)
        json.dump(gate, open(gate_file, "w"))
        allow()
    deny(
        "[fable 게이트] 이번 턴에 메인 에이전트가 직접 수정한 코드 파일이 이미 %d개입니다 (%s). "
        "추가 코드 수정은 반드시 서브에이전트에 위임하세요: 일반 구현·수정·테스트·리뷰 → 실행 에이전트(Opus), "
        "심층 추론·설계·근본원인 분석 → deep-reasoner, 단순 명령·조회 → runner. "
        "지금 하려던 수정(%s)을 명확한 지침과 함께 Agent 도구로 위임하면 됩니다."
        % (LIMIT, ", ".join(gate["files"]), path)
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open
