## Step 2: Verify the Fix — Behavior Contract Audit

**This step is the quality gate for bugfixes.** It audits that the process was followed, not just that tests pass. A retroactive test that passes proves nothing.

### 2.1 Read the plan

1. Read the plan's `## Behavior Contract` section. Note `Given / When / Currently / Expected / Anti-regression`.
2. Read Task 1's `Entry point:` and the test file/name it specifies.
3. Read `Root Cause: file:line` from the plan summary.

**If `## Behavior Contract` is missing from the plan:** the plan was written before the updated template. Reconstruct it from Summary + Fix Approach and add it to the plan before continuing.

### 2.2 Run the reproducing test

```
uv run pytest <test-path>::<test-name> -q   # or language-appropriate equivalent
```

Must PASS on the current (fixed) code. If not, the fix is incomplete — fix immediately, do not advance.

### 2.3 Prove the test is a genuine RED (always run — not optional)

**A test only has value if it would fail without the fix.** Commit order alone does not prove that — a retroactively added `assert True`-style test also satisfies commit order. The only proof is to run the test against the pre-fix code and see it fail.

**Always run this, regardless of worktree mode.** Cost is one extra run of the single reproducing test (seconds, not minutes) — cheap insurance that rules out the entire class of retroactive rubber-stamp tests.

Use one atomic bash block with trap-based cleanup. This script is universal — it works in worktree mode (fix is committed) and non-worktree mode (fix is uncommitted). The `cp + trap` approach restores the file contents reliably regardless of how the fix was applied:

```bash
ROOT_CAUSE_FILE="<path from plan Summary>"
TEST_CMD="<command that runs the single reproducing test>"

# Back up the current (fixed) version and install a trap that always restores it
BACKUP=$(mktemp)
cp "$ROOT_CAUSE_FILE" "$BACKUP"
trap 'cp "$BACKUP" "$ROOT_CAUSE_FILE" 2>/dev/null; rm -f "$BACKUP"; trap - EXIT INT TERM' EXIT INT TERM

# Replace the root-cause file with its pre-fix content
if ! git diff --quiet HEAD -- "$ROOT_CAUSE_FILE"; then
    # Non-worktree / uncommitted fix: HEAD is the pre-fix version
    git show "HEAD:$ROOT_CAUSE_FILE" > "$ROOT_CAUSE_FILE"
else
    # Worktree / committed fix: last commit touching this file IS the fix commit
    FIX_COMMIT=$(git log --format=%H -1 -- "$ROOT_CAUSE_FILE")
    git show "${FIX_COMMIT}~1:$ROOT_CAUSE_FILE" > "$ROOT_CAUSE_FILE"
fi

# Run the reproducing test — must FAIL
eval "$TEST_CMD"
TEST_EXIT=$?
# trap restores $ROOT_CAUSE_FILE from backup on exit (success or failure)
```

Why `cp + trap` instead of `git stash`: stash modifies the index/working tree globally and can leave untracked files or produce merge conflicts on pop. `cp + trap` touches only the one file that matters and always restores it, even on crash.

**Interpretation:**

- Test failed (non-zero exit) with an error matching `Currently (bug)` → RED is proven. Continue to 2.4.
- Test passed without the fix → the test does not encode the bug. STOP, set `Status: PENDING`, note "reproducing test does not fail without fix" in the plan, and return to `spec-implement` — Task 1 must be rewritten.
- Test errored for a reason unrelated to the bug (import error, missing fixture introduced by the fix, etc.) → not a valid signal. Investigate: either the test depends on something only the fix creates (design problem — test should target a stable entry point), or an unrelated change snuck into the fix commit. Resolve before accepting.

### 2.4 Root-cause-at-source audit

Compare the diff to the plan's `Root Cause: file:line`:

1. `git diff --name-only <base>..HEAD` — list files changed.
2. **The root-cause file MUST be in the diff.** If it is not, the fix is at a symptom, not the source. STOP, set `Status: PENDING`, note "fix does not touch stated root cause" in the plan, return to `spec-implement`.
3. **Flag symptom-patching smells in the diff:** new broad `try/except` around the failing call, `if value is None: return default` at the caller when the bug is that `value` is wrong upstream, swallowed exceptions, silently normalised bad inputs. If present, record a finding and require justification in the plan's Investigation section (sometimes a defensive layer is legitimate — defense-in-depth — but it must be documented, not snuck in).

### 2.5 Anti-regression audit

Run the full test suite (already done in Step 1, re-run if the revert in 2.3 left artifacts). Zero failures. The Behavior Contract's `Anti-regression:` line states what must still work — spot-check the tests covering it.

### 2.6 Scope check

Read changed files. Confirm changes match plan scope (Task 1 files + Task 2 files). Flag unplanned changes — they either belong in this plan (update the plan) or in a different plan (revert).
