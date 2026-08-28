# Task & Workflow

## Direct execution is the default

<!-- CC-ONLY -->
`/spec`, `/build`, `/fix`, and `/prd` run only when the user explicitly types them. Do not invoke them through `Skill()`, advertise them during ordinary work, or ask the user to choose a workflow because a request is large, cross-cutting, or phrased as "make it good." A clear user request is authorization to execute it directly, including investigation, implementation, verification, and affected documentation.
<!-- /CC-ONLY -->
<!-- CODEX-START
`$spec`, `$build`, `$fix`, and `$prd` run only when the user explicitly invokes them. Do not advertise them during ordinary work or ask the user to choose a workflow because a request is large, cross-cutting, or phrased as "make it good." A clear user request is authorization to execute it directly, including investigation, implementation, verification, and affected documentation.
CODEX-END -->
If the user asks about process options, explain the choices without starting one:

| Work is measured against | Workflow |
|---|---|
| A defect in behaviour that already worked | `fix` |
| An ordered plan approved before code | `spec` |
| A named outcome whose approach can emerge during work | `build` |
| An idea whose audience or success criteria are still unclear | `prd` |

Size never selects a workflow. When a Pilot workflow is explicitly active, its loaded skill is authoritative for lifecycle, gates, artifacts, and completion. Those mechanics do not constrain direct work.
Size, file count, architectural breadth, and cross-cutting scope change organization; they do not trigger a workflow question. Descriptions and mentions like "make it good" strengthen the requested outcome rather than selecting a workflow.

## Working state
- Use native task or plan state only when several dependent steps, interruptions, or compaction make state easy to lose. It is working memory, not an approval gate.
- When a native goal is active, keep working until it is achieved or genuinely blocked.
- A new user message may replace the active request or add to it. Record additions in the active task/plan state before resuming.
- Treat the current conversation, native goal, and session-scoped task state as authoritative. Shared memory can describe unrelated sessions.

## Delegation
The active agent owns the execution topology, but direct execution is the baseline: **the default is zero subagents**. Keep bounded asks, tightly coupled work, and anything finishable in a handful of tool calls in the current agent.
Delegate only concrete independent work that can run alongside useful local work or materially protect the main context. Start with the minimum useful count; multiple agents require distinct workstreams, and nesting requires a hierarchy that flat assignments cannot represent. Never fan out duplicate perspectives or checks the current agent can run.
Never stop a running task to ask the user for permission to delegate or spawn an agent. Give each agent explicit ownership with non-overlapping writes and persist returned agent/job ids to a session file. Do not redo a completed agent's exploration; integrate it and verify results from files and fresh commands.
If the user asks to stop, cancel, or kill agents or background work, **treat that as an immediate interruption**. Inspect actual current-session work and use exposed stop or interrupt controls for everything this session launched. Never claim that nothing is running from a peer-session list alone; distinguish subagents from independent sessions.
<!-- CC-ONLY -->
Claude Code: `/tasks` manages current-session work; `claude agents` and `claude stop <id>` manage separate sessions. Do not infer state from `ListAgents` alone.
<!-- /CC-ONLY -->
If the runtime cannot stop an independent session, give the exact native command and wait rather than resuming unrelated work.
When changing generated skills, hooks, rules, agents, or configuration, verify the generated artifacts directly after installation. The current session may not expose newly generated assets until the next install or session sync.

## Tool use

- Use the current tool schema; Claude Code and Codex names and parameters differ.
- Prefer repository-native search and edit tools. For Codex repository edits, prefer `apply_patch` when available.
- Use background execution for servers and watchers. Keep tests, lint, git reads, and short commands synchronous unless a resumable session is warranted.
- Use the web tools exposed by the current session. Pilot's server-selection guidance lives in `mcp-servers.md`.

<!-- CC-ONLY -->
Built-in `WebSearch` and ordinary `WebFetch` requests are hook-blocked. Authenticated `claude.ai/code/artifact/*` and `preview.claude.ai` URLs pass through to `WebFetch` because they require the user's Claude session. Use the available discovery mechanism to load replacements; do not substitute an unavailable tool with invented syntax.
<!-- /CC-ONLY -->
<!-- CODEX-START
`update_plan` is optional working memory, not an approval gate.
Do not assume Claude Code's sub-agent tools exist in Codex. Likewise, do not assume its task, skill, question, discovery, or background-command parameters exist. Use the currently exposed Codex schemas.
CODEX-END -->
