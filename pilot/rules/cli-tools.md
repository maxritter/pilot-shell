## CLI Tools

### Pilot CLI

The `pilot` binary is at `~/.pilot/bin/pilot`. Do NOT call commands not listed here.

**Session & Context:**

| Command | Purpose |
|---------|---------|
| `pilot check-context --json` | Get context usage % (informational only) |
| `pilot register-plan <path> <status>` | Associate plan with session |

**Worktree:** `pilot worktree detect|create|diff|sync|cleanup|status --json <slug>`

Slug = plan filename without date prefix and `.md`. `create` auto-stashes uncommitted changes.

**License:** `pilot activate <key>`, `pilot deactivate`, `pilot status`, `pilot verify`, `pilot trial --check|--start`

**Other:** `pilot greet`, `pilot statusline`

**Do NOT exist:** ~~`pilot pipe`~~, ~~`pilot init`~~, ~~`pilot update`~~

---

### Probe — Code Search (CLI)

**Secondary search tool.** Use Probe MCP (`search_code`/`extract_code`) first. Fall back to CLI for quick terminal searches when MCP is unavailable.

Probe is installed globally via npm: `npm install -g @probelabs/probe`

```bash
# Semantic search (Elasticsearch syntax)
probe search "authentication AND login" ./src
probe search "error AND handling" ./
probe search "database NOT sqlite" ./

# Extract code block by line or symbol
probe extract src/auth.ts:42
probe extract src/auth.ts#authenticate
probe extract src/auth.ts:10-50

# AST pattern matching
probe query "async function $NAME($$$)" --language typescript
probe query "class $CLASS: def __init__($$$)" --language python
```

**Search options:** `--max-tokens <n>`, `--max-results <n>`, `--allow-tests`, `--format markdown|json`

**File filters (inside query):** `ext:rs`, `file:src/**/*.py`, `dir:tests`

`probe --version` to verify installation.

