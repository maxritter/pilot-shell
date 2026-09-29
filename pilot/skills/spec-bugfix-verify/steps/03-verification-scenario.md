## Step 3: Verification Scenario (if exists in plan)

Check whether the plan has a `## Verification Scenario` section (only present for UI-facing bugs).

**If no Verification Scenario:** proceed to Step 4.

**If Verification Scenario exists:**

**Resolve the driver:** first check whether the project's own rules (`.claude/rules/`, `CLAUDE.md`, `AGENTS.md`) name the tool that reaches its UI — a mobile WebView or native window has one the ladder below does not cover. Otherwise use the available browser-control or Chrome DevTools tools according to their exposed schemas; fall back to installed playwright-cli or agent-browser when appropriate. Discover deferred tools using the current runtime's tool-discovery surface. See `browser-automation.md`.

```bash
<!-- CC-ONLY -->
# Chrome DevTools MCP: load via ToolSearch(query="chrome-devtools-mcp", max_results=30)
<!-- /CC-ONLY -->
<!-- CODEX-START
# Chrome DevTools MCP: use the available Chrome DevTools MCP tools if present; if deferred, load them with the available tool-discovery helper.
CODEX-END -->
# playwright-cli:
playwright-cli -s="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}" open <url>
# agent-browser fallback:
AB_SESSION="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}"
agent-browser --session "$AB_SESSION" open <url>
```

1. Execute each step from the scenario using the resolved browser tool
   - **Chrome:** `navigate`, `read_page`, `computer`/`form_input`
   - **Chrome DevTools MCP:** `navigate_page`, `take_snapshot`, `click(uid=...)`/`fill(uid=...)`
   - **playwright-cli:** `open`/`goto`, `snapshot`, `click`/`fill` (bare refs: `e1`)
   - **agent-browser:** `open`/`goto`, `snapshot -i`, `click`/`fill` (refs: `@e1`)
2. Verify the expected result for each step (read page after each interaction)
3. **PASS:** Scenario confirms fix works — close browser (CLI tools only), proceed to Step 4
4. **FAIL:** Analyze root cause, implement an evidence-backed fix, re-run tests, and re-execute the scenario.
5. **Needs implementation changes:** Follow Step 7's failed-verification flow and retain the lane on loop-back. It diagnoses and continues automatically by default; only an enabled stalled-work checkpoint or a real required decision waits for input. Fix-attempt counts are evidence for reporting, never a permission threshold. Keep the plan unverified until the scenario passes.

```bash
# Chrome DevTools MCP: no explicit close needed
# playwright-cli: playwright-cli -s="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}" close
# agent-browser: agent-browser --session "$AB_SESSION" close
```
