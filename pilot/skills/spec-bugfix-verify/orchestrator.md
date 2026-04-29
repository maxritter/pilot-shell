---
name: spec-bugfix-verify
description: "Bugfix verification phase - tests, quality checks, fix confirmation"
argument-hint: "<path/to/plan.md>"
user-invocable: false
model: sonnet
hooks:
  Stop:
    - command: uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/spec_verify_validator.py"
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Phase 3 (bugfix).** Lightweight verification: run tests, quality checks, confirm fix works end-to-end.

**Input:** Bugfix plan with `Status: COMPLETE`
**Output:** Plan → VERIFIED (success) or loop back to implementation (failure)

**Why no sub-agents:** The regression test plus end-to-end verification (Step 2.6 / Step 4 Verification Scenario) prove the fix works. The full test suite proves nothing else broke. Sub-agents would re-verify what tests + E2E already prove.

---

## Critical Constraints

- **NO review sub-agents** — tests + E2E re-check carry the proof for bugfixes
- **NO stopping** — everything automatic. Never ask "Should I fix these?"
- **Fix ALL issues automatically** — no permission needed
- **Plan file is source of truth** — re-read after auto-compaction
- ⛔ **NEVER claim VERIFIED on tests alone.** Step 2.6 (non-UI) and Step 4 (UI Verification Scenario) require running the actual program — Chrome / Chrome DevTools MCP / playwright-cli / agent-browser for UI; CLI / API / REPL for non-UI. Skip is never an option.
