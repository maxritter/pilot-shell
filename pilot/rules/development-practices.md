## Development Practices

### Codebase Exploration — CodeGraph + Probe

**⛔ STOP: Are you about to use Grep or Glob? Use CodeGraph or Probe FIRST.**

Grep and Glob are last-resort tools for exact text/regex patterns only. For everything else, CodeGraph and Probe are faster, more accurate, and return structural context that Grep cannot.

**⛔ NEVER pass `projectPath` to CodeGraph tools when searching the current project.** Omit it — the MCP server already defaults to the right project. Passing it explicitly causes "not initialized" errors even when CodeGraph is working.

#### CodeGraph-First Workflow

**Every task starts with CodeGraph.** This is not optional — it's the single highest-value habit for efficient codebase work.

```
1. codegraph_context(task="<description>")     → Orient: entry points + related symbols
2. codegraph_search(query="<symbol>")          → Find specific symbols by name
3. codegraph_explore(query="<symbol names>")   → Deep dive: full source code sections in ONE call
4. codegraph_callers/callees(symbol="<name>")  → Trace call flow before modifying
5. codegraph_impact(symbol="<name>")           → Blast radius before committing to a change
```

**`codegraph_explore` is the most powerful tool** — one call returns full source code sections from all relevant files, grouped by file. It replaces dozens of Read/Grep calls. Use specific symbol names (from `codegraph_search`), not natural language. Budget: follow the limit in the tool description (scales by project size).

**`codegraph_context` is the FIRST action for every task** — it returns entry points, related symbols, and code context. Works best when the task maps to actual code symbols (e.g., "license verification" finds auth.py). For conceptual/workflow queries that don't map to symbol names, supplement with Probe `probe search`.

**`codegraph_callers` is essential but verify with Grep** — it finds most callers via the code graph but can miss some (especially indirect or dynamically-resolved calls). After running `codegraph_callers`, also `Grep` for the symbol name to catch anything the graph missed. Trust the graph for structure, verify with text search for completeness.

#### Mandatory Checkpoints

| Before you... | ⛔ STOP and use |
|------|------|
| **Start any new task** | `codegraph_context(task=<description>)` to orient — ALWAYS FIRST |
| **Deeply understand a feature** | `codegraph_search` to find symbols → `codegraph_explore` with those symbol names |
| **Search for a function/class/symbol** | `codegraph_search` (NOT Grep) |
| **Modify a function** | `codegraph_callers` + `codegraph_callees` THEN `Grep` for the symbol name (graph may miss some callers) |
| **Plan a change** | `codegraph_impact` to check blast radius |
| **Explore file structure** | `codegraph_files` (NOT Glob/ls) |
| **Understand a feature by intent** | Probe `probe search "how does auth work"` |
| **Extract code by symbol** | Probe `probe extract src/auth.ts#login` |
| **Match AST patterns** | Probe `probe query "async function $NAME($$$)"` |
| **Search exact text/regex** | Grep/Glob (the ONLY valid use case for these) |

### Project-Specific Policies

**File Size:** Aim for production files under 800 lines. Over 1000 lines is a signal to consider splitting — but only when it's the focus of the current task, not as a side-refactor. Test files exempt.

**⛔ Dependency Check:** Before modifying any function, you MUST run `codegraph_callers` and `codegraph_callees` for the call graph, THEN `Grep` for the symbol name to catch callers the graph may miss (especially indirect or dynamic calls). CodeGraph gives you structure; Grep gives you completeness. Use both. Update all affected call sites.

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
