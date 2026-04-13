---
sidebar_position: 1
title: MCP Servers
description: External context always available to every session
---

# MCP Servers

External context always available to every session.

Six MCP servers are pre-configured in `.mcp.json` and lazy-loaded via `ToolSearch` to keep context lean. Pilot also installs the `context-mode` and `chrome-devtools-mcp` Claude plugins alongside them. Add your own MCP entries in `.mcp.json`, then run `/setup-rules` to generate documentation.

## context-mode plugin

**Context window protection — sandbox execution and FTS5 knowledge base**

Keeps large outputs out of your context window. Commands that produce more than ~20 lines of output are routed to a sandboxed executor — only your printed summary enters context. An FTS5 knowledge base indexes content for later search. This ships via the Claude plugin system, not as an entry inside `.mcp.json`. Integrated via [context-mode](https://github.com/mksglu/context-mode).

```
ctx_batch_execute(commands: [...], queries: ["find errors"])
ctx_execute(language: "javascript", code: "const r = await fetch(...)")
ctx_execute_file(path: "data.json", language: "javascript", code: "...")
ctx_search(queries: ["auth flow", "login endpoint"])
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `ctx_batch_execute` | Run multiple commands + search in one call — replaces 30+ individual tool calls |
| `ctx_execute` | Run code in sandbox (JS, Python, shell) — only stdout enters context |
| `ctx_execute_file` | Process a file in sandbox — file content never enters context |
| `ctx_search` | Query the FTS5 knowledge base with multiple queries in one call |
| `ctx_index` | Store content in the knowledge base for later search |

**Routing hooks** automatically intercept tools that produce large output (Bash, Read, Grep, WebFetch) and suggest context-mode alternatives. curl/wget and WebFetch are blocked entirely — use dedicated web-fetch and web-search MCP servers instead.

## chrome-devtools-mcp plugin

**Browser automation via Chrome DevTools Protocol**

Enterprise-friendly fallback when the Claude Code Chrome extension can't be installed. Connects directly to Chrome via CDP — no extension needed. Also provides Lighthouse audits, performance tracing, and device emulation that other browser tools lack. Integrated via [chrome-devtools-mcp](https://github.com/anthropics/chrome-devtools-mcp).

```
list_pages()
navigate_page(type="url", url="http://localhost:3000")
take_snapshot()  // a11y tree with uid refs
click(uid="1_8")
lighthouse_audit(device="desktop")
performance_start_trace(autoStop=true, reload=true)
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `take_snapshot` | A11y tree with uid refs for clicking, filling, hovering |
| `take_screenshot` | Visual capture of viewport or specific element |
| `evaluate_script` | Run JavaScript in the page context |
| `lighthouse_audit` | Accessibility, SEO, and best practices scores |
| `performance_start_trace` | Core Web Vitals (LCP, CLS), performance insights |
| `emulate` | Device viewport, mobile/touch, color scheme, CPU throttling |
| `list_network_requests` | Inspect all network traffic with headers and bodies |
| `list_console_messages` | Read console output filtered by type (error, warn, log) |

**4-tier browser priority:** Claude Code Chrome → Chrome DevTools MCP → playwright-cli → agent-browser. See the `browser-automation.md` rule for detection and fallback logic.

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

## CodeGraph

**Code knowledge graph and structural analysis**

Builds a semantic knowledge graph of your codebase — functions, classes, call chains, and dependencies. Complements Probe CLI: Probe finds code by intent ("how does auth work?"), CodeGraph finds by structure ("who calls this function?", "what's affected by changing this?").

```
codegraph_search(query="Handler", kind="function")
codegraph_callers(symbol="processOrder")
codegraph_callees(symbol="processOrder")
codegraph_impact(symbol="processOrder", depth=2)
codegraph_context(task="refactor authentication flow")
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `codegraph_search` | Find symbols by name — functions, classes, types |
| `codegraph_callers` | Who calls X? Complete caller list with file locations |
| `codegraph_callees` | What does X call? All downstream dependencies |
| `codegraph_impact` | Blast radius — transitive callers and callees affected by a change |
| `codegraph_context` | Task-driven context retrieval — entry points, related symbols, and code |
| `codegraph_node` | Get details and source code for a specific symbol |

**When to use Probe vs CodeGraph:**

| Question | Best tool |
|----------|-----------|
| "How does authentication work?" | **Probe** — natural language, intent-based search |
| "Who calls this function?" | **CodeGraph** — `codegraph_callers` with exact caller list |
| "What's the blast radius of my changes?" | **CodeGraph** — `codegraph_impact` shows transitive affected symbols |
| "Find functions matching a name" | **CodeGraph** — `codegraph_search` with kind filter |
| "Get context for a task" | **CodeGraph** — `codegraph_context` returns entry points and related code |
| "Extract a specific function's source" | **Both** — Probe `extract` for line/symbol, CodeGraph `codegraph_node` for symbol details |

:::info Tool selection
Rules specify the preferred order — Probe CLI first for intent-based codebase questions, CodeGraph for structural queries (call tracing, impact analysis), context7 for library API lookups, grep-mcp for production code examples, web-search for current information. The `tool_redirect.py` hook blocks the built-in WebSearch/WebFetch and the Explore agent, redirecting to these alternatives.
:::
