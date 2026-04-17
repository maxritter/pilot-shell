---

## Step 2: Understand the Topic

**Start here — clarify what skill to build.**

If the user provided a topic or description, work with it. If not, evaluate the current session (see Session Mode below).

### Topic-Driven Mode (Primary)

1. Restate the topic in your own words — what workflow, pattern, or problem does this skill address?
2. Ask clarifying questions if needed:
   - What triggers this workflow? (specific error, specific task type, specific file pattern)
   - What does success look like? (a command runs successfully, a file is created, a pattern is consistently applied)
   - Is this specific to this project or reusable across projects?
3. **Explore the codebase for relevant patterns:**
   ```bash
   # Find existing patterns related to the topic
   probe search "<topic keywords>" ./ --max-results 5 --max-tokens 2000
   # Extract concrete examples
   probe extract <relevant-file>:<line>
   ```
   Or use `Grep`/`Glob` if Probe is not available.
4. Review any existing documentation or onboarding notes that cover this topic
5. Build understanding of the current state: what works, what's tricky, what's non-obvious

### Session Mode (Fallback — when no topic provided)

Ask yourself:

1. "What did I learn that wasn't obvious before starting?"
2. "Would future-me benefit from having this documented?"
3. "Was the solution non-obvious from docs alone?"
4. "Is this a multi-step workflow I'd repeat?"
5. "Did I query an external service the user will ask about again?"

**If NO to all → Skip, nothing to extract.** External service queries are almost always worth extracting.
