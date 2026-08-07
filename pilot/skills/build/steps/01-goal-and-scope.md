## Step 1: Name the Goal, Scope the Work

**Goal of this step:** know enough to draft tasks and criteria in Step 2 with concrete pass conditions. Research that would not change a task or a criterion is waste — stop there.

### 1.1 Restate the end state in one line

To yourself, not to the user. If you cannot say what the finished thing is in one sentence, the criteria will be mush and the tasks will be worse.

If the request is genuinely vague about *who it serves* or *what done means* — not just about how to build it — say so in one sentence and point at `/prd`. Do not run a loop against an idea that has not settled.

### 1.2 Spend a bounded research budget

**Typically 5–15 tool calls**, on exactly three things:

- **What already exists locally** that the build should reuse or match — the conventions, components, or prose style already in play.
- **What specifically "good" means here.** You need particulars to write criteria that name real dimensions. "Good typography" is what you write when you did not look.
- **A reference, if one exists.** See 1.3 — do not invent one.

<!-- CC-ONLY -->
For the local sweep, prefer `codegraph_explore(query="<area>")` for structure and `mcp__semble__search` for intent over raw Grep/Glob — one call returns the verbatim source plus the call path. Drop to Grep only to verify a result or find exact text in a known file.

For a reference on the web, the web MCP tools are the fetchers: discover them with `ToolSearch(query="+web-fetch fetch")` and `ToolSearch(query="+web-search search")`. Built-in `WebFetch`/`WebSearch` are hook-blocked. For a live page whose *appearance* is the reference, screenshot it with the Chrome tools rather than reading its DOM — you cannot judge typography from HTML.
<!-- /CC-ONLY -->
<!-- CODEX-START
For the local sweep, use `codegraph_explore` when the area is structural or the entry point is unclear; for named files, docs, config, or UI copy, read them directly or use Semble. For a reference on the web, use the current Codex tool schema's web access, or the Pilot web MCP tools if they are listed (`tool_search(query="+web-fetch fetch")`). For a live page whose appearance is the reference, use playwright-cli or agent-browser to capture it — you cannot judge typography from HTML.
CODEX-END -->

**Widen to ~30 calls when** the domain is unfamiliar, the goal names a stack or API you have not verified, or a reference is a codebase you would have to read to compare against.

<!-- CC-ONLY -->
**One `Explore` subagent is allowed here, and only here** — when the sweep is genuinely wide (many directories, unknown naming, several unfamiliar references). One, in Step 1 only, never inside the loop. Pass `model` explicitly; do not inherit the session model.
<!-- /CC-ONLY -->

### 1.3 A reference is optional

Some goals have a real thing to sit beside: a competitor's page, a named author's post, the pre-migration version of a screen. Others do not, and forcing one is worse than having none — a reference nobody can obtain is a comparison the judge invents, and an invented comparison passes everything.

**Use a reference only when all three hold:**

- **Named.** A specific thing. "Stripe's pricing page" works; "award-winning SaaS sites" does not.
- **Obtainable.** You can fetch it, screenshot it, read it, run it, or open it — and you do so *now*, in this step, not later.
- **Comparable.** Both artifacts can sit side by side and someone can pick one. If you cannot picture the A/B, it is not a reference.

| Goal | Reference that works |
|---|---|
| Website, app, UI | A named product's live page, screenshotted at the same viewport |
| Writing | A named author's published piece, same length and format |
| Code, tooling | A named repo's implementation, plus its benchmark or test suite |
| A rewrite or migration | The **existing** artifact, captured before you touch it |

**If the user named one, use it — no question needed.** If they did not and a genuine A/B exists, offer 2–3 candidates, one line each, and take their pick.

<!-- CC-ONLY -->
Use `AskUserQuestion` for the pick — it renders a structured form; don't fall back to plain-text numbered questions. Skip the question entirely when `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"`: take the most useful candidate you can genuinely reach, name it in the Buildout, and say in one line which one you took and why.
<!-- /CC-ONLY -->
<!-- CODEX-START
Present 2–3 plain-text numbered candidates with their trade-offs and wait for the user's answer. Skip the question entirely when `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"`: take the most useful candidate you can genuinely reach, name it in the Buildout, and say in one line which one you took and why.
CODEX-END -->

**When there is no reference, say so in one line and move on.** The criteria carry the standard by themselves. Do not manufacture a comparison to fill the field.

### 1.4 Capture the reference so later rounds cannot drift

Only when you have one. Recalling a reference is how the comparison quietly becomes "whatever we already made", so pin it to something re-openable and record *how* in the Buildout:

- A URL plus the exact fetch or screenshot command.
- A file path under the project (a screenshot, a saved page, a reference doc).
- A command that reproduces it (`git show <ref>:<path>`, a benchmark invocation, a binary to run).

For a rewrite, capture the "before" **now** — once you start editing, the old version stops being obtainable.

**Done when:** you can state the end state in one sentence, you can name what specifically makes it good, and any reference has been obtained once by you with its re-obtain command written down.
