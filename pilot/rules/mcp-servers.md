## Pilot MCP Servers

MCP tools are lazy-loaded. Discover by keyword, then call directly — **the discovery tool returns the full parameter schema**, so it, not this file, is the reference for how to call anything below.

<!-- CC-ONLY -->
```
ToolSearch(query="keyword")               # discover and load by keyword
ToolSearch(query="+server keyword")       # require a specific server prefix
ToolSearch(query="select:full_tool_name") # load one tool by exact name
```
<!-- /CC-ONLY -->
<!-- CODEX-START
```
tool_search(query="keyword")              # discover and load by keyword
```

Tools may instead be registered at session start — check your available tools.
CODEX-END -->

Tools resolve as `mcp__<server>__<tool>` (e.g. `mcp__semble__search`, `mcp__codegraph__codegraph_explore`) and are callable the moment discovery returns them.

### Which server for which question

| Need | Server |
|------|--------|
| Structure — orientation, symbols, callers/callees, blast radius, deep-dive | **CodeGraph** `codegraph_explore` — one call returns verbatim source + call path + impact |
| Intent — concepts, feature areas, "where is X modified", cross-cutting or cross-language | **Semble** `search` |
| Code similar to a known `file:line` | **Semble** `find_related` (no CodeGraph equivalent) |
| Past work, decisions, prior context | **mem-search** |
| Library / framework docs | **context7** |
| Web search, GitHub READMEs | **web-search** |
| Full page content, JS-rendered pages | **web-fetch** |
| Real-world code in public repos | **grep-mcp** |

CodeGraph and Semble are co-primary: reach for one of them before Grep/Glob on any code-search task, and drop to Grep to verify their results or find exact text in a known file.

<!-- CODEX-START
**Codex proportionality:** skip CodeGraph for named paths, docs, rules, config, UI copy, and reviews of a known diff — read the file or `git diff` directly. If the first graph result is irrelevant, pivot to Semble or direct reads rather than re-querying.
CODEX-END -->

### The two contracts worth stating

**⛔ Never pass `projectPath` to CodeGraph for the current project.** The server defaults correctly; passing it takes a different code path that fails unless `.codegraph/` sits at exactly that path. Use it only for a genuinely different codebase.

**mem-search is a 3-step workflow — never skip to step 3.** `search` returns an index of IDs → `timeline` gives context around an anchor → `get_observations` fetches full detail for the filtered IDs only. Going straight to `get_observations` pulls far more than you need. `save_memory` records findings; observation types are `bugfix`, `feature`, `refactor`, `discovery`, `decision`, `change`.

Semble is also a CLI (`semble search`, `semble find-related`) — see `cli-tools.md`.
