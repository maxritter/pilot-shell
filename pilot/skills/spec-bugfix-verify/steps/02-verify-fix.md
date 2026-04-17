## Step 2: Verify the Fix

1. **Read the plan's regression test** (from Task 1)
2. **Run it specifically:** `uv run pytest <test-path>::<test-name> -q`
3. Must PASS — if not, fix is incomplete, fix immediately
4. **Scope check:** Read changed files, confirm changes match plan scope. Flag unplanned changes.
