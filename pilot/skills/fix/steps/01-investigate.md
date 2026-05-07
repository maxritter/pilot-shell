## Step 1: Investigate Root Cause

**Goal:** trace the bug to `file:lineN — function() does X but should do Y` with High or Medium confidence. If you can't, bail out (see orchestrator).

### 1.1 Reproduce & understand

- Restate **symptom**, **trigger**, **expected behaviour**.
- If too vague: one focused `AskUserQuestion` (only when `PILOT_PLAN_QUESTIONS_ENABLED` is not `"false"`).
- If you can't trigger it after 2 attempts: bail out. Tell the user the bug isn't reproducible from the description alone, ask them to either provide more detail or re-invoke with `/spec` for the full investigation workflow. The quick lane is for reproducible bugs.

### 1.2 Recent changes (one bash call, then move on)

```bash
git log --oneline -10 -- <suspected_file_or_dir> 2>/dev/null
```

Look for the commit that introduced the bug. If recent, read that diff. If nothing obvious, skip.

**Bisect when `git log` doesn't reveal it.** If the bug appeared between two known-good and known-bad states and the suspect commit isn't obvious, run `git bisect start <bad> <good>` then `git bisect run <test-cmd>` against the reproducing test you'll write in Step 2 — this pinpoints the introducing commit automatically. Skip when the surface area is small enough that a single read finds it.

### 1.3 Trace to root cause

**Start with `codegraph_context(task="<bug description>")`** — single call, returns entry points and related symbols. Read it carefully.

For local bugs (single file, single function): one or two targeted `Read`s on the file from the codegraph output is enough. **Do not** run `codegraph_callers`/`callees`/`impact` for local bugs — that's the full-lane bias and it's the single biggest time sink for trivial fixes.

For bugs that span 2 files in the same component (e.g. service.ts + service.test.ts): targeted `Read`s. Still no full call-graph traversal.

**Bail-out check at end of 1.3:** if you can't pin file:line, or each touched file would need **different** logic (not the same pattern repeated) — stop and tell the user to use `/spec` (see orchestrator's bail-out triggers for the full list). Multi-file traces are fine when each site needs the *same* fix; that's one logical bug, multiple guard sites. Don't switch lanes silently.

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

### Red flags — STOP and re-investigate

- "Quick fix for now, investigate later" → STOP, this IS the quick lane.
- "I'll just try changing X" → STOP, trace it first.
- "It's probably X" → STOP, prove it.
- "I see the symptom, let me fix it" → seeing symptoms ≠ understanding root cause.

If the user says "stop guessing", "is that not happening?", "ultrathink this" — STOP, return to 1.3.
