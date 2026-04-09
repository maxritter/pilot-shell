# context-mode — Mandatory Routing Rules

You have context-mode MCP tools available. These rules protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## Think in Code — MANDATORY

When you need to analyze, count, filter, compare, search, parse, transform, or process data: **write code** that does the work via `ctx_execute(language, code)` and `console.log()` only the answer. Do NOT read raw data into context to process mentally. Your role is to PROGRAM the analysis, not to COMPUTE it. Write robust, pure JavaScript — no npm dependencies, only Node.js built-ins (`fs`, `path`, `child_process`). Always use `try/catch`, handle `null`/`undefined`. One script replaces ten tool calls and saves 100x context.

## BLOCKED Commands

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error. Do NOT retry.
Instead use:
- Web search MCP: `ToolSearch(query="+web-search search")` then call `mcp__plugin_pilot_web-search__search`
- Web fetch MCP: `ToolSearch(query="+web-fetch fetch")` then call `mcp__plugin_pilot_web-fetch__fetch_url`
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` for API calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `http.get(` is intercepted. Do NOT retry with Bash.
Instead use `ctx_execute(language, code)` to run HTTP calls in sandbox.

### WebFetch — BLOCKED
WebFetch calls are denied entirely. Use web-fetch MCP: `ToolSearch(query="+web-fetch fetch")` then call `mcp__plugin_pilot_web-fetch__fetch_url(url="...")`.

## REDIRECTED Tools

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct.
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox.

## Tool Selection Hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: Use dedicated MCP servers — `web-search` for searching, `web-fetch` for fetching pages. NOT context-mode.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Decision Tree

```
About to run a command / read a file / call an API?
│
├── Command is on the Bash whitelist (file mutations, git writes, navigation, echo)?
│   └── Use Bash
│
├── Output MIGHT be large or you're UNSURE?
│   └── Use ctx_execute or ctx_execute_file
│
├── Fetching web documentation or HTML page?
│   └── Use web-fetch MCP (fetch_url) or web-search MCP (search)
│
├── Processing output from another MCP tool?
│   ├── Output already in context? → use it directly
│   ├── Need multi-query? → save to file, ctx_index(path) → ctx_search
│   └── One-shot? → save to file, ctx_execute_file(path)
│
└── Reading a file to analyze/summarize (not edit)?
    └── Use ctx_execute_file
```

## Automatic Triggers

Use context-mode for ANY of these without being asked:
- **API debugging**: hit endpoint, call API, check response
- **Log analysis**: check logs, read access.log, debug 500s
- **Test runs**: run tests, check if tests pass, coverage report
- **Git history**: show recent commits, git log, diff between branches
- **Data inspection**: look at CSV, parse JSON, analyze config
- **Infrastructure**: list containers, check pods, disk usage
- **Build output**: build the project, check for warnings
- **Code metrics**: count lines, find TODOs, codebase statistics

## Language Selection

| Situation | Language | Why |
|-----------|----------|-----|
| HTTP/API calls, JSON | `javascript` | Native fetch, JSON.parse, async/await |
| Data analysis, CSV, stats | `python` | csv, statistics, collections, re |
| Shell commands with pipes | `shell` | grep, awk, jq, native tools |

## Search Strategy

- BM25 uses **OR semantics** — results matching more terms rank higher
- Use 2-4 specific technical terms per query
- **Always use `source` parameter** when multiple docs are indexed
- **Always use `queries` array** — batch ALL search questions in ONE call

## Critical Rules

1. **Always console.log/print your findings.** stdout is all that enters context.
2. **Write analysis code, not data dumps.** Analyze first, print findings.
3. **Be specific in output.** Print bug details with IDs, line numbers, exact values.
4. **For files you need to EDIT**: Use the normal Read tool. context-mode is for analysis, not editing.
5. **For Bash whitelist commands only**: Use Bash for file mutations, git writes, navigation, process control, package install, and echo.
6. **Never use `ctx_index(content: large_data)`.** Use `ctx_index(path: ...)` to read files server-side.
7. **Don't re-index data already in context.** If an MCP tool returned data in a previous response, use it directly.

## Subagent Routing

When spawning subagents, the routing block is automatically injected into their prompt by the PreToolUse hook. You do NOT need to manually instruct subagents about context-mode.

## ctx Commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call `ctx_stats` MCP tool and display full output |
| `ctx doctor` | Call `ctx_doctor` MCP tool, run the returned shell command |
| `ctx purge` | Call `ctx_purge` MCP tool with confirm: true (irreversible) |

After /clear or /compact: knowledge base and session stats are preserved. Use `ctx purge` to start fresh.
