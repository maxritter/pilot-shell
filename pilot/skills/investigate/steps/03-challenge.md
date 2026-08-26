## Step 3: Challenge the Conclusion

1. Write the provisional answer in one sentence.
2. Ask: **what concrete observation would make this answer false?** Search for that counterexample before finalizing.
3. For a non-obvious or load-bearing claim, perform one orthogonal cross-check:
   - caller against callee;
   - implementation against config/default;
   - source against generated or installed artifact;
   - implementation against a focused test and its assertions;
   - static trace against a bounded runtime command;
   - one subsystem against another independently searched boundary.
4. Run commands only when they are safe, non-mutating, and materially stronger than reading. Avoid formatters, fix modes, code generation, migrations, installers, destructive operations, and external writes. Tests that only create ignored caches are acceptable; compare repository status before and after.
5. When a focused existing test directly exercises the questioned behavior, run that exact test if the environment permits. Reading its source proves the test contract; only a fresh result proves it currently passes. Check that the command actually selected the tests named in the answer.
6. If runtime proof is blocked or disproportionate, keep the static conclusion and name the missing check. Never relabel static analysis as runtime verification.

### Execution Ledger

Immediately before reporting, reconcile the proposed answer against the actual tool transcript:

- **Observed source:** files and exact ranges opened in this invocation.
- **Executed checks:** exact commands that produced a result in this invocation, including exit status and selected test count when available.
- **Inferred:** conclusions derived from observed source but not executed end-to-end.
- **Not verified:** any material boundary left unchecked.

Delete or correct every “ran”, “passed”, “confirmed”, or “verified” sentence that has no matching tool result. Never paste a command into the report as though it already ran.

### Confidence

- **High:** the full relevant path was traced and independently cross-checked; no material contradiction remains.
- **Medium:** the implementation strongly supports the answer, but a boundary or runtime condition was not directly verified.
- **Low:** multiple plausible paths remain or decisive evidence is unavailable. State the competing hypotheses and the missing evidence instead of choosing one.

**Completion:** the provisional conclusion survived a concrete falsification attempt, every execution claim maps to a real result, and remaining uncertainty is precisely bounded.
