## Pilot MCP Servers

MCP tools are lazy-loaded via `ToolSearch`. Discover tools by keyword, then call them directly.

```
ToolSearch(query="keyword")        # Discover and load tools by keyword
ToolSearch(query="+server keyword") # Require a specific server prefix
ToolSearch(query="select:full_tool_name") # Load a specific tool by exact name
```

All Pilot MCP servers use the `mcp__plugin_pilot_` prefix. Tools are available immediately after ToolSearch returns them.

---

### mem-search — Persistent Memory

**Purpose:** Search past work, decisions, and context across sessions.

**3-step workflow (token-efficient — never skip to step 3):**

| Step | Tool               | Purpose                                       |
| ---- | ------------------ | --------------------------------------------- |
| 1    | `search`           | Find observations → returns index with IDs    |
| 2    | `timeline`         | Get chronological context around an anchor ID |
| 3    | `get_observations` | Fetch full details for specific IDs only      |

| Tool               | Key Params                                                  |
| ------------------ | ----------------------------------------------------------- |
| `search`           | `query`, `limit`, `type`, `project`, `dateStart`, `dateEnd` |
| `timeline`         | `anchor` (ID) or `query`, `depth_before`, `depth_after`     |
| `get_observations` | `ids` (array, required)                                     |
| `save_memory`      | `text` (required), `title`, `project`                       |

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

| Step | Tool                 | Purpose                          |
| ---- | -------------------- | -------------------------------- |
| 1    | `resolve-library-id` | Find library ID from name        |
| 2    | `query-docs`         | Query docs using the resolved ID |

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

| Tool                  | Purpose                  | Key Params                                                          |
| --------------------- | ------------------------ | ------------------------------------------------------------------- |
| `search`              | Web search               | `query` (required), `limit` (1-50), `engines` (duckduckgo/bing/exa) |
| `fetchGithubReadme`   | Fetch GitHub repo README | `url`                                                               |
| `fetchLinuxDoArticle` | Fetch linux.do article   | `url`                                                               |
| `fetchCsdnArticle`    | Fetch CSDN article       | `url`                                                               |
| `fetchJuejinArticle`  | Fetch Juejin article     | `url`                                                               |

```
ToolSearch(query="+web-search search")

mcp__plugin_pilot_web-search__search(query="Python asyncio best practices 2026", limit=5)
mcp__plugin_pilot_web-search__fetchGithubReadme(url="https://github.com/astral-sh/ruff")
```

---

### grep-mcp — GitHub Code Search

**Purpose:** Find real-world code examples from 1M+ public repositories.

**Single tool:** `searchGitHub`

| Param       | Type              | Description                                               |
| ----------- | ----------------- | --------------------------------------------------------- |
| `query`     | string (required) | Literal code pattern (not keywords)                       |
| `language`  | string[]          | Filter by language: `["Python"]`, `["TypeScript", "TSX"]` |
| `repo`      | string            | Filter by repo: `"vercel/next-auth"`                      |
| `path`      | string            | Filter by file path: `"src/components/"`                  |
| `useRegexp` | boolean           | Regex mode. Prefix with `(?s)` for multiline              |
| `matchCase` | boolean           | Case-sensitive search                                     |

```
ToolSearch(query="+grep-mcp searchGitHub")

mcp__plugin_pilot_grep-mcp__searchGitHub(query="FastMCP", language=["Python"])
mcp__plugin_pilot_grep-mcp__searchGitHub(query="(?s)useEffect\\(.*cleanup", useRegexp=True, language=["TypeScript"])
```

---

### web-fetch — Web Page Fetching

**Purpose:** Fetch full web pages via Playwright (no truncation, handles JS-rendered pages).

| Tool              | Purpose              | Key Params                                                 |
| ----------------- | -------------------- | ---------------------------------------------------------- |
| `fetch_url`       | Fetch single page    | `url` (required), `timeout`, `extractContent`, `maxLength` |
| `fetch_urls`      | Fetch multiple pages | `urls` (array, required), same options as above            |
| `browser_install` | Install Chromium     | `withDeps`, `force`                                        |

```
ToolSearch(query="+web-fetch fetch")

mcp__plugin_pilot_web-fetch__fetch_url(url="https://docs.example.com/api")
mcp__plugin_pilot_web-fetch__fetch_urls(urls=["https://a.com", "https://b.com"])
```

Options: `waitUntil` (load/domcontentloaded/networkidle), `returnHtml`, `waitForNavigation` (for anti-bot pages).

---

### CodeGraph — Code Knowledge Graph

**Purpose:** Semantic code knowledge graph for symbol search, call tracing, impact analysis, and code context retrieval. **The primary code-search tool** — replaces Grep/Glob for any structural query.

**Complements Probe CLI:** Probe finds code by intent ("how does auth work?"). CodeGraph finds by structure ("who calls this?", "what's affected by changing this?").

| Tool                | Purpose                                                    |
| ------------------- | ---------------------------------------------------------- |
| `codegraph_context` | **START HERE** — build relevant code context for a task    |
| `codegraph_explore` | **Deep dive** — full source code from all relevant files in ONE call (replaces dozens of Read/Grep calls) |
| `codegraph_search`  | Find symbols by name (functions, classes, types)           |
| `codegraph_callers` | Find all functions/methods that call a specific symbol     |
| `codegraph_callees` | Find all functions/methods that a symbol calls             |
| `codegraph_impact`  | Analyze blast radius of changing a symbol                  |
| `codegraph_node`    | Get details and source code for a specific symbol          |
| `codegraph_files`   | Get project file structure from the index                  |

**Workflow:** `codegraph_context(task=...)` to orient → `codegraph_search` to find symbols → `codegraph_explore(query="SymbolA SymbolB file.ts")` for deep understanding → `codegraph_callers`/`codegraph_callees` to trace flow → `codegraph_impact` before changes.

**`codegraph_explore` tips:** use specific symbol names and file names as query terms — NOT natural language. Run `codegraph_search` first to discover symbol names. Follow the call budget in the tool description.

**⛔ NEVER pass `projectPath` when searching the current project.** The MCP server defaults to the current project. Passing `projectPath` explicitly triggers a different code path that fails if `.codegraph/` isn't at that exact path. Only use `projectPath` for querying a genuinely different codebase.

```
codegraph_search(query="Handler", kind="function")
codegraph_callers(symbol="processOrder")
codegraph_callees(symbol="processOrder")
codegraph_impact(symbol="processOrder", depth=2)
codegraph_context(task="refactor authentication flow")
codegraph_node(symbol="MyClass", includeCode=true)
```

**⛔ CodeGraph replaces Grep/Glob for code search:**

- `codegraph_context` → task orientation. **MUST use first on every task.**
- `codegraph_explore` → deep code understanding (NOT multiple Read calls).
- `codegraph_search` → symbol search (NOT Grep).
- `codegraph_callers`/`codegraph_callees` → call-flow tracing (NOT Grep). Supplement with Grep as a *completeness check* for indirect/dynamic callers.
- `codegraph_impact` → pre-change blast radius.
- `codegraph_files` → project file structure (NOT Glob/ls).

For intent-based search ("how does authentication work?") and AST-aware extraction by line/symbol, use Probe CLI instead.

---

### Tool Selection Quick Reference

| Need                           | Server/Tool                    | Reference                                   |
| ------------------------------ | ------------------------------ | ------------------------------------------- |
| **Codebase search**            | **Probe CLI** (`probe search`) | `cli-tools.md`                              |
| Extract code block             | Probe CLI (`probe extract`)    | `cli-tools.md`                              |
| AST pattern matching           | Probe CLI (`probe query`)      | `cli-tools.md`                              |
| **Task orientation (FIRST)**   | CodeGraph                      | `codegraph_context`                         |
| Deep code understanding        | CodeGraph                      | `codegraph_explore`                         |
| Call tracing / impact analysis | CodeGraph                      | `codegraph_callers`, `codegraph_impact`     |
| Symbol search                  | CodeGraph                      | `codegraph_search`                          |
| Past work / decisions          | mem-search                     | `search` → `timeline` → `get_observations` |
| Library/framework docs         | context7                       | `resolve-library-id` → `query-docs`        |
| Web search                     | web-search                     | `search`                                    |
| GitHub README                  | web-search                     | `fetchGithubReadme`                         |
| Production code examples       | grep-mcp                       | `searchGitHub`                              |
| Full web page content          | web-fetch                      | `fetch_url` / `fetch_urls`                  |
