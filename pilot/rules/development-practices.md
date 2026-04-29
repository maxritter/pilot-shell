## Development Practices

### Codebase Exploration — CodeGraph + Probe

**CodeGraph and Probe are the primary code-search tools.** Grep and Glob are *verifiers* — use them only for exact-text completeness checks AFTER CodeGraph, or for known-file/known-string lookups. Never start a code-search task with Grep/Glob.

**⛔ NEVER pass `projectPath` to CodeGraph tools when searching the current project.** Omit it — the MCP server defaults to the right project. Passing it explicitly causes "not initialized" errors.

#### CodeGraph-First Workflow

```
1. codegraph_context(task="<description>")     → Orient: entry points + related symbols
2. codegraph_search(query="<symbol>")          → Find specific symbols by name
3. codegraph_explore(query="<symbol names>")   → Deep dive: full source code in ONE call
4. codegraph_callers/callees(symbol="<name>")  → Trace call flow before modifying
5. codegraph_impact(symbol="<name>")           → Blast radius before committing to a change
```

`codegraph_context` is the FIRST action for every task — it returns entry points, related symbols, and code context. For conceptual queries that don't map to symbol names, supplement with `probe search`.

`codegraph_explore` is the most powerful tool — one call returns full source code from all relevant files, grouped by file. It replaces dozens of Read/Grep calls. Pass specific symbol names (from `codegraph_search`), NOT natural language. Follow the call budget in the tool description.

**Verify with Grep, don't replace.** After `codegraph_callers` returns its set, a `Grep` for the symbol name is a *completeness check* for indirect/dynamic callers the graph may miss — not the primary search.

#### Mandatory Checkpoints

| Before you... | ⛔ Use |
|------|------|
| **Start any new task** | `codegraph_context(task=<description>)` — ALWAYS FIRST |
| **Find a symbol by name** | `codegraph_search` (NOT Grep) |
| **Modify a function** | `codegraph_callers` + `codegraph_callees`, then `Grep` as completeness check |
| **Plan a change** | `codegraph_impact` for blast radius |
| **Explore by intent** | `probe search "query" ./ --max-results 5 --max-tokens 2000` |

Grep/Glob are valid for: (1) verifying CodeGraph completeness on a specific symbol name, (2) exact text/regex in a known file. They are NOT valid as the first move on a code-search task.

### Change Discipline

**Think before coding.** Don't silently pick an interpretation and run with it. When a request is ambiguous, state your assumptions explicitly, present alternatives, and ask — before writing code.

**Lineage test.** Every changed line must trace directly to the user's request. If it doesn't, revert it.

**Orphan cleanup.** Remove imports/variables/functions that YOUR changes made unused. Don't touch pre-existing dead code — mention it, don't delete it.

**Self-check.** Before submitting: "Would a senior engineer say this is overcomplicated?" If 200 lines could be 50, rewrite. Complexity is earned by actual requirements, not anticipated ones.

**Never invent values.** File paths, env var names and values, API keys and secrets, IDs (UUIDs, FK ids, third-party object ids), URLs, ports, hostnames, version numbers, third-party service names, function/class/method names not verified to exist, and library API signatures must be authoritatively confirmed before use — read the code, run the command, or ask. Pattern-matching a plausible-looking value is the most dangerous failure mode for an autonomous agent (2026 Agentic Coding Trends Report ranks action-hallucination as the top-rated cause of agent-introduced incidents). If unsure, **STOP and ask**. The cost of asking is one round-trip; the cost of acting on a hallucinated value can be catastrophic. See *Evidence Before Claims* in `verification.md` for the post-action verification protocol.

### Project-Specific Policies

**File Size:** Aim for production files under 800 lines. Over 1000 lines is a signal to consider splitting — but only when it's the focus of the current task, not as a side-refactor. Test files exempt.

**⛔ Dependency Check:** Before modifying any function, run `codegraph_callers` and `codegraph_callees` for the call graph, then `Grep` the symbol name as a completeness check (catches indirect/dynamic callers the graph may miss). CodeGraph gives structure; Grep gives completeness verification — not a primary search.

**Self-Correction:** Fix obvious mistakes (syntax errors, typos, missing imports) in code you are actively writing. Do not auto-fix errors in code the user edited — report them and let the user decide.

**Performance:** Expensive work on hot paths (render loops, request handlers, polling callbacks) must be cached or memoized. Use lighter alternatives for heavy dependencies. Repeated invocations must not redo work when input hasn't changed.

**Diagnostics:** Check before starting work and after changes. Fix all errors before marking complete.

**Formatting:** Let automated formatters handle style. **Backward Compatibility:** Only when explicitly required.

### Systematic Debugging

**No fixes without root cause investigation. Complete phases sequentially.**

**Phase 1 — Root Cause:** Read errors completely, reproduce consistently, check recent changes (git diff), instrument at boundaries.

**Phase 2 — Pattern Analysis:** Use Probe CLI to find working examples in codebase by intent. Compare against references, identify ALL differences.

**Phase 3 — Hypothesis:** Form specific, falsifiable hypothesis ("state resets because component remounts on route change"). Test with minimal change — one variable at a time.

**Phase 4 — Implementation:** Create failing test first (TDD), implement single fix, verify completely.

**3+ failed fixes = architectural problem.** Question the pattern, don't fix again.

**Red Flags → STOP:** "Quick fix for now", multiple changes at once, proposing fixes before tracing data flow, 2+ failed fixes.

**Revert-First:** When something breaks during implementation, default response = simplify, not add more code.
1. **Revert** — undo the change that broke it. Clean state.
2. **Delete** — can the broken thing be removed entirely?
3. **One-liner** — minimal targeted fix only.
4. **None of the above** → stop, reconsider the approach. 3+ failed fixes = the approach is wrong, not the fix.

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

### Constraint Classification

When exploring a problem or codebase, classify constraints you encounter:

- **Hard** — non-negotiable (physical limits, external contracts, security requirements, deadlines)
- **Soft** — preferences or conventions — negotiable if trade-off is stated explicitly
- **Ghost** — past constraints baked into the current approach that **no longer apply**

Ghost constraints are the most valuable to find: they lock out options nobody thinks are available. Ask "why can't we do X?" — if nobody can point to a current requirement, it may be a ghost.

### Git Operations

**Read git state freely. NEVER execute write commands without EXPLICIT user permission.**

This rule is about git commands, not file operations. Editing files is always allowed.

**⛔ Write commands need permission:** `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset`, `stash`, `checkout`, etc. "Fix this bug" ≠ "commit it."

**⛔ NEVER `git checkout --` on unstaged changes.** This is an **irreversible, destructive operation** — unstaged work is permanently lost, not recoverable through git. If the user wants to discard changes, tell them the consequences and let THEM run the command. No exceptions. "Remove this" or "revert this" does NOT mean "discard all unstaged work via git checkout." Use the Edit tool to make targeted changes instead.

**⛔ Never `git add -f`.** If gitignored, tell the user — don't force-add.

**⛔ Never selectively unstage.** Commit ALL staged changes as-is.

**⛔ Always `git push -u` on new branches.** When pushing a newly created branch for the first time, use `git push -u origin <branch>` (or `--set-upstream`) so the local branch tracks the correct remote. Without `-u`, the upstream stays on the old branch (e.g. `origin/master`), breaking subsequent pushes from IDEs and CLI.

**Read commands — always allowed:** `git status`, `diff`, `log`, `show`, `branch`

**Exceptions:** Explicit user override ("checkout branch X") and worktree during `/spec` (`Worktree: Yes`).
