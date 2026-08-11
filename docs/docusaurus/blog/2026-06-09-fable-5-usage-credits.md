---
title: "Claude Fable 5 Price: Is It Free + Usage Credits"
description: "Is Claude Fable 5 free? Included on Max and premium Team seats since July 20, 2026. Pro needs usage credits. Pricing, tiers, and credit math."
slug: fable-5-usage-credits
date: 2026-06-09
authors:
  - max-ritter
tags:
  - guide
  - development
---

Is Claude Fable 5 free? Included on Max and premium Team seats since July 20, 2026. Pro needs usage credits. Pricing, tiers, and credit math.

<!-- truncate -->

Short answer: **it depends on your plan, and since July 20, 2026 the split is permanent.** On **Max plans and premium seats on Team and seat-based Enterprise plans**, [Fable 5](/blog/claude-fable-5-mythos-5) is included at no extra cost for up to **50% of your weekly usage limits**. On **Pro plans and standard seats**, it runs on prepaid **usage credits** billed at API rates. On the Claude API it costs **$10 per million input tokens and $50 per million output**, double [Opus 4.8](/blog/claude-opus-4-8) and double the newer [Opus 5](/blog/claude-opus-5).

Access itself is no longer in question. Fable 5 was suspended worldwide on June 12, 2026 under a US export-control directive, and that suspension **ended on July 1, 2026**. The model has been generally available since, on the Claude Platform, claude.ai, Claude Code, and Claude Cowork, with cloud providers following. This guide covers what Fable 5 costs on each plan, how the credits system works mechanically, and how the access rules got to where they are.

## Is Claude Fable 5 free?

Not in the "costs nothing" sense, but on some plans it is included in what you already pay. Here is the current arrangement, effective **July 20, 2026**:

| Plan | Fable 5 terms |
| --- | --- |
| **Max** | Included, up to 50% of weekly usage limits, counts toward plan limits |
| **Team, premium seats** | Included, up to 50% of weekly usage limits |
| **Seat-based Enterprise, premium seats** | Included, up to 50% of weekly usage limits |
| **Pro** | Usage credits required, plus a one-time credit |
| **Team, standard seats** | Usage credits required, plus a one-time credit |
| **Seat-based Enterprise, standard seats** | Usage credits required |
| **Usage-based Enterprise and Claude API** | Standard API rates, $10/$50 per 1M |

The claude.ai free tier does not include Fable 5 at all, and on the API it was never free: it is paid from day one at the rates below. Anthropic granted eligible Pro and Team standard seats a one-time credit to soften the July 20 change, reported as $100 in Anthropic's own announcement.

The practical read for most individuals: if you are on **Max**, Fable 5 is simply available and draws on the same weekly allowance as everything else, capped at half of it. If you are on **Pro**, Fable 5 is a metered add-on, and [Opus 5](/blog/claude-opus-5) is the strongest model your subscription actually includes.

## Claude Fable 5 API Pricing

Here is the full API rate card, set against the models above and below it:

| Model | Input (per 1M) | Output (per 1M) | Cache hit (per 1M) |
| --- | --- | --- | --- |
| **Claude Fable 5** | $10 | $50 | $1 |
| **Claude Opus 5** | $5 | $25 | $0.50 |
| **Claude Opus 4.8** | $5 | $25 | $0.50 |
| **Claude Mythos Preview** | $25 | $125 | Not published |

Three things matter here. Fable 5 is priced at **exactly double Opus 5 and Opus 4.8** on both input and output. It is **less than half the price of [Mythos Preview](/blog/claude-mythos)**, the frontier-class tier that stays restricted to Project Glasswing partners. And the **90% prompt-caching discount carries forward**: a cache read costs $1 per million tokens, one tenth of the standard input rate, so heavy-context agentic workloads that reuse the same system prompt or codebase across calls pay far less than the headline number suggests.

The token math has one large upside worth stating plainly: Fable 5 ships the **full 1M-token context window at standard pricing**. A 900K-token request bills at the same per-token rate as a 9K-token request, with no long-context surcharge. For the long-horizon work Fable 5 is built for, that flat rate is the difference between "expensive" and "unworkable."

Two pricing modifiers stack on top. Batch processing cuts both input and output in half ($5/$25 per million) for non-urgent jobs. And US-only inference, set with `inference_geo: "us"`, applies a **1.1x multiplier** across every token category if you need guaranteed US data routing. Global routing is the default and uses standard pricing. The model ID is `claude-fable-5`, available on the Claude API, Claude Code, consumption-based Enterprise, plus AWS, Google Cloud's Vertex AI, and Microsoft Foundry. For where Fable 5 lands on raw capability versus its price, see the [Fable 5 benchmarks and specs](/blog/claude-fable-5-mythos-5).

## The Fable 5 Weekly Limit, and What Happens When You Hit It

Fable 5 is the first Claude model to carry a per-model ceiling on your **weekly** allowance. That is the detail almost every explanation gets wrong, and it changes what "running out" actually means.

The 50% is a cap on how much of your one weekly allowance Fable may consume, not a second allowance of its own. Fable draws from the same bucket as every other model and counts against it, and it weighs roughly double an Opus session while doing so. But because the cap applies to Fable alone, hitting it does not lock you out of Claude: up to half your weekly allowance is still there, fully available to [Opus 5](/blog/claude-opus-5) and Sonnet 5. Losing Fable is not losing Claude.

### How to see where you stand

In Claude Code, run `/usage`. On a Pro, Max, Team, or Enterprise plan it shows plan usage bars alongside a breakdown of what consumed them, attributed to skills, subagents, plugins, and individual MCP servers. Press `d` or `w` to switch between the last 24 hours and the last 7 days. On claude.ai, the same picture lives under **Settings > Usage**.

Two caveats. The figures are computed from local session history on the machine you are running, so usage from another laptop or from claude.ai will not appear. And when the usage endpoint is rate limited, `/usage` falls back to the last bars it loaded within the past 60 minutes and labels them `Showing last-known usage`. Press `r` to retry.

### When Fable is exhausted but everything else has headroom

Claude Code distinguishes two kinds of ceiling, and the distinction decides what you should do next.

**Shared windows** are the session and weekly limits. These apply across all models, so switching models does not restore access. You wait for the reset time shown in the message, or you run `/usage-credits`.

**Model-specific ceilings** apply to one model only. This is the category the Fable cap falls into, the same way "You've hit your Opus limit" is separate from your weekly window. Switching away with `/model` keeps you working immediately, because the ceiling you hit was never the one holding your remaining allowance.

So the practical answer to "Fable is gone, now what" is one command:

```
/model opus     # Opus 5, half the token weight, included on your plan
/model sonnet   # Sonnet 5, cheapest per token, fine for routine execution
```

[Opus 5](/blog/claude-opus-5) is the right default here, and not merely as a consolation. It holds the $5/$25 tier and wins seven of the eight quantified head-to-head evals against Fable 5. Our model selection guide covers which model to fall back to for which kind of task.

If you keep hitting the Fable ceiling mid-week, the fix is upstream of the limit. Running Fable as a planner while cheaper models execute reached 96% of Fable's benchmark performance at 46% of the cost, which is the difference between exhausting a weekly allowance on Wednesday and never touching the ceiling at all. See how to make a Fable weekly allowance last, and for the routing mechanics, [run Fable as an orchestrator over Sonnet workers](/blog/sub-agent-best-practices).

### "You've reached your Fable 5 limit. Run /usage-credits to continue or switch models with /model."

You have consumed your Fable allowance for the current window. Your other models are unaffected. Either fund usage credits to keep going on Fable at API rates, or run `/model` and carry on with Opus 5 at no additional cost.

### "Fable 5 is still included with your Max plan. If you see a prompt to set up usage credits for it, restart Claude Code."

This one is not a limit at all. It means your client is holding a stale view of your entitlement, most often after the July 20, 2026 change took effect mid-session. Restart Claude Code and the correct entitlement loads. If a credits prompt survives a restart on a Max plan or a premium seat, that is worth raising with support rather than funding.

### "You're out of usage credits. Run /usage-credits to keep using Fable 5 or /model to switch models."

Your prepaid balance hit zero. This is the Pro and standard-seat version of the same fork: add funds, or switch models and stay inside the allowance your plan already includes. Setting an auto-reload threshold prevents the interruption next time.

### Is Claude Fable 5 restored?

Yes. The June 12, 2026 export-control suspension ended on July 1, 2026, and Fable 5 has been generally available since across the Claude Platform, claude.ai, Claude Code, and Claude Cowork. If you are seeing a limit message today it is a quota or entitlement issue, not the old outage. The full sequence is in [how Fable 5 access evolved](#how-fable-5-access-evolved) below.

## How Fable 5 Usage Credits Work

Usage credits are Anthropic's prepaid overage system for paid plans. They are available on Pro, Max 5x, and Max 20x, and the same mechanism extends to Team and seat-based Enterprise. Here is the mechanic, straight from Anthropic's [usage-credits documentation](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans):

**They activate only after you exhaust your included plan usage.** Credits are not a substitute for your subscription. You hit your normal limit, get a notification, and then, if credits are enabled and funded, you keep going. Your standard plan usage still resets every five hours as usual; credits only cover what spills over that ceiling.

**You prepay them, in dollars.** Go to **Settings > Usage**, enable the feature, click **Add funds**, and enter an amount. There is a daily redemption limit of **$2,000**. You can also set up auto-reload so funds top up automatically when your balance drops below a threshold you choose.

**They are billed at standard API rates.** This is the key point for Fable 5. Credits are not consumed at some separate consumer rate; they draw down at the same per-token API prices in the table above. Every token counts: chat messages, Claude Code terminal usage, Research mode sessions, and project file content all consume credits once you are past your plan limit.

**When credits run out, you revert to your plan's included usage.** If the balance hits zero or the feature is disabled, you simply lose overage capacity until you add more funds. Nothing breaks; you just can't exceed your plan allotment.

One operational note: if you bought your subscription through a mobile app store, you can only enable and purchase credits on the **web version of Claude**, not in the mobile app.

## What Subscribers Should Do Now

**On Max or a premium seat, spend the 50% allowance deliberately.** Fable 5 is included, but only up to half your weekly limits, and inside subscription plans it weighs roughly double an Opus session. Burning that allowance on routine work exhausts it before the tasks that actually need it. One small mercy in the billing design: when a request gets rerouted to Opus 4.8 by the safeguard classifiers, **you are not charged Fable 5 prices for it**, so the safety fallback never silently inflates your bill. Know which model to fall back to when Fable is exhausted before you need it, so the switch is not a scramble mid-task.

**On Pro or a standard seat, decide whether you need Fable 5 at all.** Since July 20 it is prepaid API spend on top of your subscription. Before funding credits, benchmark your workload against [Opus 5](/blog/claude-opus-5), which your plan already includes and which wins seven of the eight quantified head-to-head evals against Fable 5 at half the token price. The [full comparison](/blog/claude-opus-5-vs-fable-5) makes the case in detail. If you still need Fable 5, enable usage credits, set an auto-reload threshold you are comfortable with, and remember the daily $2,000 ceiling.

**Control your effort level, not just your model.** Most of a Fable 5 bill is output tokens at $50 per million, and output volume tracks how hard you let the model think. Capping reasoning effort on routine work, the same discipline covered in our [Ultracode effort guide](/blog/ultracode), is the single biggest lever on credit burn once you are paying per token.

**For heavy use, compare the API directly against subscription credits.** Since credits bill at standard API rates anyway, the choice between "subscription plus credits" and "a straight API key" comes down to whether your base plan usage still pulls its weight. If you are blowing past plan limits constantly, an API key with [prompt caching](/blog/claude-code-subscription) and batch discounts may be the cleaner accounting. If your overage is occasional, credits on top of your existing plan are simpler. Either way, the [higher Claude Code rate limits](/blog/higher-usage-limits) that shipped alongside recent releases give you more headroom before credits ever kick in.

Once you are spending the allowance, [how to get more out of each Fable session](/blog/fable-5-best-practices) covers the prompting habits that make each session earn its cost.

## When the 2x Price Is Worth It

Doubling your token cost is a narrower decision than it was in June, because the model directly below Fable 5 got much stronger. [Opus 5](/blog/claude-opus-5), released July 24, 2026, holds the $5/$25 tier while beating Fable 5 on Frontier-Bench, GDPval-AA v2, OSWorld 2.0, AutomationBench, Humanity's Last Exam with tools, DeepSearchQA, and the Artificial Analysis Coding Agent Index. Fable 5 keeps a 0.3-point edge on CursorBench 3.2 plus the long-horizon partner evals from its own June launch that Anthropic has not re-run.

So the honest framing has shifted. In June, Fable 5 was the model you escalated to when Opus could not finish the job. Today it is a workload-specific exception worth measuring before you pay for it, and Opus 5 is the sensible default for nearly everything, including the long-horizon agentic work Fable 5 was built for. Two non-benchmark differences push the same way: Fable 5 carries mandatory 30-day retention on all Mythos-class traffic, and its cyber classifiers fire far more often than Opus 5's. For a fuller breakdown of which model fits which task, see our model selection guide. And if you are weighing Fable as an orchestrator rather than a single model for a task, know [when splitting work across models costs more than it saves](/blog/multi-agent-orchestration-cost) before you commit to the pattern.

## How Fable 5 Access Evolved

The path from launch to the current arrangement took six weeks and several changes. This is history rather than current state, but it explains why older coverage contradicts what you see in your account today.

| Date | What changed |
| --- | --- |
| **June 9, 2026** | Fable 5 launches, included at no extra cost on Pro, Max, Team, and seat-based Enterprise |
| **June 12, 2026** | US export-control directive forces Anthropic to disable Fable 5 and Mythos 5 for every customer |
| **June 23, 2026** | The launch inclusion window closes, and continued use moves to prepaid usage credits |
| **June 30, 2026** | Export controls lifted |
| **July 1, 2026** | Access restored on Claude Platform, claude.ai, Claude Code, and Claude Cowork, cloud following |
| **July 1 to 7** | Temporary window includes Fable 5 for Pro, Max, Team, and select Enterprise up to 50% of limits |
| **July 7 and 12** | Anthropic extends that window twice while it secures capacity |
| **July 19, 2026** | The promotional window ends at 11:59:59 PM PT |
| **July 20, 2026** | The permanent split takes effect: included on Max and premium seats, credits on Pro and standard |

Two details are worth carrying forward. The June suspension traced to a non-universal jailbreak, essentially asking the model to read a codebase and patch software flaws, and Anthropic shipped a new classifier alongside the restoration that blocks the reported technique in **over 99% of cases**, rerouting those requests to Opus 4.8. And Anthropic's stated reason for the staged rollout was capacity: demand was hard to predict, so it brought Fable 5 to subscription plans in stages rather than all at once.

## Frequently Asked Questions

**Is Fable 5 free on Claude Pro?** No. Since July 20, 2026, Pro plans need prepaid usage credits to run Fable 5, billed at standard API rates. Eligible Pro seats received a one-time credit when the change took effect. The model included in Pro at no extra usage cost is [Opus 5](/blog/claude-opus-5).

**Is Fable 5 included on Max?** Yes. On Max plans, and on premium seats on Team and seat-based Enterprise plans, Fable 5 is included at no extra cost for up to 50% of your weekly usage limits, counting toward your regular plan limits.

**Can I use Fable 5 right now?** Yes. The June 12, 2026 export-control suspension ended on July 1, 2026, and Fable 5 has been generally available since, on the Claude Platform, claude.ai, Claude Code, and Claude Cowork, with cloud providers restored after. Whether it costs you extra depends on your plan.

**How much does Fable 5 cost?** On the Claude API, $10 per million input tokens and $50 per million output, with a 90% prompt-caching discount on cached reads ($1 per million) and the full 1M-token context window at standard pricing. That is exactly double [Opus 5](/blog/claude-opus-5) and Opus 4.8.

**Do I need usage credits?** Only on Pro, standard Team seats, standard seat-based Enterprise seats, or if you exceed your plan's included usage. Credits are prepaid, enabled under Settings > Usage, and billed at standard API rates. Without them, your access reverts to your plan's included allowance.

**Fable 5 or Opus 5?** For most work, Opus 5. It costs half as much per token, is included on plans where Fable 5 is not, and wins seven of the eight quantified head-to-head evals. Reach for Fable 5 when your own benchmarks show it winning on your specific workload. See the [full head-to-head](/blog/claude-opus-5-vs-fable-5).
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
