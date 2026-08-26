## Step 1: Frame the Exact Claim

1. Turn the user's wording into one answerable question or falsifiable claim. Preserve explicit scope such as a branch, platform, configuration, or runtime.
   When the user enumerates cases, record every case as a required answer branch; none may first appear only in the detailed trace.
2. Check the current repository state before interpreting behavior:
   - Identify the repository root and current branch when available.
   - Read `git status --short --untracked-files=all` and the relevant diff without changing either.
   - Treat uncommitted files as current behavior, while distinguishing them from the committed baseline when that difference matters.
3. Respect repository guidance already loaded. In an isolated explorer context, read the nearest applicable `AGENTS.md`, `CLAUDE.md`, and path-scoped rules after the likely target files are known.
4. Separate discoverable facts from missing user intent. Explore first. Ask one concise question only when an identifier, input, environment, or expected behavior cannot be recovered safely from the workspace and would materially change the answer.

**Completion:** the exact question, relevant version/worktree scope, and any genuinely missing input are known.
