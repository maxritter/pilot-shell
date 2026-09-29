## Step 11: Update Plan Status

### Approval and evidence precondition

Before `Status: VERIFIED`, confirm:

1. The current reviewable result was presented through Step 10's permitted question mechanism.
2. The user explicitly approved that result after it was presented, or supplied applicable standing authorization.
3. No later code change or unresolved feedback invalidated that approval, and the required verification evidence still applies.

Preserve valid approval across turns and compaction. Do not require that the approval be the latest conversational message or match a fixed keyword list. An unrelated reply, bare resume nudge, silence, hook output, or passing tests is not approval. If required approval is missing, return to Step 10.

**When ALL passes AND user approves:**

1. Set `Status: VERIFIED` in plan
2. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" $LANE_FLAG 2>/dev/null || true`

> **`$LANE_FLAG`** is `--lane <id>` when this run was dispatched as an orchestration lane, and **nothing at all** otherwise — the value the planning phase parsed from its arguments. It keeps the registration in `sessions/<id>/lanes/<lane>/` rather than the coordinator's single slot, which is what stops a lane's plan blocking the coordinator's stop guard (issue #174). Skills build into separate SKILL.md files, so this is restated wherever the placeholder is used.

3. Re-check any Goal Verification truth that was pending only on final status. At minimum, grep the plan header for `^Status: VERIFIED$`; if a truth also references task checkboxes or artifacts, re-check those exact paths/lines before reporting it verified.
4. Report completion with summary:
   ```
   ## Verification Complete
   **Issues Found:** X
   ### Goal Achievement: N/M truths verified
   ### Must Fix (N) | Should Fix (N) | Suggestions (N) | Out-of-lineage mentions (N)
   ### Docs: [files updated in Step 6.2, or "no doc impact"]
   ### Not Verified: [list items from Step 6.3, or "None"]
   ```

5. **Instruct the user:** Include in your completion message:
   ```
   Start a fresh context for unrelated work when useful; preserve this run's evidence and state.
   ```

**When verification FAILS (missing features, serious bugs — before reaching Step 10):**

### Failed verification: diagnose and continue

At each failed verification evaluation, read `~/.pilot/config.json` fresh with the current runtime's native file-reading tool. Only JSON boolean `true` at `specWorkflow.runawayGuard` enables stalled verification checkpoints. Missing, unreadable, or malformed config, a missing key, or a non-boolean value means **off**. `Iterations:` records loop history; it never imposes an attempt cap.

- **Default (off):** Diagnose the failure, choose the next evidence-backed fix within the authorized scope, and continue automatically. New evidence narrowing failing scenarios, a newly confirmed root cause, or a fix advancing a goal criterion are meaningful progress. Record the current unresolved evidence and progress in the plan for comparison with the next evaluation; repeated output, cosmetic edits, and restated plans are not progress. Repeated failures require better investigation, not a routine permission question.
- **Enabled:** Ask a stalled-work checkpoint only when repeated failed verification has the same unresolved evidence and no meaningful progress. Continue while diagnosis or fixes make progress, regardless of the iteration count.
- **Running jobs:** Retain their handles and wait autonomously while builds, tests, deployments, or agents are still running. Elapsed time or a polling timeout alone never triggers a checkpoint or a "keep waiting?" question.
- **Required decisions:** Either setting still requires actual missing input for a true blocker or material scope choice, and preserves the review approval gate. Complete independent authorized work first. Ask once about the concrete blocker or choice and keep that decision pending across turns and compaction; do not repeat it while awaiting the answer.

For a required decision or an enabled stalled-work checkpoint, first set/register `Status: PENDING` and run `~/.pilot/bin/pilot plan-state pause --kind decision --message "<concrete question>" $LANE_FLAG`. Use the runtime's permitted question transport and `$HOME/.pilot/agents/agent-gate-protocol.md`; lanes relay unresolved decisions to their coordinator. Preserve the pending question until answered. A clear answer authorizing continuation resolves the decision: run `pilot plan-state resume $LANE_FLAG` and continue immediately, without another confirmation or a standalone resume request. A user-requested direction change or stop follows that actual choice.

**Automatic loop-back (or authorized continuation after a resolved decision):**

1. Add fix tasks to plan
2. Set `Status: PENDING`, increment `Iterations`
3. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "PENDING" $LANE_FLAG 2>/dev/null || true`
4. Write `## Verification Gaps` table to plan (overwrite if exists):
   ```markdown
   | Gap | Type | Severity | Affected Files | Fix Description |
   ```
<!-- CC-ONLY -->
5. Invoke `Skill(skill='spec-implement', args='<plan-path> $LANE_FLAG')`
<!-- /CC-ONLY -->
<!-- CODEX-START
5. Continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path> $LANE_FLAG`.
CODEX-END -->

ARGUMENTS: $ARGUMENTS
