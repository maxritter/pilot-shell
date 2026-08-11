---
title: "Ultracode in Claude Code: Effort Setting Explained"
description: "Ultracode sends xhigh effort plus auto-triggered Dynamic Workflows. How it differs from xhigh, max, and ultrathink, and what it costs on Opus 5."
slug: ultracode
date: 2026-06-01
authors:
  - max-ritter
tags:
  - guide
  - development
---

Ultracode sends xhigh effort plus auto-triggered Dynamic Workflows. How it differs from xhigh, max, and ultrathink, and what it costs on Opus 5.

<!-- truncate -->

A single Claude context window has three predictable failure modes on hard work. It quits early on a fifty-item task after finishing thirty-five and calls it done. It grades its own output too generously when you ask it to verify itself. And it slowly loses the thread of your original goal as the conversation gets long enough to need compaction. [Dynamic Workflows](/blog/dynamic-workflows) fix all three by spreading the work across separate Claudes, each with a clean context window and one focused job. The catch is that you normally have to ask for a workflow. Ultracode is the setting that makes Claude reach for one on its own.

That is the whole idea: **ultracode is the workflow toggle, left on for the entire session.** It sends `xhigh` reasoning effort to the model and additionally has Claude auto-orchestrate Dynamic Workflows for substantive tasks, so a request that would otherwise run in one overloaded window gets fanned out across verifying subagents without you asking for a workflow at all. It shipped in Claude Code v2.1.154 on May 28, 2026, alongside [Claude Opus 4.8](/blog/claude-opus-4-8). This guide covers what ultracode is, how it differs from `xhigh`, `max`, and `ultrathink`, how to enable it, where it runs, and the open-ended token cost you need to understand before turning it on for routine work.

## What Ultracode Actually Is

Here is the definition straight from Anthropic's [model configuration docs](https://code.claude.com/docs/en/model-config), worth quoting in full because the wording matters:

> "Ultracode is a Claude Code setting rather than a model effort level: it sends `xhigh` to the model and additionally has Claude orchestrate dynamic workflows for substantive tasks. It applies to the current session only."

Read that twice. Ultracode is not a deeper rung on the reasoning ladder. It is a setting that does two jobs at once. First, it pins your per-message reasoning to `xhigh`. Second, it flips on automatic workflow orchestration, so Claude decides on its own when a task is big enough to fan out across subagents.

That second job is where the leverage lives, and it is exactly the fix for the three failure modes above. A workflow spreads the task across isolated agents so no single window has to hold all fifty items, which kills the early quitting. It hands verification to a separate agent that never wrote the answer it is judging, which removes the self-preferential bias. And it keeps each agent's window short enough that goal drift never sets in, because the agent finishes and returns before compaction can blur the objective. If you want the full mechanics of how a workflow plans, fans out, and verifies, read the [Dynamic Workflows guide](/blog/dynamic-workflows). This post owns the effort-setting and cost side.

The practical upshot: with ultracode on, a single request can turn into several workflows in a row. As Anthropic's [workflows docs](https://code.claude.com/docs/en/workflows) put it, "one to understand the code, one to make the change, and one to verify it. This applies to every task in the session, so each request uses more tokens and takes longer than at lower effort levels." That is the trade. You buy depth and built-in verification on every task, and you pay for it in tokens and wall-clock time whether the task needed it or not.

## Ultracode vs xhigh vs max vs ultrathink: Which One to Pick

**The short answer:** `xhigh` is the persistent middle setting you can leave on. `max` is the deepest thinker inside a single window and resets each session. `ultracode` is the only one of the four that leaves the window at all, because it fans the work out across subagents. And `ultrathink` is not a setting, it is a word you type in a prompt.

Pick `xhigh` for deeper reasoning you want by default, `max` when one hard problem deserves unlimited thinking in one place, `ultracode` when the task is big enough that one window will quit early or grade itself too kindly, and `ultrathink` when you just want this one turn to think harder.

These four get confused constantly because they all sound like "more." They are four different mechanisms operating on different axes. Here is how they actually differ.

| Setting | What it is | API effort sent | Triggers workflows? | Scope | Persists across sessions? |
| --- | --- | --- | --- | --- | --- |
| `xhigh` | A model effort level (deep reasoning, high token spend) | `xhigh` | No | Session-wide setting | Yes |
| `max` | A model effort level (deepest reasoning, no token cap) | `max` | No | Session-wide setting | No (session-only) |
| `ultrathink` | A one-turn prompt keyword for deeper reasoning | Unchanged | No | A single turn | N/A (not a setting) |
| `ultracode` | A Claude Code setting: `xhigh` plus auto-orchestration | `xhigh` | Yes (automatic) | Session-wide setting | No (session-only) |

The `ultracode` vs `ultrathink` distinction trips up the most people. `ultrathink` is a prompt keyword. Drop the word `ultrathink` anywhere in a single prompt and Claude Code adds an in-context instruction to think harder on that one turn. It does not change your session effort level, it does not change the effort value sent to the API, and it does not trigger a workflow. It is a per-turn nudge that only affects how hard Claude thinks.

Ultracode is the opposite shape: a session-wide setting that pins effort to `xhigh` and, crucially, auto-orchestrates workflows for every substantive task until you turn it off. One is a single-turn reasoning request. The other is a session-long behavioral mode that changes what Claude does, not just how hard it thinks. They share four letters and nothing else.

The `xhigh` vs `ultracode` line is cleaner once you see it through the failure-mode lens. Both send `xhigh`, so raw reasoning depth is identical. But `xhigh` alone still runs in one context window, which means it is still exposed to early quitting, self-grading, and goal drift on big tasks. Ultracode adds the automatic workflow layer that structurally removes those risks. If you want deeper reasoning without Claude spinning up parallel subagents on its own, set `xhigh` directly and leave ultracode off.

## The Claude Code Effort Ladder

Effort levels control adaptive reasoning, which lets the model decide whether and how much to think on each step. Here is the full ladder, with use cases and persistence behavior.

| Level | Use it for | Persists across sessions |
| --- | --- | --- |
| `low` | Short, scoped, latency-sensitive tasks that aren't intelligence-sensitive | Yes |
| `medium` | Cost-sensitive work that can trade off some intelligence | Yes |
| `high` | The balanced default for most coding. Default on Opus 5, Fable 5, Opus 4.8 | Yes |
| `xhigh` | Deeper reasoning at higher token spend. Anthropic's start point on Opus 5 | Yes |
| `max` | Deepest reasoning, no token cap. Prone to overthinking, test before adopting | No (session-only) |
| `ultracode` | `xhigh` plus automatic Dynamic Workflow orchestration on substantive tasks | No (session-only) |

Notice that the first five rungs only change reasoning depth within a single window. Ultracode is the only one that also changes the execution shape, moving the work out of one window and into many. That is why it sits at the top: it is not just the deepest thinker, it is the only setting that defeats the structural failure modes instead of just thinking harder inside them.

Which rungs you actually see depends on the model. Because ultracode sends `xhigh`, it only appears in the `/effort` menu on `xhigh`-capable models.

| Model | Ladder | Default | Ultracode in `/effort`? |
| --- | --- | --- | --- |
| [Opus 5](/blog/claude-opus-5) | `low` through `max`, no beta header needed | `high` | Yes |
| [Fable 5](/blog/claude-fable-5-mythos-5) | `low` through `max` | `high` | Yes |
| [Opus 4.8](/blog/claude-opus-4-8) | `low`, `medium`, `high`, `xhigh`, `max` | `high` | Yes |
| [Opus 4.7](/blog/claude-opus-4-7) | `low`, `medium`, `high`, `xhigh`, `max` | `xhigh` | Yes |
| [Sonnet 5](/blog/claude-sonnet-5) | `low`, `medium`, `high`, `xhigh`, `max` | `high` | Yes |
| [Opus 4.6](/blog/claude-opus-4-6), [Sonnet 4.6](/blog/claude-sonnet-4-6) | `low`, `medium`, `high`, `max`, no `xhigh` | `high` | No |

Sonnet 5 in that table surprises people: it carries the full ladder including `xhigh`, so ultracode is available on the cheap tier too. That is the most under-used combination in Claude Code right now, because a fan-out multiplies whatever per-token rate you are paying, and Sonnet 5's is the lowest of any `xhigh`-capable model.

If you set a level the active model does not support, Claude Code falls back to the highest supported level at or below it, so `xhigh` runs as `high` on Opus 4.6 rather than erroring. And note one persistence quirk: when you first run Fable 5, Opus 4.8, or Opus 4.7, Claude Code applies that model's default effort and holds it across sessions until you make an explicit choice. Opus 5 has no such hold, so a level you set earlier carries over.

A common error worth correcting: **the current models default to `high`, not `xhigh`.** That holds for Opus 5, Fable 5, and Opus 4.8. Opus 4.7 was the only model that ever defaulted to `xhigh`, and that default did not carry forward. So anything above balanced effort is a deliberate opt-in on every model shipping today, and ultracode is the most aggressive opt-in on the list.

Opus 5 changes what the lower rungs are worth, which matters more than it sounds. Anthropic recommends starting at `xhigh` for coding and agentic work on Opus 5, and separately notes that `low` and `medium` are meaningfully stronger there than on earlier Opus models, so use them liberally wherever your evals show quality holds. It also recommends against porting effort settings you tuned on Opus 4.7 or 4.8: the cost-to-quality curve moved, so run a fresh sweep.

## Model Is Who You Ask. Effort Is How Long They Work

The ladder above is one axis. Model choice is the other, and people collapse the two constantly, usually by turning effort up when they should have changed models, or by paying for a higher tier when a cheaper one at `xhigh` would have finished the job.

The distinction is easier to hold with a small mental model. Think of the lineup as people rather than tiers:

- **[Fable 5](/blog/claude-fable-5-mythos-5) is the specialist** you call in when everyone else is stuck. Narrow, expensive, occasionally the only one who can do it. On Max plans it is capped at 50% of your weekly usage limits and weighs roughly double an Opus session against that bucket, which is a fair description of how you should treat a specialist's calendar.
- **[Opus 5](/blog/claude-opus-5) is the expert.** Deep, broadly capable, and since July 24, 2026 it costs the same $5/$25 Opus 4.8 did while more than doubling it on Frontier-Bench. It is the default on Claude Max and the strongest model on Claude Pro, so on a subscription there is no premium to ration.
- **[Sonnet 5](/blog/claude-sonnet-5) is the strong generalist.** It will not out-reason the expert on the hardest work, and on high-volume execution it is the correct answer anyway at $3/$15.
- **Effort decides how long any of them works on the problem.** It does not change who is answering.

That gives you a clean two-step routing rule. First pick the person: does this need the expert, or will the generalist finish it identically? Then pick the duration: is this a `high` question, an `xhigh` question, or a question big enough that one window will quit early and needs ultracode to fan it out?

The failure mode worth naming is running the generalist at `max` on work that needed the expert at `high`. You pay for a great deal of thinking and still get an answer bounded by what that model knows. The model selection guide covers the first half of the decision in full, including what each tier costs and how the weekly allowance changes the math.

## How to Enable Ultracode

Three methods work. Two that look like they should work don't. Get this right and you'll save yourself a confusing debugging session.

**The three that work:**

The simplest is the `/effort` menu. Run `/effort` to open the slider, or set it directly:

```
/effort ultracode
```

You can also start a session in ultracode from the command line, which begins at `xhigh` effort with orchestration already on:

```
claude --effort ultracode
```

Or pass it through settings as a boolean, either via `--settings` on launch or through an Agent SDK control request:

```
{ "ultracode": true }
```

The `--effort ultracode` route needs **Claude Code v2.1.203 or later**. On older versions it prints `Unknown --effort value 'ultracode'` and the session quietly starts at your default effort instead, which is the kind of failure you only notice on the bill.

**The two that don't work:**

Ultracode is not part of the persisted `effortLevel` settings field, and it is not honored through the `CLAUDE_CODE_EFFORT_LEVEL` environment variable. Both channels handle `low` through `xhigh`, but ultracode (like `max`) is session-only and lives outside them. If you put `"effortLevel": "ultracode"` in your settings file, it silently won't take. Worse, if `CLAUDE_CODE_EFFORT_LEVEL` is set to anything other than `xhigh`, requests run at that level and ultracode's workflow orchestration stays inactive entirely; selecting ultracode then shows a warning that the environment variable is overriding effort for the session.

That session-only nature is the other thing to remember. Ultracode lasts for the current session and resets the moment you start a new one. Anthropic's guidance is blunt: "Drop back with `/effort high` when you return to routine work." It won't follow you between sessions the way `high` or `xhigh` will, which is by design. You don't want yesterday's audit-grade orchestration mode quietly applying to today's one-line typo fix.

If you want workflow behavior for a single task without committing the whole session to ultracode, there's an escape hatch. Include the keyword `ultracode` anywhere in a prompt and Claude Code runs that one task as a workflow without changing your effort level. Asking in your own words works too: "use a workflow" is treated as the same opt-in. (The literal trigger word was `workflow` before v2.1.160, which is why older write-ups still say so.) If the keyword fires when you didn't mean it, press `Option+W` on macOS or `Alt+W` on Windows and Linux to dismiss it for that prompt, or backspace right after the highlighted word. To switch the trigger off entirely, toggle "Ultracode keyword trigger" off in `/config`.

The keyword is an opt-in only in a prompt you type yourself, at the interactive prompt, in an IDE panel, in a Remote Control client, or in an Agent SDK app that stamps your keystrokes as human input. It deliberately does not fire from a `-p` prompt, an unstamped SDK prompt, a scheduled task, or a webhook payload or pull request comment relayed into the conversation. That last one matters: before v2.1.210 a PR comment containing the keyword could start a workflow on your account.

## Plan and Model Availability

Dynamic Workflows, which ultracode drives, are available on all paid plans, plus the Anthropic API, Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. They require Claude Code v2.1.154 or later. Only Pro needs a toggle:

| Plan | Workflows default | What you do |
| --- | --- | --- |
| Pro | Off | Turn on the Dynamic workflows row in `/config` |
| Max | On | Available out of the box |
| Team | On | Available out of the box |
| Enterprise | On | An admin can disable it org-wide in managed settings |

Pro is not gated out. That's a meaningful correction to the assumption that workflow-style orchestration is a Max-and-up feature. Pro users enable it from `/config` and then ultracode becomes available on `xhigh`-capable models just like anywhere else.

Two requirements gate everything. You need Claude Code v2.1.154 or later, so run `claude update` if you're behind. And ultracode only shows up when workflows are enabled. If you disable workflows through the `/config` toggle, through `"disableWorkflows": true` in settings, or through `CLAUDE_CODE_DISABLE_WORKFLOWS=1`, ultracode is removed from the `/effort` menu entirely. No workflows means no ultracode, because the orchestration half of the setting has nowhere to run.

If Fable 5 is the model behind your ultracode session, [how to brief Fable 5 so the extra effort is not wasted](/blog/fable-5-best-practices) covers the prompting habits that make the extra effort pay off.

## The Token-Cost Reality Check

This is the section that matters most, so let's be precise and balanced about it.

The official cost language is direct. A workflow spawns many agents, so "a single run can use meaningfully more tokens than working through the same task in conversation. Runs count toward your plan's usage and rate limits." With ultracode on, that multiplier applies to every substantive task in the session, not just one run you chose to fire. The same isolation that defeats the three failure modes is what makes ultracode expensive: you are paying for many agents instead of one, every time.

Here is the part people miss: there is no token spending cap. What bounds a run is the agent caps, 16 concurrent and 1,000 total, which stop a runaway script rather than a costly one. A thousand agents is a very expensive ceiling.

Two real controls exist, and both are worth setting before you turn ultracode on:

**The size guideline** in `/config` keeps the workflows Claude writes smaller by default. `unrestricted` is the default; `small` aims for fewer than 5 agents, `medium` fewer than 15, and `large` fewer than 50. Claude Code passes this to Claude as advice, so a prompt calling for a different scale still overrides it, and the runtime caps apply regardless. Requires v2.1.202 or later.

**The large-workflow warning** flags a run that schedules more than 25 agents or projects past 1.5 million tokens, showing a `Large workflow` notice on the run's progress line so you can stop it from `/workflows`. It is advisory: it does not pause or limit anything. Requires v2.1.203 or later. If you set a size guideline, its agent count replaces the 25-agent threshold.

**And here is the trap.** Sessions with ultracode on **do not show that warning at all**, because turning ultracode on is already treated as opting in to large runs. So the one automatic signal that a run is getting expensive is switched off by the exact setting most likely to make runs expensive. If you run ultracode, the warning is not coming; watch `/workflows` yourself.

One more lever that costs nothing to pull: every agent in a workflow uses your session's model unless the script routes a stage elsewhere or `CLAUDE_CODE_SUBAGENT_MODEL` is set, and that variable overrides both. Check `/model` before a large run if you habitually sit on an expensive tier, and point the sub-agent variable at [Sonnet 5](/blog/claude-sonnet-5) so a fan-out multiplies the cheaper rate instead of the dearer one.

The community reaction reflects that double edge. These are practitioner reports, not Anthropic figures, so treat them as anecdotes rather than guaranteed numbers. On Hacker News, one user said they "spun up 62 Opus 4.8 sub-agents and hit the 5-hour cap in 18 minutes," and another described roughly 90 agents running to review a fairly small package. A more pointed critic called it "tokenmaxxing disguised as a product," while others reported reliability gripes about runs that "give up constantly." Separately, findskill.ai (citing r/ClaudeAI) reported a Max ($200/mo) user burning about 20% of their weekly token limit on day one, and a Pro user reportedly hitting their cap in roughly ten minutes. The sentiment splits cleanly: powerful for genuinely large work, easy to overspend on small work.

The defense is straightforward: calibrate before you commit. Run ultracode on a scoped task first to see how it decomposes and how many subagents it spawns, then decide whether the budget makes sense for your real workload. Anthropic raised Claude Code's rate limits alongside the Opus 4.8 launch specifically to absorb heavier workflow consumption, so if you've bumped the old ceiling, the new headroom helps. If you want to cut the token cost of a long session, our usage optimization guide covers the patterns that keep multi-agent runs inside their token envelope. And because a fan-out is not automatically a win, see [when fanning out across agents adds cost without adding quality](/blog/multi-agent-orchestration-cost) before you leave ultracode on by default. The [higher usage limits guide](/blog/higher-usage-limits) covers the rate-limit headroom directly.

## When to Use Ultracode (and When to Avoid It)

The test is the same one the [Dynamic Workflows guide](/blog/dynamic-workflows) lands on: **does this task really need more compute?** Most traditional coding tasks do not need a panel of five reviewers. Reserve ultracode for work you'd otherwise hand to several engineers in parallel, where the task naturally decomposes into independent angles that benefit from cross-checking. If it's one person, one afternoon, ultracode is overkill and a single agent at `high` or `xhigh` is the right tool.

**Use ultracode when:**

- You're running a codebase-wide audit (security, dead code, performance) where coverage matters more than speed, and the early-quitting failure mode would otherwise leave files unchecked.
- You're planning a migration that touches hundreds of files and you want every change verified before it lands. The [large codebase playbook](/blog/large-codebase-playbook) covers this class of work in depth.
- You're stress-testing a plan from multiple independent angles, where you specifically want agents that did not write the plan to try to refute it.
- The work is high-stakes enough that the adversarial verification loop is worth paying for.

**Avoid ultracode when:**

- The task fits a single agent in one pass. There is no failure mode to defeat, so the token cost dwarfs the benefit and the verification loop adds latency you don't need.
- You already know the role decomposition. If you can name "Frontend, Backend, Quality" up front, a deliberately structured [Agent Teams](/blog/agent-teams) setup gives you tighter control than letting Claude auto-orchestrate. For a side-by-side of when to reach for each, see [Ultracode and Dynamic Workflows vs Agent Teams](/blog/ultracode-dynamic-workflows-agent-teams).
- You're doing routine editing. Ultracode applies its behavior to every substantive task, so ordinary changes get the full treatment whether they need it or not.

One case deserves its own line: running ultracode with Fable 5 as the model. Fable already draws on half your weekly allowance on Max plans, so a large fan-out under ultracode is the fastest way to burn through it. Check [what ultracode does to your Fable weekly allowance](/blog/fable-5-usage-credits) before combining the two.

A few operational facts are worth naming. Workflow subagents always run in `acceptEdits` mode and inherit your session tool allowlist regardless of your permission mode, so file edits are auto-approved inside a workflow. Parallel agents can step on each other when they edit the same file, which is why file-mutating fan-outs run in isolated worktrees. There's no mid-run human input, so you can't redirect an agent partway through. But a run isn't fragile: you can pause and resume it, and an interrupted run picks up from its last completed stage by run ID rather than restarting, replaying the finished stages from cache instead of re-running them. For unattended runs, pair ultracode with [Auto Mode](/blog/auto-mode). Worth noting: in Auto permission mode, the per-run workflow approval prompt is skipped entirely when ultracode is on, which keeps the parallelism flowing but removes one of your last manual checkpoints.

The runtime has guardrails. A workflow runs up to 16 concurrent agents (fewer on machines with limited CPU cores) and caps at 1,000 agents total per run as a runaway-loop backstop. The workflow script has no direct filesystem or shell access of its own. Only the spawned agents read, write, and run commands. Those bounds limit the blast radius, but they don't impose a token cap, which is exactly why the cost discipline lands on you. The orchestration patterns underneath all of this map onto the broader thread model in [thread-based engineering](/blog/thread-based-engineering).

## Frequently Asked Questions

**What's the difference between ultracode and ultrathink?**

They're completely different mechanisms. `ultrathink` is a one-turn prompt keyword: drop it in a prompt and Claude reasons harder on that single turn, without changing your session effort or the effort value sent to the API, and without triggering a workflow. Ultracode is a session-wide setting that pins effort to `xhigh` and auto-orchestrates Dynamic Workflows for every substantive task until you turn it off. One is a per-turn nudge. The other is a session-long mode that changes what Claude does.

**Does ultracode persist across sessions?**

No. Ultracode applies to the current session only and resets when you start a new one. Anthropic's recommendation is to drop back to `/effort high` when you return to routine work. The persistent levels are `low`, `medium`, `high`, and `xhigh`. Both `max` and ultracode are session-only.

**Can my admin disable ultracode for our org?**

Yes, indirectly. Ultracode depends on Dynamic Workflows, and an org admin can disable workflows for the whole organization through managed settings or the Claude Code admin settings page. When workflows are disabled, ultracode is removed from the `/effort` menu, so disabling workflows disables ultracode.

**Is there a spending cap on ultracode?**

No token cap, no. The runtime caps agents (16 concurrent, 1,000 total per run), which stops a runaway script rather than an expensive one, and runs count toward your plan's usage and rate limits. Your real controls are the Dynamic workflow size setting in `/config`, pointing `CLAUDE_CODE_SUBAGENT_MODEL` at a cheaper model, and calibrating on a scoped slice before committing to a large task. Note that the automatic `Large workflow` warning, which fires above 25 agents or 1.5 million projected tokens, is suppressed in ultracode sessions, so on ultracode you watch `/workflows` yourself.

**Which models support ultracode?**

Any model with `xhigh` on its effort ladder, which today means [Opus 5](/blog/claude-opus-5), [Fable 5](/blog/claude-fable-5-mythos-5), Opus 4.8, and Opus 4.7. On models without `xhigh` (Opus 4.6, Sonnet 4.6), the `/effort` menu doesn't offer ultracode at all. It shipped alongside Opus 4.8, and most ultracode sessions now run on Opus 5, which is the default model on Claude Max and the strongest model on Claude Pro.

**Should I run ultracode on Opus 5 or Fable 5?**

Opus 5, in almost every case. It costs $5/$25 against Fable 5's $10/$50 and wins seven of the eight published head-to-head evals, and ultracode multiplies whatever the per-token rate is across many agents at once. Fable 5 also draws on a 50% cap of your weekly usage limits on Max plans and weighs roughly double an Opus session against that bucket, so a fan-out on Fable is the fastest way to exhaust a weekly allowance. Run Fable 5 under ultracode only on a workload you have measured Opus 5 falling short on. The model selection guide covers that call in full.

**Does Opus 5 default to ultracode or xhigh?**

Neither. Opus 5 defaults to `high`, the same as Fable 5 and Opus 4.8. Opus 4.7 was the only model that defaulted to `xhigh`, and that behavior did not carry forward. Anthropic recommends starting at `xhigh` for coding and agentic work on Opus 5, which means setting it yourself with `/effort xhigh`. Ultracode is always an explicit opt-in.

**Can Pro users use ultracode?**

Yes. Dynamic Workflows are available on all paid plans including Pro. On Pro, you enable workflows from the Dynamic workflows row in `/config` first. Once workflows are on and you're on an `xhigh`-capable model, ultracode appears in `/effort` like it does on any other plan. Pro is not gated out.

## The Bottom Line

Ultracode is the most aggressive setting on the `/effort` ladder, and the only one that changes what Claude does rather than just how hard it thinks. It is the workflow toggle left on for the whole session, which means it structurally defeats the three failure modes (early quitting, self-grading, goal drift) that a single context window hits on hard work. That makes it genuinely powerful for audits, migrations, and plan stress-tests you'd otherwise split across several engineers. It also makes it the easiest setting to overspend on, because the automatic workflow layer applies to every substantive task and convergence has no token cap. The Bun team's Zig-to-Rust port (about 750,000 lines of Rust, 11 days from first commit to merge, 99.8% of the test suite passing) is the headline example of what orchestration at this scale can do. You may see it cited elsewhere as a six-day, million-line effort: that framing comes from Bun's own account (six days of active work, roughly 960,000 lines of Zig translated), while the figures here follow Anthropic's count of the Rust output from first commit to merge. Most teams won't be porting a runtime. They'll be deciding, task by task, whether this particular job is worth several engineers' worth of parallel work.

Treat ultracode as a deliberate mode, not a default. Turn it on for the work that earns it, calibrate the cost on a scoped run, and drop back to `/effort high` when you're back to routine edits.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
