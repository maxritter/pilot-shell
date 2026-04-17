## Step 8: Re-verification (Only for Structural Fixes)

**⛔ If `PILOT_CHANGES_REVIEW_ENABLED` is `"false"` (from Step 0 — Steps 4/7 were skipped),** skip this step entirely and proceed to Phase B.

**When enabled:** **Skip** when fixes were localized (terminology, error handling, test updates, minor bugs). Run tests + lint to confirm, proceed to Phase B.

**Re-verify** when fixes required new functionality, changed APIs, or significant new code paths: re-launch changes-review, fix new findings. Max 2 iterations before adding remaining issues to plan.
