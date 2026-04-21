---

## Step 1: Red Flags — STOP and Follow Process

**This is a gate, not a reminder.** If any of the following applies, you are NOT allowed to proceed to Step 4 until Step 3 is fully complete with root cause traced to file:line.

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "I know this codebase, I don't need to trace it"
- "The fix is obvious, let me skip the test"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place

**Enforcement:** Before writing any task in Step 4, you must be able to answer YES to all of these:

1. Can I state the root cause as `file/path:lineN — function_name() does X but should do Y`?
2. Can I explain WHY this causes the symptom (not just what is wrong)?
3. Have I run `codegraph_callers`/`codegraph_callees` on the function at the root cause?
4. Is my confidence High or Medium (not Low)?

If any answer is NO → return to Step 3 before continuing. No exceptions, no shortcuts — even for "obvious" bugs.
