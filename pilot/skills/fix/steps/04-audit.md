## Step 4: Single-Pass Audit

**One bash + one mental check.** Replaces the eight-substep audit in the full lane.

### 4.1 Scope sanity

```bash
git diff --name-only
```

Check:

- Root-cause file IS in the diff. (If not, fix is at a symptom — return to Step 3.)
- No unplanned files appear. (If they do, revert them now.)
- Diff is small — usually < 20 lines. If it ballooned, you're not in a quick-lane bug — bail out (tell the user to re-invoke with `/spec`).

### 4.2 Symptom-patching grep

```bash
git diff | grep -E "^\+.*\b(try:|except|catch \(|return None|return \[\]|return \{\}|console\.log|print\()"
```

Inspect every match:

- New `try/except`/`catch`: is it hiding the bug instead of fixing it? Revert if yes.
- `return None`/`return []`/`return {}`: is it swallowing the bad value? Revert if yes.
- `console.log` / `print` left over from debugging: remove unless intentionally added with a `SPEC-DEBUG:` marker.

Zero matches = clean. Any match = justify or revert.

### 4.3 End-to-end verification — MANDATORY

⛔ **A passing unit test does not prove the bug is fixed.** Unit tests can sit below the layer the user interacts with. A green test plus a still-broken app is the most common "fixed but not really" failure mode. You MUST run the actual program with the original input and observe the symptom is gone.

**Skip is NOT an option.** No exceptions for "small fix", "obvious fix", "test covers it", "I'm confident". If the bug had a user-visible symptom, you re-execute the user-visible scenario.

Pick the lane that matches the bug:

| Bug surface | What to run | How |
|-------------|-------------|-----|
| **UI / web frontend** | Browser automation against the running app | 4-tier resolution from `browser-automation.md`: **Claude Code Chrome** (`mcp__claude-in-chrome__*` if available — load via ToolSearch) → **Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` if available) → **playwright-cli** → **agent-browser**. Navigate to the affected page, walk the user's repro steps, read the page after each interaction, confirm the correct behaviour. |
| **CLI** | The exact command the user ran | `bash` with the original arguments and environment. Capture stdout/stderr and exit code. |
| **HTTP API** | A real request | `curl` or HTTP client with the user's body/headers. Capture status code and response body. |
| **Library / SDK / function-level** | A real invocation | `python -c '...'`, `node -e '...'`, or a temporary scratch script that calls the function with the user's args. |
| **Background job / cron / worker** | Trigger the job | Run the job manually with the failure-triggering input. Read logs. |

**Proof requirement.** Capture concrete evidence of what you ran AND what you observed. Examples:

- UI: read the page after the fix, confirm the rendered state matches expected. Cite the elements you checked.
- CLI: paste the command and the relevant lines from its output (or exit code).
- API: paste status code + the field/value that proves the fix.
- Library: paste the REPL/script invocation and the returned value.

Bare assertions like "the bug is gone", "looks fixed", "behaves correctly" without evidence are insufficient — Step 6 will reject the report.

**If the symptom persists:** the unit test is at the wrong layer. Move the assertion up to the user's actual entry point, re-run Step 2.3 (RED) → Step 3.3 (test passes) → Step 4.3 (E2E re-check).

**If the running program is unavailable** (build broken, infra missing, integration env down): stop and tell the user. Do not finalise the fix without E2E verification — that is the failure mode this step prevents.

If the symptom is gone with evidence captured: proceed to Step 5.
