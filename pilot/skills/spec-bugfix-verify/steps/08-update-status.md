## Step 8: Update Plan Status

**All passes and user approves:** Set `Status: VERIFIED`, register:
```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true
```
Report:
```
Bugfix verified — regression test passes, full suite green.
Run /clear before starting new work — this resets context while keeping project rules loaded.
```

**Fails:**

⛔ **Iteration cap.** Read `Iterations:` from the plan header. If `Iterations >= 3` BEFORE incrementing, stop the fix-on-fix loop:

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

Handle:
- **Continue:** increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')` as below.
- **Pivot:** set `Status: PENDING`, do NOT invoke spec-implement. Tell the user you're standing by for new investigation direction.
- **Abandon:** leave `Status: PENDING`, do not invoke spec-implement. Stop.

**When `Iterations < 3`:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

ARGUMENTS: $ARGUMENTS
