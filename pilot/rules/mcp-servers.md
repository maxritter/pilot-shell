## Pilot MCP Servers

MCP tools are lazy-loaded via `ToolSearch`. Discover tools by keyword, then call them directly.

```
ToolSearch(query="keyword")        # Discover and load tools by keyword
ToolSearch(query="+server keyword") # Require a specific server prefix
ToolSearch(query="select:full_tool_name") # Load a specific tool by exact name
```

All Pilot MCP servers use the `mcp__plugin_pilot_` prefix. Tools are available immediately after ToolSearch returns them.

---

### probe — Code Search Agent

**Purpose:** Semantic codebase search and AST-aware code extraction. Primary search tool for understanding code by intent.

**⛔ Use Probe MCP FIRST for all codebase searches.** Fallback: Probe CLI → Grep/Glob.

| Tool | Purpose |
|------|---------|
| `search_code` | Semantic search — natural language questions about the codebase |
| `extract_code` | AST-aware code extraction by file path, line, or symbol name |

```
# Discover tools
ToolSearch(query="+probe search")

# Semantic search — ask questions about the codebase
mcp__plugin_pilot_probe__search_code(query="how does authentication work?")
mcp__plugin_pilot_probe__search_code(query="where is config loaded", path="/abs/path/to/project")

# Extract code by line, range, or symbol
mcp__plugin_pilot_probe__extract_code(
  path="/abs/path/to/project",
  files=["src/auth.ts#authenticate", "src/config.ts:42", "src/utils.ts:10-50"]
)
```

`extract_code` formats: `"file.ts"` (whole file), `"file.ts:42"` (block at line), `"file.ts:10-50"` (range), `"file.ts#symbolName"` (by symbol).

**MCP config** (already in `pilot/.mcp.json`):
```json
{"probe": {"command": "npx", "args": ["-y", "@probelabs/probe@latest", "agent", "--mcp"]}}
```

---

### mem-search — Persistent Memory

**Purpose:** Search past work, decisions, and context across sessions.

**3-step workflow (token-efficient — never skip to step 3):**

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `search` | Find observations → returns index with IDs |
| 2 | `timeline` | Get chronological context around an anchor ID |
| 3 | `get_observations` | Fetch full details for specific IDs only |

| Tool | Key Params |
|------|------------|
| `search` | `query`, `limit`, `type`, `project`, `dateStart`, `dateEnd` |
| `timeline` | `anchor` (ID) or `query`, `depth_before`, `depth_after` |
| `get_observations` | `ids` (array, required) |
| `save_memory` | `text` (required), `title`, `project` |

**Types:** `bugfix`, `feature`, `refactor`, `discovery`, `decision`, `change`

```
# Discover tools
ToolSearch(query="+mem-search search")

# Then call directly
mcp__plugin_pilot_mem-search__search(query="authentication flow", limit=5)
mcp__plugin_pilot_mem-search__timeline(anchor=22865, depth_before=3, depth_after=3)
mcp__plugin_pilot_mem-search__get_observations(ids=[22865, 22866])
mcp__plugin_pilot_mem-search__save_memory(text="Important finding", title="Short title")
```

---

### context7 — Library Documentation

**Purpose:** Fetch up-to-date docs and code examples for any library/framework.

**2-step workflow:**

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `resolve-library-id` | Find library ID from name |
| 2 | `query-docs` | Query docs using the resolved ID |

```
ToolSearch(query="+context7 resolve")

mcp__plugin_pilot_context7__resolve-library-id(query="how to use fixtures", libraryName="pytest")
# → returns libraryId like "/pypi/pytest"
mcp__plugin_pilot_context7__query-docs(libraryId="/pypi/pytest", query="how to create and use fixtures")
```

Use descriptive queries. Max 3 calls per question per tool.

---

### web-search — Web Search

**Purpose:** Search the web via DuckDuckGo, Bing, or Exa (no API keys needed).

| Tool | Purpose | Key Params |
|------|---------|------------|
| `search` | Web search | `query` (required), `limit` (1-50), `engines` (duckduckgo/bing/exa) |
| `fetchGithubReadme` | Fetch GitHub repo README | `url` |
| `fetchLinuxDoArticle` | Fetch linux.do article | `url` |
| `fetchCsdnArticle` | Fetch CSDN article | `url` |
| `fetchJuejinArticle` | Fetch Juejin article | `url` |

```
ToolSearch(query="+web-search search")

mcp__plugin_pilot_web-search__search(query="Python asyncio best practices 2026", limit=5)
mcp__plugin_pilot_web-search__fetchGithubReadme(url="https://github.com/astral-sh/ruff")
```

---

### grep-mcp — GitHub Code Search

**Purpose:** Find real-world code examples from 1M+ public repositories.

**Single tool:** `searchGitHub`

| Param | Type | Description |
|-------|------|-------------|
| `query` | string (required) | Literal code pattern (not keywords) |
| `language` | string[] | Filter by language: `["Python"]`, `["TypeScript", "TSX"]` |
| `repo` | string | Filter by repo: `"vercel/next-auth"` |
| `path` | string | Filter by file path: `"src/components/"` |
| `useRegexp` | boolean | Regex mode. Prefix with `(?s)` for multiline |
| `matchCase` | boolean | Case-sensitive search |

```
ToolSearch(query="+grep-mcp searchGitHub")

mcp__plugin_pilot_grep-mcp__searchGitHub(query="FastMCP", language=["Python"])
mcp__plugin_pilot_grep-mcp__searchGitHub(query="(?s)useEffect\\(.*cleanup", useRegexp=True, language=["TypeScript"])
```

---

### web-fetch — Web Page Fetching

**Purpose:** Fetch full web pages via Playwright (no truncation, handles JS-rendered pages).

| Tool | Purpose | Key Params |
|------|---------|------------|
| `fetch_url` | Fetch single page | `url` (required), `timeout`, `extractContent`, `maxLength` |
| `fetch_urls` | Fetch multiple pages | `urls` (array, required), same options as above |
| `browser_install` | Install Chromium | `withDeps`, `force` |

```
ToolSearch(query="+web-fetch fetch")

mcp__plugin_pilot_web-fetch__fetch_url(url="https://docs.example.com/api")
mcp__plugin_pilot_web-fetch__fetch_urls(urls=["https://a.com", "https://b.com"])
```

Options: `waitUntil` (load/domcontentloaded/networkidle), `returnHtml`, `waitForNavigation` (for anti-bot pages).

---

### Tool Selection Quick Reference

| Need | Server | Tool |
|------|--------|------|
| **Codebase search** | **probe** | `search_code` |
| Extract code block | probe | `extract_code` |
| Past work / decisions | mem-search | `search` → `timeline` → `get_observations` |
| Library/framework docs | context7 | `resolve-library-id` → `query-docs` |
| Web search | web-search | `search` |
| GitHub README | web-search | `fetchGithubReadme` |
| Production code examples | grep-mcp | `searchGitHub` |
| Full web page content | web-fetch | `fetch_url` / `fetch_urls` |
