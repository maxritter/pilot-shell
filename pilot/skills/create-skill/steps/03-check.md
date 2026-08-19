## Step 3: Check Existing

```bash
# Canonical project skills and generated Claude Code mirror
ls .agents/skills/ .claude/skills/ 2>/dev/null
rg -i "keyword" .agents/skills/ .claude/skills/ 2>/dev/null

# Repository synchronization health
test -f scripts/sync-agent-assets.mjs && node scripts/sync-agent-assets.mjs --check

<!-- CC-ONLY -->
# Global skills (user + Pilot defaults live in the active Claude config dir)
ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/" 2>/dev/null
rg -i "keyword" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/" 2>/dev/null
<!-- /CC-ONLY -->
<!-- CODEX-START
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

For tracked project skills, treat `.agents/skills/` as authoritative. A tracked match found only in `.claude/skills/` is a migration issue, not a new skill: preserve its unique content in the canonical directory through `/setup-rules` before editing. If both tracked copies exist but differ, stop and resolve the drift before changing the skill. An untracked or ignored Claude-only extension is local and out of scope; do not convert or overwrite it without an explicit request.
