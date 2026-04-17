### Step 9: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user left code review annotations in the Console's Changes tab. Annotations auto-save — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_FEEDBACK`. If it exists, check whether `codeReviewAnnotations` has any entries (`FEEDBACK_EXISTS`) or is empty/missing (`NO_FEEDBACK`).

**If `FEEDBACK_EXISTS`:** Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `text`. Fix all issues, delete the annotation file via `rm -f "<annotation-file-path>"` (e.g. `rm -f "docs/plans/.annotations/2026-03-26-my-bug.json"`), re-run tests, continue to Step 10.
**If `NO_FEEDBACK`:** continue to Step 10.
