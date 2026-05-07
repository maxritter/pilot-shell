## Development Practices

### Codebase Exploration

CodeGraph (structure) and Probe (intent) are primary; Grep/Glob are *verifiers* for completeness checks or known-string lookups. Never start a code-search task with Grep/Glob.

**⛔ NEVER pass `projectPath` to CodeGraph for the current project** — it causes "not initialized" errors. The MCP server defaults correctly.

#### Mandatory Checkpoints

| Before you... | Use |
|---------------|-----|
| Start any new task | `codegraph_context(task=...)` — ALWAYS FIRST |
| Find a symbol by name | `codegraph_search` (NOT Grep) |
| Modify a function | `codegraph_callers` + `codegraph_callees`, then `Grep` as completeness check |
| Plan a change | `codegraph_impact` for blast radius |
| Explore by intent | `probe search "query" ./ --max-results 5 --max-tokens 2000` |
| Deep dive across files | `codegraph_explore(query="SymA SymB file.ts")` — replaces dozens of Reads |

Grep/Glob are valid only for: (1) verifying CodeGraph completeness on a specific symbol name, (2) exact text/regex in a known file. See `mcp-servers.md` for full CodeGraph reference and `cli-tools.md` for Probe.

### Change Discipline

- **Think before coding.** When a request is ambiguous, state assumptions, present alternatives, ask — before writing code.
- **Lineage test.** Every changed line must trace to the user's request. If it doesn't, revert.
- **Orphan cleanup.** Remove imports/vars/functions YOUR changes made unused. Don't touch pre-existing dead code — mention, don't delete.
- **Self-check.** "Would a senior engineer call this overcomplicated?" If 200 lines could be 50, rewrite. Complexity is earned by actual requirements.

**⛔ Never invent values.** File paths, env var names/values, API keys, IDs (UUIDs, FK ids, third-party object ids), URLs, ports, hostnames, version numbers, third-party service names, function/class names not verified to exist, library API signatures — must be authoritatively confirmed (read the code, run the command, or ask). Pattern-matching a plausible value is the top cause of agent-introduced incidents per the 2026 Agentic Coding Trends Report. If unsure, **STOP and ask** — one round-trip beats a hallucination. See *Evidence Before Claims* in `verification.md`.

### Project Policies

- **File size:** aim < 800 lines. > 1000 is a split signal — only when it's the focus of the current task, not a side-refactor. Test files exempt.
- **⛔ Dependency check** before modifying any function: `codegraph_callers` + `codegraph_callees`, then Grep as completeness check.
- **Self-correction:** fix obvious mistakes (syntax, typos, missing imports) in code you're actively writing. Do NOT auto-fix code the user edited — report it.
- **Performance:** hot paths (render loops, request handlers, polling) must cache/memoize. Use lighter alternatives for heavy deps. Don't redo work when input hasn't changed.
- **Diagnostics:** check before starting, after changes. Fix all errors before marking complete.
- **Formatting:** automated formatters handle style. **Backward compatibility:** only when explicitly required.

### Systematic Debugging

**No fixes without root cause investigation.** Phases run sequentially:

1. **Root cause** — read errors completely, reproduce consistently, check `git diff`, instrument at boundaries.
2. **Pattern analysis** — Probe CLI to find working examples; compare; identify ALL differences.
3. **Hypothesis** — specific, falsifiable ("state resets because component remounts on route change"). Test with minimal change, one variable at a time.
4. **Implementation** — failing test first (TDD), single fix, verify completely.

**Red flags → STOP:** "quick fix for now," multiple changes at once, proposing fixes before tracing data flow, 2+ failed fixes. **3+ failed fixes = architectural problem** — question the pattern, don't fix again.

**Revert-first.** When something breaks: (1) revert the change, (2) consider deleting the broken thing entirely, (3) one-liner targeted fix, (4) none of the above → stop, reconsider. 3+ failed fixes = the approach is wrong, not the fix.

**Meta-debugging:** treat your own code as foreign. Your mental model is a guess — the code's behavior is truth.

#### Defense-in-Depth (after fixing)

Make the bug structurally impossible, not just patched. Trace backward from symptom to original trigger (LSP `incomingCalls`, or `new Error().stack` instrumentation). Fix at the source. Then add validation at every layer the data passes:

| Layer | Purpose |
|-------|---------|
| Entry point | Reject invalid input at API boundary |
| Business logic | Ensure data makes sense for this operation |
| Environment guards | Prevent dangerous ops in specific contexts (e.g., refuse destructive ops outside temp dirs in tests) |
| Debug instrumentation | Capture context for forensics (cwd, stack, args before risky ops) |

Single validation = "fixed." All four layers = "impossible."

#### Condition-Based Waiting (Flakiness)

Replace arbitrary `sleep`/`setTimeout` with polling for the actual condition:

```python
# ❌ flaky
await sleep(500); result = get_result()

# ✅ reliable
result = await wait_for(lambda: get_result() is not None, timeout=5.0)
```

**Use:** flaky tests, async waits. **Don't use** when testing actual timing (debounce, throttle) — document WHY in that case. Poll every 10 ms, always include a timeout with a clear error, call the getter inside the loop (no stale cache).

### Constraint Classification

- **Hard** — non-negotiable (physics, external contracts, security, deadlines)
- **Soft** — conventions or preferences — negotiable if trade-off is stated
- **Ghost** — past constraints baked in that no longer apply

Ghost constraints are the highest-value to find — they lock out options nobody realises are available. Ask "why can't we do X?" — if nobody can name a current requirement, it may be a ghost.

### Git Operations

**Read git state freely. NEVER execute write commands without EXPLICIT user permission.** This is about git commands, not file edits — file editing is always allowed.

- **⛔ Write commands need permission:** `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset`, `stash`, `checkout`. "Fix this bug" ≠ "commit it."
- **⛔ NEVER `git checkout --` on unstaged changes.** Irreversible — work is permanently lost. Tell the user the consequences and let THEM run it. "Remove this" / "revert this" do NOT mean "discard all unstaged work." Use Edit for targeted changes.
- **⛔ Never `git add -f`** — if gitignored, tell the user.
- **⛔ Never selectively unstage** — commit all staged changes as-is.
- **⛔ Always `git push -u` on new branches** so the local branch tracks the correct remote.
- **⛔ Respect the active branch. Never auto-branch.** Work on whatever branch the user has checked out. Do NOT run `git checkout -b`, do NOT switch branches, do NOT invent branch names (e.g. `<username>/<feature>`, `feat/<slug>`, `fix/<slug>`) unless the user explicitly asks for a new branch in *this* request. Project conventions in `CLAUDE.md` / `AGENTS.md` that mandate a branch-naming pattern do NOT count as a request to create one now — surface the convention and ask. The exception is `/spec` with `Worktree: Yes`, which manages branches in an isolated worktree.
- **Read commands always allowed:** `status`, `diff`, `log`, `show`, `branch`.
- **Exceptions:** explicit override ("checkout branch X", "create a new branch for this"), and worktree during `/spec` (`Worktree: Yes`).
- **Credential leak prevention:** `git commit` (and chained `git add … && git commit …`) is scanned at PreToolUse for staged secrets. See `security-credentials.md` for the rule set, `[allow-secret]` bypass, and toggle.
