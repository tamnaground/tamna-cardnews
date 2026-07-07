---
name: session-start-hook
description: Create or fix a SessionStart hook (.claude/hooks/session-start.sh) that installs project dependencies for Claude Code on the web. Use when the user asks for a session-start/startup hook, wants dependencies (npm/pip/cargo/go/bundler) installed automatically when a session begins, or reports that tests or linters fail in remote/web sessions because dependencies are missing. Do NOT use for other hook types (PostToolUse, Stop, etc.) or general settings.json/permissions changes — use the update-config skill for those.
---

# SessionStart Hook for Claude Code on the web

Create a SessionStart hook that installs dependencies so tests and linters work in Claude Code on the web sessions.

Scope guard: this skill covers ONLY the SessionStart event and dependency/environment setup. If the user wants any other hook event or settings change, stop and use the update-config skill instead.

## Hook Basics

### Input (via stdin)
```json
{
  "session_id": "abc123",
  "source": "startup|resume|clear|compact",
  "transcript_path": "/path/to/transcript.jsonl",
  "permission_mode": "default",
  "hook_event_name": "SessionStart",
  "cwd": "/workspace/repo"
}
```

### Execution modes

**Synchronous (default — always use this unless the user explicitly asks for async):** the script runs to completion before the session starts. Dependencies are guaranteed to be installed before the agent does anything.

**Async (only on explicit user request):** the script prints `{"async": true, "asyncTimeout": 300000}` as its first line, then keeps running in the background while the session starts. Faster startup, but the agent may run tests before the install finishes — a race condition. Never choose async on your own initiative.

### Environment Variables

- `$CLAUDE_PROJECT_DIR` — repository root path
- `$CLAUDE_ENV_FILE` — file to append `export` lines to; they persist for the whole session
- `$CLAUDE_CODE_REMOTE` — set to `"true"` in remote environments (Claude Code on the web)

Persist a variable for the session:
```bash
echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
```

Restrict the hook to remote sessions (do this by default, so local sessions are unaffected):
```bash
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
```

## Workflow

Make a todo list for the steps below and work through them in order.

### 1. Analyze dependencies

Find EVERY dependency manifest, not just the first one — monorepos often have several:
- `package.json` / `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` → npm/pnpm/yarn (match the lockfile, don't assume npm)
- `pyproject.toml` / `requirements.txt` / `poetry.lock` / `uv.lock` → pip/Poetry/uv
- `Cargo.toml` → cargo
- `go.mod` → go
- `Gemfile` → bundler

Also read the README and any `docs/` or `CONTRIBUTING.md` setup instructions — projects often need extra steps (codegen, `.env` templates, submodules) beyond the package manager.

### 2. Design the hook

**Requirements — every hook must satisfy all of these:**
- Synchronous mode (no `{"async": ...}` line) unless the user explicitly asked for async
- Guarded by the `$CLAUDE_CODE_REMOTE` check unless the user wants it to run locally too
- Idempotent: safe to run on every session start, including `resume`/`clear`/`compact` sources. Skip work that is already done (e.g. `[ -d node_modules ] ||` guards) — the container state is cached after the hook completes, so re-runs should be near-instant
- Non-interactive: no prompts, use `-y`/`--yes` flags where needed
- Prefer cache-friendly install commands: `npm install` over `npm ci` (the container cache makes incremental installs cheap; `npm ci` deletes node_modules every time)
- Exit non-zero on failure so the problem is visible, but don't let one optional step (e.g. a lint plugin) kill required steps — order required installs first

**Edge cases to handle explicitly:**
- Multiple manifests: install each one, or at minimum the packages needed for tests and linters
- Network-restricted environments: installs go through the environment's proxy; if a registry is blocked, say so in the summary rather than silently shipping a hook that fails
- Private registries / auth tokens: never hardcode credentials; read them from the environment and document what the user must configure

### 3. Create the hook file

```bash
mkdir -p .claude/hooks
cat > .claude/hooks/session-start.sh << 'EOF'
#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install dependencies here
EOF

chmod +x .claude/hooks/session-start.sh
```

(For an async hook — explicit user request only — add `echo '{"async": true, "asyncTimeout": 300000}'` as the first command after the remote guard.)

### 4. Register in settings

Add to `.claude/settings.json` (create it if missing):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

If `.claude/settings.json` already exists, MERGE — do not overwrite other keys. If a `SessionStart` entry already exists, read the existing script first: extend it or append a second hook entry, never silently replace it.

### 5. Validate the hook

Run the script exactly as the harness would:
```bash
CLAUDE_CODE_REMOTE=true ./.claude/hooks/session-start.sh
```
Verify it exits 0 and the dependencies are actually present afterwards. Then run it a SECOND time to confirm idempotency (the re-run should succeed and be fast).

### 6. Validate the linter

Find the project's lint command and run it on one example file (not the whole project). If it fails because of a missing dependency, fix the hook and re-run step 5.

### 7. Validate a test

Find the project's test command and run one test (not the whole suite). If it fails because of a missing dependency, fix the hook and re-run step 5.

### 8. Commit

Commit the hook and settings change with a clear message. Push to the designated branch if the session has one; otherwise ask the user before pushing.

## Wrap up

In your final message, report:

* Summary of the changes made
* Validation results:
  1. ✅/‼️ Hook execution — including the idempotency re-run (details if it failed)
  2. ✅/‼️ Linter execution (details if it failed)
  3. ✅/‼️ Test execution (details if it failed)
* Hook execution mode — state the mode you ACTUALLY used:
  * If synchronous: dependencies are guaranteed ready before the session starts, at the cost of slower session startup; offer to switch to async if they prefer faster startup
  * If async: startup is faster, but warn about the race condition where the agent may act before installs finish
* Remind the user that the hook takes effect for all future sessions once merged into the repo's default branch.
