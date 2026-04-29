## Step 3: Implement the Fix at the Root Cause

### 3.1 Make the minimal change

Edit only the file at the root cause. One change, one variable, one logical fix. **No "while I'm here" cleanups.** No bundled refactoring. No formatting passes. Lineage rule: every changed line traces directly to the bug.

### 3.2 Forbidden patterns (symptom-patching)

If the buggy data flows from upstream, fix upstream. The following are red flags in the diff:

- Broad new `try/except` around the failing call.
- `if value is None: return default` at the caller when the bug is that `value` is wrong upstream.
- Swallowed exceptions, silently normalised bad inputs.
- Early return that hides wrong state from the caller.
- Renamed/suppressed log lines that previously surfaced the bug.

If a defensive layer is genuinely needed (defense-in-depth, not symptom-patching): note it explicitly when you summarise the fix in Step 6.

### 3.3 Run the reproducing test — it MUST pass now

```bash
<same single-test command from Step 2.3>
```

If it doesn't pass: stop adding more code. Revert your edit. Return to Step 1.3 and re-trace — your root cause hypothesis was wrong.

### 3.4 Run the targeted scope (NOT full suite)

Run the test module(s) covering the file you just changed. Fast, scoped:

```bash
# Python example
uv run pytest <path/to/test_module.py> -q
# TypeScript example
bun test <path/to/test-file.test.ts>
```

Zero failures. If a nearby test in the same module breaks: the fix has a regression in the immediate neighbourhood, fix now.

**The full anti-regression suite runs once at Step 5 (Quality Gate). Running it after every fix iteration is the quick-lane anti-pattern — don't.**

### 3.5 If your first fix doesn't work — one re-attempt, then bail out

If Step 3.3 fails: revert, re-investigate, try once more.

If the second attempt also fails: **stop and tell the user to re-invoke with `/spec`**. Two failed quick-lane attempts means the bug is deeper than the lane is built for. Don't loop here.
