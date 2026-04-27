## Verification

**Core Rules:** (1) Tests passing ≠ program working — always execute. (2) No completion claims without fresh evidence in the current message.

### Execution Verification

Unit tests with mocks prove nothing about real-world behavior. After tests pass:

- CLI command → **run it** | API endpoint → **call it** | Frontend UI → **use browser automation** (see `browser-automation.md` for 4-tier tool selection: Chrome → Chrome DevTools MCP → playwright-cli → agent-browser)
- Any runnable program → **run it**

**When:** After tests pass, after refactoring, after changing imports/deps/config, before marking any task complete.

**Skip only for:** documentation-only, test-only, pure internal refactoring (no entry points), config-only changes.

### ⛔ Frontend Changes Require Browser Verification

**Unit tests and typechecks are NOT sufficient.** After tests pass, verify with browser automation that the change works in the running app. This applies in BOTH `/spec` and quick mode.

**Procedure (quick mode — outside `/spec`):**

1. Build/deploy the change
2. **Resolve browser tool** (see `browser-automation.md` for full details):
   - **Chrome extension** (`mcp__claude-in-chrome__*` in tools list): Use Claude Code Chrome.
   - **Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` in tools list): Fallback when extension unavailable.
   - **Otherwise:** Use playwright-cli for thorough verification, or agent-browser for simple checks.
3. Navigate to the affected page, interact with the changed UI, verify correct behavior
4. Report what you saw — "UI works" requires browser evidence, not just "tests pass"

**Do NOT skip this step.** "It's a small CSS change" or "the tests cover it" is not an excuse — CSS layout issues, stale bundles, and elements in DOM but not visible/interactive are invisible to tests.

**Common pitfalls:** stale cached bundles, bundle not deployed to served location, CSS layout issues invisible to tests, elements in DOM but not visible/interactive.

### Output Correctness

**Running without errors ≠ correct output.** If code processes external data, fetch that data independently and compare. Numbers and content MUST match.

### Evidence Before Claims

**Before proceeding:** Ask "Do these tests verify what matters, or only what was easy to test?" If important edge cases go untested, acknowledge the gap explicitly — don't claim full coverage when you only have partial coverage.

1. **Identify** — What command proves this claim?
2. **Execute** — Run the full command (not cached)
3. **Read output** — Check exit code, count failures
4. **Report** — State claim WITH evidence

**If you haven't run the command in this message, you cannot claim it passes.**

| Claim | Required Evidence | Insufficient |
|-------|-------------------|-------------|
| "Tests pass" | Fresh run: 0 failures | Previous run, "should pass" |
| "Build succeeds" | Build exit 0 | "Linter passed" |
| "Bug fixed" | Reproducing test passes | "Code changed" |
| "UI works" | Browser verification (Chrome `read_page`, DevTools MCP `take_snapshot`, playwright-cli `snapshot`, or agent-browser `snapshot -i`) | "API returns 200" |
| "No perf regression" | Hot paths cache/memoize, no heavy full imports, no redundant work on repeat | "Tests pass" |

### ⛔ Fix ALL Errors — No Exceptions, No Asking

When verification reveals errors during a `/spec` workflow, fix ALL of them without asking. Outside of `/spec`, respect the user's current mode — if in plan mode, present the issues and proposed fixes instead of applying them directly.

### ⛔ Auto-Fix in /spec Workflow

**must_fix** and **should_fix** → Fix immediately. **suggestions** → Implement if quick. The ONLY user interaction in /spec is plan approval. These auto-fix rules apply exclusively within `/spec` — they do not override the user's plan mode or approval preferences outside of `/spec`.

### Stop Signals — Verify NOW

If you're about to use uncertain language ("should", "probably"), express satisfaction ("Done!"), commit/push, or mark task complete — run verification first.

### When Execution Fails After Tests Pass

This is a real bug. During `/spec`, fix immediately → re-run tests → re-execute → add test to catch this failure type. Outside `/spec`, report the issue and proposed fix to the user.

### Five Failure Modes Self-Check

Before reporting completion, do an explicit pass against each of the five failure modes identified in the 2026 Agentic Coding Trends Report. These are the predictable ways autonomous agents go wrong; naming them keeps each one distinct in attention.

#### Hallucinated Actions

Did the implementation invent file paths, env var names, IDs, function names, library APIs, URLs, or other external values that aren't authoritatively confirmed? Common example: `process.env.STRIPE_SECRET_KEY` when the actual var is `STRIPE_SK`. See *Never invent values* in `development-practices.md` for the upstream rule.

#### Scope Creep

Does the diff touch files or behaviors outside the request? Bundled refactors, "while I'm here" cleanups, or stylistic changes that should be a separate PR? Apply the lineage test (`development-practices.md`) — every changed line must trace directly to the user's request.

#### Cascading Errors

Was a failure suppressed/caught/wrapped in a way that hides the root cause from callers? Silent fallbacks (try/except returning empty arrays, default values that paper over missing data, swallowed exceptions) mask bugs and metastasize them.

#### Context Loss

Does the diff contradict earlier decisions in the session, the plan, CLAUDE.md, or `CONTEXT.md`? Names, conventions, invariants applied inconsistently? Industry research finds ~65% of agent failures trace to context drift, not raw token exhaustion.

#### Tool Misuse

Wrong tool for the job (e.g., `Bash` for file reads when `Read` exists, MCP server when CLI was simpler), or right tool with wrong parameters (e.g., `Grep` without proper escaping, `Edit` without reading first)? Re-check against the tool selection guidance in `cli-tools.md` and `mcp-servers.md`.

**If any mode flagged → fix and re-run, don't claim done.** See also *Stop Signals — Verify NOW* (above) for context-drift signals that warrant verification mid-work, and *Evidence Before Claims* (above) for the verification protocol when *Hallucinated Actions* or *Context Loss* are suspected. Five Failure Modes is the explicit pre-completion checklist; Stop Signals and Evidence Before Claims are the active-during-work guards.
