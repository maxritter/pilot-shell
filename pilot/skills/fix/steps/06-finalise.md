## Step 6: Finalise

### 6.1 Worktree mode — single commit

If a worktree was created: bundle test + fix into one commit.

```bash
git add <test_file> <fix_file>
git commit -m "fix: <one-line description>"
```

The conventional `fix:` prefix triggers a patch release if/when this branch ships. Do not split into multiple commits in the quick lane.

### 6.2 Approval gate (only when enabled)

⛔ **Before showing the approval question, you MUST have completed Step 4 (Verify End-to-End) with evidence.** "Tests pass" is not enough — the approval summary must include what you actually ran and what you observed. If you cannot fill in `**E2E:**` below with concrete evidence, you have not finished Step 4 — go back, do not ask for approval.

Read `PILOT_PLAN_APPROVAL_ENABLED`. If `"false"` → skip 6.2 entirely, mark done.

When approval is enabled, summarise + ask:

```
AskUserQuestion(
  question="Bugfix complete.\n\n**Bug:** <one line>\n**Root cause:** `<file>:<line>` — <what>\n**Fix:** <one-line description of the change>\n**Tests:** reproducing test added (`<test_name>`), full suite green.\n**E2E:** <command/URL you ran and the concrete observation that proves the fix — e.g. 'curl /search -d {} → 200 with [results]', 'opened /tasks page, saved end_date=2026-05-15, list shows 2026-05-15', 'ran pilot register-plan ./foo.md PENDING → exit 0, plan visible in console'>\n\nReview the diff in the Console's Changes tab. Approve when ready:",
  options=[
    "Approve — done",
    "Issues — describe them, I'll address",
    "Manual — let me test, I'll come back"
  ]
)
```

Handle:

- **Approve** → done.
- **Issues** → user describes problem. Treat as a new investigation: re-run Step 1.3 (re-trace) → Step 2 onward.
- **Manual** → ask once more (`AskUserQuestion` for the stop-guard) and wait. On user return, treat new content as either approval or new issues.

### 6.3 Console notification (always, when binary present)

```bash
~/.pilot/bin/pilot notify plan_approval "Bugfix complete" "<one-line bug>" 2>/dev/null || true
```

Best-effort — don't block on failure.

### 6.4 Report

```
Bugfix complete — <bug>.
Root cause: <file>:<line>.
Tests: 1 new reproducing test, full suite green.
E2E: <command/URL run> → <observation that proves the symptom is gone>.

Run /clear before starting new work — this resets context while keeping project rules loaded.
```

The `E2E:` line is **mandatory** — it documents that the actual program was exercised, not just the unit tests.

ARGUMENTS: $ARGUMENTS
