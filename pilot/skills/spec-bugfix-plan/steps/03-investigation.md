---

## Step 3: Root Cause Investigation

**Complete each sub-step before the next. No shortcuts.**

### 3.1: Reproduce & Understand

1. Restate: **symptom** (what user observes), **trigger** (when/how), **expected behavior**
2. If too vague: `AskUserQuestion` with ONE focused question
3. Can you trigger it reliably? What are the exact steps?
4. **If not reproducible after 2 focused attempts:** STOP investigating silently. `AskUserQuestion` for the missing signal — exact command, input, environment, stack trace, or a recording. A speculative fix for an unreproduced bug is roughly 50% wasted effort; asking is cheaper than guessing.
5. **If intermittent (flaky / race / timing):** trigger it 10+ times, record how often it fires and what state correlates with failures. Flaky bugs need a test that **forces** the race (deterministic ordering, frozen clock, blocked event loop), not a test that hopes to hit it.

### 3.2: Check Recent Changes

- What changed that could cause this? `git log --oneline -10 -- <file>`, `git diff`
- **When a specific token appeared or disappeared:** `git log -S "<string>" -- <path>` finds commits that added/removed that exact string. For regex patterns: `git log -G "<pattern>"`. Faster than `git bisect` when the bug correlates with a specific symbol.
- New dependencies, config changes, environmental differences?

### 3.3: Trace the Root Cause

**⛔ START WITH CODEGRAPH — before reading any files.**

**Step 1: Orient with CodeGraph (MANDATORY FIRST ACTION):**
```
codegraph_context(task="<bug description and symptoms>")
```
This reveals entry points, related symbols, and code context for the bug area. Read the output carefully before diving deeper.

**Step 2: Deep dive if needed:** Use `codegraph_search` to find the specific symbol, then `codegraph_explore(query="<symbol names>")` to get full source code from all relevant files in one call.

**Step 3: Trace and investigate.** Use Probe for intent-based search (`probe search`), CodeGraph for structural tracing. Fall back to Grep/Glob only for exact patterns.

Read as many files as needed. For each: read completely, trace execution path from user action to symptom, note specific lines where behavior diverges.

**Backward tracing technique (from symptom to source):**

1. Find where the error/wrong behavior appears — note file:line
2. Use `codegraph_callers` to trace what called this with the wrong value/state
3. Keep tracing until you find the **source** — where the bad data originates
4. **Fix at the source, not where the error appears**

**Multi-component systems:** Before concluding, instrument at component boundaries:

- What data enters each component? What exits?
- WHERE does it break? Run once to gather evidence, THEN investigate the failing component.
- **Mark every temporary log/print with `SPEC-DEBUG:`** (e.g. `console.log("SPEC-DEBUG: filters=", filters)`, `# SPEC-DEBUG: print(x)`). Verification greps the diff for this marker — any match fails verification and forces cleanup. This is the only way temporary diagnostics are allowed in the fix diff.

**⛔ Structural tracing (MANDATORY):** Run `codegraph_callers` and `codegraph_callees` on the function where the bug manifests AND the function at the root cause. Then run `codegraph_impact` to see the full blast radius — essential for understanding how bad data flows through the system.

Tools: CodeGraph (`codegraph_context`, `codegraph_explore`, `codegraph_callers`/`codegraph_callees`, `codegraph_impact`, `codegraph_search`), Probe CLI (`probe search` for intent, `probe extract` for symbols), Read/Grep/Glob for exact patterns.

### 3.4: Pattern Analysis

1. Find **working examples** — similar code in the codebase that works correctly
2. Compare: what's different between working and broken?
3. List every difference, however small — don't assume "that can't matter"

### 3.5: Root Cause Statement

State clearly:

- **Root cause:** `file/path.py:lineN` — `function_name()` does X but should do Y
- **Why:** Explain WHY it causes the symptom (not just what's wrong)
- **Confidence:** High (traced fully) / Medium (strong hypothesis) / Low (needs more data)

If confidence is Low: gather more evidence. Don't guess.

**Escalation:** If 3+ hypotheses have failed, STOP — this is likely an architectural problem, not a simple bug. `AskUserQuestion` to discuss with user before continuing.
