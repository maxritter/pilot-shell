---

## Step 1: Red Flags — STOP and Follow Process

**This is a gate, not a reminder.** If any red flag below applies, you are NOT allowed to proceed to Step 4 until Step 3 is fully complete with root cause traced to file:line.

### Internal red flags (your own thoughts)

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "I know this codebase, I don't need to trace it"
- "The fix is obvious, let me skip the test"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple bugs have root causes too. The process is fast for simple bugs. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write the test after confirming the fix works" | Untested fixes don't stick. Test first proves the bug exists. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

### User signals you're off track

If the user says any of these, STOP and return to investigation — you assumed without verifying:

- "Stop guessing"
- "Is that not happening?" / "Will it show us…?"
- "Ultrathink this"
- "We're stuck?" (frustrated tone)
- Any redirect implying "you should have checked first"

### Enforcement

Before writing any task in Step 4, you must answer YES to all of these:

1. Can I state the root cause as `file/path:lineN — function_name() does X but should do Y`?
2. Can I explain WHY this causes the symptom (not just what is wrong)?
3. Is my confidence High or Medium (not Low)?

If any answer is NO → return to Step 3. No exceptions, even for "obvious" bugs. Call-graph traversal (`codegraph_callers`/`codegraph_callees`) is required only for cross-component bugs (Step 3.3) — not for local fixes.
