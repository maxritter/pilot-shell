## Step 5: Check for Code Review Feedback

**Run BEFORE marking VERIFIED.** Check if the user left code review annotations in the Console's Changes tab. Annotations auto-save — no "Send Feedback" button needed.

Derive the annotation file path: `docs/plans/.annotations/<plan-filename>.json` (same basename as the plan, `.json` extension).

Read the annotation file with the Read tool. If the file doesn't exist, treat as `NO_ANNOTATIONS_FOUND`. If it exists, check whether `codeReviewAnnotations` has any entries (`ANNOTATIONS_FOUND`) or is empty/missing (`NO_ANNOTATIONS_FOUND`).

**⛔ Absence of annotations ≠ approval.** Annotations are an *optional* inline channel; most users approve verbally via Step 6. Never collapse Step 5 → Step 7 because the file is missing or empty.

**If `ANNOTATIONS_FOUND`:** Each annotation in `codeReviewAnnotations` has `filePath`, `lineStart`, `text`. Fix all issues, delete the annotation file via `rm -f "<annotation-file-path>"` (e.g. `rm -f "docs/plans/.annotations/2026-03-26-my-bug.json"`), re-run tests, continue to Step 6.
**If `NO_ANNOTATIONS_FOUND`:** continue to Step 6. **You still MUST run Step 6 (the human gate).**
