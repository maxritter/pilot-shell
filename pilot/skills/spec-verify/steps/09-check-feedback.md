## Step 9: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user has left code review annotations in the Console's Changes tab. Annotations auto-save to the unified JSON — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_ANNOTATIONS_FOUND`. If it exists, check whether `codeReviewAnnotations` has any entries (`ANNOTATIONS_FOUND`) or is empty/missing (`NO_ANNOTATIONS_FOUND`).

**⛔ Absence of annotations ≠ approval.** Annotations are an *optional* inline-comment channel; most users approve verbally via Step 10. Never collapse Step 9 → Step 11 because the file is missing or empty.

**If `ANNOTATIONS_FOUND`:**
1. Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `lineEnd`, `side`, and `text` (user's annotation)
2. Fix all issues raised (each annotation = a required fix at the indicated file/line)
3. Delete the annotation file: `rm -f "<annotation-file-path>"` (e.g. `rm -f "docs/plans/.annotations/2026-03-26-my-feature.json"`). By this phase, plan annotations were already consumed by `spec-plan`, so deleting the whole file is safe. Direct deletion avoids curl which is blocked in several hook environments.
4. Re-run tests and typecheck
5. Continue to Step 10

**If `NO_ANNOTATIONS_FOUND`:** continue to Step 10. **You still MUST run Step 10 (the human gate).**
