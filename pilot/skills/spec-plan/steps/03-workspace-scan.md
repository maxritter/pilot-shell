## Step 3: Workspace Scan (MANDATORY, BEFORE QUESTIONS)

**Why this step exists.** Batch 1 clarifying questions (Step 4) are generated *before* exploration. Without code context, options collapse to generic shapes ("extend existing" vs "new module") instead of grounded ones ("Extend `LicenseAuth` in `launcher/auth.py:42`"). A single ~2-second scan up front fixes that — and the same scan is reused in Step 5 so we never pay for `codegraph_context` twice.

**⛔ Always runs**, regardless of `PILOT_PLAN_QUESTIONS_ENABLED`. Autonomous mode benefits *more* from grounded defaults, not less — when there is no user to disambiguate, the codebase has to.

### 3.1: Run the scan

1. **CodeGraph orientation** (always):

   ```
   codegraph_context(task="<task description from user>")
   ```

   Returns entry points, related symbols, and key code locations.

2. **Semble pattern search** (skip if `codegraph_context` already returned ≥3 highly relevant hits AND the task has no clear noun targets — keep total budget under ~2s):

   ```
   mcp__semble__search(query="<2-3 key nouns from task>")
   ```

   Use natural-language intent for conceptual tasks ("how does auth work"); use identifier-like queries when the task names a symbol ("LicenseAuth save_pretrained"). One call, top-k default.

### 3.2: Capture structured output (in-context, NOT in the plan file yet)

Record the scan results in this shape so Steps 3, 4, and 5 can all consume them:

```
Workspace Scan
- Entry points: [file:line, file:line, ...]
- Related symbols: [Name @ file:line, ...]
- Similar patterns: [Semble hit @ file:line — 1-line summary, ...]
- Greenfield?: [yes | no]
```

`Greenfield?: yes` ⇔ both CodeGraph and Semble returned no relevant hits for this task. Set this explicitly — Steps 4 and 6 use it to decide whether to ground options in real code or fall back to generic options.

### 3.3: Hand-off to downstream steps

- **Step 4 (Batch 1 questions)** consumes the scan output and grounds every option label in real files/symbols when they exist. If `Greenfield?: yes`, falls back to generic options and documents the fallback under "Autonomous Decisions".
- **Step 5 (Exploration)** skips 5.1's `codegraph_context` re-run — that work happened here. It proceeds directly to deeper exploration (`codegraph_explore`, `codegraph_search`, dependency analysis).
- **Step 6 (Batch 2 questions)** applies the same labeling discipline to approach and design options.

**Do NOT write scan output into the plan file at this step** — the plan file is composed in Step 9. The scan output is working context for the planning phase.
