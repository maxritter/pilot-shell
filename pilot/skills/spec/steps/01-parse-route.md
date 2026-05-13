## Step 1: Parse & Route

```
IF arguments end with ".md" AND file exists:
    → Read plan, dispatch by status (Section 2)
ELSE:
    → Detect type, ask worktree, invoke Skill, STOP
```

### 1.1 Detect Type (new plans only)

- **Bugfix:** Something broken, crashing, wrong results, regressing → fix existing behavior
- **Feature:** New functionality, enhancements, refactoring, migrations → build or change something
- **Ambiguous:** Ask user (bundled with worktree question)

### 1.2 Read Environment & User Questions (new plans only)

**⛔ MANDATORY FIRST STEP — read env vars before ANY user interaction:**

```bash
echo "BRANCH_ISO=$PILOT_BRANCH_ISOLATION_ENABLED QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED"
```

**⛔ When `BRANCH_ISO` is `"false"`: NEVER ask about branch choice. The dispatcher invokes the planning skill immediately with `--worktree=no` (defaults to the current branch).**

**Note:** The `QUESTIONS` toggle (`PILOT_PLAN_QUESTIONS_ENABLED`) does NOT affect the branch/type questions in this dispatcher. That toggle only controls Q&A questions during planning (Steps 5/7 in spec-plan). The dispatcher-level branch question is gated entirely by `PILOT_BRANCH_ISOLATION_ENABLED`.

**Codex reviewers are controlled entirely by Console Settings.** The `PILOT_CODEX_SPEC_REVIEW_ENABLED` and `PILOT_CODEX_CHANGES_REVIEW_ENABLED` env vars are read directly by spec-plan and spec-verify — no per-session question needed.

| BRANCH_ISO | Type | Action |
|------------|------|--------|
| `false` | Clear | NO question; invoke skill with `--worktree=no` |
| `false` | Ambiguous | Ask ONLY the type question; invoke skill with `--worktree=no` |
| `true`  | Clear | Ask 3-option branch question; pass selected flag |
| `true`  | Ambiguous | Ask type + 3-option branch question (bundled); pass selected flag |

**Branch question options (only when `BRANCH_ISO` is `"true"` — use these as predefined AskUserQuestion options, listed in recommended order):**

| Option | Flag passed | Behavior |
|--------|-------------|----------|
| **Continue on current branch** (recommended) | `--worktree=no` | Works on current branch as-is |
| New branch from default branch | `--new-branch` | Creates a clean branch from origin/main (or master), checks it out, then works there |
| Use worktree (isolated branch, squash-merged after) | `--worktree=yes` | Creates isolated worktree |

**⛔ When the user selects "New branch" or sends a custom response mentioning "new branch", "clean branch", or "branch from master/main": pass `--new-branch`, NOT `--worktree=yes`.** `AskUserQuestion` allows users to type a free-text "Other" response, and previously such responses requesting a new branch were misinterpreted as worktree requests. This rule applies only when `BRANCH_ISO=true` — when off, the question is not asked.

### 1.3 Invoke Skill and STOP

- **Bugfix:** `Skill(skill='spec-bugfix-plan', args='<task_description> --worktree=yes|no|--new-branch')`
- **Feature:** `Skill(skill='spec-plan', args='<task_description> --worktree=yes|no|--new-branch')`

**Note:** Users who want a bugfix workflow without a plan file invoke `/fix` directly — that's a separate user-facing command. The `/spec` dispatcher does not route to `/fix`. When a user types `/spec`, they want the full spec workflow.
