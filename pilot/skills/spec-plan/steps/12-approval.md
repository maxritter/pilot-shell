## Step 12: Get User Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"` (from Step 0),** skip this step: set `Approved: Yes` in the plan file automatically and immediately invoke `Skill(skill='spec-implement', args='<plan-path>')`. No AskUserQuestion, no notification.

**When `PILOT_PLAN_APPROVAL_ENABLED` is NOT `"false"` — MANDATORY APPROVAL GATE:**

0. Notify:

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Plan Ready for Review" "<plan_name> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
   ```

1. Summarize: goal, key tasks, approach

2. AskUserQuestion:
   - "Yes, proceed with implementation" — Approve as-is and start spec-implement (TDD loop)
   - "No, I have feedback" — I've annotated in the Console or edited the plan file; process my feedback

   The user can pause at this prompt, annotate in the Console's Specifications tab (annotations auto-save), or edit the plan file directly, then pick option 2. No "ready" handshake required.

   Note: `Worktree:` field was already set at creation time (Step 2). Do NOT ask again here.

3. **If "Yes":** Set `Approved: Yes`, invoke `Skill(skill='spec-implement', args='<plan-path>')`
   **If "No, I have feedback":** Re-run Step 11 (process Console annotations), re-read the plan file (in case the user edited it directly), then return to Step 12 and ask again.
   **If other free-text feedback (config values, threshold changes, clarifications):** This is NOT approval — incorporate the changes into the plan, then re-ask with a fresh AskUserQuestion.

ARGUMENTS: $ARGUMENTS
