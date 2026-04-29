---

## Step 3: Root Cause Investigation

Complete each sub-step before the next. No shortcuts.

### 3.1 Reproduce & understand

- Restate **symptom** (what user observes), **trigger** (when/how), **expected behaviour**.
- Vague? One focused `AskUserQuestion`.
- Reliable repro? Steps?
- **Not reproducible after 2 attempts:** STOP guessing. `AskUserQuestion` for the missing signal — exact command, input, environment, stack trace, or recording.
- **Intermittent (flaky / race):** trigger 10+ times, record state at failure. Flaky bugs need a test that **forces** the race (deterministic ordering, frozen clock, blocked event loop), not one that hopes to hit it.

### 3.2 Recent changes

- `git log --oneline -10 -- <file>`, `git diff` for the obvious suspects.
- **A specific token appeared/disappeared?** `git log -S "<string>" -- <path>` (added/removed). Regex: `git log -G "<pattern>"`. Faster than bisect when correlated with a symbol.
- New deps, config changes, env differences?

### 3.3 Trace the root cause

**Start with `codegraph_context(task="<bug description and symptoms>")`** — single call, returns entry points, related symbols, and code context. Read it before going deeper.

**Deep dive when needed:** `codegraph_search` to find a specific symbol, then `codegraph_explore(query="<symbol names>")` for full source from all relevant files in one call.

**Backward tracing (symptom → source):**

1. Find where the wrong behaviour appears — note `file:line`.
2. `codegraph_callers` traces what called this with the bad value/state.
3. Keep tracing until you find the **source** where the bad data originates.
4. **Fix at the source, not where the error appears.**

**Multi-component systems — instrument at boundaries before concluding:**

```bash
# Layer 1: entry point
echo "=== enter handler — input: ==="
echo "$INPUT"

# Layer 2: business logic
echo "=== leave handler / enter service — payload: ==="
jq . <<< "$PAYLOAD"

# Layer 3: storage
echo "=== query result: ==="
psql -c "SELECT id, status FROM jobs WHERE id=$JOB_ID"
```

This reveals **which** layer breaks. Investigate that layer next — don't speculate across layers.

**⛔ Mark every temporary log/print with `SPEC-DEBUG:`** (e.g. `console.log("SPEC-DEBUG: filters=", filters)`, `# SPEC-DEBUG: print(x)`). Verification greps the diff for this marker — any match fails verification and forces cleanup. Only way temporary diagnostics are allowed in the fix diff.

**Structural tracing — proportional to bug scope.** For bugs spanning 2+ files, modules, or components, run `codegraph_callers` + `codegraph_callees` on the root-cause function plus `codegraph_impact` for blast radius. For local bugs (typo, off-by-one, wrong constant in one function, missing null check at one call site), `codegraph_context` from above plus a targeted Read is enough — skip the full call-graph traversal.

Tools: CodeGraph, Probe CLI (`probe search`/`probe extract`), Read/Grep/Glob for exact patterns.

### 3.4 Pattern analysis

1. Find **working examples** — similar code in the codebase that works correctly.
2. Compare: what's different between working and broken?
3. List every difference — don't assume "that can't matter".

### 3.5 Root cause statement

State clearly:

- **Root cause:** `file/path.py:lineN` — `function_name()` does X but should do Y
- **Why:** WHY it causes the symptom (not just what is wrong)
- **Confidence:** High (traced fully) / Medium (strong hypothesis) / Low (needs more data)

Low confidence → gather more evidence. Don't guess.

**Escalation:** if 3+ hypotheses have failed, this is likely architectural. STOP and `AskUserQuestion` before continuing.
