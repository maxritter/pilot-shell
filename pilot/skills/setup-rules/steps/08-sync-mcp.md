## Step 8: Sync MCP Rules

**Document user-configured MCP servers.** Skip framework-provided servers (e.g., Pilot core: context7, mem-search, web-search, web-fetch, grep-mcp) — only document servers the user added themselves.

### Step 8.1: Discover

Parse `.mcp.json`, exclude framework-provided servers (Pilot core servers if present: context7, mem-search, web-search, web-fetch, grep-mcp).

### Step 8.2: Smoke-Test

For each user server:

1. `ToolSearch(query="+server-name keyword")` to discover tools
2. Call 1-2 read-only tools per server as a connectivity check (**safety: only read-only tools**) — no need to test every tool, just confirm the server responds
3. Record per-server: ✅ connected | ⚠️ partial (note issues) | ❌ unreachable
4. Report health check:
   ```
   ✅ polar — connected, tools responding
   ⚠️ typefully — connected, 1 permission error on write tools
   ❌ my-api — connection refused
   ```
5. If issues: AskUserQuestion "Document working servers only" | "Document all with status notes" | "Skip MCP sync"

### Step 8.3: Document

Compare against existing `{slug}-mcp-servers.md`. If changes detected, ask user: "Update all" | "Review each" | "Skip"

Also look for a legacy unscoped `mcp-servers.md` — if found, migrate content into `{slug}-mcp-servers.md` and delete the old file.

### Step 8.4: Write

**MCP tools are self-describing** — Claude Code already gets tool names, descriptions, and schemas when it connects to a server. Do NOT enumerate individual tools or create per-tool tables. That information is redundant and wastes context tokens every session.

**Focus on behavioral guidance** — what the rules should capture is context that tool descriptions alone cannot provide: when to consult the server, how it fits into the project's workflow, and decision-making guidance.

Create/update `.claude/rules/{slug}-mcp-servers.md`:

```markdown
## [server-name]

**Purpose:** [What this server provides — one line]
**Status:** ✅ All working | ⚠️ Partial (note which tools have issues) | ❌ Broken

**Consult this MCP when:**
- [Situation where this server should be used instead of alternatives]
- [Decision point where the server provides relevant context]
- [Workflow step where consulting this server prevents mistakes]

**Usage:** `ToolSearch(query="+server-name keyword")` then call the discovered tools directly.
```

**Do NOT include:**
- Per-tool tables (`| Tool | Description |`) — tools describe themselves
- Tool parameter documentation — schemas are provided by the server
- Usage examples for individual tools — Claude reads the tool schema

**DO include:**
- When to consult vs. when NOT to (decision boundaries)
- Project-specific workflow context (e.g., "check this before upgrading @dialpad/ deps")
- Gotchas or non-obvious behaviors specific to this project's usage
- Required env vars or auth setup if not obvious from server config

**Skip if:** no `.mcp.json`, no user-added servers, user declines.
