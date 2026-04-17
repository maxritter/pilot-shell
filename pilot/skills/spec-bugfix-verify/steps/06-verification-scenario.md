## Step 6: Verification Scenario (if exists in plan)

Check whether the plan has a `## Verification Scenario` section (only present for UI-facing bugs).

**If no Verification Scenario:** proceed to Final.

**If Verification Scenario exists:**

**Resolve browser tool (4-tier):** Check if `mcp__claude-in-chrome__*` tools are available → use Chrome. Otherwise check for `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` → use Chrome DevTools MCP. Otherwise use playwright-cli (preferred CLI) or agent-browser (lightweight). See `browser-automation.md`.

```bash
# Chrome DevTools MCP: load via ToolSearch(query="chrome-devtools-mcp", max_results=30)
# playwright-cli:
playwright-cli -s=$PILOT_SESSION_ID open <url>
# agent-browser fallback:
AB_SESSION="${PILOT_SESSION_ID:-default}"
agent-browser --session "$AB_SESSION" open <url>
```

1. Execute each step from the scenario using the resolved browser tool
   - **Chrome:** `navigate`, `read_page`, `computer`/`form_input`
   - **Chrome DevTools MCP:** `navigate_page`, `take_snapshot`, `click(uid=...)`/`fill(uid=...)`
   - **playwright-cli:** `open`/`goto`, `snapshot`, `click`/`fill` (bare refs: `e1`)
   - **agent-browser:** `open`/`goto`, `snapshot -i`, `click`/`fill` (refs: `@e1`)
2. Verify the expected result for each step (read page after each interaction)
3. **PASS:** Scenario confirms fix works — close browser (CLI tools only), proceed to Final
4. **FAIL (attempt 1):** Analyze root cause, implement fix, re-run tests, re-execute scenario
5. **FAIL (attempt 2):** Implement second fix, re-run tests, re-execute scenario
6. **FAIL after 2 attempts:** The bug is not fully fixed — set `Status: PENDING`, increment `Iterations`, invoke `Skill(skill='spec-implement', args='<plan-path>')`. Do not proceed to VERIFIED.

```bash
# Chrome DevTools MCP: no explicit close needed
# playwright-cli: playwright-cli -s=$PILOT_SESSION_ID close
# agent-browser: agent-browser --session "$AB_SESSION" close
```
