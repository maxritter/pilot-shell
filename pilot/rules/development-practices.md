## Development Practices

### Codebase Search — Probe MCP First

**⛔ Always use Probe MCP (`search_code`) as the first tool for codebase search.** It finds by intent, not exact text. Only fall back to Grep/Glob when you need an exact symbol or pattern match that Probe missed.

```
ToolSearch(query="+probe search")
mcp__plugin_pilot_probe__search_code(query="how is authentication handled")
mcp__plugin_pilot_probe__search_code(query="database connection setup")
```

### Project-Specific Policies

**File Size:** Aim for production files under 800 lines. Over 1000 lines is a signal to consider splitting — but only when it's the focus of the current task, not as a side-refactor. Test files exempt.

**Dependency Check:** Before modifying any function, use Probe MCP first (then `Grep` or LSP `findReferences` if needed) to find all callers. Update all affected call sites.

**Self-Correction:** Fix obvious mistakes (syntax errors, typos, missing imports) in code you are actively writing. Do not auto-fix errors in code the user edited — report them and let the user decide.

**Diagnostics:** Check before starting work and after changes. Fix all errors before marking complete.

**Formatting:** Let automated formatters handle style. **Backward Compatibility:** Only when explicitly required.

### Systematic Debugging

**No fixes without root cause investigation. Complete phases sequentially.**

**Phase 1 — Root Cause:** Read errors completely, reproduce consistently, check recent changes (git diff), instrument at boundaries.

**Phase 2 — Pattern Analysis:** Use Probe MCP to find working examples in codebase by intent. Compare against references, identify ALL differences.

**Phase 3 — Hypothesis:** Form specific, falsifiable hypothesis ("state resets because component remounts on route change"). Test with minimal change — one variable at a time.

**Phase 4 — Implementation:** Create failing test first (TDD), implement single fix, verify completely.

**3+ failed fixes = architectural problem.** Question the pattern, don't fix again.

**Red Flags → STOP:** "Quick fix for now", multiple changes at once, proposing fixes before tracing data flow, 2+ failed fixes.

**Meta-Debugging:** Treat your own code as foreign. Your mental model is a guess — the code's behavior is truth.

#### Defense-in-Depth & Root-Cause Tracing

**After fixing a bug, make it structurally impossible — not just patched.**

When a bug is caused by invalid data flowing through multiple layers:

1. **Trace backward** from symptom through the call chain to the original trigger. Use LSP `incomingCalls` or add `new Error().stack` instrumentation before the failing operation. Fix at the source — never fix just where the error appears.
2. **Then add validation at every layer** the data passes through:

| Layer | Purpose | Example |
|-------|---------|---------|
| Entry point | Reject invalid input at API boundary | Validate non-empty, exists, correct type |
| Business logic | Ensure data makes sense for this operation | Validate required fields for specific context |
| Environment guards | Prevent dangerous operations in specific contexts | Refuse destructive ops outside temp dirs in tests |
| Debug instrumentation | Capture context for forensics | Log directory, cwd, stack trace before risky ops |

**Single validation = "we fixed the bug". All four layers = "we made the bug impossible."**

#### Condition-Based Waiting (Test Flakiness)

**Replace arbitrary `sleep`/`setTimeout` with polling for the actual condition.**

```
# ❌ Guessing at timing (flaky)
await sleep(500)
result = get_result()

# ✅ Wait for the condition (reliable)
result = await wait_for(lambda: get_result() is not None, timeout=5.0)
```

**When to use:** Tests with arbitrary delays, flaky tests, waiting for async operations.

**When NOT to use:** Testing actual timing behavior (debounce, throttle) — document WHY the timeout is needed.

**Rules:** Poll every 10ms (not 1ms — wastes CPU). Always include timeout with clear error message. Call getter inside loop for fresh data (no stale cache).

### Git Operations

**Read git state freely. NEVER execute write commands without EXPLICIT user permission.**

This rule is about git commands, not file operations. Editing files is always allowed.

**⛔ Write commands need permission:** `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset`, `stash`, `checkout`, etc. "Fix this bug" ≠ "commit it."

**⛔ Never `git add -f`.** If gitignored, tell the user — don't force-add.

**⛔ Never selectively unstage.** Commit ALL staged changes as-is.

**Read commands — always allowed:** `git status`, `diff`, `log`, `show`, `branch`

**Exceptions:** Explicit user override ("checkout branch X") and worktree during `/spec` (`Worktree: Yes`).
