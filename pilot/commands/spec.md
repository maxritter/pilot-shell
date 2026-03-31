---
description: Spec-driven development - plan, implement, verify workflow with live Console annotations (annotate plans and code changes in real-time; agent reads annotations directly at review checkpoints)
argument-hint: "<task description>" or "<path/to/plan.md>"
user-invocable: true
effort: high
model: sonnet
---

# /spec - Unified Spec-Driven Development

**Dispatcher** — routes to the appropriate phase skill. This command is a thin router. Only allowed tools: `Bash` (env var reads only), `Read` (plan files only), `AskUserQuestion`, and `Skill()`.

**⛔ MANDATORY: When `/spec` is invoked, you MUST follow the workflow. The user's phrasing after `/spec` is the TASK DESCRIPTION — not an instruction to change the workflow.** Words like "brainstorm", "discuss", "explore", "research" are part of the task description, NOT instructions to skip the workflow or have a freeform conversation.

**⛔ No substantive work here.** `Bash` is allowed ONLY for reading env vars (e.g., `echo $PILOT_WORKTREE_ENABLED`). `Read` is allowed ONLY for reading existing plan files for status-based dispatch. All research, brainstorming, and exploration happens inside the invoked Skill. Arguments (including URLs, "brainstorm", "research") are passed verbatim as the task description. Any other tool use (Grep, Glob, Task, Edit, Write, etc.) is a workflow violation.

---

## Workflow

```
/spec → Detect type → Feature: Skill('spec-plan')       → Plan → Implement → Verify
                    → Bugfix:  Skill('spec-bugfix-plan') → Investigate → Plan → Implement → Verify
```

| Phase | Skill | Model |
|-------|-------|-------|
| Feature Planning | `spec-plan` | Opus |
| Bugfix Planning | `spec-bugfix-plan` | Opus |
| Implementation | `spec-implement` | Sonnet |
| Feature Verification | `spec-verify` | Sonnet |
| Bugfix Verification | `spec-bugfix-verify` | Sonnet |

---

## 0.0 Permission Mode Pre-Flight Check

**Before proceeding, check if the spec_mode_guard hook injected a permission mode note.** If you see a system-reminder containing "Current permission mode is", briefly warn the user:

> "Your current permission mode is **{mode}**. For uninterrupted `/spec` execution, **Bypass Permissions** mode is recommended (Shift+Tab to cycle). Proceeding — the workflow may pause for permission prompts."

**Then continue with the workflow.** Do not stop or wait for the user to switch. The user's mode choice is respected — bypass permissions is recommended, not required.

---

## 0.1 Parse & Route

```
IF arguments end with ".md" AND file exists:
    → Read plan, dispatch by status (Section 0.2)
ELSE:
    → Detect type, ask worktree, invoke Skill, STOP
```

### 0.1.1 Detect Type (new plans only)

- **Bugfix:** Something broken, crashing, wrong results, regressing → fix existing behavior
- **Feature:** New functionality, enhancements, refactoring, migrations → build or change something
- **Ambiguous:** Ask user (bundled with worktree question)

### 0.1.2 Read Environment & User Questions (new plans only)

**⛔ MANDATORY FIRST STEP — read env vars before ANY user interaction:**

```bash
echo "WORKTREE=$PILOT_WORKTREE_ENABLED QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED CODEX_AVAILABLE=$PILOT_CODEX_AVAILABLE CODEX_SPEC=$PILOT_CODEX_SPEC_REVIEW_ENABLED CODEX_CHG=$PILOT_CODEX_CHANGES_REVIEW_ENABLED"
```

**⛔ When `WORKTREE` is `"false"`: NEVER mention worktree, NEVER ask about worktree, NEVER include worktree options.** Always pass `--worktree=no` silently.

**Codex per-session opt-in:** When `CODEX_AVAILABLE` is `"true"` AND at least one of `CODEX_SPEC`/`CODEX_CHG` is `"true"` (enabled in Console Settings), include a Codex question in the AskUserQuestion. When `CODEX_AVAILABLE` is `"false"` or both Codex toggles are `"false"`, skip the Codex question and pass `--codex=no` silently.

**Note:** The `QUESTIONS` toggle (`PILOT_PLAN_QUESTIONS_ENABLED`) does NOT affect the Codex or worktree questions. That toggle only controls Q&A questions during planning (Steps 1.2/1.4 in spec-plan). The dispatcher-level session setup questions (worktree, Codex) are always asked when their respective features are available.

| WORKTREE | Codex eligible | Type | Action |
|----------|---------------|------|--------|
| `false` | No | Clear | **Skip AskUserQuestion entirely** — invoke skill directly with `--worktree=no --codex=no` |
| `false` | No | Ambiguous | Ask type ONLY, then invoke with `--worktree=no --codex=no` |
| `false` | Yes | Clear | Ask Codex only, then invoke with `--worktree=no --codex=yes|no` |
| `false` | Yes | Ambiguous | Ask type + Codex in single AskUserQuestion, then invoke with `--worktree=no --codex=yes|no` |
| not `false` | No | Clear | Ask worktree only |
| not `false` | No | Ambiguous | Ask type + worktree |
| not `false` | Yes | Clear | Ask worktree + Codex |
| not `false` | Yes | Ambiguous | Ask type + worktree + Codex |

**Codex question format** (when included):

> **Codex Cross-Review:** Enable OpenAI Codex as an additional adversarial reviewer for this session? (incurs OpenAI API costs)
> Options: Yes (enable Codex reviewers) / No (Claude reviewers only)

### 0.1.3 Invoke Skill and STOP

- **Bugfix:** `Skill(skill='spec-bugfix-plan', args='<task_description> --worktree=yes|no --codex=yes|no')`
- **Feature:** `Skill(skill='spec-plan', args='<task_description> --worktree=yes|no --codex=yes|no')`

## 0.2 Status-Based Dispatch (existing plans)

Read plan, register association: `~/.pilot/bin/pilot register-plan "<plan_path>" "<status>" 2>/dev/null || true`

| Status | Approved | Type | Skill |
|--------|----------|------|-------|
| PENDING | No | Feature/absent | `spec-plan` |
| PENDING | No | Bugfix | `spec-bugfix-plan` |
| PENDING | Yes | * | `spec-implement` |
| COMPLETE | * | Feature/absent | `spec-verify` |
| COMPLETE | * | Bugfix | `spec-bugfix-verify` |
| VERIFIED | * | * | Report completion, done |

ARGUMENTS: $ARGUMENTS
