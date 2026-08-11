---
title: "Claude Code Nested Subagents: 5 Levels Deep"
description: "Claude Code subagents can now spawn their own subagents, capped at depth 5. How nesting works, the workflows it unlocks, and the token costs."
slug: nested-subagents
date: 2026-06-11
authors:
  - max-ritter
tags:
  - guide
  - agents
---

Claude Code subagents can now spawn their own subagents, capped at depth 5. How nesting works, the workflows it unlocks, and the token costs.

<!-- truncate -->

For two years, the rule was absolute: a subagent could not spawn another subagent. The official docs still say so today, in three separate places. Then on June 9, Boris Cherny shipped v2.1.172 and quietly broke his own rule. **Claude Code subagents can now spawn their own subagents, up to 5 levels deep.**

The changelog entry is one line: "Sub-agents can now spawn their own sub-agents (up to 5 levels deep)." No config flag, no settings reference, no migration note. Cherny announced it on X the same day: "Just landed nested subagent support in Claude Code. Capped at depth=5 to start. Lmk what you think!" He framed the cap as a starting point and asked for feedback. The motivation, in his words, is "agents kicking off agents as a way to better manage context."

That last phrase is the whole story. Nesting is not about running more agents in parallel. It is about pushing noisy work further away from the conversation you actually care about. This guide covers what shipped, why context management is the real driver, how the mechanics work, the workflows it unlocks with copy-pasteable prompts, and the token math you need to respect before going five layers deep.

## What Actually Shipped in v2.1.172

The feature is recursion for the Agent tool. Before v2.1.172, only your main Claude Code thread could spawn subagents. A subagent was a leaf node. It did its work, returned a summary, and that was the end of the branch. Now any subagent can call the Agent tool itself, and the children it spawns can spawn their own children, down to a hard ceiling of five levels.

Two things are worth flagging immediately.

First, **the plumbing predates the feature by weeks.** Version 2.1.139 added `x-claude-code-agent-id` and `x-claude-code-parent-agent-id` headers to every API request a subagent makes, plus `agent_id` and `parent_agent_id` attributes on `claude_code.llm_request` OTEL spans. Version 2.1.145 extended that to `claude_code.tool` spans and fixed trace parenting so a background subagent's spans nest under the dispatching Agent tool span. The identity and lineage tracking was laid down first. v2.1.172 just turned on the actual recursion. If you run OpenTelemetry, you already have the observability to watch a nested run unfold as a proper tree.

Second, **the same release fixed a bug that only nesting could produce:** "a background sub-agent staying stuck as 'active' in the agent panel after a nested agent it spawned was stopped." You do not write that fix unless agents are spawning agents. The feature is fresh, and the rough edges show it. (For the running record of releases like this, we mirror Anthropic's official notes in our changelog.)

### The Docs Contradiction Worth Knowing About

Here is the part that will confuse you if you go reading the official documentation. As of this writing, the [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents) still state the opposite of what shipped. Three times:

> Subagents cannot spawn other subagents. If your workflow requires nested delegation, use Skills or chain subagents from the main conversation.

And again, in the plan-mode section: "This prevents infinite nesting (subagents cannot spawn other subagents)." And once more in the tools reference: "Subagents cannot spawn other subagents, so `Agent(agent_type)` has no effect in subagent definitions."

All three are now stale. The shipped binary contradicts the published docs. This is normal for a same-week feature release, but it matters for you in one practical way: if a subagent does not nest when you expect it to, do not trust the docs to explain why. Trust the changelog and test it yourself. The docs will catch up; until they do, the behavior is the source of truth.

## Why Context Management, Not Parallelism

It is tempting to read "agents spawning agents" as a parallelism story, like you can now run more work at once. That is not the point, and conflating the two will lead you to burn tokens for nothing. [Sub-agent best practices](/blog/sub-agent-best-practices) already cover parallel-versus-sequential dispatch from the main thread, and that surface has not changed.

What nesting changes is *where the noise lives.* When a subagent is about to do something messy, fifteen web searches, a dozen log greps, a wide codebase scan, it can now offload that mess into a child subagent before its own window fills with junk. The child does the dirty work in *its* throwaway window and returns only the distilled verdict. The parent's context stays lean.

The mental model is a simple one: **push noisy tool calling as far from the main conversation as possible, so only distilled signal flows upward.** Important decisions happen early, in a high-signal context window that never got polluted. This is the same principle behind [dynamic workflows](/blog/dynamic-workflows), where isolation defeats goal drift because each agent's window is short and its objective is crisp. Nesting extends that isolation one dimension deeper: not just across agents, but down through them.

Think of a deep debugging session. Layer 1 loads the incident and fans out four layer-2 agents, one per candidate cause. One of them needs to cross-reference server logs against the codebase, a genuinely noisy job. Pre-v2.1.172, it had to do that inline and return with a bloated window. Now it spawns a layer-3 agent to grep the logs and hand back a one-line correlation, staying focused on its single hypothesis. The main thread, four levels up, sees four clean verdicts instead of raw log lines, and decides. That is the use case: not more, but cleaner.

## How Nesting Works Mechanically

Three properties define the behavior.

**Fresh context per layer.** Each spawned subagent, at any depth, starts with its own clean window and custom system prompt. A layer-4 agent gets the same fresh-start treatment as a layer-1 agent, which is what makes the offload-the-noise pattern work at every level.

**Results collapse upward.** A child returns its final text (or a validated object if you passed a schema) to its parent, and only that. The parent never inherits the child's tool calls, intermediate reasoning, or raw inputs. By the time a verdict reaches the root, it has been distilled at every layer it passed through.

**Lineage is observable.** Thanks to the v2.1.139 and v2.1.145 plumbing, every agent in the tree carries its own `agent_id` and a `parent_agent_id` pointing at whoever spawned it. If you have OTEL configured, a nested run renders as a literal tree of spans, each child nested under its dispatching parent. That is how you audit what a deep run actually did and where the tokens went.

### The Depth Cap and the Missing Knob

The cap is five levels, and it is a hard limit. Reverse-engineering of the v2.1.172 client binary turned up no `MAX_DEPTH` constant, which strongly suggests the ceiling is enforced server-side. There is no setting to raise it, lower it, or turn it off. The only related control is the `Agent(agent_type)` allowlist in an agent's `tools` field, which governs *which* subagent types can be spawned, not how deep the spawning goes.

One ambiguity is worth stating plainly: the official sources do not specify whether "depth=5" means five spawned levels beneath the root (six agents in the deepest chain) or five agents total including the root. The docs are silent, and Cherny's announcement does not clarify. If you are architecting a workflow that genuinely needs the full depth, do not assume; build in a layer of margin and test where the wall actually is.

### How Anthropic's Cap Compares to Codex

The "no knob" choice is a real design decision, and the contrast with OpenAI's Codex makes it sharp. Codex has supported nested agents for months, and it made depth user-configurable from the start. Its `~/.codex/config.toml` exposes the controls directly:

```
[agents]
max_depth = 1   # default; root sessions start at depth 0
max_threads = 6 # concurrent agent thread ceiling
```

Codex ships a conservative default of `max_depth = 1`, so only one level of spawned agents is permitted out of the box, and leaves it to you to raise the ceiling deliberately. Anthropic went the opposite way: a fixed cap of 5, no default to reason about, no config to forget. The Codex approach trusts you to opt into depth and own the cost; the Claude Code approach picks a ceiling for you and refuses to let you exceed it. Neither is obviously right, but given that Anthropic previously had to ship fixes for runaway parallel subagent spawning, the locked ceiling reads as a deliberate guardrail.

## Workflows Nesting Unlocks

Models do not reliably nest on their own yet. This is experimental, and in practice you often have to *tell* Claude to delegate downward, by name, in the prompt. Here are the patterns worth reaching for, with prompts you can adapt.

**Research with claim verification.** One layer-1 agent per source extracts the claims. Each spawns layer-2 verifiers that do the noisy web searching to confirm or refute each claim. Only the verdicts flow up.

```
Research the current state of WebGPU browser support. Spawn one subagent per
major browser. Instruct each of those subagents to spawn its own verifier
subagents that web-search the actual release notes for each claim, and return
only confirmed facts with source URLs. I want clean verdicts, not raw search dumps.
```

**Debugging fan-out with deep cross-checks.** The pattern from earlier, made explicit. The win is that the investigation goes deep enough to catch the *underlying* cause instead of stopping at the first plausible one, while your main context stays clean for the actual fix.

```
Investigate why checkout latency spiked after Tuesday's deploy. Spawn one
subagent per candidate cause (DB, cache, third-party API, new code path).
Tell each one it may spawn its own subagents to cross-check server logs against
the codebase. Return ranked hypotheses with evidence. Do not surface raw logs to me.
```

**Blast-radius analysis.** For a contract, schema, or doc change, run one agent per affected document. Each considers first-order implications, then spawns nested agents to trace second- and third-order effects through the dependency graph.

**Skill A/B comparison.** Two layer-1 agents each load a different version of a skill (say, two code-review skills) that itself spawns subagents. The main thread compares the two outputs head to head, testing not just the skill but its whole nested behavior.

**Overnight skill optimization.** An agent iterates versions of a skill, spawning nested test runs per version, and converges on a better one. It pairs naturally with async background agents so it runs while you sleep.

Across all five, the shape matches the orchestration patterns you already know, with one new degree of freedom: the workers can now recurse. Contrast this with [Agent Teams](/blog/agent-teams), which is peer coordination, named roles talking laterally. Nesting is strictly hierarchical: a parent, its children, their children. Teams go wide; nesting goes deep.

## The Costs and When Not to Nest

Now the part the excitement glosses over. **Nesting multiplies tokens, and the multiplication compounds with depth.** Subagent-heavy workflows already run roughly seven times the tokens of a single-threaded session. Add layers, and each layer can fan out again, so cost grows geometrically, not linearly. One developer summed up the fear with an image captioned "one token here costs 20k on the main thread." That is the right intuition to hold.

Early community reaction split roughly 64% positive, 35% negative. The positives are context control and the flexibility to express genuinely complex workflows. The negatives are concrete: token cost multiplication, rate-limit pressure, and a real question about model quality four or five levels down, where the agent doing the work is furthest from your original intent. One commenter cautioned that nesting "makes it worse up to a certain point" if you do not scope tightly. They are right. Depth is not free, and it is not automatically better.

So, when *not* to nest:

- **The task fits one window.** If a single subagent can hold the whole job without drowning in noise, nesting adds cost and latency for nothing.
- **You are chasing parallelism, not isolation.** Use parallel dispatch from the main thread instead. Nesting is the wrong tool for "do more at once."
- **The work is shallow.** A two-step lookup does not need a three-layer tree.
- **You have not scoped the children.** A vague prompt at depth 1 becomes four vague prompts at depth 2 and sixteen at depth 3. Imprecision compounds faster than tokens do.

Keep a usage monitor open the first few times you run a deep workflow. Watch where the tokens actually land. The honest test before going deep is the same one that governs any heavy run: does this task genuinely need more compute, or are you reaching for depth because it is new?

## What Comes Next

Treat all of this as experimental, because it is. Cherny shipped depth 5 "to start" and openly asked whether the cap is right. The same-release bug fix tells you nesting was exercised hard enough to surface edge cases within days, and the docs have not caught up. None of that is a reason to avoid the feature; it is a reason to use it deliberately, with telemetry on and a token budget in mind.

The deeper shift is worth watching. Orchestration in Claude Code keeps moving from something you script by hand toward something the model decides on its own, first across agents, now down through them. The open question is whether a Claude four levels removed from your original prompt still does its best work, or whether quality decays with distance. Anthropic capped depth at 5 precisely because nobody knows yet. Go deep when the task earns it, keep your scopes tight at every layer, and let the verdicts, not the noise, be the only thing that climbs back up to you.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
