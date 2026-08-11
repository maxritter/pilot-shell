---
title: "Claude's $200 Agent SDK Credit: Who Wins on June 15?"
description: "Anthropic is splitting Agent SDK and claude -p from subscription limits. Max 20x gets $200/mo, Max 5x $100, Pro $20. What changes June 15."
slug: agent-sdk-credit
date: 2026-05-14
authors:
  - max-ritter
tags:
  - guide
  - development
---

Anthropic is splitting Agent SDK and claude -p from subscription limits. Max 20x gets $200/mo, Max 5x $100, Pro $20. What changes June 15.

<!-- truncate -->

Anthropic is unbundling the Claude Agent SDK and `claude -p` from your subscription. Starting June 15, every Pro, Max, Team, and eligible Enterprise plan gets a separate monthly credit that pays for SDK and headless usage. Max 20x gets the headline number: **$200 a month**. Max 5x gets $100. Pro gets $20. Your subscription limits stay the same and stay reserved for the interactive stuff: Claude Code in the terminal, Claude Cowork, and chat.

The framing in Anthropic's email is that this clarifies a policy users complained was unclear. The framing in the community is split. Some people read it as a generous handout, because $200 a month of free Sonnet credit on Max 20x is real money. Others read it as the first metering of usage that used to count against a single fungible subscription pool, with extra usage as the only path forward once even the top-tier $200 ceiling empties.

Both reads are right, depending on how you actually use Claude Code. This post walks through what changes, what doesn't, how the credit drains, and what to do before June 15 if you run any kind of agent loop or scheduled `claude -p` workflow.

## What's Actually Changing on June 15

Anthropic published the full mechanics on the [Agent SDK credit help page](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan). The change is narrower than the email suggests, and the wording matters.

The **Agent SDK monthly credit** is a new, separate pool. It pays only for Claude Agent SDK usage, `claude -p` (non-interactive mode), the Claude Code GitHub Actions integration, and third-party apps that authenticate with your Claude subscription via the Agent SDK.

Your **subscription usage limits do not change**. The 5-hour rate-limit window and the weekly cap are the same size they were yesterday. They are now reserved for Claude Code in the terminal or IDE, Claude Cowork, and Claude chat.

Past the monthly credit, additional Agent SDK usage moves to **extra usage** at standard API rates, but only if you have turned extra usage on. If you have not, the SDK stops until the credit refreshes with the next billing cycle.

The clean way to think about it: there used to be one bucket, your subscription, and everything drank from it. There are now two buckets. One drains for interactive work and is the same size as before. One drains for SDK and headless calls and is brand new, and on Max 20x that new bucket starts the month with $200 in it.

The interactive bucket also got bigger last week. Pro and Max 5-hour limits [doubled and peak-hour throttling was removed](/blog/higher-usage-limits). With this change, that doubled bandwidth is no longer eaten by any SDK loops or `claude -p` cron jobs you happened to be running on the same account. Whether that's a net gain or a net loss depends entirely on how much SDK you actually use.

## Credit by Plan (Top Tier First)

Here's the published schedule, ordered from largest credit to smallest. None of these credits roll over.

| Plan | Monthly Agent SDK credit |
| --- | --- |
| **Max 20x** | **$200** |
| **Enterprise (seat-based, Premium seats)** | **$200** |
| Max 5x | $100 |
| Team (Premium seats) | $100 |
| Pro | $20 |
| Team (Standard seats) | $20 |
| Enterprise (usage-based) | $20 |

A note for Enterprise admins: members on seat-based Enterprise plans on Standard seats are not eligible for the credit at all. Anthropic is treating Premium seats as the developer audience and Standard seats as the chat audience. If your shop hands out Enterprise Standard for everyone, the people doing SDK work will either need to move to Premium seats or use a Claude Developer Platform API key.

Credits are per-user. They cannot be pooled, transferred, or shared across teammates. Each eligible user claims their own once. After the one-time opt-in, the credit refreshes automatically with each billing cycle.

The Max 20x and Enterprise Premium tier is where the credit is most generous, and it's the tier Anthropic is clearly aiming at the heaviest individual developer. $200 a month of free Sonnet-equivalent SDK usage is the most an individual subscriber will get, and it lines up with the plan price 1:1, which is unusual for Anthropic and worth pausing on.

## What the Credit Covers

Looking at it from a tooling angle, the credit pays for the entire programmatic surface of Claude Code:

- **The Agent SDK** in your own projects, Python or TypeScript.
- **`claude -p`**, which is Claude Code's non-interactive mode. This is what powers most agent loops, scheduled jobs, and any pipeline that calls Claude without a human at the keyboard. If you've built [scheduled tasks](/blog/scheduled-tasks) or any kind of background workflow on top of Claude Code, you've been running `claude -p` whether you've called it that or not.
- **The Claude Code GitHub Actions integration**, which uses the same headless surface.
- **Third-party apps that authenticate via the Agent SDK** with your Claude subscription. This is the cleanest answer Anthropic has ever given to the third-party harness question, which had been [flipped on twice in two months](/blog/claude-code-subscription).

The credit explicitly does not cover:

- Interactive Claude Code in the terminal or your IDE.
- Claude conversations on web, desktop, or mobile.
- Claude Cowork.
- Anything else that currently routes through extra usage.

If you're an API-key user on the Claude Developer Platform, nothing changes. Pay-as-you-go billing continues, and you do not receive the credit. The credit is strictly a subscription-side benefit.

## How the Credit Actually Drains

The order of operations is precise and worth memorizing before you wire any production loop to it:

1. **The credit drains first.** Any SDK or `claude -p` call hits the monthly credit before any other billing source on your account.
2. **At zero, behavior depends on extra usage.** If extra usage is on, additional SDK calls bill at standard API rates against extra usage. If extra usage is off, SDK requests stop until your credit refreshes.
3. **The credit refreshes monthly with your billing cycle.** Unused balance does not roll over.

The implication for anyone running a meaningful agent workflow is that the credit functions like a free tier on a metered API, not like a buffer on a flat-rate plan. You will, eventually, hit zero. Even at the $200 Max 20x ceiling, a serious orchestration workload finds the bottom of that bucket. What happens when it does is entirely controlled by your extra-usage configuration. If you've never been to Settings then Usage on the web and turned that switch on, your scheduled jobs will simply fail when the credit empties. For anyone running an [autonomous agent loop](/blog/autonomous-agent-loops) overnight, that's the failure mode to plan for.

## Why the Reaction Is Split

The honest answer: this change is a clarification that costs some users and benefits others.

It benefits anyone who was already mostly using interactive Claude Code and only occasionally running SDK loops or `claude -p`. The doubled 5-hour limits from last week are now actually doubled for that user, because no parallel agent workflow is sharing them. The $200 Max 20x credit then sits on top as effectively free SDK budget for casual use.

It costs anyone who was orchestrating heavy `claude -p` workflows on a single Max plan. Before, your `claude -p` calls drew from the same big bucket as your interactive sessions, and once a 5-hour limit was raised, both benefited. After June 15, the SDK side is capped at $200 of Sonnet-equivalent usage per month, even on the top-tier Max 20x plan. Past that, you're on extra usage at API rates or you're blocked. $200 covers a serious amount of routine Sonnet work, but a single deep-research run can chew through a million tokens, and once you start chaining loops the math gets uncomfortable fast.

It also draws a clearer line for third-party tools. The community has been arguing about whether Claude Code subscriptions cover third-party harnesses since Boris Cherny's April 3 statement that they didn't, followed by softening on April 9, followed by a quiet A/B test that briefly blocked Pro entirely. The new policy is the cleanest answer yet: third-party apps that use the Agent SDK authenticate against your subscription and are paid for out of the credit. Past zero, you go to extra usage or stop. That's a real, enforceable line, and it ends the policy whiplash that has been making people nervous about [which tier of Claude Code use is safe](/blog/claude-code-subscription).

Whether you see this as a win or a tax depends entirely on whether you were the kind of user the old fuzzy policy was implicitly subsidizing.

## Who Wins and Who Loses

**Wins:**

- **Max 20x and Enterprise Premium users.** $200 a month of effectively free SDK budget, on top of unchanged (and recently doubled) interactive limits. This is the cleanest win in the policy.
- **Casual SDK users on Max 5x.** $100 a month is plenty for most experimentation.
- **People building or using third-party Claude Code harnesses.** Clear policy, predictable billing, no more vibes-based bans.
- **Team and Enterprise admins.** Each user has their own credit and their own ceiling, so production runaway from one developer no longer eats team-wide subscription headroom.

**Losses:**

- **Power users orchestrating heavy `claude -p` workflows on even a Max 20x account.** The $200 credit is sized for individual experimentation, not production-scale automation. Anthropic explicitly says so in their admin notes.
- **Anyone running long autonomous loops that previously drew on subscription rate limits.** Past the credit, the math against extra usage at API rates is the same math as just using an API key.
- **Enterprise Standard seat users.** No credit at all.

## What This Means If You Orchestrate Agents

If you've built any kind of multi-agent setup on top of Claude Code, this is the change that pushes you to actually understand your token economics, even at the top tier.

Three things to actually do before June 15:

1. **Audit your `claude -p` usage.** If you have cron jobs, GitHub Actions, or scheduled SDK workflows running on a Claude subscription today, find them. They will all start drawing from the new credit instead of your subscription pool.
2. **Decide on extra usage.** Go to Settings then Usage on the web and either turn extra usage on with a spending cap you can live with, or accept that your SDK workflows will pause when the credit empties. Don't get surprised by a failed cron at 3 a.m.
3. **Right-size your model selection.** Anything you were running on Opus through the SDK should be re-examined against Sonnet 4.6 or Haiku 4.5. Most SDK loops do not need the most expensive model. The model selection guide is the framework for this.

If your workflows are routinely past $200 a month of legitimate Sonnet usage, you're not the user this credit was sized for, even on Max 20x. The Anthropic admin documentation says it plainly: production automation at scale should run on the Claude Developer Platform with an API key for predictable pay-as-you-go billing. That's not a workaround. It's the recommended architecture once you cross the casual-experimentation line.

## The Bigger Picture

The interesting move here isn't the $200 number on its own. It's that Anthropic is willing to publicly split the subscription product into two priced surfaces, which they hadn't done before. Interactive use stays on the flat rate. Programmatic use moves to a credit, then a metered overflow, then an API key. That's the same shape as every mature API product, and it's a stronger answer than the policy whiplash of the past six weeks.

Nothing breaks on June 14. The email Anthropic sent this week is the warning shot. The actual claim flow opens at the start of the next billing cycle past June 15, and the credit auto-refreshes from then on. There's no downside to claiming it the moment it appears in your account, especially if you're on Max 20x and the full $200 is sitting there waiting.

The work between now and then is making sure you know which of your workflows are about to start drawing from a credit pool instead of a subscription pool, and what you want to happen when that pool hits zero.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
