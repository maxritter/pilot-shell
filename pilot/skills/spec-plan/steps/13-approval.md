## Step 13: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"` — MANDATORY APPROVAL GATE:**

0. Notify:

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Plan Ready for Review" "<plan_name> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```

1. Summarize: goal, key tasks, approach

2. AskUserQuestion:
   - "Yes, proceed with implementation" — I've reviewed and it looks good
   - "No, I need to make changes" — Let me edit the plan file first
   - "No, I'll annotate in the Console" — I'll use the Specifications tab to mark up the plan visually

   Note: `Worktree:` field was already set at creation time (Step 4). Do NOT ask again here.

3. **If "Yes":** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **If "No, I need to make changes":** Tell user to edit plan directly or annotate in the Console's Specifications tab (annotations auto-save — no button needed), then say "ready". Wait. Re-run Step 12 (check for annotation feedback), re-read plan, ask again
   **If "No, I'll annotate in the Console":** Tell user to annotate in the Console Specifications tab — annotations save automatically as they type. Say "ready" when done. Wait. Re-run Step 12, re-read plan, ask again
   **If other feedback (config values, threshold changes, clarifications):** This is NOT approval — incorporate changes into plan, then re-ask with fresh AskUserQuestion.

ARGUMENTS: $ARGUMENTS
