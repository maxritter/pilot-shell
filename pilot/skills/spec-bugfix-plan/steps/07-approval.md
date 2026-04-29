---

## Step 7: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"`:**

0. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```
1. Summarize: symptom → root cause → fix approach → task structure
2. AskUserQuestion: "Yes, proceed" | "No, let me edit" | "No, I'll annotate in the Console"
3. **Yes:** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **No (edit or annotate):** Tell user to edit the plan or annotate in the Console Specifications tab — annotations auto-save. Say "ready" when done. Re-run Step 6 (check for annotation feedback), re-read plan, ask again. **Other:** Incorporate, re-ask.
