### Step 6: Feature Parity Check (migration/refactoring only)

Skip unless the plan has a Feature Inventory section.

1. Compare old vs new implementation
2. Verify each feature exists in new code
3. Run new code and verify same behavior

**If features are MISSING:** Add tasks with `[MISSING]` prefix, set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')`.
