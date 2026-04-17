---

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
echo "WORKTREE=$PILOT_WORKTREE_ENABLED QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED"
```

**⛔ When `WORKTREE` is `"false"`: NEVER mention worktree, NEVER ask about worktree, NEVER include the worktree option.** Still ask about branch choice (current branch vs new branch).

**Note:** The `QUESTIONS` toggle (`PILOT_PLAN_QUESTIONS_ENABLED`) does NOT affect the branch/worktree question. That toggle only controls Q&A questions during planning (Steps 5/7 in spec-plan). The dispatcher-level branch question is always asked.

**Codex reviewers are controlled entirely by Console Settings.** The `PILOT_CODEX_SPEC_REVIEW_ENABLED` and `PILOT_CODEX_CHANGES_REVIEW_ENABLED` env vars are read directly by spec-plan and spec-verify — no per-session question needed.

| WORKTREE | Type | Action |
|----------|------|--------|
| `false` | Clear | Ask branch choice only (2 options: current branch, new branch — NO worktree) |
| `false` | Ambiguous | Ask type + branch choice (2 options — NO worktree) |
| not `false` | Clear | Ask branch choice (all 3 options including worktree) |
| not `false` | Ambiguous | Ask type + branch choice (all 3 options) |

**Branch/worktree question options (use these as predefined AskUserQuestion options — listed in recommended order):**

When `WORKTREE` is `"false"` (2 options):

| Option | Flag passed | Behavior |
|--------|-------------|----------|
| **Continue on current branch** (recommended) | `--worktree=no` | Works on current branch as-is |
| New branch from default branch | `--new-branch` | Creates a clean branch from origin/main (or master), checks it out, then works there |

When `WORKTREE` is not `"false"` (3 options):

| Option | Flag passed | Behavior |
|--------|-------------|----------|
| **Continue on current branch** (recommended) | `--worktree=no` | Works on current branch as-is |
| New branch from default branch | `--new-branch` | Creates a clean branch from origin/main (or master), checks it out, then works there |
| Use worktree (isolated branch, squash-merged after) | `--worktree=yes` | Creates isolated worktree |

**⛔ When the user selects "New branch" or sends a custom response mentioning "new branch", "clean branch", or "branch from master/main": pass `--new-branch`, NOT `--worktree=yes`.** Custom responses requesting a new branch were previously misinterpreted as worktree requests.

### 0.1.3 Invoke Skill and STOP

- **Bugfix:** `Skill(skill='spec-bugfix-plan', args='<task_description> --worktree=yes|no|--new-branch')`
- **Feature:** `Skill(skill='spec-plan', args='<task_description> --worktree=yes|no|--new-branch')`
