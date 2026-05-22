---
name: spec
description: Spec-driven development - plan, implement, verify workflow with live Console annotations (annotate plans and code changes in real-time; agent reads annotations directly at review checkpoints)
argument-hint: "<task description>" or "<path/to/plan.md>"
user-invocable: true
---

# /spec - Unified Spec-Driven Development

**Dispatcher** — routes to the appropriate phase skill. This command is a thin router. Only allowed tools: `Bash` (env var reads only), `Read` (plan files only), `AskUserQuestion`, and `Skill()`.

**⛔ MANDATORY: When `/spec` is invoked, you MUST follow the workflow. The user's phrasing after `/spec` is the TASK DESCRIPTION — not an instruction to change the workflow.** Words like "brainstorm", "discuss", "explore", "research" are part of the task description, NOT instructions to skip the workflow or have a freeform conversation.

**⛔ No substantive work here.** `Bash` is allowed ONLY for reading env vars (e.g., `echo $PILOT_BRANCH_ISOLATION_ENABLED`). `Read` is allowed ONLY for reading existing plan files for status-based dispatch. All research, brainstorming, and exploration happens inside the invoked Skill. Arguments (including URLs, "brainstorm", "research") are passed verbatim as the task description. Any other tool use (Grep, Glob, Task, Edit, Write, etc.) is a workflow violation.

---

## Workflow

```
/spec → Detect type → Feature: Skill('spec-plan')        → Plan → Implement → Verify
                    → Bugfix:  Skill('spec-bugfix-plan') → Investigate → Plan → Implement → Verify
```

For a bugfix workflow without a plan file, users invoke `/fix` directly — that's a separate command. `/spec` always runs the full spec workflow.

| Phase | Skill | Model |
|-------|-------|-------|
| Feature Planning | `spec-plan` | inherits `/model` (recommend Opus) |
| Bugfix Planning | `spec-bugfix-plan` | inherits `/model` (recommend Opus) |
| Implementation | `spec-implement` | inherits `/model` |
| Feature Verification | `spec-verify` | inherits `/model` |
| Bugfix Verification | `spec-bugfix-verify` | inherits `/model` |
| Bugfix (separate command, `/fix`) | `fix` | inherits `/model` |

> **Note:** Every phase runs on the model the user has currently selected via Claude Code's `/model` command. The `spec-mode-guard` hook blocks `/spec` invocations when the active model is not Opus (planning's reasoning hop benefits most from Opus). With the **Model Switching** toggle ON (default), the planner stops after approval so you can run `/model <sonnet|sonnet[1m]|opus|opus[1m]>` and then type any prompt (e.g. `continue`) to resume — the `spec_handoff_resume` hook routes the next prompt directly to `spec-implement`, with no `/clear` and no `/spec <plan-path>` re-invocation. With it OFF, plan → implement → verify run continuously on whichever model is active. Sub-agents (`spec-review`, `changes-review`, `web-search-agent`) are hard-coded to Sonnet because sub-agents do not support 1M context.
