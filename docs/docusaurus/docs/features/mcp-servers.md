---
sidebar_position: 1
title: MCP Servers
description: Pre-configured MCP servers — context7 for library docs, mem-search for persistent memory, web-search, grep-mcp, web-fetch, CodeGraph, and Semble in every session, plus chrome-devtools-mcp.
---

# MCP Servers

External context always available to every session.

Seven MCP servers are pre-configured and lazy-loaded to keep context lean.

- **Claude Code:** configured in `~/.claude.json` (merged from `.mcp.json` during install). Add custom servers in `.mcp.json`.
- **Codex:** configured in `~/.codex/config.toml` under `[mcp_servers.*]`.

Run `/setup-rules` (or `$setup-rules`) to generate documentation for your custom MCP servers. Pilot also installs the `chrome-devtools-mcp` plugin for browser automation.

## chrome-devtools-mcp plugin

**Browser automation via Chrome DevTools Protocol**

Enterprise-friendly fallback when the Claude Code Chrome extension can't be installed. Connects directly to Chrome via CDP — no extension needed. Also provides Lighthouse audits, performance tracing, and device emulation that other browser tools lack. Integrated via [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp).

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

**4-tier browser priority (Claude Code):** Claude Code Chrome extension → Chrome DevTools MCP → playwright-cli → agent-browser. On Codex, the Chrome extension is not available — Chrome DevTools MCP is the preferred tool.

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

Builds a local knowledge graph of runtime code — functions, classes, call chains, and dependencies. CodeGraph exposes one MCP tool: `codegraph_explore`. Give it a task, symbol, file, or structural question and it returns the relevant source sections together with graph context.

```
codegraph_explore(query="processOrder callers and callees")
codegraph_explore(query="authentication flow entry points and blast radius")
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `codegraph_explore` | Orient on runtime code, inspect known symbols, trace callers/callees, and estimate blast radius in one call |

**When to use CodeGraph, Semble, or a direct read:**

These are complementary routes to the source, not interchangeable search engines.

| Question | Best tool |
|----------|-----------|
| "Who calls this known function?" | **CodeGraph** — `codegraph_explore(query="functionName callers")` |
| "What's the blast radius of changing this symbol?" | **CodeGraph** — ask `codegraph_explore` for callers, callees, and impact |
| "How does authentication work?" | **Semble** — natural-language intent search |
| "Where is this setting modified?" | **Semble** — search for the behavior or mutation by intent |
| "Find code similar to this location" | **Semble** — `find_related` discovers parallel implementations |
| "What does this named file, rule, or config say?" | **Direct read** — the file is already known and is authoritative |
| "Find every occurrence of this exact string or symbol" | **Exact repository search** — use `rg` as a completeness check |

:::info Tool selection
If the target is already named, read it directly. If the implementation is unknown, use Semble to find it by intent. Use CodeGraph when the uncertainty is structural: entry points, callers, callees, or blast radius. Then read the concrete source before editing it.

Graph and search indexes are navigation aids. Generated or vendored code can add noise, and dynamic or reflective references may be invisible. For cleanup or deletion, corroborate results with exact repository search and the project's compiler, static analyzers, build, and tests.

On Claude Code, the `tool_redirect.py` hook blocks built-in WebSearch and ordinary WebFetch requests, redirecting to these MCP alternatives automatically. Authenticated `claude.ai/code/artifact/*` and `preview.claude.ai` URLs pass through because only built-in WebFetch has access to the user's Claude session.
:::

Pilot runs CodeGraph locally and disables its optional telemetry. Code, paths, symbols, and queries are not uploaded by the Pilot integration.

## Semble

**Hybrid code search — semantic embeddings + BM25 lexical**

Builds a local CPU index that combines [Model2Vec](https://github.com/MinishLab/model2vec) static code embeddings (`potion-code-16M`) with BM25 lexical scoring, fused via Reciprocal Rank Fusion. Code-aware chunking via [Chonkie](https://github.com/chonkie-inc/chonkie) adds definition boosts, identifier stem matching, and noise penalties. Local indexes update when files change. Integrated via [Semble](https://github.com/MinishLab/semble).

```text
mcp__semble__search(query="authentication flow")
mcp__semble__search(query="deployment guide", content="docs")
mcp__semble__find_related(file_path="src/auth.ts", line=42)
```

**Key capabilities:**

| Tool | Use case |
|------|----------|
| `search` | Natural-language or code search; select `code`, `docs`, `config`, or `all` content when needed |
| `find_related` | Find code similar to a specific `file:line` — useful for parallel implementations and patterns |

**Token efficiency.** Semble returns bounded matched chunks instead of dumping whole file sets. Per-call savings are recorded to `~/.semble/savings.jsonl`. RTK output-compression savings are shown in the Console "Usage" tab (as a share of would-be I/O tokens, per day/week/month).

**Also available as a CLI** (`semble search`, `semble find-related`, `semble savings`) — see the rules doc for the full reference.
