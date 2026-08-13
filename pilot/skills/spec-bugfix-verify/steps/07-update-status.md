## Step 7: Update Plan Status

### ⛔ Precondition Gate — verify ALL THREE before writing `Status: VERIFIED`

1. The Step 6 gate **was actually put to the user** in **this same conversation turn flow** (not a previous, abandoned one) — by `AskUserQuestion`, or, for an agent that cannot emit it, by the prose ask + yield in `agent-gate-protocol.md`. What matters is that the question was asked and the turn ended so it could be answered; *which* mechanism asked it is not the test. (An agent with no `AskUserQuestion` can never satisfy a tool-presence check, which would make `VERIFIED` unreachable for an orchestration lane no matter how legitimately the gate was answered.)
2. The user's most recent reply contains one of the **explicit approve keywords**: `Approve`, `approve`, `lgtm`, `looks good`. (A bare `continue`/`proceed` is a resume nudge, NOT approval.)
3. That reply arrived **after** the AskUserQuestion call — not before, not as a stale message.

If any of the three is false → return to Step 6 and re-ask. Common traps that DO NOT count as approval: "no annotations in file", "all tests pass", "user has been idle", "session was resumed", "user said 'thanks'/'ok'/anything else."

**All passes and user approves:** Set `Status: VERIFIED`, register:
```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" $LANE_FLAG 2>/dev/null || true
```

> **`$LANE_FLAG`** is `--lane <id>` when this run was dispatched as an orchestration lane, and **nothing at all** otherwise — the value the planning phase parsed from its arguments. It keeps the registration in `sessions/<id>/lanes/<lane>/` rather than the coordinator's single slot, which is what stops a lane's plan blocking the coordinator's stop guard (issue #174). Skills build into separate SKILL.md files, so this is restated wherever the placeholder is used.

Report:
```
Bugfix verified — regression test passes, full suite green.
Run /clear before starting new work — this resets context while keeping project rules loaded.
```

**Fails:**

⛔ **Iteration cap.** Read `Iterations:` from the plan header. If `Iterations >= 3` BEFORE incrementing, stop the fix-on-fix loop:

<!-- CC-ONLY -->
```
AskUserQuestion(
  question="Three fix iterations have failed verification. This pattern usually means the bug is architectural — fixing symptoms in different places, each fix revealing a new failure mode. What now?",
  options=[
    "Continue — try one more fix (rarely the right answer)",
    "Pivot — let me re-investigate root cause with you",
    "Abandon — leave PENDING, I'll come back to it"
  ]
)
```
<!-- /CC-ONLY -->
<!-- CODEX-START
Present these numbered options and wait for user response:

1. Continue — try one more fix (rarely the right answer)
2. Pivot — let me re-investigate root cause with you
3. Abandon — leave PENDING, I'll come back to it
CODEX-END -->

Handle:
<!-- CC-ONLY -->
- **Continue:** **set `Status: PENDING`**, add fix tasks, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')` as below. (Do NOT hand a `Status: COMPLETE` plan to spec-implement.)
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Continue:** **set `Status: PENDING`**, add fix tasks, increment `Iterations`, then continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path>`. (Do NOT hand a `Status: COMPLETE` plan to spec-implement.)
CODEX-END -->
- **Pivot:** set `Status: PENDING`, do NOT invoke spec-implement. Tell the user you're standing by for new investigation direction.
- **Abandon:** leave `Status: PENDING`, do not invoke spec-implement. Stop.

<!-- CC-ONLY -->
**When `Iterations < 3`:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`.
<!-- /CC-ONLY -->
<!-- CODEX-START
**When `Iterations < 3`:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, then continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path>`.
CODEX-END -->

ARGUMENTS: $ARGUMENTS
