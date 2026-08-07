## Step 1: Scope and Research

**Goal:** know enough to write every criterion in Step 3 with a concrete pass condition. Research that does not change a criterion is waste — stop there.

### 1.1 Restate the goal in one line

To yourself, not to the user. If you cannot say what is being built in one line, the criteria will be mush.

If the request is genuinely vague about *who it serves* or *what done means* — not just about how to build it — say so in one sentence and point at `/prd`. Do not run a rubric against an idea that has not settled.

### 1.2 Spend a bounded research budget

**Typically 5–15 tool calls**, on exactly three things:

- **Confirm the bar is obtainable.** Open the URL, find the repo, locate the article, run the binary. Do this *now*, not in Step 2 — a bar you cannot obtain is a bar the judge will hallucinate, and a hallucinated comparison passes everything.
- **Learn what specifically makes it good.** You need particulars to write criteria that name real dimensions. "Good typography" is what you write when you did not look.
- **Read what already exists locally** that the build should reuse or match — the conventions, components, or prose style already in play.

<!-- CC-ONLY -->
For the local sweep, prefer `codegraph_explore(query="<area>")` for structure and `mcp__semble__search` for intent over raw Grep/Glob — one call returns the verbatim source plus the call path. Drop to Grep only to verify a result or find exact text in a known file.

For the bar, the web MCP tools are the fetchers: discover them with `ToolSearch(query="+web-fetch fetch")` and `ToolSearch(query="+web-search search")`. Built-in `WebFetch`/`WebSearch` are hook-blocked. For a live page whose *appearance* is the bar, screenshot it with the Chrome tools rather than reading its DOM — you cannot judge typography from HTML.
<!-- /CC-ONLY -->
<!-- CODEX-START
For the local sweep, use `codegraph_explore` when the area is structural or the entry point is unclear; for named files, docs, config, or UI copy, read them directly or use Semble. For the bar, use the current Codex tool schema's web access, or the Pilot web MCP tools if they are listed (`tool_search(query="+web-fetch fetch")`). For a live page whose appearance is the bar, use playwright-cli or agent-browser to capture it — you cannot judge typography from HTML.
CODEX-END -->

**Widen to ~30 calls when** the domain is unfamiliar, the bar is a codebase you would have to read to compare against, or the goal names a stack or API you have not verified.

<!-- CC-ONLY -->
**One `Explore` subagent is allowed here, and only here** — when the sweep is genuinely wide (many directories, unknown naming, several unfamiliar references). One, in Step 1 only, never inside the loop. Pass `model` explicitly; do not inherit the session model.
<!-- /CC-ONLY -->

### 1.3 Note what you learned, in criteria terms

Before leaving this step, write down — to yourself — the three to five **specific dimensions** the bar is strong on. Not "it's polished": "the hero pairs a 96px display face with 16px body copy and never mixes weights inside a line", "every error path returns a typed result rather than throwing", "each section opens with a concrete example before the abstraction".

Those dimensions become the criteria. If you cannot name them, you did not look hard enough — go back to 1.2.

**Done when:** the bar has been obtained once by you, and you can name what specifically makes it good.
