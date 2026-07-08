# fable 스위치 로더 (.bashrc에서 source 됨)
# 스위치가 on이면 claude 실행 시 sonnet->Opus 리매핑을 주입한다.
_fable_on() { [ "$(cat "$HOME/.claude/.fable-state" 2>/dev/null)" = "on" ]; }
_fable_run() {
  if _fable_on; then
    ANTHROPIC_DEFAULT_SONNET_MODEL="claude-opus-4-8" "$@"
  else
    "$@"
  fi
}
claude() { _fable_run command claude "$@"; }
