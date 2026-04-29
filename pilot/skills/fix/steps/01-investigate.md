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

### 1.3 Trace to root cause

**Start with `codegraph_context(task="<bug description>")`** — single call, returns entry points and related symbols. Read it carefully.

For local bugs (single file, single function): one or two targeted `Read`s on the file from the codegraph output is enough. **Do not** run `codegraph_callers`/`callees`/`impact` for local bugs — that's the full-lane bias and it's the single biggest time sink for trivial fixes.

For bugs that span 2 files in the same component (e.g. service.ts + service.test.ts): targeted `Read`s. Still no full call-graph traversal.

**Bail-out check at end of 1.3:** if your trace touched 3+ files, or you found yourself running `codegraph_callers`, or you can't pin file:line — stop and tell the user to use `/spec` (see orchestrator's bail-out triggers). Don't switch lanes silently.

### 1.4 Instrument when needed (UI / async / race / timing bugs)

For bugs that don't surface clearly through stack traces or static reading — UI rendering glitches, async timing, race conditions, integration-layer issues — add **temporary diagnostic logging** to the production code and trigger the bug to read the output:

- Log input values entering the suspect function.
- Log branch conditions (which path executed?).
- Log computed intermediate results.
- Log return values at layer boundaries.

**Mark every temporary log with `SPEC-DEBUG:`** (e.g. `console.log("SPEC-DEBUG: filters=", filters)`). Step 3.5 greps for this marker — any unremoved match fails the diff sanity check.

Skip 1.4 when the stack trace already names the failing line, or when a static read of the file is enough to see the bug. Skip is the default.

### 1.5 State the root cause

Out loud, in one sentence to the user, before writing any test:

> "Root cause: `<file>:<line>` — `<function>()` does <X>, should do <Y>. This causes the symptom because <reason>. Confidence: <High|Medium>."

If confidence is Low: bail out. Don't guess in the quick lane.

### Red flags — STOP and re-investigate

- "Quick fix for now, investigate later" → STOP, this IS the quick lane.
- "I'll just try changing X" → STOP, trace it first.
- "It's probably X" → STOP, prove it.
- "I see the symptom, let me fix it" → seeing symptoms ≠ understanding root cause.

If the user says "stop guessing", "is that not happening?", "ultrathink this" — STOP, return to 1.3.
