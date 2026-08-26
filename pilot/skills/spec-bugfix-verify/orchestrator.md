---
name: spec-bugfix-verify
description: "Verification phase of the /spec bugfix workflow — decides whether a finished bugfix earns VERIFIED, and sends it back to implementation when it does not. Entered from the /spec dispatcher for a plan with Type: Bugfix marked Status: COMPLETE."
argument-hint: "<path/to/plan.md>"
user-invocable: false
---

# /spec-bugfix-verify - Bugfix Verification Phase

**Phase 3 (bugfix).** Lightweight verification: run tests, quality checks, confirm fix works end-to-end.

**Input:** Bugfix plan with `Status: COMPLETE`
**Output:** Plan → VERIFIED (success) or loop back to implementation (failure)

Choose the verification topology autonomously. Claude Code or Codex may spawn, resume, or nest agents for any verification work it judges useful, without asking the user for delegation permission. The final verdict still cites the reproducing test, full suite, and end-to-end evidence regardless of which agent collected it.

---

## Critical Constraints

- **No delegation permission gate** — use available agents whenever useful and continue automatically; coordinate ownership and consolidate their evidence into one verdict.
- **NO stopping** — everything automatic. Never ask "Should I fix these?"
- **Fix ALL issues automatically** — no permission needed
- **Plan file is source of truth** — re-read after auto-compaction
- ⛔ **NEVER claim VERIFIED on tests alone.** Step 1.6 (non-UI) and Step 3 (UI Verification Scenario) require running the actual program — Chrome / Chrome DevTools MCP / playwright-cli / agent-browser for UI; CLI / API / REPL for non-UI. Skip is never an option.
