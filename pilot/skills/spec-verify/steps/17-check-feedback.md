## Step 17: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user has left code review annotations in the Console's Changes tab. Annotations auto-save to the unified JSON — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether `codeReviewAnnotations` has any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).

**If `FEEDBACK_EXISTS`:**
1. Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `lineEnd`, `side`, and `text` (user's annotation)
2. Fix all issues raised (each annotation = a required fix at the indicated file/line)
3. Delete the annotation file: `rm -f "<annotation-file-path>"` (e.g. `rm -f "docs/plans/.annotations/2026-03-26-my-feature.json"`). By this phase, plan annotations were already consumed by `spec-plan`, so deleting the whole file is safe. Direct deletion avoids curl which is blocked in several hook environments.
4. Re-run tests and typecheck
5. Continue to Step 18

**If `NO_FEEDBACK`:** continue to Step 18.
