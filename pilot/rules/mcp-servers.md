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

### codebase-memory-mcp — Code Knowledge Graph

**Purpose:** Structural code analysis, call tracing, dead code detection, and impact analysis via a persistent code graph.

**Complements Probe CLI:** Probe finds code by intent ("how does auth work?"). codebase-memory finds by structure ("who calls this?", "what's dead?", "what's the blast radius?").

**Key tools:**

| Tool               | Purpose                                                         |
| ------------------ | --------------------------------------------------------------- |
| `index_repository` | Parse repo into graph (once — auto-sync keeps it fresh)         |
| `search_graph`     | Find functions/classes by name pattern, label, degree           |
| `trace_call_path`  | BFS call chain — who calls X, what does X call                  |
| `detect_changes`   | Map git diff to affected symbols + blast radius                 |
| `get_code_snippet` | Source code + caller/callee metadata                            |
| `query_graph`      | Cypher-like graph queries                                       |
| `get_architecture` | Codebase overview (languages, packages, hotspots, entry points) |
| `search_code`      | Grep-like text search within indexed files                      |

**Workflow:** Check `index_status` → `index_repository` if needed → `search_graph` / `trace_call_path` / `query_graph`

```
ToolSearch(query="+codebase-memory-mcp search")

mcp__plugin_pilot_codebase-memory-mcp__search_graph(label="Function", name_pattern=".*Handler.*")
mcp__plugin_pilot_codebase-memory-mcp__trace_call_path(function_name="ProcessOrder", direction="both", depth=2)
mcp__plugin_pilot_codebase-memory-mcp__detect_changes(scope="all")
mcp__plugin_pilot_codebase-memory-mcp__get_code_snippet(qualified_name="MyClass", auto_resolve=true, include_neighbors=true)
```

**Primary use cases (Probe can't do these):**

- **`trace_call_path`** — complete caller/callee graph with risk classification. The highest-value tool. Use before modifying any function during `/spec`.
- **`detect_changes`** — maps git diff to affected symbols + blast radius. Use during planning.
- Dead code detection (`search_graph` with `max_degree=0, exclude_entry_points=true`) — good starting point, but expect false positives from dynamic dispatch and CLI handlers.

**Lower-value features (use selectively):**

- `get_architecture` — hotspots/clusters polluted by minified JS bundles in mixed codebases. Useful if your project is pure Python/Go/TS source.
- `query_graph` (Cypher) — powerful for cross-service HTTP edges and interface implementations.
- `FILE_CHANGES_WITH` coupling — mostly shows obvious src↔test pairs. More useful in large, interconnected codebases.

**When Probe is better:**

- Intent-based search ("how does authentication work?")
- Natural language queries
- AST-aware code extraction by line/symbol

Full reference in skills: `codebase-memory-reference`, `codebase-memory-tracing`, `codebase-memory-exploring`, `codebase-memory-quality`.

---

### Tool Selection Quick Reference

| Need                           | Server/Tool                    | Reference                                  |
| ------------------------------ | ------------------------------ | ------------------------------------------ |
| **Codebase search**            | **Probe CLI** (`probe search`) | `cli-tools.md`                             |
| Extract code block             | Probe CLI (`probe extract`)    | `cli-tools.md`                             |
| AST pattern matching           | Probe CLI (`probe query`)      | `cli-tools.md`                             |
| Call tracing / impact analysis | codebase-memory-mcp            | `trace_call_path`, `detect_changes`        |
| Dead code / quality analysis   | codebase-memory-mcp            | `search_graph` with degree filters         |
| Structural graph queries       | codebase-memory-mcp            | `query_graph` (Cypher)                     |
| Past work / decisions          | mem-search                     | `search` → `timeline` → `get_observations` |
| Library/framework docs         | context7                       | `resolve-library-id` → `query-docs`        |
| Web search                     | web-search                     | `search`                                   |
| GitHub README                  | web-search                     | `fetchGithubReadme`                        |
| Production code examples       | grep-mcp                       | `searchGitHub`                             |
| Full web page content          | web-fetch                      | `fetch_url` / `fetch_urls`                 |
