## Step 6: Per-Task DoD Audit & Not-Verified Acknowledgment

### 6.1 Per-Task DoD Audit

**If runtime profile is Minimal:** Skip.

For EACH task, verify its Definition of Done criteria against the running program with evidence (command output, API response, screenshot).

If any criterion unmet: fix inline if possible, or add task and loop back.

### 6.2 Not Verified Acknowledgment

List what was **NOT** verified and why. Include in the verification report (Step 10). Every gap must have a reason:

| Not Verified | Reason |
|-------------|--------|
| [criterion or scenario] | No test environment / Out of scope / Untestable statically / Deferred |

"None — all criteria have automated verification" is a valid answer if true. Do not omit this section: absence of acknowledged gaps ≠ absence of real gaps.
