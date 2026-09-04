## Code Review Reception

Applies to feedback from users, the `/code-review` skill, review agents, and external tools like CodeRabbit.

Read the whole thing before reacting. **If any item is unclear, stop and ask about every unclear item before implementing anything** — partial understanding produces the wrong fix. Then work one item at a time, testing each: blocking issues (breaks, security) first, then simple fixes, then complex ones.

### How much to trust the source

| Source | Approach |
|--------|----------|
| **User** | Trusted — implement after understanding. Still ask if scope is unclear. |
| **External reviewers** | Verify first: is it correct *for this codebase*, does it break something, is there a reason the code is the way it is, does it conflict with the user's earlier decisions? If it conflicts, stop and discuss before changing anything. |
| **Workflow reviews** (`spec-review`, `changes-review`, `/code-review`, Codex companion) | `must_fix` and `should_fix` → fix immediately, no discussion. `suggestion` → implement if quick. Where the invoking workflow has its own finding→action table, that table wins — out-of-lineage and scope-expanding findings follow its lane rules, not blanket auto-fix. |

### Verify before you agree

When a reviewer says to add or "properly implement" something, search for actual usage first. If nothing calls it, push back — that's YAGNI, not a gap. If something does, implement it properly.

Push back with technical reasoning whenever the suggestion breaks existing behaviour, misses context the reviewer didn't have, is wrong for this stack, or contradicts an architectural decision the user already made. If you pushed back and were wrong, say so factually in one line and move on.

**Respond with the technical substance, not affirmation.** State the requirement, or the fix and what changed. "You're absolutely right", "great point", "thanks for catching that" are all noise where a description of the change belongs.
