## Research Tools

### Search Priority

**⛔ Probe MCP first, always.** Finds by intent, not exact text. Zero context cost until you read results.

**Fallback chain:** Probe MCP (`search_code`) → Probe CLI → Grep/Glob (exact patterns) → Explore sub-agent (multi-step reasoning only)

Full Probe reference in `cli-tools.md` (CLI) and `mcp-servers.md` (MCP). Full MCP tool reference in `mcp-servers.md`.

### Tool Selection Guide

| Need | Tool | Notes |
|------|------|-------|
| **Codebase search** | **Probe MCP** (`search_code`) | Always first. Semantic, by intent. |
| Exact pattern / known symbol | Grep / Glob | Only after Probe misses |
| Extract specific code block | Probe MCP (`extract_code`) | AST-aware, by line or symbol name |
| Library/framework docs | Context7 (MCP) | `resolve-library-id` → `query-docs` |
| Production code examples | grep-mcp (MCP) | Literal code patterns, not keywords |
| Web search | web-search (MCP) | DuckDuckGo/Bing/Exa |
| Full web page | web-fetch (MCP) | Playwright-based, handles JS |
| GitHub README | web-search (MCP) | `fetchGithubReadme` |
| GitHub operations | `gh` CLI | Authenticated, `--json` + `--jq` |
| Past work / decisions | mem-search (MCP) | `search` → `timeline` → `get_observations` |

### ⛔ Web Search/Fetch

**NEVER use built-in `WebFetch` or `WebSearch` — blocked by hook.** Use MCP alternatives via `ToolSearch`:

| Need | ToolSearch query |
|------|-----------------|
| Web search | `+web-search search` |
| GitHub README | `+web-search fetch` |
| Fetch page | `+web-fetch fetch` |
