## Development Practices

### Codebase Exploration

Server routing lives in `mcp-servers.md` — CodeGraph for structure, Semble for intent, Grep/Glob to verify them or find exact text in a known file.

<!-- CODEX-START
**Codex budget:** during `$spec` and `$prd` planning, one CodeGraph orientation call plus one Semble search covers most plans. If either result is irrelevant, pivot to direct file reads and draft. Skip the graph entirely for docs, rules, config, UI copy, named paths, and reviews of a known diff.
CODEX-END -->

### Change Discipline

- **Think before coding.** When a request is ambiguous, state assumptions, present alternatives, ask — before writing code.
- **Lineage test.** Every changed line must trace to the user's request. If it doesn't, revert.
- **Orphan cleanup.** Remove imports/vars/functions YOUR changes made unused. Don't touch pre-existing dead code — mention, don't delete.
- **Self-check.** "Would a senior engineer call this overcomplicated?" If 200 lines could be 50, rewrite. Complexity is earned by actual requirements.

<!-- The "build the least" ladder + deliberate-shortcut convention below are adapted from ponytail (MIT, © Dietrich Gebert): https://github.com/DietrichGebert/ponytail -->

#### Build the least that works — the ladder

Before writing code, stop at the **first rung that holds**. It's a reflex, not a research project — two rungs both work, take the higher one and move on.

1. **Does this need to exist at all?** Speculative need → skip it, say so in one line. (YAGNI)
2. **Standard library does it?** Use it.
3. **Native platform feature covers it?** Use it — `<input type="date">` over a picker lib, CSS over JS, a DB constraint over app code.
4. **Already-installed dependency solves it?** Use it. Never add a new dependency for what a few lines can do.
5. **Can it be one line?** Make it one line.
6. **Only then** write the minimum code that works.

No unrequested abstractions (no interface with one implementation, no factory for one product, no config for a value that never changes), no boilerplate "for later," fewest files possible. Lazy means *less code, not the flimsier algorithm*: between two same-size stdlib options, take the one correct on edge cases.

**Never simplify away** (these are not on the chopping block): trust-boundary input validation, error handling that prevents data loss, security, accessibility, and the calibration real hardware needs — a minimal model can't see that a real clock drifts or a sensor reads off. Anything the user explicitly asked for stays; if they want the full version, build it without re-arguing.

- **Mark deliberate shortcuts.** When you intentionally ship a simplification with a known ceiling (global lock, O(n²) scan, naive heuristic), leave a `SHORTCUT:` comment naming the ceiling **and** the upgrade trigger: `# SHORTCUT: global lock, per-account locks if throughput matters`. A shortcut with no named trigger rots into "never" — name the trigger or don't take the shortcut. `grep -rnE '(#|//) ?SHORTCUT:' .` harvests the ledger; `/spec`, `/build`, and `/fix` verification surface unresolved markers (see `verification.md`).

**⛔ Never invent values.** File paths, env var names/values, API keys, IDs (UUIDs, FK ids, third-party object ids), URLs, ports, hostnames, version numbers, third-party service names, function/class names not verified to exist, library API signatures — must be authoritatively confirmed (read the code, run the command, or ask). Pattern-matching a plausible value is the top cause of agent-introduced incidents per the 2026 Agentic Coding Trends Report. If unsure, **STOP and ask** — one round-trip beats a hallucination. See *Evidence Before Claims* in `verification.md`.

### Project Policies

- **File size:** aim < 800 lines. > 1000 is a split signal — only when it's the focus of the current task, not a side-refactor. Test files exempt.
- **Dependency check:** before modifying a shared or non-trivial function, run `codegraph_explore(query="<fn> callers and impact")` — its response includes the call path and blast radius, catching callers you'd otherwise miss. Grep only as a completeness check for dynamic/reflective call sites the AST can't follow, not to re-verify codegraph's structural results. A self-contained local function the plan already isolated doesn't need it.
- **Self-correction:** fix obvious mistakes (syntax, typos, missing imports) in code you're actively writing. Do NOT auto-fix code the user edited — report it.
- **Performance:** hot paths (render loops, request handlers, polling) must cache/memoize. Use lighter alternatives for heavy deps. Don't redo work when input hasn't changed.
- **Diagnostics:** check before starting, after changes. Fix all errors before marking complete.
- **Formatting:** automated formatters handle style. **Backward compatibility:** only when explicitly required.

### Systematic Debugging

**No fixes without root cause investigation.** Phases run sequentially:

1. **Root cause** — read errors completely, reproduce consistently, check `git diff`, instrument at boundaries. For multi-factor repros, **minimise**: shrink to the smallest scenario that still fails, cutting elements (halve first, then one at a time) and re-running after each cut; done when every remaining element is load-bearing. A minimal repro shrinks the hypothesis space and becomes the regression test.
2. **Pattern analysis** — `semble search` to find working examples and related code; `semble find-related` from the bug site to discover parallel implementations. Compare; identify ALL differences.
3. **Hypothesis** — when the trace hasn't conclusively pinned the cause, generate **2–3 ranked, specific, falsifiable hypotheses before testing the first**; single-hypothesis generation anchors on the first plausible idea. Each names a concrete mechanism ("state resets because component remounts on route change") and the prediction that would confirm or refute it — no stated prediction means discard or sharpen. Test the top one with minimal change, one variable at a time.
4. **Implementation** — failing test first (TDD), single fix, verify completely.

**Red flags → STOP:** "quick fix for now," multiple changes at once, proposing fixes before tracing data flow, 2+ failed fixes. **3+ failed fixes = architectural problem** — question the pattern, don't fix again.

**Revert-first.** When something breaks: (1) revert the change, (2) consider deleting the broken thing entirely, (3) one-liner targeted fix, (4) none of the above → stop, reconsider.

**Meta-debugging:** treat your own code as foreign. Your mental model is a guess — the code's behavior is truth.

#### Defense-in-Depth (after fixing)

Make the bug structurally impossible, not just patched. Trace backward from symptom to original trigger (`codegraph_explore(query="<fn> callers")`, or `new Error().stack` instrumentation). Fix at the source. Then add validation at every layer the data passes:

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
await sleep(500)
result = get_result()

# ✅ reliable
result = await wait_for(lambda: get_result() is not None, timeout=5.0)
```

**Use:** flaky tests, async waits. **Don't use** when testing actual timing (debounce, throttle) — document WHY in that case. Poll every 10 ms, always include a timeout with a clear error, call the getter inside the loop (no stale cache).

### Merge Conflict Resolution

Resolve hunk by hunk, preserving both intents. When the code alone doesn't settle a hunk, read why each side changed (commit messages, PRs, issues); regenerate lockfiles and build output rather than hand-resolving them. When the two intents are genuinely incompatible and neither the merge's goal nor the user's request discriminates, stop and ask — never invent new behaviour inside a resolution. Run the project's checks afterwards.

**⛔ Never `--abort` on your own initiative.** Resolving is the default; abandoning the merge is the user's call. Completing it (`git add`, `git commit`, `git rebase --continue`) needs permission like any other git write.

### Git Operations

**Read git state freely. NEVER execute write commands without EXPLICIT user permission.** This is about git commands, not file edits — file editing is always allowed.

- **⛔ Write commands need permission:** `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset`, `stash`, `checkout`. "Fix this bug" ≠ "commit it."
- **⛔ NEVER `git checkout --` on unstaged changes.** Irreversible — work is permanently lost. Tell the user the consequences and let THEM run it. "Remove this" / "revert this" do NOT mean "discard all unstaged work." Use Edit for targeted changes.
- **⛔ Never `git add -f`** — if gitignored, tell the user.
- **⛔ Never write a repo-local git identity.** `git config user.email <value>` / `user.name <value>` is forbidden: repo config beats `~/.gitconfig`, so a throwaway identity silently re-authors every later commit, and the author is part of the commit hash — only a history rewrite undoes it. Reads and explicit `--global` / `--system` writes are fine. Need a scratch identity for a temp repo? Use `git -c user.email=… commit` per command, or set it inside the temp repo only.
- **⛔ Never selectively unstage** — commit all staged changes as-is.
- **⛔ Always `git push -u` on new branches** so the local branch tracks the correct remote.
- **⛔ Respect the active branch. Never auto-branch.** Work on whatever branch the user has checked out. Do NOT run `git checkout -b`, do NOT switch branches, do NOT invent branch names (e.g. `<username>/<feature>`, `feat/<slug>`, `fix/<slug>`) unless the user explicitly asks for a new branch in *this* request. Project conventions in `CLAUDE.md` / `AGENTS.md` that mandate a branch-naming pattern do NOT count as a request to create one now — surface the convention and ask. The exception is `/spec` with `Worktree: Yes`, which manages branches in an isolated worktree.
- **Read commands always allowed:** `status`, `diff`, `log`, `show`, `branch`.
- **Exceptions:** explicit override ("checkout branch X", "create a new branch for this"), and worktree during `/spec` (`Worktree: Yes`).
