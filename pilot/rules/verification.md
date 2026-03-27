## Verification

**Core Rules:** (1) Tests passing ≠ program working — always execute. (2) No completion claims without fresh evidence in the current message.

### Execution Verification

Unit tests with mocks prove nothing about real-world behavior. After tests pass:

- CLI command → **run it** | API endpoint → **call it** | Frontend UI → **open with `agent-browser --session "${PILOT_SESSION_ID:-default}"`** (session isolation — see `agent-browser.md`)
- Any runnable program → **run it**

**When:** After tests pass, after refactoring, after changing imports/deps/config, before marking any task complete.

**Skip only for:** documentation-only, test-only, pure internal refactoring (no entry points), config-only changes.

### ⛔ Frontend Changes Require agent-browser Verification

**Unit tests and typechecks are NOT sufficient.** After tests pass, verify with `agent-browser` (with session isolation) that the change works in the running app: build → open → snapshot -i → interact → close.

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
| "UI works" | agent-browser snapshot -i | "API returns 200" |
| "No perf regression" | Hot paths cache/memoize, no heavy full imports, no redundant work on repeat | "Tests pass" |

### ⛔ Fix ALL Errors — No Exceptions, No Asking

When verification reveals errors during a `/spec` workflow, fix ALL of them without asking. Outside of `/spec`, respect the user's current mode — if in plan mode, present the issues and proposed fixes instead of applying them directly.

### ⛔ Auto-Fix in /spec Workflow

**must_fix** and **should_fix** → Fix immediately. **suggestions** → Implement if quick. The ONLY user interaction in /spec is plan approval. These auto-fix rules apply exclusively within `/spec` — they do not override the user's plan mode or approval preferences outside of `/spec`.

### Stop Signals — Verify NOW

If you're about to use uncertain language ("should", "probably"), express satisfaction ("Done!"), commit/push, or mark task complete — run verification first.

### When Execution Fails After Tests Pass

This is a real bug. During `/spec`, fix immediately → re-run tests → re-execute → add test to catch this failure type. Outside `/spec`, report the issue and proposed fix to the user.
