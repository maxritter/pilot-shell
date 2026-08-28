## Step 7: E2E Verification & Final Regression

**If runtime profile is not Full:** Skip directly to sub-section 7f (Final Regression). The Full-profile E2E sub-steps below assume a UI/browser entry point.

### ⛔ 7a-pre: Resolve a Live Target Before Touching the Browser

**⛔ MANDATORY — never skip to "unit-verified" without completing this probe.** The single most common verify-phase failure mode is: tests pass, no live server is up, the model concludes "unit-verified" and marks the plan VERIFIED without ever interacting with a deployed instance. The four-tier browser priority below is useless if no URL exists to navigate to. This sub-step exists to force an actual deploy attempt before any "I can't run E2E" claim.

Run the probe in order. The FIRST tier that returns a working URL wins; later tiers exist only as fallbacks.

#### Tier 1 — Reuse an already-running local server

If the plan's `## Runtime Environment` section names a local port:

```bash
PORT="<port from plan, e.g. 41777>"
if curl -s --max-time 3 -o /dev/null -w '%{http_code}' "http://localhost:$PORT/" | grep -qE '^(2|3)'; then
  TARGET_URL="http://localhost:$PORT"
  echo "TIER1_OK $TARGET_URL"
fi
```

When the harness blocks `curl`, substitute `mcp__plugin_pilot_web-fetch__fetch_url` with a 3s timeout.

#### Tier 2 — Start the local dev server yourself

If Tier 1 fails AND the plan's Runtime Environment names a start command (`bun run dev`, `npm run dev`, `vercel dev --listen <port>`, `flask run`, `uvicorn ...`):

<!-- CC-ONLY -->
1. Start in background: `Bash(command="cd <cwd> && <start command>", run_in_background=true, timeout=180000)`
<!-- /CC-ONLY -->
<!-- CODEX-START
1. Start the server as a background process from `<cwd>` using `<start command>`. Use the available background process tool or dev-server workflow, and keep the session id isolated when required by `browser-automation.md`.
CODEX-END -->
2. Poll the health endpoint for up to 60s (200/301/302 = ready)
3. On success: `TARGET_URL=http://localhost:<port>`, proceed
4. On failure: capture the last 30 lines of the background process's output file and INCLUDE THEM in the verification report — do NOT silently drop to Tier 3

#### Tier 3 — Probe deploy credentials and attempt a preview deploy

Generic across deploy backends. Detect from repo:

| Marker file / dir | Backend | Auth-check command | Preview deploy |
|---|---|---|---|
| `vercel.json` / `.vercel/` | Vercel | `vercel whoami` | `vercel deploy --yes` |
| `fly.toml` | Fly.io | `flyctl auth whoami` | `flyctl deploy --strategy immediate` |
| `netlify.toml` / `.netlify/` | Netlify | `netlify status` | `netlify deploy --build` |
| `wrangler.toml` / `wrangler.jsonc` | Cloudflare | `wrangler whoami` | `wrangler deploy --dry-run=false` |
| `render.yaml` | Render | `render whoami` (or skip — Render needs PR) | n/a |
| `cdk.json` / `serverless.yml` | AWS | `aws sts get-caller-identity` | `cdk deploy` / `serverless deploy` |
| `.github/workflows/deploy*.yml` | GitHub Actions | `gh auth status` + `gh workflow run` | trigger workflow + poll |
| `Procfile` | Heroku | `heroku auth:whoami` | `heroku create --no-remote && git push heroku` |

**Probe algorithm:**

1. Detect candidate backends by checking marker files (`ls vercel.json fly.toml ...` or `git ls-files`).
2. For each candidate, run its auth-check command with a short timeout. Authenticated → eligible.
3. If ≥ 1 backend is eligible, pick the first one (or the user-preferred one if the plan / `CLAUDE.md` specifies) and run its preview-deploy command. Capture the resulting URL.
4. **Project-config gotchas to handle automatically:**
   - Vercel projects with a `rootDirectory` set in dashboard need the CLI run from the **repo root** (not the configured root directory), otherwise the CLI duplicates the path. If the first deploy attempt errors with `<path>/<configured-root>` doesn't exist, retry from the repo root.
   - Builds that need a fresh dependency install: pass the appropriate flag (`vercel deploy --build-env INSTALL=true` / `fly deploy --build-only`).
5. On success: `TARGET_URL=<preview URL>`, proceed.
6. If NO backend is eligible (no marker files, OR markers exist but every auth-check fails): produce a one-line probe summary in the verification report (`Deploy probe: vercel auth=missing, fly auth=missing → no live target available`) and proceed to the unit-only fallback below — explicitly acknowledging the gap.

#### Tier 4 — Unit-only fallback (only after Tiers 1–3 above all returned no URL)

⛔ **You MUST have executed Tiers 1, 2, AND 3 above** — and recorded their outcomes — before marking any scenario `UNIT_VERIFIED` instead of `LIVE_PASS`. Document:

```
Live-target probe summary:
- Tier 1 (local port <p>): <FAIL reason or NOT_APPLICABLE>
- Tier 2 (start dev server): <FAIL reason or NOT_ATTEMPTED because Tier 1 succeeded>
- Tier 3 (deploy creds): <backend auth status, deploy outcome, error if any>
- Falling back to UNIT_VERIFIED for the following scenarios: …
```

Failing to record this gap in the verification report is a `must_fix` finding by definition — the next reviewer will treat absence of the summary as silent skip.

### 7a: Resolve Browser Tool

**Driver resolution** (see `browser-automation.md`): the tool the project's own rules name, else the 4-tier ladder — Chrome → Chrome DevTools MCP → playwright-cli → agent-browser.

<!-- CC-ONLY -->
1. **Claude Code Chrome:** Check if `mcp__claude-in-chrome__*` tools are in your available/deferred tools list. If available, use Chrome for all E2E steps below. Load tools via `ToolSearch(query="select:mcp__claude-in-chrome__<tool>")`. No session isolation needed.

2. **Chrome DevTools MCP:** If Chrome extension is unavailable, check for `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` tools. Load via `ToolSearch(query="chrome-devtools-mcp", max_results=30)`. Use `take_snapshot()` for a11y tree with uids, `click(uid=...)` / `fill(uid=...)` for interaction.
<!-- /CC-ONLY -->

3. **playwright-cli (CLI fallback):** If neither Chrome tool is available, use playwright-cli for thorough E2E.
```bash
playwright-cli -s="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}" open <url>
```

4. **agent-browser (lightweight fallback):** If none of the above are available:
```bash
AB_SESSION="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}"
agent-browser --session "$AB_SESSION" open <url>
```

### 7b: Check for Structured Scenarios

Read the plan's `## E2E Test Scenarios` section (if it exists).

**If structured scenarios exist (TS-NNN format):** Follow 7c below.

**If no structured scenarios:** Fall back to ad-hoc verification — test the primary user workflow (every view, interaction, state transition), then cover edge cases:

| Category | What to test |
|----------|-------------|
| Empty state | No data, no results |
| Invalid input | Bad params, wrong types, injection |
| Stale state | References to deleted data |
| Error state | Backend unreachable |
| Boundary | Max values, zero, single item |

Then skip to 7e (close browser + write results).

### 7c: Execute Structured Scenarios

Execute Critical first, then High, then Medium.

<!-- CC-ONLY -->
Create one task per scenario for tracking:

```
TaskCreate(subject="TS-NNN: [name]", description="[priority] | [preconditions]")
```
<!-- /CC-ONLY -->

**For each scenario:**

<!-- CC-ONLY -->
1. `TaskUpdate → in_progress`
<!-- /CC-ONLY -->
1. Execute each step using the resolved browser tool:
   - **Chrome:** `navigate` to open pages, `read_page` after interactions, `computer`/`form_input` per the step's action
   - **Chrome DevTools MCP:** `navigate_page` to open pages, `take_snapshot` after interactions, `click(uid=...)`/`fill(uid=...)` per the step's action
   - **playwright-cli:** `open`/`goto` to navigate, `snapshot` after interactions, `click`/`fill`/`press` per the step's action (refs are bare: `e1` not `@e1`)
   - **agent-browser:** `open`/`goto` to navigate, `snapshot -i` after interactions, `click`/`fill`/`press` per the step's action (refs use `@`: `@e1`)
   - Verify the expected result by reading the page output
3. **PASS:** All steps match expected results → note `TS-NNN: PASS`
4. **FAIL:** Step result doesn't match expected:
   - Analyze root cause, implement minimal fix, re-run relevant tests (stay in Phase B — no code changes that need re-review)
   - Re-execute the scenario (counts as fix attempt 1)
   - If still failing: implement second fix, re-execute (fix attempt 2)
   - After 2 failed fix attempts: note `TS-NNN: KNOWN_ISSUE — [description]`
<!-- CC-ONLY -->
5. **Critical KNOWN_ISSUE** → run the iteration-cap check from Step 11 (read `Iterations:` from the plan header; if `>= 3` ask the user Continue / Pivot / Abandon before incrementing). On Continue: set `Status: PENDING`, increment `Iterations`, register status change, invoke `Skill(skill='spec-implement', args='<plan-path>')` — do not proceed to VERIFIED. On Pivot/Abandon: do not invoke spec-implement; surface to user per Step 11.
<!-- /CC-ONLY -->
<!-- CODEX-START
5. **Critical KNOWN_ISSUE** → run the iteration-cap check from Step 11 (read `Iterations:` from the plan header; if `>= 3` present the user with Continue / Pivot / Abandon options before incrementing). On Continue: set `Status: PENDING`, increment `Iterations`, register status change, then continue immediately with the `$spec-implement` skill instructions using arguments: `<plan-path>` — do not proceed to VERIFIED. On Pivot/Abandon: do not invoke spec-implement; surface to user per Step 11.
CODEX-END -->
6. **High/Medium KNOWN_ISSUE** → document and continue (non-blocking)

### 7d: Write E2E Results to Plan

After all scenarios are executed, append to the plan file:

```markdown
## E2E Results

| Scenario | Priority | Result | Fix Attempts | Notes |
|----------|----------|--------|--------------|-------|
| TS-001   | Critical | PASS   | 0            |       |
| TS-002   | High     | PASS   | 1            | Fixed: missing validation on empty submit |
| TS-003   | Medium   | KNOWN_ISSUE | 2       | Tooltip misaligned on narrow viewport |
```

### 7d-design: Design-Quality Detector (best-effort, advisory)

Full profile only. When `impeccable` is on PATH, run the deterministic design anti-pattern detector on the UI the change touched (run-when-available, not discretionary) — the findings are an advisory signal, never a Phase-B failure and never a reason to withhold VERIFIED. Run this while the browser is still open (before 7e) so an SPA's rendered DOM is available. Follow the full contract in `browser-automation.md` → "Design-Quality Detector"; the essentials:

1. **Skip cleanly** when `which impeccable` fails (`impeccable not installed — design check skipped`) or runtime profile is not Full. A skip is a one-line note, not a failure.
2. **Pick a bounded target:** the explicit changed UI files, or one narrow built-output dir. For a client-rendered SPA, save the open browser's rendered HTML to a temp file and scan that (the static shell undercounts). Never scan cwd/repo-root.
3. **Run and classify by JSON, not exit code:** `impeccable detect --json <target> || true`. Exit `0`/`2` both mean it ran — parse stdout JSON. A missing binary, a non-0/non-2 exit, or unparseable output is a skip-with-note.
4. **Record findings as advisory notes** in a `Design Notes:` line under the E2E Results table (e.g. `Design Notes: 3 advisory (2 overused-font, 1 side-tab) — non-blocking`). Do NOT add must_fix/should_fix from these, do NOT flip the plan away from VERIFIED, do NOT re-enter spec-implement for them.

### 7e: Close Browser

```bash
# Chrome / Chrome DevTools MCP: no explicit close needed
# playwright-cli: playwright-cli -s="${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-${PILOT_SESSION_ID:-default}}}" close
# agent-browser: agent-browser --session "$AB_SESSION" close
```

### 7f: Final Regression

Re-run full test suite + type checker + build one final time. If code changed during Phase B (E2E fixes), this catches regressions. If no code changed, it confirms Phase A's green state — cheap insurance.
