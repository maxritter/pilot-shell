---

## Step 6: All Tasks Complete → Verification

1. Check diagnostics + run test suite
2. **For migrations:** Feature parity check against old code. If features missing: add tasks, do NOT mark complete.
3. Set `Status: COMPLETE` in plan
4. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "COMPLETE" 2>/dev/null || true`
5. Read `Type:` field → Bugfix: `Skill(skill='spec-bugfix-verify', args='<plan-path>')` | Otherwise: `Skill(skill='spec-verify', args='<plan-path>')`
