# Codex Companion Run Protocol

> Shared runbook for every Pilot workflow step that launches a Codex companion review
> (`spec-plan` plan review, `spec-verify` changes review, `fix` bugfix review).
> Claude Code only — the companion broker ships with the `openai-codex` plugin.
>
> Skill steps reference this file instead of restating it. Read it only when the
> calling step has confirmed its Codex toggle is `"true"` and the codex-once
> sentinel is absent.

## What the caller supplies

| Value | Meaning |
|---|---|
| `PROMPT_TEMPLATE` | `$HOME/.claude/agents/spec-review-codex.md` (plans) or `changes-review-codex.md` (code) |
| Placeholders | The template's `{{...}}` keys and their values — resolved by the caller, never guessed |
| `SLUG` | Plan slug (filename minus `YYYY-MM-DD-` prefix and `.md`), or `fix` for `/fix` |
| `CODEX_FLAG` | Session sentinel path enforcing codex-once |

Everything below is identical across callers.

## Non-negotiables

These three exist because each has produced a real, reproduced failure:

- **Launch from the main conversation via `Bash`, never through a subagent** (`codex:codex-rescue` included). A subagent-launched job's ID is unreachable afterwards — no findings file, no `TaskOutput`, no `SendMessage`, no recovery.
- **Never read the result file before the monitor exits.** Partial output parses as "no findings" — the single most common cause of a premature Codex skip.
- **Never pass `--model`.** Fast-model aliases are rejected on ChatGPT-plan auth (`400`). The user's default model always stays.

## 1. Locate the companion

```bash
CODEX_COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"; mkdir -p "$SESS_DIR"
[ -z "$CODEX_COMPANION" ] && echo "MISSING"
```

`MISSING` → tell the user "Codex companion not found — install the openai-codex plugin or disable the Codex reviewer in Console Settings", continue with the caller's other reviewer, and record the gap in the caller's report. Do not fail the workflow.

## 2. Render the prompt file

The template is the single source of truth for review semantics — never restate its prompt inline.

```bash
PROMPT_FILE="$SESS_DIR/codex-review-$SLUG.md"
# Export each placeholder the template declares, then substitute:
PROMPT_TEMPLATE="$PROMPT_TEMPLATE" PROMPT_FILE="$PROMPT_FILE" \
node -e '
const fs = require("fs");
let text = fs.readFileSync(process.env.PROMPT_TEMPLATE, "utf8");
for (const key of Object.keys(process.env))
  if (/^[A-Z_]+$/.test(key)) text = text.split("{{" + key + "}}").join(process.env[key]);
fs.writeFileSync(process.env.PROMPT_FILE, text);
'
grep -c "{{" "$PROMPT_FILE"   # must print 0 — an unsubstituted placeholder means the review runs blind
```

`node` (not `uv`/`python`) because the companion is itself node — it is guaranteed present on this path. `split`/`join` rather than `replace` so a value containing `$&` cannot trigger JS pattern expansion.

## 3. Launch in the background

Review effort defaults to `medium` and fails closed. A review is a bounded read-only audit; the user's interactive default (often `xhigh`) runs ~2× longer for the same material findings. Users override with `PILOT_CODEX_REVIEW_EFFORT`.

```bash
CODEX_EFFORT="${PILOT_CODEX_REVIEW_EFFORT:-medium}"
case "$CODEX_EFFORT" in none|minimal|low|medium|high|xhigh) ;; *) CODEX_EFFORT=medium ;; esac
```

`task --background` is the only companion subcommand whose own background mode works (`review` / `adversarial-review` do not detach). It returns the job id on stdout immediately:

```
Bash(
  command="cd $PROJECT_ROOT && node $CODEX_COMPANION task --background --effort \"$CODEX_EFFORT\" --prompt-file \"$PROMPT_FILE\"",
  run_in_background=false,
  timeout=60000
)
```

Extract the `task-…` token as `JOB_ID`. If the launch itself errors on the effort value (a model rejecting `reasoning.effort` fails within seconds with a `400`), relaunch once without `--effort`.

Verify the broker actually registered the job — this catches a synthetic id before you spend a whole poll cycle on it:

```bash
node "$CODEX_COMPANION" status "$JOB_ID" --json 2>/dev/null | grep -q '"status":' \
  || { echo "Codex launch did not register with broker (synthetic task id?). Skipping Codex this run."; JOB_ID=""; }
```

Empty `JOB_ID` → skip collection entirely and note the gap.

**Then return to the calling step and keep working.** The companion runs in parallel with the caller's own checks; do not idle waiting for it.

## 4. Wait with the stall monitor

Broker `status` is not a liveness signal: a silent job keeps reporting `running`/`verifying` with a climbing elapsed, so a status-only loop burns its full timeout before noticing. This monitor watches `job.logFile` mtime alongside status and returns the moment the job finishes **or** goes quiet.

```bash
STALL=90 CEILING=480 node -e '
const { execFileSync } = require("child_process");
const fs = require("fs");
const [companion, jobId] = process.argv.slice(1);
const stallMs = (Number(process.env.STALL) || 90) * 1000;
const ceilingMs = (Number(process.env.CEILING) || 480) * 1000;
const start = Date.now();
let lastChange = Date.now(), lastMtime = 0, logFile = null;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  while (true) {
    let job = {};
    try {
      job = JSON.parse(execFileSync(process.execPath, [companion, "status", jobId, "--json"], { encoding: "utf8", timeout: 30000 })).job ?? {};
    } catch { console.log("FAIL state=status_error"); return; }
    const st = job.status ?? "unknown";
    if (st === "completed") { console.log(`READY elapsed=${Math.round((Date.now() - start) / 1000)}s`); return; }
    if (st === "failed" || st === "cancelled" || st === "unknown") { console.log(`FAIL state=${st}`); return; }
    if (!logFile) logFile = job.logFile ?? null;
    let m = 0;
    try { if (logFile) m = fs.statSync(logFile).mtimeMs; } catch {}
    if (m > lastMtime) { lastMtime = m; lastChange = Date.now(); }
    if (Date.now() - lastChange >= stallMs) { console.log(`STALLED no_log_growth=${Math.round((Date.now() - lastChange) / 1000)}s`); return; }
    if (Date.now() - start >= ceilingMs) { console.log(`CEILING elapsed=${Math.round((Date.now() - start) / 1000)}s`); return; }
    await sleep(5000);
  }
})();
' "$CODEX_COMPANION" "$JOB_ID"
```

Run as `Bash(run_in_background=true, timeout=600000)` — the CEILING exits first. A single node process avoids per-poll `uv`/`python` spawns, zsh's read-only `status` variable, and `stat -f`/`stat -c` platform juggling. A status JSON with no `logFile` degrades it to status + CEILING, still better than spinning blind. Typical runtimes at `medium`: plan reviews under 2 min (no diff to load), code reviews 1–3 min.

**Waiting does not mean ending your turn.** A closing message ("waiting for Codex…") reads as a finished workflow and trips the stop guard. Stay in-turn and do something useful: re-read the plan or diff for gaps you would fix anyway, draft text for a queued follow-up, run cheap sanity one-liners. `AskUserQuestion` is the only tool whitelisted for a genuine pause while a background job is in flight.

| Monitor output | Action |
|---|---|
| `READY` | Fetch the result (§5) |
| `FAIL` | Genuine launch/broker failure — relaunch once synchronously, then §5 |
| `STALLED` / `CEILING` | Cancel and relaunch **once** under the same monitor, **without** `--effort` (inherit the user's Codex default) so the retry has no configuration variable in play |

```bash
node "$CODEX_COMPANION" cancel "$JOB_ID" --json 2>/dev/null || true
node "$CODEX_COMPANION" task --background --prompt-file "$PROMPT_FILE"   # retry: NO --effort
```

If the retry also stalls or fails: do not spin a third time and do not silently skip. Proceed without the Codex pass, continue with the caller's other reviewer, and record the gap explicitly (how long it ran, when the log last advanced) in the caller's report.

## 5. Fetch and act on findings

```bash
node "$CODEX_COMPANION" result "$JOB_ID" --json > "$SESS_DIR/codex-result-$SLUG.json"
```

Read that file. Deterministic name, never `$$` — each Bash call is a new shell with a new PID, so a PID-based path cannot be reconstructed by a later step.

- `storedJob.status` must be `"completed"`; anything else is a relaunch trigger, never a silent pass.
- `storedJob.result.rawOutput` — Codex's response; with these templates it is JSON matching `{verdict, summary, findings, next_steps}`.
- `storedJob.rendered` — display fallback when `rawOutput` will not parse. Surface it as one suggestion-level finding and continue; a parse failure never earns a relaunch, because Codex runs at most once per invocation.

**Severity → action.** Evaluate lineage FIRST: a finding on a file outside the change's lineage is mention-only regardless of severity — out-of-lineage crashes get reported to the user, never auto-fixed. For in-lineage findings:

| Codex severity | Action |
|---|---|
| `critical` / `high` | must_fix — fix now, then re-run the caller's tests |
| `medium` / `low` | should_fix — fix now when single-site; summarise if it would expand scope |
| `info` | Mention in the report |

Verdict `approve` with no findings → report "Codex: no blocking findings" in one line.

Codex findings frequently surface architectural gaps the Claude reviewer misses (chained-command bypasses, fail-open paths, encoding edges) — weigh them at least equally.

## 6. Mark and clean up

```bash
[ -n "$JOB_ID" ] && touch "$CODEX_FLAG"      # codex-once: later iterations in this session skip the launch
rm -f "$PROMPT_FILE" "$SESS_DIR/codex-result-$SLUG.json"
```
