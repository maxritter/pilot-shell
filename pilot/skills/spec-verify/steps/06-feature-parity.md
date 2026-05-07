## Step 6: Feature Parity Check (migration/refactoring only)

Skip unless the plan has a Feature Inventory section.

1. Compare old vs new implementation
2. Verify each feature exists in new code
3. Run new code and verify same behavior

**If features are MISSING:** Run the iteration-cap check from Step 19 first (read `Iterations:` from the plan header; if `>= 3` ask the user Continue / Pivot / Abandon before incrementing). On Continue: add tasks with `[MISSING]` prefix, set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')`.
