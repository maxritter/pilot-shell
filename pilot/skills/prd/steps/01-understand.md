---

## Step 1: Understand the Idea

1. **Restate the idea** in your own words — confirm you understand what the user is thinking
2. **Explore the project context with CodeGraph** — start with `codegraph_context(task="<idea description>")` to discover relevant entry points, symbols, and existing code. Use `codegraph_search` + `codegraph_explore` for deeper understanding of specific areas. Use `codegraph_files` to understand project structure. Check docs and recent commits for additional context.
3. **Identify the core problem** — what problem does this solve? For whom? Why now?
4. **Scope check — is this one PRD, or several?** If the request spans multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag it now. Do not spend the rest of the workflow refining details of a project that needs to be split first.

   When the project is too large for a single PRD, help the user decompose:
   - List the independent pieces and how they relate
   - Suggest a build order (what unblocks what)
   - Pick **one** sub-project to PRD now — the rest become follow-up PRDs

   Use `AskUserQuestion` to confirm the chosen sub-project before continuing.

Do NOT jump to solutions. Understand the problem space first.
