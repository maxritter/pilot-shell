---
sidebar_position: 1
title: MCP Servers
description: External context always available to every session
---

# MCP Servers

External context always available to every session.

Six MCP servers are pre-configured and always available. They're lazy-loaded via `ToolSearch` to keep context lean — discovered and called on demand. Add your own in `.mcp.json`, then run `/setup-rules` to generate documentation.

## context7

**Library documentation lookup**

Get up-to-date API docs and code examples for any library or framework. Two-step: resolve the library ID, then query for specific documentation.

```
resolve-library-id(libraryName="react")
query-docs(libraryId="/npm/react", query="useEffect cleanup")
```

## mem-search

**Persistent memory search**

Recall decisions, discoveries, and context from past sessions. Three-layer workflow: search → timeline → get_observations for token efficiency.

```
search(query="authentication flow", limit=5)
timeline(anchor=22865, depth_before=3)
get_observations(ids=[22865, 22866])
```

## web-search

**Web search + article fetching**

Web search via DuckDuckGo, Bing, and Exa (no API keys needed). Also fetches GitHub READMEs, Linux.do articles, and other content sources.

```
search(query="React Server Components 2026", limit=5)
fetchGithubReadme(url="https://github.com/org/repo")
```

## grep-mcp

**GitHub code search**

Find real-world code examples from 1M+ public repositories. Search by literal code patterns, filter by language, repo, or file path. Supports regex.

```
searchGitHub(query="useServerAction", language=["TypeScript"])
searchGitHub(query="FastMCP", language=["Python"])
```

## web-fetch

**Full web page fetching**

Fetch complete web pages via Playwright (handles JS-rendered content, no truncation). Fetches single or multiple URLs in one call.

```
fetch_url(url="https://docs.example.com/api")
fetch_urls(urls=["https://a.com", "https://b.com"])
```

## codebase-memory-mcp

**Code knowledge graph and structural analysis**

Builds a persistent graph of your codebase — functions, classes, call chains, and dependencies. Complements Probe CLI: Probe finds code by intent ("how does auth work?"), codebase-memory finds by structure ("who calls this function?", "what's the blast radius of this change?").

```
search_graph(label="Function", name_pattern=".*Handler.*")
trace_call_path(function_name="processOrder", direction="both", depth=2)
detect_changes(scope="all")
query_graph(query="MATCH (c:Class)-[:DEFINES_METHOD]->(m) RETURN c.name, m.name")
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `search_graph` | Find functions/classes by name pattern with degree filtering (dead code, high fan-out) |
| `trace_call_path` | Who calls X? What does X call? Full call chain with risk classification |
| `detect_changes` | Map git diff to affected symbols and blast radius |
| `query_graph` | Cypher-like graph queries for structural relationships |
| `get_architecture` | Codebase overview — languages, packages, hotspots, entry points |
| `get_code_snippet` | Source code with caller/callee metadata |

**When to use Probe vs codebase-memory-mcp:**

| Question | Best tool |
|----------|-----------|
| "How does authentication work?" | **Probe** — natural language, intent-based search |
| "Who calls this function?" | **codebase-memory** — `trace_call_path` with exact call chain |
| "What's the blast radius of my changes?" | **codebase-memory** — `detect_changes` maps diffs to affected symbols |
| "Find functions matching a pattern" | **codebase-memory** — `search_graph` with regex, label, and degree filters |
| "Find unused/dead code" | **codebase-memory** — `search_graph` with `max_degree=0` |
| "Extract a specific function's source" | **Both** — Probe `extract` for line/symbol, codebase-memory for caller/callee context |

:::info Tool selection
Rules specify the preferred order — Probe CLI first for intent-based codebase questions, codebase-memory-mcp for structural queries (call tracing, impact analysis, dead code), context7 for library API lookups, grep-mcp for production code examples, web-search for current information. The `tool_redirect.py` hook blocks the built-in WebSearch/WebFetch and the Explore agent, redirecting to these alternatives.
:::
