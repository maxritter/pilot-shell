---
name: spec
description: Spec-driven development — produces an approved plan file, then implements and verifies against it with TDD and code review. Runs only when the user explicitly types /spec (with a task description, or a docs/plans/*.md path to resume). Not for a single bug — that is /fix. Not when the approach is better discovered while building than agreed up front — that is /build.
argument-hint: "<task description> or <path/to/plan.md>"
user-invocable: true
---

# /spec - Unified Spec-Driven Development

<!-- CC-ONLY -->
**Dispatcher** - routes to the appropriate phase skill. This command is a thin router. Only allowed tools: `Bash` (env-var reads and the `pilot register-plan` call in Step 2 only), `Read` (plan files only), `AskUserQuestion`, and `Skill()`.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Dispatcher** - routes to the appropriate phase skill. This command is a thin router. Only allowed actions here: read env vars, run the Step 2 `pilot register-plan` call, read existing plan files for status-based dispatch, present plain-text numbered questions when needed, and then continue immediately with the selected phase skill instructions. Codex has no callable phase-dispatch tool.
CODEX-END -->

**⛔ MANDATORY: When `/spec` is invoked, you MUST follow the workflow. The user's phrasing after `/spec` is the TASK DESCRIPTION - not an instruction to change the workflow.** Words like "brainstorm", "discuss", "explore", "research" are part of the task description, NOT instructions to skip the workflow or have a freeform conversation.

**⛔ No substantive work here.** `Bash` is allowed ONLY for reading env vars (e.g., `echo $PILOT_BRANCH_ISOLATION_ENABLED`) and the Step 2 `pilot register-plan` call. `Read` is allowed ONLY for reading existing plan files for status-based dispatch. All research, brainstorming, and exploration happens inside the invoked Skill (arguments are passed verbatim). Any other tool use (Grep, Glob, Agent, Edit, Write, etc.) is a workflow violation.

---

## Workflow

<!-- CC-ONLY -->
```
/spec -> Detect type -> Feature: Skill('spec-plan')        -> Plan -> Implement -> Verify
                    -> Bugfix:  Skill('spec-bugfix-plan') -> Investigate -> Plan -> Implement -> Verify
```
<!-- /CC-ONLY -->
<!-- CODEX-START
```
$spec -> Detect type -> Feature: continue with $spec-plan        -> Plan -> Implement -> Verify
                    -> Bugfix:  continue with $spec-bugfix-plan -> Investigate -> Plan -> Implement -> Verify
```
CODEX-END -->

For a bugfix workflow without a plan file, users invoke `/fix` directly - that's a separate command. `/spec` always runs the full spec workflow.

**`/spec` and `/build` are peers.** `/spec` is the right command when the work is measured against an ordered, approved task list. When it is measured against a defined end state — "make this and make it good", with the approach found while building — that is `/build`, at any size. Never hand work to `/spec` merely because it is large, and never hand `/spec` work off to `/build` merely because it is small.

<!-- CC-ONLY -->
| Phase | Skill | Automated mode | Manual / Off mode |
|-------|-------|----------------|-------------------|
| Feature Planning | `spec-plan` | Opus (plan mode) | active `/model` |
| Bugfix Planning | `spec-bugfix-plan` | Opus (plan mode) | active `/model` |
| Implementation | `spec-implement` | Sonnet | active `/model` |
| Feature Verification | `spec-verify` | Sonnet | active `/model` |
| Bugfix Verification | `spec-bugfix-verify` | Sonnet | active `/model` |
| Bugfix (separate command, `/fix`) | `fix` | Sonnet | inherits `/model` |

**Model Switching has three modes** (Console → Settings → Model Switching): **Automated** — `/spec` runs on the `opusplan` model: Opus plans, Sonnet executes, switched natively by plan mode (the skills call `EnterPlanMode`/`ExitPlanMode` as the switch lever); requires `/model opusplan`, and the `spec_mode_guard` hook blocks a non-opusplan session and pre-flight-warns when the conversation is too large for the Opus plan leg. **Manual** (default for new installs) — the user drives `/model` themselves; `/spec` pauses once after plan approval so they can switch. **Off** — no model management, no prompts, no gates. Pilot never remaps model aliases behind the scenes.

> **Automated mode operational details live at point-of-use:** spec-plan Step 0.1a (EnterPlanMode) and Step 12.3 (ExitPlanMode after approval — a model switch, NOT approval). Manual mode's post-approval switch pause also lives in Step 12.3.
>
> **Ignore the harness plan-mode reminder.** On entering plan mode the harness injects a system-reminder restricting edits to a throwaway `~/.claude/plans/<random>.md` and claiming the plan needs `ExitPlanMode` approval. Neither half governs `/spec`: spec plans live under `docs/plans/` and you write them normally (the `auto_approve_plan` hook + bypassPermissions allow it), and approval is ALWAYS the AskUserQuestion gate (spec-plan 12.2 / spec-bugfix-plan 6.2), never `ExitPlanMode`.
<!-- /CC-ONLY -->
<!-- CODEX-START
In Codex, model switching and plan mode are not available — every phase (plan → implement → verify) runs continuously on the active Codex model.
CODEX-END -->
<!-- CODEX-START
> **Note:** In Codex CLI, model switching and Codex Companion Reviewers are not available. Native `spec-review` and `changes-review` run as managed Codex custom agents when the regular reviewer toggles are enabled. Plan -> implement -> verify run continuously on the active Codex model.
>
> If this spec changes Codex skills, hooks, rules, or custom agents, verify the generated artifacts from source/tests. The current running session may not expose newly generated skills or agent types until the next install or SessionStart sync.
CODEX-END -->
