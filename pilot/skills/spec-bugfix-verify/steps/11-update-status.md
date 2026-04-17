## Step 11: Update Plan Status

**All passes and user approves:** Set `Status: VERIFIED`, register:
```bash
~/.pilot/bin/pilot register-plan "<plan_path>" "VERIFIED" 2>/dev/null || true
```
Report:
```
Bugfix verified — regression test passes, full suite green.
Run /clear before starting new work — this resets context while keeping project rules loaded.
```

**Fails:** Add fix tasks, set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`.

ARGUMENTS: $ARGUMENTS
