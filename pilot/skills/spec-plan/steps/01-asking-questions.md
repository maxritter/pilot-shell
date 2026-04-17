---

## Step 1: Asking User Questions

**⛔ If `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"` (from Step 0),** skip ALL `AskUserQuestion` calls in Steps 5 and 7. Make reasonable default choices (including selecting the recommended approach in Step 7) and document them in the plan under an "Autonomous Decisions" sub-section. Continue to the next step immediately.

**⛔ ALWAYS use the `AskUserQuestion` tool** (when questions are enabled) — never list numbered questions in plain text. Each question gets its own entry with predefined options users can select. This provides a structured form UI that is much easier to answer than freeform numbered lists.

**⛔ Default is to ASK, not skip.** Every plan benefits from at least one round of user alignment. Only skip questions when the task is a single-file change with zero ambiguity.

**Questions batched into max 2 interactions:** Batch 1 (before exploration) clarifies task/scope/priorities. Batch 2 (after exploration) covers approach selection and design decisions. **Both batches are expected for most tasks** — skipping both is the exception, not the norm.

**Principles:** Present options with trade-offs (not open-ended). Start open, narrow down. Challenge vagueness — make abstract concrete. 1-2 focused questions beat 4 vague ones. Questions clarify HOW to implement, not whether to expand scope.
