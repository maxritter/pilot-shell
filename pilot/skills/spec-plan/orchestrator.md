---
name: spec-plan
description: "Planning phase of the /spec feature workflow — owns the plan file until the user approves it. Entered for a new feature task, or for an existing plan still marked Status: PENDING and Approved: No."
argument-hint: "<task description> or <path/to/plan.md>"
user-invocable: false
hooks:
  Stop:
    - command: uv run --no-project --python python3 python "$HOME/.pilot/hooks/spec_plan_validator.py"
---

# /spec-plan - Planning Phase

**Phase 1 of the /spec workflow.** Explores codebase, designs implementation plan, verifies it, gets user approval.

**Input:** Task description (new) or plan path (continue unapproved)
**Output:** Approved plan at `docs/plans/YYYY-MM-DD-<slug>.md`
<!-- CC-ONLY -->
**Next:** On approval → `Skill(skill='spec-implement', args='<plan-path>')`
<!-- /CC-ONLY -->
<!-- CODEX-START
**Next:** On approval → continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path>`.
CODEX-END -->

---

## ⛔ Critical Constraints

<!-- CC-ONLY -->
- **NO writing sub-agents during planning.** Read-only fan-out is allowed: the Step 5.3 `Explore`/`general-purpose` survey subagents, and the Step 10 `spec-review` reviewer (when enabled in settings). No sub-agent may edit or write files.
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Use bounded read-only agents for independent planning questions.** Give each agent a distinct surface and evidence request; the main thread owns the plan file and all design decisions. Run the managed `spec-review` agent in Step 10 when enabled.
CODEX-END -->
- **Run spec-review when enabled** — it runs for every feature spec when `$PILOT_SPEC_REVIEW_ENABLED` is not `"false"`. Context level is NOT a valid reason to skip. To disable, use Console Settings → Reviewers → Spec Review toggle.
- **NEVER write code during planning** — planning and implementation are separate phases
- **NEVER assume — verify by reading files**
- **ONLY stopping point is plan approval** — everything else is automatic. Never ask "Should I fix these?"
- **Re-read plan after user edits** — before asking for approval again
- **Plan file is source of truth** — survives across auto-compaction cycles
- **⛔ No workflow narration** — never output text describing what step you are about to execute ("I'm scanning the workspace…", "I'm creating the plan header…", "The harness injected a reminder…"). Just do the work. The user sees tool calls and the final plan, not a running commentary.
<!-- CC-ONLY -->
- **Quality over speed** — never rush due to context pressure
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Bounded quality** — do enough verification to make the plan actionable, then draft it.
CODEX-END -->

<!-- CODEX-START

### Codex Planning Speed Contract

For Codex, quality means enough verified context to write an implementable plan, not exhaustive research. This block overrides broader "always" and "mandatory" exploration language in this skill and in the rules when they conflict.

- Reach a first complete plan draft before context reaches 35%.
- **Planning context ceiling — total planning must not exceed ~55% of the context window (hard cap 60%).** The 35% target above is the *first-draft* budget; the remaining headroom is for self-review, annotation processing, and refinement — NOT more exploration. On the ~256K Codex window that is ≈140K tokens. If context approaches ~55% before approval, STOP all exploration and refinement and finalize the plan immediately with what you have; push remaining detail into per-task DoD for implementation to resolve. Crossing the ceiling means the plan is too granular — trim scope, do not keep researching. Implementation needs the larger share of the window, so planning that eats >60% has already failed.
- Use a bounded scan: at most one CodeGraph orientation call when runtime-code structure is unknown, plus one Semble intent search at most before asking or choosing. If either result is irrelevant, pivot immediately to direct file reads. Skip CodeGraph for docs, rules, markdown, config, UI copy, reviews of a known diff, or named paths.
- Ask at most one clarification/design batch before approval. If you can make a reversible assumption, document it under "Assumptions" or "Autonomous Decisions" and continue.
- Stop exploration once you can name the files, commands, tests, and user-visible checks for each task. Leave implementation-time details to task DoD.
CODEX-END -->
