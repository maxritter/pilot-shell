## Systematic Debugging

**Rule:** No fixes without root cause investigation. Complete phases sequentially.

### Tools for Debugging Research

| Tool | When to Use |
|------|-------------|
| **Context7** | Library/framework API lookup (see `context7-docs.md` for full docs) |
| **Vexor** | Find similar patterns in codebase (`vexor search "error handling"`) |
| **grep-mcp** | Find how others solved similar issues (`searchGitHub(query="error pattern")`) |

**Context7 Quick Reference:**
```
resolve-library-id(query="descriptive question", libraryName="lib")
query-docs(libraryId="/npm/lib", query="specific question")
```
Both parameters required. Descriptive queries enable server-side reranking.

### Cognitive Biases That Derail Debugging

| Bias | Trap | Antidote |
|------|------|----------|
| **Confirmation** | Only look for evidence supporting your hypothesis | Actively seek disconfirming evidence: "What would prove me wrong?" |
| **Anchoring** | First explanation becomes your anchor | Generate 3+ independent hypotheses before investigating any |
| **Availability** | Recent bugs → assume similar cause | Treat each bug as novel until evidence says otherwise |
| **Sunk Cost** | Spent ages on one path, keep going despite evidence | "If I started fresh right now, would I take this same path?" |

### Meta-Debugging: When You Wrote the Code

When debugging code you wrote (or that an earlier session wrote), you're fighting your own mental model.

- **Treat your code as foreign** — Read it as if someone else wrote it
- **Your design decisions are hypotheses, not facts** — The code's behavior is truth; your mental model is a guess
- **Prioritize code you touched** — If you modified 100 lines and something breaks, those are prime suspects
- **The hardest admission:** "I implemented this wrong" — not "requirements were unclear"

### Phase 1: Root Cause Investigation

Complete ALL before proposing fixes:

1. **Read errors completely** - Full stack traces, line numbers, error codes
2. **Reproduce consistently** - Document exact steps; if not reproducible, gather more data
3. **Check recent changes** - git diff, new dependencies, config changes
4. **Instrument multi-component systems** - Log at each boundary (input/output/state), run once to identify failing layer

### Phase 2: Pattern Analysis

1. **Find working examples** - Similar working code in codebase
2. **Compare against references** - Read reference implementations completely, every line
3. **Identify ALL differences** - Include small differences
4. **Understand dependencies** - Required components, settings, assumptions

### Phase 3: Hypothesis and Testing

1. **Form specific, falsifiable hypothesis** - Not "something is wrong with state" but "state resets because component remounts on route change"
2. **Test with minimal change** - One variable at a time. Multiple changes = no idea what mattered
3. **Verify result** - Worked → Phase 4; Failed → new hypothesis, return to step 1
4. **Acknowledge uncertainty** - Say so explicitly, never guess

**When to restart from scratch:** 3+ fixes that didn't work, you can't explain the current behavior, or the fix works but you don't know why (that's luck, not debugging).

### Phase 4: Implementation

1. **Create failing test first** - TDD principles
2. **Implement single fix** - ONE change, no bundled improvements
3. **Verify completely** - New test passes, no regressions
4. **If fix fails:**
   - < 3 attempts → Return to Phase 1 with new information
   - ≥ 3 attempts → **Question architecture** (each fix reveals new problems = wrong pattern)

### Red Flags → STOP, Return to Phase 1

- "Quick fix for now" / "Just try X"
- Multiple changes at once
- "Skip the test" / "Probably X"
- "Don't fully understand but might work"
- Proposing fixes before tracing data flow
- 2+ failed fixes and wanting "one more attempt"

### User Signals You're Wrong

- "Is that not happening?" → You assumed without verifying
- "Stop guessing" → Proposing fixes without understanding
- "We're stuck?" → Your approach isn't working

### Quick Reference

| Phase | Activities | Criteria |
|-------|------------|----------|
| 1. Root Cause | Read errors, reproduce, check changes, instrument | Understand WHAT and WHY |
| 2. Pattern | Find working examples, compare | Identify differences |
| 3. Hypothesis | Form theory, test minimally | Confirmed or new hypothesis |
| 4. Implementation | Create test, fix, verify | Bug resolved, tests pass |

**3+ failed fixes = architectural problem. Question the pattern, don't fix again.**
