---
name: spec-bugfix-verify
description: "Verification phase of the /spec bugfix workflow — decides whether a finished bugfix earns VERIFIED, and sends it back to implementation when it does not. Entered for a plan with Type: Bugfix marked Status: COMPLETE."
argument-hint: "<path/to/plan.md>"
user-invocable: false
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Phase 3 (bugfix).** Lightweight verification: run tests, quality checks, confirm fix works end-to-end.

**Input:** Bugfix plan with `Status: COMPLETE`
**Output:** Plan → VERIFIED (success) or loop back to implementation (failure)

**Why no sub-agents:** The regression test plus end-to-end verification (Step 1.6 / Step 3 Verification Scenario) prove the fix works. The full test suite proves nothing else broke. Sub-agents would re-verify what tests + E2E already prove.

---

## Critical Constraints

- **NO review sub-agents** — tests + E2E re-check carry the proof for bugfixes
- **NO stopping** — everything automatic. Never ask "Should I fix these?"
- **Fix ALL issues automatically** — no permission needed
- **Plan file is source of truth** — re-read after auto-compaction
- ⛔ **NEVER claim VERIFIED on tests alone.** Step 1.6 (non-UI) and Step 3 (UI Verification Scenario) require running the actual program — Chrome / Chrome DevTools MCP / playwright-cli / agent-browser for UI; CLI / API / REPL for non-UI. Skip is never an option.
