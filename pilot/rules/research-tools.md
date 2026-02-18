## Research Tools

### Vexor — Codebase Search (ALWAYS FIRST)

**⛔ Try vexor before Grep, Glob, or any Explore sub-agent.** Finds by intent, not exact text. Zero context cost until you read results.

**Fallback chain:** Vexor → Grep/Glob (exact patterns) → Explore sub-agent (multi-step reasoning only)

Full reference in `cli-tools.md`.

---

### Context7 — Library Documentation

**MANDATORY: Use before writing code with unfamiliar libraries.**

```
resolve-library-id(query="your question", libraryName="package-name")
→ Returns libraryId (e.g., "/npm/react")

query-docs(libraryId="/npm/react", query="specific question")
→ Returns documentation with code examples
```

Use descriptive queries ("how to create and use fixtures in pytest" not "fixtures"). Multiple queries encouraged. If library not found, try variations (`@types/react`, `node:fs`).

### grep-mcp — GitHub Code Search

**Find real-world code examples from 1M+ public repositories.**

Search for literal code patterns, not keywords: `useState(` not `react hooks tutorial`.

```python
searchGitHub(query="FastMCP", language=["Python"])
searchGitHub(query="(?s)useEffect\\(.*cleanup", useRegexp=True, language=["TypeScript"])
searchGitHub(query="getServerSession", repo="vercel/next-auth")
```

Parameters: `query`, `language`, `repo`, `path`, `useRegexp`, `matchCase`

### Web Search / Fetch (MCP)

**Use MCP tools for web access. Built-in WebSearch/WebFetch are blocked by hook.**

| Need | Tool |
|------|------|
| Web search | `web-search/search` (DuckDuckGo/Bing) |
| GitHub README | `web-search/fetchGithubReadme` |
| Fetch full page | `web-fetch/fetch_url` (Playwright, no truncation) |
| Fetch multiple | `web-fetch/fetch_urls` |

Built-in `WebFetch` truncates at ~8KB — MCP tools provide full content.

### GitHub CLI (gh)

**Use `gh` for all GitHub operations.** Authenticated, handles pagination, structured data with `--json` + `--jq`.

```bash
gh pr view 123 --json title,body,files
gh issue view 456
gh pr checks 123
gh api repos/{owner}/{repo}/pulls/123/comments
```

### Tool Selection Guide

| Need | Best Tool |
|------|-----------|
| **Any codebase question** | **Vexor first — always** |
| Exact pattern / known symbol | Grep / Glob (only after vexor misses) |
| Library/framework docs | Context7 |
| Production code examples | grep-mcp |
| Web research | web-search/search |
| GitHub operations | gh CLI |

**⛔ Never reach for Grep, Glob, or an Explore sub-agent before trying vexor.** Vexor finds by intent across any codebase size. Grep/Glob are for exact patterns when you already know what to search for. Explore sub-agents only when multi-step reasoning across many files is unavoidable.
