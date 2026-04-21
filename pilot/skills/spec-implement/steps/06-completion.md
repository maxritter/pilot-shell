---

## Step 6: All Tasks Complete → Verification

1. Check diagnostics. **Run the full test suite ONLY if `Type:` is NOT `Bugfix`.** For bugfix plans, Task 2 ran the suite (anti-regression gate), Task 3 ran it again (post lint/types auto-fixes), and the verify phase will run it once more as the authoritative final check. A fourth run here is wasted runtime (30s–5min) and adds nothing.
2. **For migrations:** Feature parity check against old code. If features missing: add tasks, do NOT mark complete.
3. Set `Status: COMPLETE` in plan
4. Register: `~/.pilot/bin/pilot register-plan "<plan_path>" "COMPLETE" 2>/dev/null || true`
5. Read `Type:` field → Bugfix: `Skill(skill='spec-bugfix-verify', args='<plan-path>')` | Otherwise: `Skill(skill='spec-verify', args='<plan-path>')`
