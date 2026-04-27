## Step 11: Sync Rules Back to AGENTS.md — CONDITIONAL

**Only if Step 2 detected an existing AGENTS.md.** Skip entirely otherwise — never create AGENTS.md.

AGENTS.md is the cross-framework agent context file (Codex, Cursor, etc.). When a repo uses both Pilot rules and AGENTS.md, the two should not drift. After rules have been synced (Steps 7–10), offer to re-export the relevant content back into AGENTS.md so other agents see the same context.

### Step 11.1: Always Ask First

AskUserQuestion: "AGENTS.md exists at the repo root. Sync the updated rules back into it so non-Claude agents (Codex, Cursor, etc.) see the same context?"

- **"Yes, sync now"** — proceed to Step 11.2
- **"Show diff first"** — generate the proposed AGENTS.md content, show a diff against the current file, then ask again
- **"Skip"** — leave AGENTS.md untouched, continue to Summary

### Step 11.2: Generate Synced Content

Build the new AGENTS.md from the current rule set:

1. Start with `{slug}-project.md` content (overview, tech stack, directory structure, commands, architecture notes) as the base
2. Append condensed summaries from other root-level rules (`{slug}-conventions.md`, `{slug}-mcp-servers.md`, etc.) — full content for short rules, headings + key bullets for long ones
3. For nested rules (product/team), include a short index pointing to the file paths rather than inlining everything
4. Preserve any user-authored sections from the existing AGENTS.md that aren't covered by rules — detect them by section heading and re-attach under a `## Additional Notes` block
5. Add a one-line auto-generation marker at the top:

   ```markdown
   <!-- Synced from .claude/rules/ by /setup-rules on [Date]. User-authored sections under "Additional Notes" are preserved. -->
   ```

### Step 11.3: Write and Confirm

Write the merged content to AGENTS.md. Report what changed: sections added, sections updated, user content preserved.

**Rules:**

- Never delete AGENTS.md
- Never create AGENTS.md if it didn't already exist
- Always preserve user-authored content not derivable from rules
- Keep AGENTS.md under ~400 lines — link to rule files for deep detail rather than inlining everything
