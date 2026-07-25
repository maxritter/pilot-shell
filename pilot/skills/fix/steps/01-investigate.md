## Step 1: Investigate Root Cause

**Goal:** trace the bug to `file:lineN — function() does X but should do Y` with High or Medium confidence. If you can't, bail out (see orchestrator).

### 1.1 Reproduce & understand

- Restate **symptom**, **trigger**, **expected behaviour**.
- **Runnable reproduction? Execute it NOW — before reading any code.** When the report names a failing test, a CI failure, or a crashing command, running it locally is the FIRST investigative action — before `git log` (1.2), before tracing (1.3), before forming any hypothesis. Capture everything:

  ```bash
  REPRO_LOG="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}/fix-repro.log"; mkdir -p "$(dirname "$REPRO_LOG")"
  set -o pipefail; <repro command> 2>&1 | tee "$REPRO_LOG"
  ```

  (`pipefail` keeps the test's failing exit status visible through the pipe — without it, `tee` reports exit 0 and a failing run looks like a pass.)

- **Read the COMPLETE output, not just the failing assertion.** Warning lines, stderr, "exception caught/swallowed/ignored" notices, and log output *above* the failure frequently name the root cause directly — one warning line read here can replace the entire tracing phase. Skim the whole capture, then sweep it as a completeness check:

  ```bash
  grep -niE "warn|error|exception|traceback|ignored|swallowed" "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}/fix-repro.log"
  ```

- **CI-only failure?** Still run the test locally first. A local pass against a CI fail is itself a finding (environment or mocking drift), and the local output is your baseline either way.
- **Multi-factor repro? Minimise first** (Systematic Debugging step 1) — the minimal repro becomes the Step 2 test.
- If the description is too vague to reproduce: one focused `AskUserQuestion` (only when `PILOT_PLAN_QUESTIONS_ENABLED` is not `"false"`).
- If you can't trigger it after 2 attempts because you don't understand the bug (unknown input, steps, or data): bail out. Tell the user the bug isn't reproducible from the description alone, ask them to either provide more detail or re-invoke with `/spec` for the full investigation workflow. The quick lane is for reproducible bugs. A reproduction blocked by the *environment* is NOT this case — `/spec` would hit the same wall; use the blocker protocol below instead.

**Environment blocker protocol — involve the user, NEVER speculate around it.** When the reproduction cannot run because the environment blocks it — expired cloud auth (`gcloud` / `aws` / `az`), dependencies behind a private registry, a credential or service only the user has:

1. Make at most ONE quick attempt at a workaround (an already-provisioned `.venv` / `.tox`, a cached environment). One. Not a research project.
2. Then STOP and ask the user to unblock — name the exact blocker and the exact unblock command (e.g. "dependency install needs Google Artifact Registry auth — run `gcloud auth application-default login`"). Ask via `AskUserQuestion` with two options: **"Unblocked — re-run the repro"** and **"Continue without running (static investigation, degraded confidence)"**.
3. This question is **exempt from the `PILOT_PLAN_QUESTIONS_ENABLED` toggle** — a blocked reproduction is a hard stop, not a planning preference.
<!-- CC-ONLY -->
4. For interactive logins, tell the user they can type `! <command>` (e.g. `! gcloud auth application-default login`) to run it inline in this session so the output lands in the conversation.
<!-- /CC-ONLY -->
<!-- CODEX-START
4. For interactive logins, ask the user to run the command in a separate terminal and reply here when it's done.
CODEX-END -->
5. Once unblocked, re-run the reproduction and continue from the top of 1.1.

⛔ Forbidden moves when the repro is blocked:

- "I might not need to run the test at all" — you do. The run's output is primary evidence; this exact rationalization is the documented derail the protocol exists to prevent.
- Pivoting to recent diffs or unrelated code as a *substitute* for the run. (Reading code while you WAIT for the user is fine; concluding from it without ever running is not.)
- Silently choosing the degraded static path. Only the USER may choose it, and if they do, the Step 6 report must state that the reproduction was never executed.

### 1.2 Recent changes (one bash call, then move on)

```bash
git log --oneline -10 -- <suspected_file_or_dir> 2>/dev/null
```

Look for the commit that introduced the bug. If recent, read that diff. If nothing obvious, skip.

**Bisect when `git log` doesn't reveal it.** If the bug appeared between two known-good and known-bad states and the suspect commit isn't obvious, run `git bisect start <bad> <good>` then `git bisect run <test-cmd>` against the reproducing test you'll write in Step 2 — this pinpoints the introducing commit automatically. Skip when the surface area is small enough that a single read finds it.

### 1.3 Trace to root cause

<!-- CC-ONLY -->
**Start with `codegraph_explore(query="<bug description>")`** for structure, then `mcp__semble__search` for intent ("where does X get modified", "how is Y configured") — especially for cross-language or cross-cutting bugs.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Use `codegraph_explore` only when the bug is structural or the entry point is unclear.** For docs, rules, markdown, config, UI copy, or a named local file/function, start with targeted reads or Semble. If the user names a concrete path or the symptom points to one file, read that file first and add CodeGraph only if the call path becomes the actual question.
CODEX-END -->

For local bugs (single file, single function): one or two targeted `Read`s is enough. **Do not** run `codegraph_explore` for callers/callees/impact on local bugs — that's the full-lane bias and it's the single biggest time sink for trivial fixes.

For bugs that span 2 files in the same component (e.g. service.ts + service.test.ts): targeted `Read`s. Still no full call-graph traversal.

**Bail-out check at end of 1.3:** if you can't pin file:line, or the trace fails the logic-divergence test in the orchestrator's bail-out section, stop and hand off to `/spec`. Don't switch lanes silently.

### 1.4 Instrument when needed (UI / async / race / timing bugs)

For bugs that don't surface clearly through stack traces or static reading — UI rendering glitches, async timing, race conditions, integration-layer issues — add **temporary diagnostic logging** to the production code and trigger the bug to read the output:

- Log input values entering the suspect function.
- Log branch conditions (which path executed?).
- Log computed intermediate results.
- Log return values at layer boundaries.

**Mark every temporary log with `SPEC-DEBUG:`** (e.g. `console.log("SPEC-DEBUG: filters=", filters)`). Step 3.5 greps for this marker — any unremoved match fails the diff sanity check.

**Unknown caller?** If the bug is in shared code reached from many sites and you don't know which caller triggers it, capture the call chain inline:

```js
// SPEC-DEBUG: who is calling this with bad input?
console.error("SPEC-DEBUG:", { args, stack: new Error().stack });
```

Run, read the stack, identify the offending caller, then trace upward to the original trigger.

**Performance regressions are different.** Value-logging is the wrong tool — replace it with baseline measurement: timing harness, `performance.now()`, profiler, or query plan / `EXPLAIN`. Establish current vs expected timing first, then bisect against that signal (Step 1.2). Measure first, fix second.

Skip 1.4 when the stack trace already names the failing line, or when a static read of the file is enough to see the bug. Skip is the default.

### 1.5 State the root cause

Out loud, in one sentence to the user, before writing any test:

> "Root cause: `<file>:<line>` — `<function>()` does <X>, should do <Y>. This causes the symptom because <reason>. Confidence: <High|Medium>."

If confidence is Low: bail out. Don't guess in the quick lane.

### 1.6 Lock in a fast signal before Step 2

Your reproducing signal — what runs in <30s and definitively shows fail/pass — must be **fast and deterministic** before you write the fix. For most bugs that's the unit test you're about to write in Step 2. For UI / integration / async bugs the unit-test seam may be wrong, and your real signal is a `curl`, CLI invocation, or headless-browser command (the same one you'll run in Step 4 E2E).

Whichever it is, sharpen it now:

- **Slow loop (>30s)?** Narrow the test scope, skip unrelated setup, cache fixtures. A flaky 30s loop is the slowest path to a fix.
- **Flaky?** Pin time, seed RNG, isolate filesystem, freeze network. For non-deterministic bugs, raise the reproduction rate (loop the trigger 50–100×, parallelise) until it's debuggable — a 1% flake is not.
- **Wrong symptom?** The signal must fail with the **user's** reported symptom, not a different failure that happens to be nearby. Wrong bug = wrong fix.

If you cannot get a fast deterministic signal after one pass of sharpening, that's a bail-out trigger — tell the user to use `/spec`. Don't hypothesise into a flaky loop.

### User signal you're off track

If the user says "stop guessing", "is that not happening?", or "ultrathink this", they are telling you a hypothesis got treated as a finding. Return to 1.3 and trace.
