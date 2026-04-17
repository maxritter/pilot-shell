---

## Step 4: Create Skill

**Create the skill directory and SKILL.md:**

```bash
# Project scope — skill lives in this repo's .claude/skills/
mkdir -p .claude/skills/{slug}-{name}
# Write SKILL.md (see template in Step 1)

# Global scope — skill applies across all projects
mkdir -p ~/.claude/skills/{slug}-{name}
# Write SKILL.md
```

Skills in `.claude/skills/` (project) or `~/.claude/skills/` (global) are automatically available to Claude — no sync step needed.

Edit the created `SKILL.md` with the skill content using the template from Step 1.

**Portability checklist** — skills are shared with users who may NOT have Pilot Shell:

- **Only use built-in Claude Code tools** in skill instructions: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Agent`, `WebFetch`, `WebSearch`, `Notebook`, `LSP`, `TodoRead`/`TodoWrite`
- **Never reference Pilot-specific tools:** `probe search/extract/query`, `agent-browser`, `pilot` CLI, Pilot MCP servers (`mem-search`, `context7`, `grep-mcp`, `web-fetch`, `web-search`)
- **Substitute with built-in equivalents:** `probe search` → `Grep`/`Glob`, `agent-browser` → Claude Code Chrome (`mcp__claude-in-chrome__*`) or `Bash` with `npx agent-browser`, web fetch → `WebFetch`
- If a skill genuinely requires a non-standard tool, document it as a prerequisite in the skill body (not silently assume it exists)

**Determinism checklist** — maximize reliability:

- Prefer exact commands over descriptions (`run prettier --write .` not "format the code")
- Prefer scripts over multi-step instructions (reference `scripts/deploy.sh` not 5 prose steps)
- Use explicit values over judgment (`block files > 100KB` not "block large files")
- For high-risk operations (DB migrations, deploys): exact commands, validation steps, rollback plan
- For low-risk operations (code review, docs): general guidelines, let AI use judgment

**One skill = one purpose.** If the skill handles review AND testing AND deployment, split it.

**Security:** Skills must not contain malware, exploit code, or content that could compromise system security. A skill's contents should not surprise the user in their intent. Don't create skills designed to facilitate unauthorized access or data exfiltration.
