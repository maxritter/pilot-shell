---
name: spec-implement
description: "Spec implementation phase - TDD loop for each task in the plan"
argument-hint: "<path/to/plan.md>"
user-invocable: false
effort: high
model: sonnet
---

# /spec-implement - Implementation Phase

**Phase 2 of the /spec workflow.** Reads approved plan, implements each task using TDD (Red → Green → Refactor).

**Input:** Approved plan file (`Approved: Yes`)
**Output:** All tasks completed, status → COMPLETE
**Next:** Verify phase (type-aware: `spec-verify` for features, `spec-bugfix-verify` for bugfixes)

---

## ⛔ Critical Constraints

- **NO sub-agents** — all tasks execute sequentially in main context
- **TDD is MANDATORY** — no production code without failing test first
- **NEVER SKIP TASKS** — every task must be fully implemented, no "MVP scope" exceptions
- **Quality over speed** — never rush due to context pressure. Context warnings are informational. Finish current task with full quality — auto-compaction handles the rest.
- **Plan file is source of truth** — re-read after auto-compaction, don't rely on conversation memory
- **NEVER stop during implementation** — the stop guard blocks premature exits. If blocked: your very next action must be a tool call (TaskList, Read plan, or code change). After user interruptions or "Continue" messages: re-read the plan and resume from the current task. Never produce text-only responses when work remains.

---

## Feedback Loop Awareness

This phase may be called multiple times:
```
spec-implement → spec-verify → issues found → spec-implement → ...
```
When called after verification: read plan, check `Iterations` field, report "Starting Iteration N...", focus on uncompleted `[ ]` tasks (look for `[MISSING]` markers from verification).
