---
title: "Claude Opus 4.7 Best Practices for Claude Code"
description: "Opus 4.7 interprets instructions literally. Learn how detailed plans, xhigh effort, and explicit agents unlock better results in Claude Code."
slug: opus-4-7-best-practices
date: 2026-04-16
authors:
  - max-ritter
tags:
  - guide
  - development
---

Opus 4.7 interprets instructions literally. Learn how detailed plans, xhigh effort, and explicit agents unlock better results in Claude Code.

<!-- truncate -->

Opus 4.7's biggest shift is not raw intelligence. It is literalism. The model does exactly what you tell it, which punishes vague prompts and rewards detailed plans. Boris Cherny from Anthropic put it plainly: "it took a few days for me to learn how to work with it effectively." Most users will notice the same thing. Prompts that produced clean output on 4.6 now generate narrower, more literal results unless you restructure how you brief the model.

## What Actually Changed for Practitioners

The headline [benchmark numbers for Opus 4.7](/blog/claude-opus-4-7) are useful, but four behavioral changes matter more for day-to-day Claude Code work:

**Stricter instruction-following.** Opus 4.7 interprets instructions more literally than 4.6. Notion found it was the first model to pass their implicit-need tests. The flip side is that prompts relying on the model to fill in context now underperform.

**More selective subagent spawning.** The default favors doing work in one response over fanning out. If you want parallelization, say so explicitly.

**Adaptive thinking.** Fixed thinking budgets are gone. The model decides how long to reason based on context. You influence it by prompting: "think carefully before responding" for more, "prioritize responding quickly" for less.

**New `xhigh` default.** The effort scale now runs `low`, `medium`, `high`, `xhigh`, `max`. Claude Code defaults to `xhigh`, which sits between `high` and `max` and gives most of the reasoning depth without the full cost of `max`.

Anthropic's framing: treat Claude like a capable engineer you are delegating to, not a pair programmer you are chatting with. Front-load intent, constraints, acceptance criteria, and file paths. Batch your questions. Every user turn adds reasoning overhead.

## The Detailed Plan Is the New Prompt

The single biggest leverage point for 4.7 is a well-scoped plan. Anthropic is explicit about this: include intent, constraints, acceptance criteria, and relevant file paths in the first turn. Stricter instruction-following means a plan with 12 acceptance criteria produces 12 checked items. A plan with vague intent produces a vague implementation.

- Intent and scope boundaries
- Relevant files with line numbers
- Acceptance criteria per task
- Specialist agent assignments
- Verification steps before completion

Three v5.2 upgrades tighten this loop specifically for 4.7:

**Mandatory plan reading.** Every sub-agent dispatched by `/build` must read the full plan file as its first action. On 4.6 you could get away with agents working from a task summary. On 4.7, literal interpretation means sub-agents drift without the full context. Mandatory reading eliminates that drift.

**Verification Before Completion.** Sub-agents verify their work against acceptance criteria before marking tasks complete. This mirrors Opus 4.7's native self-verification behavior, which Intuit described as "catching its own logical faults during the planning phase." The plan file becomes the checklist the model verifies against.

**Assumption surfacing.** Moderate and complex tasks now state key assumptions before implementing. If multiple valid approaches exist, the model presents options rather than choosing silently. This matches 4.7's strictness, it will choose silently only when given permission to.

Large refactors get an additional hook. CodeStats, the new codebase intelligence CLI in v5.2, feeds dependency graphs, hotspot scores, and blast radius analysis into the plan before any code is written. The model now starts with structural context that used to require several exploratory turns. Combine this with [ultraplan](/blog/ultraplan) for architectural work and you have a briefing document that 4.7 can execute literally.

## Opus 4.7 xhigh Effort: When to Use It (and When Not To)

Opus 4.7 has five effort levels: `low`, `medium`, `high`, `xhigh`, and `max`. Claude Code defaults to `xhigh` on every plan tier. This is the single biggest lever for balancing intelligence against token spend, and unlike 4.6, the choice matters because adaptive thinking is now the only thinking mode.

| Level | Use Case | Token Cost | Example |
| --- | --- | --- | --- |
| **`low`** | Classification, extraction, formatting, grammar fixes | Lowest | "Tag these 50 support tickets by intent" |
| **`medium`** | General questions, short summaries, docs lookups | Low | "Summarize this ADR in 200 words" |
| **`high`** | Most intelligence-sensitive work, API callers not on Claude Code | Moderate | Default for Messages API apps doing real reasoning |
| **`xhigh`** | Coding, multi-step reasoning, agentic work, trade-off analysis | High | `/team-plan`, `/build`, refactors, design reviews |
| **`max`** | Correctness-critical evals, benchmark iteration, hardest algorithms | Highest | Running an eval suite, final-pass review on shipping code |

Hex's CTO noted that "low-effort Opus 4.7 is roughly equivalent to medium-effort Opus 4.6." So bumping everything to `xhigh` is wasteful. A practical recipe for long development sessions:

| Phase | Effort | Why |
| --- | --- | --- |
| Planning | `xhigh` | Plan quality compounds into every execution step |
| Execution | `high` | Specialist agents working from clear plans |
| Verification | `xhigh` | Catching drift before it ships |
| Exploratory / docs | `medium` | Cost-sensitive, low-stakes |
| Deep evals | `max` | Worth the cost for correctness-critical work |

Switch with `/effort xhigh` mid-session. Existing users without a manually set effort level were auto-upgraded to `xhigh` when 4.7 shipped.

The updated tokenizer is worth noting. The same input may map to roughly 1.0 to 1.35x more tokens than 4.6 depending on content type. Combined with deeper reasoning at higher effort, sessions run hotter. Task budgets and conciseness prompting are the main controls.

## Task Budgets: Capping Agent Spend in Opus 4.7

Task budgets are Opus 4.7's soft token ceiling for an entire agentic loop, thinking plus tool calls plus tool results plus final output. The model sees a running countdown and uses it to prioritize, finishing gracefully as the budget drains. Public beta, enabled by the `task-budgets-2026-03-13` header. Minimum budget: 20,000 tokens.

```
response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=128000,
    output_config={
        "effort": "xhigh",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    betas=["task-budgets-2026-03-13"],
    messages=[
        {"role": "user", "content": "Review this codebase and propose a refactor plan."}
    ],
)
```

A task budget is a suggestion the model sees, not a hard cap. `max_tokens` is the hard per-request cap, and the model is **not** aware of it. Use `task_budget` when you want the model to self-moderate. Use `max_tokens` as a ceiling to prevent runaway spend.

Rule of thumb for setting budgets: start at 2-3x the tokens a competent human engineer would need to do the task themselves. If the model hits the ceiling, the prompt is the problem, not the model. Pair budgets with stop criteria ("stop when tests pass") and fallbacks ("if you can't find X, return Y, don't guess") or the end-of-budget becomes a hallucination.

Don't set a task budget for open-ended work where quality matters more than speed. Anthropic's own docs note: "too-restrictive task budgets may lead to less-thorough completion or outright refusal."

For Agent SDK users, `maxBudgetUsd` is the dollar-denominated cousin:

```
options: {
  maxBudgetUsd: 0.15,
  maxTurns: 5,
}
```

## Subagent Selectivity Is a Feature When Your Plan Is Explicit

4.7 spawns fewer subagents by default. Anthropic's framing: "Do not spawn a subagent for work you can complete directly in a single response. Spawn multiple subagents in the same turn when fanning out across items."

1. `/team-plan` outputs a plan file with specialist assignments per task
2. `/build` dispatches each specialist with mandatory plan reading
3. Each specialist reads the full plan, runs its scoped work, and uses TaskUpdate to mark completion
4. Quality-engineer validation fires sequentially against each build

The shift from "agent chooses when to spawn" to "plan specifies who runs what" is the right fit for 4.7. The model respects the plan. Specialists stay in their lanes. Parallel specialists run concurrently while validation gates sequentially through `addBlockedBy` dependencies.

If you want more subagents, say so. Positive framing outperforms negative on 4.7 per Anthropic's guidance: use positive examples of desired voice rather than negative don't-do-this instructions. A prompt like "spawn a specialist for each of: frontend, backend, database" outperforms "don't try to do this in one response." This applies to all [sub-agent best practices](/blog/sub-agent-best-practices) with the new model.

## Auto Mode + xhigh + team-build: The Long-Running Combo

Anthropic's recommendation for trusted long-running tasks is [auto mode](/blog/auto-mode) combined with `xhigh`. This is the golden path in v5.2 for multi-hour agentic sessions.

The supporting infrastructure in v5.2 was tuned for this exact workload:

- **Early context backups.** The [Context Recovery Hook](/blog/context-recovery-hook) now fires its first backup at 50k tokens used, then every 10k after. On 1M context, this triggers long before percentage-based thresholds would.
- **Backup compactor.** After 14 days, individual session backups compact into 7-session summaries with `claude --resume` commands preserved. Subscription-only cost, no API charges.
- **Peak/off-peak awareness.** The StatusLine shows `Off-peak (2d4h30m)` in green or `Peak (1h15m)` in red with countdown. Anthropic confirmed peak hours (weekdays 8AM-2PM ET) drain sessions faster, valuable information when planning a long session.
- **LibraryHook.** Auto-syncs library-managed file edits back to your central library with a 180-second debounce. Detached workers survive session close, so long-running work does not lose config changes.

Practical rhythm: plan at `xhigh`, flip on auto mode, let the team build, check in at natural stopping points. Cognition (Devin) reports 4.7 "works coherently for hours, pushes through hard problems." That behavior only surfaces when you stop interrupting it mid-flow.

## Migrating Prompts from 4.6

### Breaking API Changes

Three things return a 400 error on Opus 4.7 that worked on 4.6. Strip them before migrating:

```
# BROKEN on Opus 4.7
response = client.messages.create(
    model="claude-opus-4-7",
    temperature=0,                          # 400: sampling params removed
    top_p=0.95,                             # 400: sampling params removed
    thinking={"type": "enabled", "budget_tokens": 32000},  # 400: extended thinking budgets removed
)
 
# WORKS on Opus 4.7
response = client.messages.create(
    model="claude-opus-4-7",
    thinking={"type": "adaptive", "display": "summarized"},  # adaptive is the only thinking-on mode
    output_config={"effort": "xhigh"},
)
```

A silent change: `thinking.display` now defaults to `"omitted"`. If your product streams reasoning to users, set `display: "summarized"` explicitly or users will see a long blank pause before output begins. No error fires, but the UX regresses.

If you were using `temperature=0` for determinism, note that it never guaranteed identical outputs on Anthropic's API. The safest migration is to remove the parameter entirely.

### Tokenizer Changes: Expect 1.0-1.35x More Tokens

Opus 4.7 ships with a new tokenizer. The same input encodes into 1.0 to 1.35x as many tokens depending on content type (up to roughly 35% more for token-heavy workloads). List pricing is unchanged at $5/$25 per million, but effective cost per request can rise. Run `v1/messages/count_tokens` on a representative workload before you migrate. Update `max_tokens` to give additional headroom, particularly on compaction triggers.

### Rewriting Vague Prompts for Literal Interpretation

1. **Convert implicit context to explicit.** If a prompt worked because 4.6 inferred "obviously you also want tests," add tests to acceptance criteria for 4.7.
2. **Replace don't-do-this with do-this.** Negative instructions produce unreliable results. Positive examples match intent directly.
3. **Be explicit about parallelism.** If you want multiple agents, state the fan-out pattern. 4.7's default is single-response.
4. **Batch questions into single turns.** Every user turn adds reasoning overhead. Three related questions in one turn beats three sequential turns.
5. **Front-load file paths.** The model processes paths literally. Passing `apps/web/src/app/(home)/page.tsx` saves two tool calls versus "the homepage file."
6. **Remove scaffolding the model no longer needs.** Prompts with "double-check the slide layout before returning" or forced interim status messages can be stripped. Anthropic explicitly recommends removing these and re-baselining, since 4.7 now self-verifies and emits regular progress updates natively.

## Claude Code Commands That Pair Well With Opus 4.7

4.7 rewards explicit plans and explicit dispatch. These commands codify that:

- **`/model claude-opus-4-7`**: switches the model for the current session without touching config.
- **`/effort xhigh`**: overrides default effort mid-session. Drop to `medium` for exploratory work, bump to `max` for final-pass review.
- **`/team-plan`**: produces the plan file 4.7 executes literally. Auto-detects session type (Development, Debugging, Migration, TDD, Research, Repo-Port) and loads the matching protocol.
- **`/build`**: dispatches specialists from the plan file with mandatory plan reading. Isolated, parallel where independent, gated where dependent.
- **`/team-build`**: cross-domain collaborative variant. Agents coordinate in real time on shared interfaces.
- **`/ultrareview`**: the new Opus 4.7 command. Spawns four specialist agents in parallel (security, logic, performance, style), each reading the diff with its own system prompt. Pro and Max users get 3 free runs.
- **`/rewind`** or double-tap `esc`: beats in-place correction when a first attempt goes wrong. Strips the failed attempt's tool calls from context and re-prompts with only the learning.

## Frequently Asked Questions

**What is xhigh effort in Claude Opus 4.7?** xhigh is a new fifth tier between `high` and `max`. Claude Code defaults to it on every plan. It gives deeper reasoning than `high` without the full token cost of `max`, suited to agentic coding, multi-step reasoning, and trade-off analysis.

**Should I always use xhigh?** No. xhigh on trivial work wastes tokens because adaptive thinking runs longer on ambiguous prompts. Drop to `medium` or `low` for classification, extraction, formatting, or short summaries.

**How do I set a task budget in Opus 4.7?** Pass the `task-budgets-2026-03-13` beta header and add `task_budget: {type: "tokens", total: N}` to `output_config`. Minimum is 20,000 tokens. It is a soft suggestion the model sees, not a hard cap.

**Why are my 4.6 prompts giving worse results on 4.7?** Almost always because 4.6 silently filled in implicit context and 4.7 does not. Rewrite the prompt with explicit intent, success criteria, and constraints. Strip `temperature`, `top_p`, `top_k`. If you streamed reasoning, set `thinking.display: "summarized"`.

**Is the tokenizer change a price increase?** No, list pricing is identical. Effective cost per request can rise 1.0 to 1.35x because the same input encodes into more tokens. Benchmark your workload with `count_tokens` before migrating.

## What's Next

4.7 rewards operators who invest in planning. The model does not need less guidance than 4.6, it needs better-scoped guidance. Every hour spent on a detailed `/team-plan` output pays back across the execution phase because the model holds the plan literally instead of loosely.

If you have not switched yet:

```
claude config set model claude-opus-4-7
/effort xhigh
```

Then point it at a plan and let it run. For the model's full capability profile, specs, and benchmarks see the [Claude Opus 4.7 overview](/blog/claude-opus-4-7). For the head-to-head against OpenAI's flagship, see [Opus 4.7 vs GPT-5.4](/blog/claude-opus-4-7-vs-gpt-5-4).
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
