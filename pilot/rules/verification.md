## Verification

**Core rules:** (1) Tests passing ≠ program working — always execute. (2) No completion claim without fresh evidence in the current message.

### Execution Verification

Unit tests with mocks prove nothing about real-world behavior. After tests pass:

- CLI command → run it. API endpoint → call it. Frontend UI → use browser automation (see `browser-automation.md`). Any runnable program → run it.

**When:** after tests pass, after refactoring, after changing imports/deps/config, before marking any task complete. **Skip only for:** docs-only, test-only, pure internal refactoring with no entry points, config-only.

### ⛔ Frontend changes need browser evidence

Resolve a live target via the probe below, then follow `browser-automation.md`. "UI works" requires a browser, not a passing test — stale bundles, undeployed assets, and CSS breakage are all invisible to unit tests. "Small CSS change" is not an exemption.

### ⛔ Live-Target Probe — required before any "I can't run live E2E" claim

**Failure mode this rule prevents:** unit tests pass, no local server is running, the model concludes "unit-verified is sufficient" and marks the work done WITHOUT ever opening a browser against a deployed instance. The user's local setup was perfectly capable of a preview deploy — the model just didn't ask.

Before declaring live E2E impossible, you MUST run a 4-tier probe and record the outcome of each tier:

| Tier | What | Skip reason allowed |
|---|---|---|
| 1 | Reuse an already-running local server (curl/health check the port named in the plan or repo defaults) | No process listening AND no health endpoint |
| 2 | Start the dev server yourself in background, poll its health endpoint up to 60s | No documented start command in plan / `package.json` / `pyproject.toml` / `Makefile` |
| 2b | **The artifact is installed, not served** — a mobile app, a desktop app, an extension, a packaged CLI. Build and install it the way the repo's own docs say (emulator, simulator, device, local install), then drive the installed copy | No documented build-and-install path |
| 3 | Detect deploy backends (Vercel, Fly, Netlify, Cloudflare Wrangler, Render, AWS, Heroku, GitHub-Actions deploy workflow), run the backend's auth-check command, attempt a preview deploy with the eligible one | Every detected backend's auth-check returns "not logged in" — quote the exact command + output |
| 4 | Unit-only fallback (`UNIT_VERIFIED` instead of `LIVE_PASS`) | Only after Tiers 1–3 above ALL failed with documented reasons |

⛔ **A dev server is not automatically the artifact.** For a mobile or desktop app the dev server serves the *source* while the thing under test is the installed build — different bundle, sometimes different network stack, and the difference is exactly where shipped-only bugs live. Tier 2b exists so such a project does not fall through to Tier 4 and get its UI ruled from source. When 2 and 2b both apply, take 2b: verify what the user would actually open.

**Acceptance criteria for the probe:**

- Every tier you attempted must have its outcome in the verification report (command run, exit status, error captured if any). "I assumed it wasn't available" is not a documented outcome.
- "No marker files for any deploy backend" is the ONLY no-attempt skip allowed for Tier 3. If `vercel.json` / `fly.toml` / etc. exists, you MUST run the auth-check for that backend before claiming Tier 3 is unavailable.
- Tier 3 success obligates you to clean up: e.g. `vercel rm <deployment-id>` for ad-hoc preview deploys created solely for verification, OR leave them with an explicit note in the verification report.

**The probe is generic across backends.** Do not hard-code Vercel — detect the backend from repo markers and use the right command. Adding a new backend is a one-row table edit in `spec-verify/steps/07-e2e-and-final-regression.md`.

### Output Correctness

Running without errors ≠ correct output. If code processes external data, fetch independently and compare. Numbers and content MUST match.

### Evidence Before Claims

Before proceeding, ask: "Do these tests verify what matters, or only what was easy to test?" If important edge cases go untested, acknowledge the gap explicitly — don't claim full coverage with partial.

1. **Identify** — what command proves this claim?
2. **Execute** — run the full command (not cached).
3. **Read output** — check exit code, count failures.
4. **Report** — state claim WITH evidence.

**If you haven't run the command in this message, you cannot claim it passes.**

| Claim | Required Evidence | Insufficient |
|-------|-------------------|--------------|
| "Tests pass" | Fresh run: 0 failures | Previous run, "should pass" |
| "Build succeeds" | Build exit 0 | "Linter passed" |
| "Bug fixed" | Reproducing test passes | "Code changed" |
| "Regression test works" | Red-green verified: revert the fix, watch the test FAIL, restore, watch it pass | "The test passes" (it may pass without the fix) |
| "UI works" | Browser snapshot/read_page | "API returns 200" |
| "Sub-agent completed the work" | The VCS diff shows the changes | The agent reported success |
| "No perf regression" | Hot paths cached/memoized (per `development-practices.md` §Performance) | "Tests pass" |

### ⛔ Fix Verification Errors in /spec and /build Without Asking

In `/spec`, fix all verification errors without asking — `must_fix` / `should_fix` immediately, `suggestions` if quick (severity → action policy: `code-review-reception.md`). The user-interaction points in `/spec` are the four listed in `task-and-workflow.md` (not just plan approval).

The same holds in `/build`: a failing criterion is the next round's job, never a question. Its three interaction points are also listed in `task-and-workflow.md`. Renegotiating a criterion you cannot close IS a question — lowering one quietly is the failure this workflow exists to prevent.

Outside both, respect the user's mode — in plan mode, present issues and proposed fixes instead of applying them.

### Stop Signals — Verify NOW

About to use uncertain language ("should", "probably"), express satisfaction ("Done!"), commit/push, or mark complete? Run verification first.

### When Execution Fails After Tests Pass

This is a real bug. During `/spec` or `/build`: fix → re-run tests → re-execute → add a test to catch this failure type. Outside them: report and propose.

### Five Failure Modes Self-Check

Before reporting completion, pass against each of the five (2026 Agentic Coding Trends Report):

- **Hallucinated actions** — invented paths, env vars, IDs, function names, library APIs, URLs (e.g., `STRIPE_SECRET_KEY` when actual is `STRIPE_SK`). Cross-ref *Never invent values* in `development-practices.md`.
- **Scope creep** — diff touches files/behaviors outside the request? Bundled refactors, "while I'm here" cleanups? Apply the lineage test (`development-practices.md`).
- **Cascading errors** — a failure suppressed/caught/wrapped in a way that hides root cause. Silent fallbacks (try/except returning `[]`, papering over missing data) metastasize bugs.
- **Context loss** — diff contradicts earlier decisions in the session, plan, CLAUDE.md, or CONTEXT.md? ~65% of agent failures trace to context drift, not token exhaustion.
- **Tool misuse** — wrong tool for the job (Bash for file reads, MCP when CLI was simpler), or right tool with wrong params (Grep without escaping, Edit without reading first). Re-check `cli-tools.md` and `mcp-servers.md`.

**Any mode flagged → fix and re-run, don't claim done.** Stop Signals and Evidence Before Claims are the during-work guards; Five Modes is the pre-completion checklist.

### Over-Engineering & Shortcut Debt

Beyond "does it work," check "is it the least that works" — run the ladder (`development-practices.md` → *Build the least that works*) over the diff before claiming done:

- **Over-built?** An abstraction with one implementation, a dependency the stdlib/platform already covers, boilerplate nobody asked for, a config for a value that never changes → flag and simplify. Same lens the native `/code-review` and `/simplify` skills apply — but both are user-invoked, so run it yourself here rather than waiting on a skill you cannot launch.
- **Shortcut debt harvested?** `grep -rnE '(#|//) ?SHORTCUT:' .` the change and list unresolved markers in the completion report so a deferral can't quietly become permanent (the ceiling+trigger contract lives in `development-practices.md` → *Mark deliberate shortcuts*).
