## Step 3: Fix at the Root Cause

### 3.1 Make the minimal change

Edit only the file(s) at the root cause. One logical fix. No "while I'm here" cleanups, no bundled refactoring, no formatting passes. **Lineage rule:** every changed line traces directly to the bug.

**Multi-site is allowed when each site gets the same conceptual fix** (e.g., adding the same iteration cap to two parallel guard layers because the missing-budget defect lives at both). The constraint is *one logical change, repeated where the same pattern lives* — not "while I'm here, also tweak X."

### 3.2 Forbidden patterns — fix at source, not symptom

If the buggy data flows from upstream, fix upstream. Red flags in the diff:

- Broad new `try/except` around the failing call.
- `if value is None: return default` at the caller when the bug is that `value` is wrong upstream.
- Swallowed exceptions, silently normalised bad inputs.
- Early return that hides wrong state from the caller.
- Renamed/suppressed log lines that previously surfaced the bug.

**Quick-lane fixes are single-pattern.** If each candidate fix site needs **different** logic (entry validation + a business rule + a storage migration, each non-trivial), you're in `/spec` territory — bail out. Adding the *same* guard at multiple parallel sites is fine; that's still one logical change. The trigger is *logic divergence*, not site count.

### 3.3 Run the reproducing test — it MUST pass

```bash
<same single-test command from Step 2.3>
```

If it doesn't pass: stop adding more code. Revert your edit. Return to Step 1.3 — your root cause hypothesis was wrong.

### 3.4 Run the targeted scope (NOT full suite)

Run the test module(s) covering the file you just changed. Fast, scoped:

```bash
# Python example
uv run pytest <path/to/test_module.py> -q
# TypeScript example
bun test <path/to/test-file.test.ts>
```

Zero failures. The full anti-regression suite runs once at Step 5 — running it after every fix iteration is the quick-lane anti-pattern.

### 3.5 Diff sanity

```bash
git diff --name-only
git diff | grep -E "^\+.*\b(try:|except|catch \(|return None|return \[\]|return \{\}|console\.log|print\()"
```

- **Root-cause file IS in the diff.** If not, the fix is at a symptom — return to 3.1.
- **No unplanned files appear.** If they do, revert them now.
- **Diff is small** — usually < 20 lines for single-site fixes, < ~150 net new production lines for multi-site pattern fixes. If it ballooned past that ceiling, the bug exceeds the quick lane — bail out.
- **Every grep match must be justified or reverted.** Look for symptom-patching, swallowed returns, or leftover `print` / `console.log` / `SPEC-DEBUG:` markers.

### 3.6 If your first fix doesn't work — one re-attempt, then bail out

If Step 3.3 fails: revert, re-investigate, try once more.

If the second attempt also fails: **stop and tell the user to re-invoke with `/spec`**. Two failed quick-lane attempts means the bug is deeper than the lane is built for.
