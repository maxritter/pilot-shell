## Step 19: Update Plan Status

### ⛔ Precondition Gate — verify ALL THREE before writing `Status: VERIFIED`

1. `AskUserQuestion` was called in **this same conversation turn flow** as part of Step 18 (not a previous, abandoned one).
2. The user's most recent reply contains one of the **explicit approve keywords**: `Approve`, `approve`, `lgtm`, `looks good`, `continue`, `proceed`.
3. That reply arrived **after** the AskUserQuestion call — not before, not as a stale message.

If any of the three is false → return to Step 18 and re-ask. Common traps that DO NOT count as approval: "no annotations in file", "all tests pass", "user has been idle", "session was resumed", "user said 'thanks'/'ok'/anything else."

**When ALL passes AND user approves:**

1. Set `Status: VERIFIED` in plan
2. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true`
3. Report completion with summary:
   ```
   ## Verification Complete
   **Issues Found:** X
   ### Goal Achievement: N/M truths verified
   ### Must Fix (N) | Should Fix (N) | Suggestions (N)
   ### Not Verified: [list items from Step 12, or "None"]
   ```

4. **Instruct the user:** Include in your completion message:
   ```
   Run /clear before starting new work — this resets context while keeping project rules loaded.
   ```

**When verification FAILS (missing features, serious bugs — before reaching Step 18):**

⛔ **Iteration cap — check BEFORE re-invoking spec-implement.** Read `Iterations:` from the plan header. If `Iterations >= 3` BEFORE incrementing, stop the verify→implement loop and surface to the user. An infinite verify→implement loop on a feature plan is the single largest token-burn pattern in the workflow — three failed verifications means the plan is wrong, not that one more implement pass will fix it.

```
AskUserQuestion(
  question="Three verify iterations have failed for this plan. This pattern usually means the plan's design is incomplete or a verify check is mis-specified — not that one more implement pass will fix it. What now?",
  options=[
    "Continue — try one more iteration (rarely the right answer)",
    "Pivot — let me re-investigate the plan with you",
    "Abandon — leave PENDING, I'll come back to it"
  ]
)
```

Handle:
- **Continue:** increment `Iterations`, write `## Verification Gaps`, register status, invoke `Skill(skill='spec-implement', args='<plan-path>')` as below.
- **Pivot:** set `Status: PENDING`, do NOT invoke spec-implement. Tell the user you're standing by for new investigation direction.
- **Abandon:** leave `Status: PENDING`, do not invoke spec-implement. Stop.

**When `Iterations < 3`:**

1. Add fix tasks to plan
2. Set `Status: PENDING`, increment `Iterations`
3. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" 2>/dev/null || true`
4. Write `## Verification Gaps` table to plan (overwrite if exists):
   ```markdown
   | Gap | Type | Severity | Affected Files | Fix Description |
   ```
5. Invoke `Skill(skill='spec-implement', args='<plan-path>')`

ARGUMENTS: $ARGUMENTS
