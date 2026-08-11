---
title: "Claude Code Subscription: Safe Use Without a Ban"
description: "How to use your Claude Code subscription safely. The one rule, three tiers of use (safe, gray, bannable), and when to switch to an API key."
slug: claude-code-subscription
date: 2026-04-30
authors:
  - max-ritter
tags:
  - guide
  - development
---

How to use your Claude Code subscription safely. The one rule, three tiers of use (safe, gray, bannable), and when to switch to an API key.

<!-- truncate -->

You're paying $20, $100, or $200 a month for a Claude Code subscription. You don't want to also pay API token rates for things your subscription should already cover. So the question hits every developer eventually: can I just use my Pro or Max plan instead of an API key?

Short answer: yes, for most things. There's one rule that decides where the line is, and crossing it is how engineers get instant-banned. Lose your account and you lose access to one of the strongest coding models on the market, which is a much worse trade than the few hundred dollars you were trying to save.

This guide breaks the **claude code subscription** into three usage tiers (safe, controversial, bannable), so you know exactly what your Pro or Max plan covers, when to switch to an API key, and how to set up your OAuth token correctly without accidentally billing your API key instead.

## The One Rule That Decides Everything

Memorize this single line and it covers about 90% of the policy:

> Your Pro or Max subscription is for **your own individual use**. The moment your code routes someone else's request through your seat, stop using the subscription OAuth token and switch to an API key.

Anthropic's official [usage policy](https://docs.claude.com/en/docs/claude-code/legal-and-compliance) phrases it the same way. OAuth authentication on Free, Pro, Max, Team, and Enterprise plans is intended exclusively for **ordinary individual use** of Claude Code and other native Anthropic apps. Developers building products or services that interact with Claude's capabilities (including via the Agent SDK) should use API key authentication through the Claude Console.

The second another human becomes the intended user, you've crossed from individual use into product territory. That's the tripwire. Two phrases to lock in:

1. **"Your own individual use"** is the permission Anthropic grants.
2. **"Someone else's request"** is the tripwire that revokes it.

Everything below is just applying that rule to specific scenarios.

## Tier 1: Safe Use (Green)

These are the cases Anthropic explicitly endorses. You are the only human whose work the agent runs.

- **Personal scripts on your own laptop.** Cron jobs, dotfiles, pipelines, agentic workflows you author for yourself.
- **The Claude Agent SDK running your own agents and research.** If the prompts and outputs are yours, you're inside fair use.
- **CI on your own repository** with `CLAUDE_CODE_OAUTH_TOKEN` set as a secret, as long as you're the only contributor whose work it acts on.
- **Claude Code on your work laptop for engineering you author.** Building products, shipping features, refactoring. Building a product is fine. Embedding your subscription **into** the product is not.
- **Claude Code Web, Claude Desktop, and any first-party Anthropic app.** Anthropic obviously wants you using their tools.

The mantra to remember: **one human, one subscription, one beneficiary.** If a single individual is the only person on the receiving end of the tokens, you're safe. Team and Enterprise plans relax this for the named team, but for individual Pro and Max, the rule is one-to-one.

For optimizing how far that subscription stretches, see our usage optimization guide. It covers `ccusage`, model switching, and context strategies that cut token burn by 70%.

## Tier 2: Controversial Use (Gray)

This is where things get murky. The honest move in this entire tier is the same: **grab an API key and stop guessing.**

- **Agency or contractor work using your personal token.** If a client is the eventual beneficiary of the output, the OAuth token is the wrong auth method.
- **Slack bots or daily reports used by multiple humans.** Even if the bot reads your prompts, the consumers of the output are other people. That's product territory.
- **Open-source CLIs that ship with your token embedded.** Only safe if every user brings their own token.
- **Internal team tools running on one developer's Pro or Max token.** Even with low volume, you're routing other people's requests through your seat. Switch to an API key, or upgrade to a Team plan.
- **Third-party agent harnesses (OpenClaw-style and similar).** This is the most contested case. Anthropic has flipped on it twice in the last two months. As of late April 2026, OpenClaw documentation states that staff confirmed CLI-style usage is allowed again, while still recommending API keys for long-lived gateway hosts. If you're curious about how that ecosystem stacks up, see [OpenClaw vs Claude Code](/blog/openclaw-vs-claude-code).

Anthropic's own messaging here has been a mess. Boris Cherny posted on April 3, 2026 that subscriptions would no longer cover third-party tool usage; six days later the line softened; an A/B test then surfaced that briefly blocked Claude Code on Pro accounts entirely. Read the [usage policy page](https://docs.claude.com/en/docs/claude-code/legal-and-compliance) yourself, then decide. When the policy is genuinely ambiguous, [contact Anthropic sales](https://docs.claude.com/en/docs/claude-code/legal-and-compliance) directly. That link sits inside the policy itself.

## Tier 3: Bannable Use (Red)

These will get your account banned, and the abuse classifier finds them quickly.

1. **Shipping a product whose users hit your Pro or Max OAuth token.** Token volume and prompt classification make this easy to detect.
2. **Multi-tenant SaaS apps signing in to Claude on your behalf.** Same issue: many users, one seat.
3. **Pooling one subscription across a team without Team or Enterprise seats.** Buy seats or use the API.
4. **Reselling Claude.** Instant ban.
5. **Extracting tokens from `pier.json`, the system keychain, or environment dumps and reusing them.** Both a TOS violation and a security failure.

Don't trade a Frontier-model account for a few hundred saved dollars. The downside is permanent loss of access to one of the most capable models in the industry, plus the entire Claude Code tooling stack. Set strong boundaries on permissions so an agent can't accidentally exfiltrate or reuse credentials in a way that triggers the abuse system.

## How to Use Your OAuth Token Correctly

Once you've placed your work in the green tier, the technical setup is straightforward. There's one gotcha that silently bills your API key instead.

**Step 1. Generate an OAuth token from your subscription:**

```
claude setup-token
```

That opens a browser, completes the OAuth flow, and returns a token that bills against your subscription's 5-hour rate limit window (not your API key balance).

**Step 2. Set the token as an environment variable:**

```
export CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-..."
```

**Step 3. Unset your API key in the same process.** If `ANTHROPIC_API_KEY` is also defined, the SDK and CLI prefer it and silently bill the API key instead of your subscription. In Python:

```
import os, subprocess
 
env = os.environ.copy()
env.pop("ANTHROPIC_API_KEY", None)  # Force OAuth path
 
subprocess.run(
    ["claude", "-p", "ping"],
    env=env,
    capture_output=True,
)
```

**Step 4. Verify which credential actually billed.** Run a test prompt with `--output-format json` and inspect the response:

- `apiKeySource: "none"` and a `rateLimitType: "5h"` field means the OAuth token billed your subscription. Correct.
- Any other `apiKeySource` value means your API key billed instead. Re-check the environment.

If the request hits your Pro or Max plan, you should also see usage reflected in the rate-limit window for your subscription tier. Combine this with model-aware routing from the model selection guide to keep heavy reasoning on Opus while your subscription handles the bulk of routine edits.

## Quick Decision Framework

Before any non-trivial integration, run through these in order:

1. **Am I the only human these agents are running for?** Yes: OAuth token. No: API key.
2. **Is the output consumed by anyone other than me?** Yes: API key.
3. **Is this work I author and own?** Yes: OAuth fine. No: API key.
4. **Is the case in Tier 2 (gray)?** Default to API key. The cost difference rarely beats account risk.
5. **Anything in Tier 3?** Stop. Restructure the architecture before continuing.

If you're still new to the tooling itself, start with what Claude Code is. The auth model makes more sense once the agentic workflow is clear.

## What To Actually Do

Anthropic is compute-constrained, growing fast, and clearly defending its highest-tier subscriber experience. That priority is reasonable. What's not reasonable is leaving developers to track policy across scattered tweets, and until that improves, the conservative path wins.

Use the OAuth token for personal engineering, your own agents, and research. Use an API key the moment another person's request flows through your code, when an open-source tool will ship with your credential, or when you're plugging into a third-party harness whose status changes monthly. Your Max plan is already paid for. Use it the right way, keep your account, and route the gray cases through an API key that bills predictably and survives policy whiplash.

The few dollars you save by stretching a subscription into product territory are not worth a permanent ban from the model your career increasingly depends on.

[Auto Mode](/blog/auto-mode)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
