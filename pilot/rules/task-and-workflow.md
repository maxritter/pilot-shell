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

The active agent owns the execution topology. It may spawn, resume, nest, or skip subagents whenever the tools exposed by Claude Code or Codex make that useful. **Never stop a running task to ask the user for permission to delegate or spawn an agent**; availability of the agent tool is sufficient authority. If no agent tool is exposed, continue directly without turning that into a user question.
- Give each agent explicit ownership, keep writes non-overlapping, and tell them other agents share the checkout.
- Launch independent work together when the current tool schema supports it.
- Do not redo a completed agent's exploration. Integrate its evidence.
- Verify returned work from the diff and fresh commands; an agent's completion report is not proof.
- Use only the agent names, parameters, waiting mechanism, and background controls exposed by the current session; persist returned agent/job ids to a session file before unrelated long-running checks.

When changing generated skills, hooks, rules, agents, or configuration, verify the generated artifacts directly after installation. The current session may not expose newly generated assets until the next install or session sync.

## Tool use

- Use the current tool schema; Claude Code and Codex names and parameters differ.
- Prefer repository-native search and edit tools. For Codex repository edits, prefer `apply_patch` when available.
- Use background execution for servers and watchers. Keep tests, lint, git reads, and short commands synchronous unless a resumable session is warranted.
- Use the web tools exposed by the current session. Pilot's server-selection guidance lives in `mcp-servers.md`.

<!-- CC-ONLY -->
Built-in `WebFetch` and `WebSearch` are hook-blocked. Use the available discovery mechanism to load replacements; do not substitute an unavailable tool with invented syntax.
<!-- /CC-ONLY -->
<!-- CODEX-START
`update_plan` is optional working memory, not an approval gate.
Do not assume Claude Code's sub-agent tools exist in Codex. Likewise, do not assume its task, skill, question, discovery, or background-command parameters exist. Use the currently exposed Codex schemas.
CODEX-END -->
