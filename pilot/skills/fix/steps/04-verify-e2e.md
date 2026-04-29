## Step 4: Verify End-to-End

⛔ **The primary proof that the bug is fixed.** Run the actual program with the original input and observe the symptom is gone. A passing unit test alone is never accepted.

This is the most important step in the workflow. Skip is NOT an option — no exceptions for "small fix", "obvious fix", "test covers it", "I'm confident".

### Pick the lane that matches the bug

| Bug surface | Tool | Evidence to capture |
|-------------|------|---------------------|
| **UI / web frontend** | 4-tier resolution from `browser-automation.md`: **Claude Code Chrome** → **Chrome DevTools MCP** → **playwright-cli** → **agent-browser**. Walk the user's repro steps. | Page state and element values that prove the correct behaviour |
| **CLI** | The exact command the user ran, with original args + env | Stdout/stderr lines + exit code |
| **HTTP API** | `curl` / HTTP client with the user's body and headers | Status code + the response field that proves the fix |
| **Library / SDK / function** | `python -c '…'`, `node -e '…'`, REPL, or scratch script with the user's args | Returned value |
| **Background job / cron / worker** | Trigger the job manually with the failing input | Relevant log lines |

### Proof requirement

Concrete evidence is mandatory in the Step 6 report. Bare assertions are insufficient:

- ❌ "Looks fixed", "behaves correctly", "tests pass"
- ✅ `curl /search -d '{}' → 200, response.results.length=42`
- ✅ "Saved end_date 2026-05-15, list shows 2026-05-15 (read_page after save confirms)"

### When the symptom persists

The unit test is at the wrong layer — it sits below the user's interaction point. Move the assertion up to the user's actual entry point (API, browser, CLI), then re-run **Step 2.3 (RED) → Step 3.3 (test passes) → Step 4 (E2E re-check)**.

### When the running program is unavailable

Build broken, infra missing, integration env down? Stop and tell the user. Do not finalise the fix without E2E verification — that is the failure mode this step prevents.
