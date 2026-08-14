## Step 1: Verify the Fix — Behavior Contract Audit

Audits that the process was followed. A retroactive test that passes proves nothing.

### 1.0 Run Full Test Suite (Baseline)

Run all tests. Fix any failures immediately. Re-run until green. The remaining sub-steps assume a clean baseline.

### 1.1 Read the plan

Read: `## Behavior Contract`, Task 1's `Entry point:` and test file/name, `Root Cause: file:line` from the summary.

If `## Behavior Contract` is missing (older plan): reconstruct from Summary + Fix Approach and add it to the plan before continuing.

### 1.2 Run the reproducing test

```bash
uv run pytest <test-path>::<test-name> -q   # or language-appropriate equivalent
```

Must PASS. If not, fix is incomplete — fix immediately.

### 1.3 Prove the test is a genuine RED (always run)

A test only has value if it would fail without the fix. Run the test against pre-fix code; it must fail. One atomic bash with trap-based cleanup — touches only the root-cause file, always restores it (works in worktree and non-worktree mode):

```bash
ROOT_CAUSE_FILE="<path from plan Summary>"
TEST_CMD="<command that runs the single reproducing test>"

BACKUP=$(mktemp)
cp "$ROOT_CAUSE_FILE" "$BACKUP"
trap 'cp "$BACKUP" "$ROOT_CAUSE_FILE" 2>/dev/null; rm -f "$BACKUP"; trap - EXIT INT TERM' EXIT INT TERM

if ! git diff --quiet HEAD -- "$ROOT_CAUSE_FILE"; then
    git show "HEAD:$ROOT_CAUSE_FILE" > "$ROOT_CAUSE_FILE"
else
    FIX_COMMIT=$(git log --format=%H -1 -- "$ROOT_CAUSE_FILE")
    git show "${FIX_COMMIT}~1:$ROOT_CAUSE_FILE" > "$ROOT_CAUSE_FILE"
fi

eval "$TEST_CMD"
```

`cp + trap` instead of `git stash`: stash modifies index/working-tree globally and can leave untracked files or merge conflicts on pop. `cp + trap` touches one file and always restores it.

Outcomes:

- **Test failed with the documented `Currently (bug)` error** → RED proven.
- **Test passed without fix** → test doesn't encode the bug. Set `Status: PENDING`, note "reproducing test does not fail without fix", return to `spec-implement`.
- **Test errored unrelated** (import, missing fixture) → not a valid signal. Investigate: test depends on something only the fix creates (design problem) or unrelated change snuck in. Resolve before accepting.

### 1.4 Root-cause + scope audit

**Resolve the diff base once with the resolver** — ⛔ do NOT derive it by hand:

> **`$LANE_FLAG`** is `--lane <id>` when this run was dispatched as an orchestration lane, and **nothing at all** otherwise — the value the invocation parsed from its arguments. It keeps worktree and plan identity scoped to this lane; an unflagged call resolves a different identity and silently finds nothing (issue #174).

```bash
SCOPE=$(~/.pilot/bin/pilot review-scope --slug <plan-slug> $LANE_FLAG --json 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["diff_range"]); print(d.get("warning",""))' 2>/dev/null)
DIFF=$(printf '%s' "$SCOPE" | head -1)
printf '%s' "$SCOPE" | tail -n +2 | grep . && echo "^ scope degraded - fix this before trusting the checks below"
[ -n "$DIFF" ] || DIFF=HEAD   # older pilot binary: resolve by hand if the fix is worktree-committed
```

⛔ **`$LANE_FLAG` is load-bearing, and a `warning` is a stop sign.** A lane's branch is `spec/<slug>-<lane>`, so an unflagged resolve finds nothing and degrades to `git diff HEAD` — empty when the fix is committed on the worktree branch, so rule 1 below would fire on a diff that was never read (issue #176). Resolve the warning and re-run; do not check against the degraded scope.

⛔ Pipe through `--json` + a parse — do NOT use `... 2>/dev/null || echo HEAD`. A `pilot` binary predating `review-scope` does not fail on it: it prints the "runs directly inside Claude Code" transition banner and exits **0**, so `||` never fires and `$DIFF` silently becomes the banner text. The `json.load` parse fails on that banner, so the fallback actually runs.

That yields `HEAD` when the fix is UNCOMMITTED in the working tree (the default), and `<base_branch>...HEAD` when it is per-task-committed in a worktree. A committed ref-range in the uncommitted case shows nothing and would falsely fire rule 1 every run; a two-dot range in the worktree case would fold the base branch's own post-fork commits into this diff **inverted** — a base-branch addition reading as a deletion the fix never made — silently corrupting both the root-cause check and the scope check below. `pilot review-scope` encodes both rules; see `launcher/worktree.py:resolve_review_scope`.

```bash
git diff --name-only $DIFF
```

1. **Root-cause file MUST be in the diff.** If not, fix is at symptom — set `Status: PENDING`, return to `spec-implement` (via the Step 7 iteration-cap check).
2. **Symptom-patching smells:** new broad `try/except` around the failing call, `if value is None: return default` at the caller when the bug is upstream, swallowed exceptions, silently normalised bad inputs, early returns hiding wrong state, renamed/suppressed log lines. Record + justify in Investigation, or revert.
3. **Scope check:** diff matches plan scope (Task 1 tests + Task 2 root-cause file ± documented defense-in-depth). Unplanned changes belong elsewhere — revert or extend the plan.

### 1.5 Instrumentation cleanup

```bash
if git diff $DIFF | grep -n "SPEC-DEBUG"; then
    echo "Temporary debug markers present — remove before continuing"
    exit 1
fi
```

Zero matches = clean. Any match = remove and re-run. Unmarked `console.log`/`print` additions are also suspect — inspect, justify, or remove.

### 1.6 Original symptom re-check — MANDATORY end-to-end verification

⛔ **The regression test passing does NOT prove the bug is fixed.** Unit tests can sit below the user's layer. A green test plus a still-broken app is the most common "fixed but not really" failure mode. You MUST run the actual program with the original input and observe the symptom is gone.

**Skip is NOT an option.** Capture concrete evidence (command, output, page state, status code) — bare assertions are insufficient.

Re-run the original repro from `## Summary — Trigger:` using the matching lane:

| Bug surface | What to run | Evidence to capture |
|-------------|-------------|---------------------|
| **CLI** | The exact command the user ran | Command + relevant output lines + exit code |
| **API** | `curl` / HTTP client with the user's input | Status code + the field/value that proves the fix |
| **Library / SDK / function** | `python -c '...'`, `node -e '...'`, REPL, or scratch script | Invocation + returned value |
| **Background job / cron / worker** | Trigger the job manually with the failing input | Run + log lines |
| **UI** | **Skip here — handled by Step 3 (Verification Scenario)** with browser automation — the driver the project's rules name, else the 4-tier ladder, per `browser-automation.md` | — |

**If the regression test passes but the original repro still fails:** test is at the wrong layer. Set `Status: PENDING`, note "test green but original repro still fails — layer mismatch", return to `spec-implement` to rewrite Task 1's test at the user's entry point.

**If the running program is unavailable** (build broken, infra missing, integration env down): set `Status: PENDING`, note the blocker, escalate to the user. Do not advance to VERIFIED on tests alone.
