## Step 6: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"`:**

0. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```
1. Summarize: symptom → root cause → fix approach → task structure
2. AskUserQuestion:
   - "Yes, proceed" — Approve as-is and start spec-implement
   - "No, I have feedback" — I've annotated in the Console or edited the plan file; process my feedback

   The user can pause at this prompt, annotate in the Console's Specifications tab (auto-saves), or edit the plan file directly, then pick option 2. No "ready" handshake required.
3. **Yes:** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **No, I have feedback:** Re-run Step 5 (process Console annotations), re-read the plan file (in case the user edited it), then return to Step 6 and ask again.
   **Other free-text feedback:** Incorporate the changes into the plan, then re-ask with a fresh AskUserQuestion.
