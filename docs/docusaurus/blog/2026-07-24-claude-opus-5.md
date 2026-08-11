---
title: "Claude Opus 5: Frontier Results at Half the Price"
description: "Claude Opus 5 benchmarks, pricing, and specs: $5/$25 unchanged from Opus 4.8, near-Fable 5 results, thinking on by default, and a new max effort."
slug: claude-opus-5
date: 2026-07-24
authors:
  - max-ritter
tags:
  - models
---

Claude Opus 5 benchmarks, pricing, and specs: $5/$25 unchanged from Opus 4.8, near-Fable 5 results, thinking on by default, and a new max effort.

<!-- truncate -->

**Claude Opus 5 is the first Anthropic release where the price line did not move but the capability line did.** It ships **July 24, 2026** at **$5 per million input tokens and $25 per million output**, exactly what [Opus 4.8](/blog/claude-opus-4-8) has cost since May, and exactly half of [Fable 5](/blog/claude-fable-5-mythos-5). On Anthropic's launch charts it more than doubles Opus 4.8 on Frontier-Bench (43.3 vs 18.9), takes GDPval-AA v2, OSWorld 2.0, and AutomationBench outright, and scores twenty times Opus 4.8 on ARC-AGI-3. The API ID is `claude-opus-5`, it is the default model on Claude Max, and it is the strongest model available on Claude Pro.

The number that matters more than any single benchmark is the shape of the curves. Every benchmark chart Anthropic published plots score against dollars spent across the effort ladder, and on nearly all of them Opus 5's curve sits above and to the **left** of Fable 5's. That is not "better results if you pay more." That is better results for less money. If you only read one thing here, read [What Changes in Your Prompts](#what-changes-in-your-prompts): thinking is now on by default, one thinking configuration now returns a 400 error, and the verification instructions you carried over from earlier models are now actively costing you tokens.

## Key Specs

| Spec | Details |
| --- | --- |
| **API ID** | `claude-opus-5` |
| **Release Date** | July 24, 2026 |
| **Context Window** | 1M tokens, both the default and the maximum (no smaller variant) |
| **Max Output** | 128,000 tokens (up to 300,000 via the Batch API extended-output beta) |
| **Knowledge Cutoff** | May 2026 (reliable and training data cutoff) |
| **Thinking** | Adaptive, on by default |
| **Effort Levels** | `low`, `medium`, `high` (default), `xhigh`, `max`, no beta header required |
| **Pricing** | $5 input / $25 output per 1M tokens; Fast mode $10 / $50 |
| **Prompt Cache Min** | 512 tokens, down from 1,024 on Opus 4.8 |
| **Data Retention** | No mandatory retention for general access |
| **Availability** | Claude API, AWS Bedrock, Google Cloud, Microsoft Foundry, claude.ai, Claude Code, Claude Cowork |
| **Status** | Active, default on Claude Max, strongest model on Claude Pro |

## What Opus 5 Is: Frontier Intelligence That Stayed at Opus Prices

Every previous jump toward the frontier came with a bill. [Mythos Preview](/blog/claude-mythos) landed at $25/$125 in April. [Fable 5](/blog/claude-fable-5-mythos-5) made Mythos-class capability public in June at $10/$50, exactly double Opus. The implied trade was always the same: you can have the ceiling, and you can pay for the ceiling.

Opus 5 breaks that pattern. Anthropic's framing is that it delivers frontier intelligence close to Fable 5 at half the cost, and the partner evals back it. Cognition CEO Scott Wu reported that "on FrontierCode 1.1, Claude Opus 5 approaches Fable-level performance at half the cost. Within Devin, it also shows particular strength on difficult debugging and root-cause analysis tasks." Cursor Co-Founder Sualeh Asif put it more bluntly: "Claude Opus 5 delivers near Fable 5 intelligence at Opus speed and cost."

The efficiency story shows up in operational numbers, not just scores. Fundamental Labs' Richard Pham, Evals and Product Lead, reported that "across effort levels it averaged 9 percentage points higher accuracy with a third fewer turns and tool calls and 60% less time" on their hardest financial-modeling tasks. Harvey Head of Applied Research Niko Grupen found Opus 5 "achieving similar performance while generating 26% fewer tokens on average compared to Opus 4.8 at max reasoning." Fewer turns, fewer tokens, and a flat price is a compounding win for anyone running [long agentic sessions](/blog/agent-teams) where token spend scales with session length.

Anthropic is also candid about the ceiling. Opus 5 stays behind Mythos 5 on offensive cybersecurity and on autonomous biology research. It is not the most capable model Anthropic has. It is the most capable model most people can actually justify running all day.

## Benchmark Results

Anthropic published nine benchmark charts with this launch, plus two more on safety, and the nine share an axis convention worth internalizing: score on the vertical, **dollars spent per task on the horizontal**, with each model drawn as a curve across its effort ladder from `low` through `max`. The interesting comparison is not which model peaks highest. It is which curve sits higher at the same spend.

| Benchmark | Opus 5 | Fable 5 | Opus 4.8 | GPT-5.6 Sol |
| --- | --- | --- | --- | --- |
| **Frontier-Bench v0.1** (agentic coding) | 43.3 at max, 44.3 peak | 33.7 (~$27) | 18.9 | 37.5 |
| **CursorBench 3.2** (agentic coding) | 70.1 (~$8) | 70.4 (~$17) | 62.3 | 67.1 |
| **GDPval-AA v2** (knowledge work, Elo) | 1,862 (~$1,500) | 1,748 (~$1,700) | 1,595 | 1,738 |
| **ARC-AGI-3** (novel problem-solving) | 30.2 at high effort | not charted | 1.5 | 7.9 |
| **OSWorld 2.0** (computer use) | 70.5 (~$25) | 66.1 (~$47) | 57.1 | 62.7 |
| **AutomationBench** (business workflows) | 25.8 | 17.4 | 17.0 | 18.2 |
| **Humanity's Last Exam** (with tools) | 64.8 | 63.9 | 58.0 | not stated |
| **DeepSearchQA** (agentic search) | 95.0 (~$4.20) | 94.7 (~$7.30) | 93.2 | not stated |
| **AA Coding Agent Index** | 66.7 (~$8.50) | 65.9 (~$13) | 60.5 | 66.7 (~$7) |

Read the cost column and the pattern is unmistakable. On Frontier-Bench, Opus 5's peak of 44.3 lands around $14.50 per task at `xhigh`, while Fable 5 needs roughly $27 to reach 33.7. On OSWorld 2.0 it clears Fable 5's ceiling at close to half the spend. On DeepSearchQA and the Artificial Analysis Coding Agent Index the score gaps are fractions of a point and the cost gaps are 35% or more.

Two results deserve separating from the rest. **ARC-AGI-3** is the one that looks like a different generation of model: 30.2 for Opus 5 at high effort against 7.9 for GPT-5.6 Sol and 1.5 for Opus 4.8. That is twenty times Opus 4.8 on a benchmark built specifically to resist memorization. Anthropic describes the result as three times the next-best model; on the published chart the gap to GPT-5.6 Sol is closer to four.

**AutomationBench** is the other. Zapier CEO Wade Foster described what the score means in practice: "Claude Opus 5 topped Zapier's AutomationBench leaderboard without spending more tokens than prior Claude models. It took a raw account-health workbook and ran a full churn-prevention sequence end to end: flagging at-risk accounts, alerting the right owner, and summarizing for retention ops. Previous models didn't pass; Opus 5 hit 100%."

### Where Fable 5 Still Wins

CursorBench 3.2, and only barely. Fable 5 scores 70.4 to Opus 5's 70.1, a gap of three tenths of a point, and it takes roughly twice the money to get there. Anthropic's own framing is that Opus 5 lands within 0.5% of Fable 5 on CursorBench 3.2 at max effort at half the cost per task. If your workload is the one Cursor's benchmark models, Fable 5 remains the marginally stronger model and a much more expensive one. That is the entire remaining case for the higher tier on coding, and we work through the rest of it in [Opus 5 vs Fable 5](/blog/claude-opus-5-vs-fable-5).

Outside the charts, Cognition CEO Scott Wu reports that Opus 5 "approaches Fable-level performance at half the cost" on **FrontierCode 1.1**, a partner impression rather than a scored result. Anthropic also reports life-sciences gains over Opus 4.8 of **10.2 percentage points on organic chemistry** and **7.7 points on protein function prediction**.

### The Harness Caveat

The same warning applies here that applies to every frontier launch. Anthropic configures its own benchmark harness while competitor numbers come from their own setups, so the direction of these results is real and the partner statements are independent, but the exact margins are not an apples-to-apples scoreboard. The Frontier-Bench chart carries its own footnote: "These results are from an internal run of Frontier-Bench v0.1, on the mini-SWE-agent harness and a GKE backend, mean reward over 5 attempts per task. Opus 4.8 served as fallback on safety-classifier refusals for Opus 5 and Fable 5." Benchmark on your own workload before you move a production pipeline.

## What Changes in Your Prompts

This is the part of the launch that will cost you money if you skip it, and the part almost no coverage leads with. Three things changed in how Opus 5 behaves, and all three interact with prompts you already wrote. A fourth item is not a behavior change at all, but it belongs in the same migration pass.

### Thinking Is On by Default

On Opus 4.8, a request ran without thinking unless you explicitly set `thinking: {"type": "adaptive"}`. On Opus 5 that same request runs **with** thinking on: the model decides when and how much to think per turn, and the [effort dial](/blog/ultracode) is now the control for thinking depth. The wire value did not change, so `thinking: {"type": "adaptive"}` remains valid and equivalent to the default.

The trap is `max_tokens`. It is a hard limit on total output, thinking plus response text together. Any workload that ran thinking-less on Opus 4.8 with a tight `max_tokens` is now splitting that budget with a thinking block it did not have before. Revisit the value before you migrate. At `xhigh` or `max`, Anthropic recommends starting at 64k and tuning from there.

### Disabling Thinking at High Effort Now Returns a 400

This is the release's only breaking change, and it is enforced per request:

```
thinking: {"type": "disabled"} + effort xhigh  ->  400 error
thinking: {"type": "disabled"} + effort max    ->  400 error
thinking: {"type": "disabled"} + effort high or below  ->  accepted
```

On Opus 4.8, disabling thinking was independent of the effort level. On Opus 5 it is not. If you disable thinking at a high effort level today, you have two options: keep thinking disabled and drop effort to `high` or below, or keep the effort level and remove the `thinking` field entirely.

Anthropic recommends the second. With thinking disabled, Opus 5 can occasionally write a tool call into its visible text output instead of emitting a structured `tool_use` block, which means the call never runs and, in an agentic loop, the leaked text stays in conversation history and poisons later turns. It can also emit `<thinking>` tags or other internal XML into the visible response. The documented mitigation for both is to keep thinking on and control cost with lower effort instead.

### Delete Your Verification Instructions

Opus 5 verifies its own work without being asked. Anthropic's guidance is unusually direct about what that means for existing prompts: if yours contains "include a final verification step for any non-trivial task" or "use a subagent to verify," **remove it**. Those instructions compound with behavior the model already has, and removing them "reduces wasted tokens with no loss in quality." The same applies to "double-check your answer" and "re-verify before responding," and to any legacy harness scaffolding that bolts on a separate verification pass.

Triple Whale Co-Founder and CEO AJ Orbach described the self-verification concretely: "Claude Opus 5 checks its own work the way a real frontend developer would. On our benchmark it opened its pages in a browser at desktop and phone widths, caught a product hidden below the mobile fold and an off-screen checkout button, and fixed both before handing the work back."

Three more behavior shifts are worth a line in your system prompt if they bother you. Default responses and written deliverables run **longer**, and effort does not reliably shorten them, so prompt for length explicitly. The model **narrates progress** more often in agentic sessions. And it **delegates to subagents** more readily, which pays off on genuinely independent tracks of work and multiplies cost when applied to small ones. Anthropic's suggested cap reads like this:

```
Delegate to a subagent only for large tasks that are genuinely independent and
parallelizable, such as a wide multi-file investigation. Do not delegate work you
can finish yourself in a handful of tool calls, and do not use subagents to verify
or double-check your own work. If one subagent can complete the task, use one
rather than several, and keep spawn counts low.
```

If you run [dynamic workflows](/blog/dynamic-workflows) or multi-agent fan-out, that cap is the difference between a useful parallel run and a very expensive one.

### Two New Betas Worth Wiring In

Both ship alongside Opus 5 and both cut cost on long-running agents rather than changing how the model reasons.

**Mid-conversation tool changes** let you add or remove tools between turns without invalidating the prompt cache, so a session no longer has to carry a fixed tool list for its entire life. It is in beta behind the `mid-conversation-tool-changes-2026-07-01` header.

**Default fallbacks mode** adds a `"default"` value to the `fallbacks` parameter, applying Anthropic's recommended fallback model per refusal category instead of a list you maintain yourself. Server-side fallback is in beta, and `"default"` requires the `server-side-fallback-2026-07-01` header. Paired with the classifier behavior in the [safety section](#safety-profile), this is how you stop a flagged request from becoming a failed one.

## Pricing and Access

| Tier | Cost |
| --- | --- |
| **Standard (all contexts)** | $5 input / $25 output per 1M tokens |
| **Fast mode (~2.5x speed)** | $10 input / $50 output per 1M tokens |
| **Prompt caching** | Up to 90% savings on cached reads |
| **Batch processing** | 50% savings |

The standard tier is unchanged from Opus 4.8, which is the headline. The [1M-token context window](/blog/1m-context-ga) is included at that flat rate, and on Opus 5 it is both the default and the maximum: there is no smaller context variant to opt into or out of.

Two smaller pricing details are worth knowing. The **minimum cacheable prompt drops to 512 tokens**, down from 1,024 on Opus 4.8, so short system prompts that were previously too small to cache now create cache entries with zero code changes. And [Fast mode](/blog/fast-mode) runs at roughly 2.5x default speed for $10/$50, but it is a research preview on the **Claude API only**: not Bedrock, not Google Cloud, not Microsoft Foundry. In Claude Code it is available via usage credits.

On plans, Opus 5 is the **default model on Claude Max** and the **strongest model available on Claude Pro**. On the API it is available to all customers as `claude-opus-5`, on AWS as `anthropic.claude-opus-5`, and on Google Cloud and Microsoft Foundry from launch. Opus 4.8 stays available everywhere. For how the tiers compare on cost per task across a working week, see the usage optimization guide.

## Safety Profile

Opus 5 is the most aligned model Anthropic has shipped, and the automated behavioral audit is the cleanest evidence for it. On the misaligned-behavior score, where lower is better on a 1 to 10 scale, the chart lists **Opus 5 at 2.30**, Mythos 5 at 2.81, Opus 4.8 at 2.85, and Sonnet 5 at 3.35. Note that the chart plots Mythos 5 while Anthropic's prose compares Opus 5 against Fable 5; the two share weights, so read 2.81 as the Mythos-class figure. Anthropic reports the model adheres better to Claude's Constitution, shows the lowest rates of deceptive behavior, and is the least susceptible to being tricked into misuse.

The cybersecurity picture is the more interesting one, because it is where Anthropic deliberately did not advance the frontier. On the OSS-Fuzz evaluation, Opus 5 **identifies** vulnerabilities at 79.4% pass@1 against Mythos 5's 80.0% and Opus 4.8's 61.5%. On **exploiting** them, the gap reopens hard: Mythos 5 solves 13 challenges at grade 1.0, Opus 5 solves 4, and Opus 4.8 solves 0. Finding bugs and weaponizing them are separable capabilities, and Opus 5 was trained to be strong at the first without matching Mythos on the second.

That separation buys real ergonomics. Opus 5's cyber classifiers are expected to intervene roughly **85% less often than Fable 5's**. Anyone who ran legitimate security research, code auditing, or life-sciences work on Fable 5 and hit the false-positive tax will feel that immediately. The classifiers still allow vulnerability identification in source code while blocking binary-based scanning, penetration testing, and exploit generation, and flagged requests on claude.ai, Claude Code, and Claude Cowork fall back to Opus 4.8 by default. Enterprises and researchers who need the restrictions loosened can apply to the Cyber Verification Program.

Biology safeguards match Opus 4.8's, which makes Opus 5 the most capable generally available model for scientific research. Biology-related requests blocked on Fable 5 now route to Opus 5 rather than Opus 4.8. And unlike Fable 5, **Opus 5 carries no mandatory data retention** for general access. Anthropic frames this as continuity with prior Opus models rather than a new concession, but if your organization holds a zero-retention agreement that Fable 5's Mythos-class policy overrode, it is the line that decides whether Opus 5 needs a legal review at all.

## How to Use Opus 5 in Claude Code

Set it as your default:

```
claude config set model claude-opus-5
```

Override for one session, or switch mid-session:

```
claude --model claude-opus-5
```

```
/model claude-opus-5
```

Effort defaults to `high` in Claude Code and on the Claude API. Anthropic's recommendation is to **start at `xhigh` for coding and agentic work** and use `high` for other intelligence-sensitive workloads, with a specific caveat attached: `low` and `medium` are meaningfully stronger on Opus 5 than on earlier Opus models, so use them liberally wherever your evals show quality holds.

```
/effort xhigh
```

If you are migrating an existing integration, Claude Code ships a migration command that updates model strings and suggests Opus 5-tuned prompt improvements through the built-in claude-api skill:

```
/claude-api migrate
```

## Opus 5 vs Opus 4.8

| Feature | Opus 4.8 | Opus 5 |
| --- | --- | --- |
| **API ID** | `claude-opus-4-8` | `claude-opus-5` |
| **Standard pricing** | $5 / $25 per 1M | $5 / $25 per 1M (unchanged) |
| **Frontier-Bench v0.1** | 18.9 | 43.3 at max, 44.3 peak |
| **CursorBench 3.2** | 62.3 | 70.1 |
| **GDPval-AA v2 (Elo)** | 1,595 | 1,862 |
| **ARC-AGI-3** | 1.5 | 30.2 |
| **OSWorld 2.0** | 57.1 | 70.5 |
| **Misaligned behavior** | 2.85 | 2.30 (lower is better) |
| **Thinking** | Off unless set to adaptive | On by default |
| **Effort ladder** | low to max, default `high` | low to max including explicit `max`, default `high` |
| **Disabling thinking** | Independent of effort | Only at effort `high` or below, else 400 |
| **Prompt cache minimum** | 1,024 tokens | 512 tokens |
| **Context window** | 1M tokens | 1M tokens, default and maximum |
| **Knowledge cutoff** | January 2026 | May 2026 |
| **Self-verification** | Prompted | Unprompted, remove legacy verification instructions |
| **Data retention** | Standard policy | No mandatory retention |

The upgrade decision is close to trivial: same price, materially better results, one breaking change to check. Read the [behavior changes](#what-changes-in-your-prompts) before you flip the model string, run an effort sweep on your own evals, and audit your prompts for verification instructions that are now dead weight. If you are still on Opus 4.7, the [agentic coding practices from that generation](/blog/opus-4-7-best-practices) still hold, minus the verification scaffolding.

## Frequently Asked Questions

**Is Claude Opus 5 free?** Not on the claude.ai free tier. It is the default model on Claude Max and the strongest model available on Claude Pro, both paid plans, with no separate per-token charge inside those subscriptions. On the API it is paid from day one at $5/$25 per million tokens.

**How much does Claude Opus 5 cost?** $5 per million input tokens and $25 per million output tokens on the standard tier, unchanged from Opus 4.8 and exactly half of [Fable 5](/blog/claude-fable-5-mythos-5). Fast mode is $10/$50. Prompt caching cuts cached reads by up to 90% and the Batch API halves both rates.

**Is Opus 5 better than Fable 5?** On the published evidence, yes: Opus 5 wins seven of the eight quantified head-to-head evals at half the token price, and Fable 5 keeps only a 0.3-point edge on CursorBench 3.2. The full breakdown, including the retention and classifier differences that matter more than the scores, is in [Opus 5 vs Fable 5](/blog/claude-opus-5-vs-fable-5).

**What is the Opus 5 context window?** 1 million tokens, and on Opus 5 that figure is both the default and the maximum. There is no smaller context variant. Max output is 128,000 tokens per response, up to 300,000 through the Batch API extended-output beta.

**Does Opus 5 break my existing Opus 4.8 code?** One case does. `thinking: {"type": "disabled"}` is now accepted only at effort `high` or below, and pairing it with `xhigh` or `max` returns a 400 error. Everything else carries forward, though thinking now runs by default, so revisit `max_tokens` on any workload that previously ran without it.

**What is the new `max` effort level?** `max` is the explicit top of the five-level ladder (`low`, `medium`, `high`, `xhigh`, `max`) and requires no beta header on Opus 5. It removes constraints on token spend for the deepest reasoning. Anthropic still recommends `xhigh` as the starting point for coding and agentic work and reserves `max` for tasks that justify unconstrained spend.

**Should I remove verification instructions from my prompts?** Yes. Opus 5 verifies its own work unprompted, and instructions like "include a final verification step" or "use a subagent to verify" cause over-verification: more tokens, no quality gain. Remove them along with any harness scaffolding that adds a separate verification pass.

**How does Opus 5 compare to GPT-5.6 Sol?** Opus 5 leads on Frontier-Bench (43.3 vs 37.5), ARC-AGI-3 (30.2 vs 7.9), GDPval-AA v2 (1,862 vs 1,738), OSWorld 2.0 (70.5 vs 62.7), CursorBench 3.2 (70.1 vs 67.1), and AutomationBench (25.8 vs 18.2). They tie at 66.7 on the Artificial Analysis Coding Agent Index, where Sol gets there slightly cheaper. See the [GPT-5.6 breakdown](/blog/gpt-5-6) for the full family comparison.

## Related Pages

- [Claude Opus 5 vs Fable 5](/blog/claude-opus-5-vs-fable-5) for the head-to-head and whether Fable 5 still has a job
- [Claude Opus 4.8](/blog/claude-opus-4-8) for the model Opus 5 supersedes at the same price
- [Claude Fable 5 and Mythos 5](/blog/claude-fable-5-mythos-5) for the Mythos-class tier above the Opus line
- [Claude Sonnet 5](/blog/claude-sonnet-5) for the cheaper daily driver you escalate to Opus 5 from
- Every Claude Model for the complete timeline from Claude 3 to Opus 5
- Model selection guide for switching models tactically mid-session
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** handles model routing in one config file: Opus for `/spec` planning, Sonnet for everyday iteration, Haiku for trivial calls. You set the policy; Pilot Shell picks per request.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
