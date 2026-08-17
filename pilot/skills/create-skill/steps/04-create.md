## Step 4: Create Skill

**Create the skill directory and SKILL.md:**

<!-- CC-ONLY -->
```bash
# Project scope — skill lives in this repo's .claude/skills/
mkdir -p .claude/skills/{slug}-{name}
# Write SKILL.md (see template in Step 1)

# Global scope — skill applies across all projects
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills/{slug}-{name}
# Write SKILL.md
```

Skills in `.claude/skills/` (project) or `~/.claude/skills/` (global) are automatically available to Claude — no sync step needed.
<!-- /CC-ONLY -->
<!-- CODEX-START
```bash
# Project scope — skill lives in this repo's .agents/skills/
mkdir -p .agents/skills/{slug}-{name}
# Write SKILL.md

# Global scope — skill applies across all projects
mkdir -p ~/.agents/skills/{slug}-{name}
# Write SKILL.md
```

Skills in `.agents/skills/` (project) or `~/.agents/skills/` (global) are available to Codex — no sync step needed.
CODEX-END -->

Edit the created `SKILL.md` with the skill content using the template from Step 1.

**Portability checklist** — skills are shared with users who may NOT have Pilot Shell:

<!-- CC-ONLY -->
- **Only use built-in Claude Code tools** in skill instructions: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Agent`, `WebFetch`, `WebSearch`, `Notebook`, `LSP`, `TodoRead`/`TodoWrite`
- **Never reference Pilot-specific tools:** `semble search/find-related` (CLI or MCP), `agent-browser`, `pilot` CLI, Pilot MCP servers (`mem-search`, `context7`, `grep-mcp`, `web-fetch`, `web-search`)
- **Substitute with built-in equivalents:** `semble search` → `Grep`/`Glob`, `agent-browser` → Claude Code Chrome (`mcp__claude-in-chrome__*`) or `Bash` with `npx agent-browser`, web fetch → `WebFetch`
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Use capabilities from the current Codex tool schema, not a hardcoded namespace.** Core file/shell tools (`Read`, `apply_patch`, `Bash`, `Grep`, `Glob`) are portable. Agent and web tools may also be exposed; name their required capability and tell the skill to use the current schema's parameters.
- **Never reference Pilot-specific tools:** `semble search/find-related` (CLI or MCP), `agent-browser`, `pilot` CLI, Pilot MCP servers (`mem-search`, `context7`, `grep-mcp`, `web-fetch`, `web-search`)
- **Provide a fallback for optional capabilities:** `semble search` → `Grep`/`Glob`; unavailable agent tools → direct execution or `codex exec`; unavailable web tools → `curl` when network access permits.
CODEX-END -->
- If a skill genuinely requires a non-standard tool, document it as a prerequisite in the skill body (not silently assume it exists)

**Determinism checklist** — maximize reliability:

- Prefer exact commands over descriptions (`run prettier --write .` not "format the code")
- Prefer scripts over multi-step instructions (reference `scripts/deploy.sh` not 5 prose steps)
- Use explicit values over judgment (`block files > 100KB` not "block large files")
- For high-risk operations (DB migrations, deploys): exact commands, validation steps, rollback plan
- For low-risk operations (code review, docs): general guidelines, let AI use judgment

**One skill = one purpose.** If the skill handles review AND testing AND deployment, split it.

**Security:** Skills must not contain malware, exploit code, or content that could compromise system security. A skill's contents should not surprise the user in their intent. Don't create skills designed to facilitate unauthorized access or data exfiltration.
