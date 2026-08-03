## Step 3: Check Existing

```bash
<!-- CC-ONLY -->
# Project skills
ls .claude/skills/ 2>/dev/null
rg -i "keyword" .claude/skills/ 2>/dev/null
# Global skills (user + Pilot defaults live in the active Claude config dir)
ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/" 2>/dev/null
rg -i "keyword" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/" 2>/dev/null
<!-- /CC-ONLY -->
<!-- CODEX-START
# Project skills
ls .agents/skills/ 2>/dev/null
rg -i "keyword" .agents/skills/ 2>/dev/null
# Global skills (user + Pilot defaults all live at ~/.agents/skills/)
ls ~/.agents/skills/ 2>/dev/null
rg -i "keyword" ~/.agents/skills/ 2>/dev/null
CODEX-END -->
```

| Found | Action |
|-------|--------|
| Nothing related | Create new |
| Same trigger/fix | Update existing (bump version) |
| Partial overlap | Update with new variant |
