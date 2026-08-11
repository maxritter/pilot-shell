---
title: "Claude Code Loops: Stop Prompting, Start Looping"
description: "Claude Code runs four loop types: turn-based, goal-based, time-based, and proactive. What each means and how to set a real stop condition."
slug: claude-code-loops
date: 2026-07-07
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code runs four loop types: turn-based, goal-based, time-based, and proactive. What each means and how to set a real stop condition.

<!-- truncate -->

For most of the last two years, using Claude Code meant prompting it. You wrote a request, it worked, you read the result, you wrote the next one. You were the loop. Claude Code loops move that job to the agent: it repeats cycles of work on its own until a stop condition is met.

A loop is simple to define. An agent repeats cycles of work until a stop condition is met. The skill is no longer writing the perfect prompt. It is choosing the right kind of loop and giving it a stop condition it can actually check. The community got here first, wiring up overnight runs with [the Ralph Wiggum technique](/blog/ralph-wiggum-technique). Claude Code now ships the loop types natively, and the Claude Code team named the taxonomy in its June 2026 guide, [Getting started with loops](https://claude.com/blog/getting-started-with-loops). This post builds on that framework: the four loop types, what each one hands off, and how to stop it before it burns tokens on work you did not ask for.

## The agent loop vs loops

Two things share the word loop, and the current search results blur them. Keeping them apart is the whole game.

The agent loop, singular, is the execution cycle Claude runs to answer one prompt. Anthropic's Agent SDK docs describe it precisely: Claude "evaluates your prompt, calls tools to take action, receives the results, and repeats until the task is complete." That is the engine. It cycles through as many tool-calling turns as the task needs, then replies. It runs whether you notice it or not, every time you send a prompt. If you have ever asked what an agent loop is, this cycle is the answer.

Loops, plural, are the user-facing patterns you design around that engine: how a run is triggered, when it stops, and how many turns it gets. This post is about the plural. Designing agentic loops means choosing among those patterns, not re-implementing the engine. Claude Code gives you four of them.

## Loop engineering: why loops are everywhere now

Loop engineering is the name for this shift. You stop typing every prompt and start designing the system that prompts the agent for you. Simon Willison was early to it in [Designing agentic loops](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/), framing an agent as something that runs tools in a loop to reach a goal, where the skill is in how carefully you set that loop up. The phrase spread across engineering blogs through mid-2026 for a concrete reason: once an agent can verify its own work, the bottleneck stops being how fast you can type and starts being how well you can specify done.

That is the trade. A turn-based session keeps you in the loop on every step. A well-built loop takes you out of it, which is only safe when the agent can check the thing you would have checked. Most of this post is about making that check real. Not every task needs a loop, though. Start with the simplest thing that works, and reach for a loop only when the task repeats, runs long, or has a finish line you can measure.

## The four types of Claude Code loops

Claude Code loops come in four types, sorted by what you hand off to the agent. Each answers the same four questions: what triggers it, when it stops, what it is best for, and how to keep the cost down.

### Turn-based loops

- **Triggered by:** a prompt you send.
- **Stops when:** Claude judges the task is done or needs more from you.
- **Best for:** short, one-off work that is not part of a schedule.
- **Manage cost by:** writing specific prompts and moving verification into skills so fewer turns are wasted.

Every prompt is already a loop. Claude gathers context, edits, runs the check, and hands back what it thinks works. Then you check it and write the next prompt. You are the verification step.

Move that step into a skill and Claude checks more of its own work. Ask it to add a like button, and a verification skill can tell it what done means instead of leaving that judgment to you. The more measurable the check, the better this holds. [Claude Code skills](/blog/claude-skills-guide) are where that verification lives:

```
<!-- .claude/skills/verify-frontend-change/SKILL.md -->
 
1. Start the dev server and open the edited page.
2. Interact with the change: click the control, confirm the state change.
3. Screenshot before and after.
4. Check the browser console for zero new errors or warnings.
5. Run a performance trace and audit Core Web Vitals.
   If any step fails, fix it and rerun from step 1.
```

Give the skill tools or connectors so Claude can see, measure, and interact with the result. Quantitative checks self-verify far more reliably than "looks right."

### Goal-based loops (/goal)

- **Triggered by:** a prompt you send in real time.
- **Stops when:** the goal is met, or a turn cap you set is reached.
- **Best for:** tasks with a verifiable exit condition.
- **Manage cost by:** setting a specific success criterion and an explicit turn cap.

One turn is often not enough. Agents do better when they can iterate, and `/goal` lets Claude keep going until it hits a target you define. Each time Claude tries to stop, an evaluator model checks your condition and sends it back to work if the condition is not met. You are no longer the one deciding whether the result is good enough. You wrote the definition of good enough up front, so Claude does not end the loop early on its own judgment.

Deterministic criteria work best: a test count, a score threshold, an empty lint report.

```
/goal get the homepage Lighthouse score to 90 or above, stop after 5 tries
```

The turn cap is the safety valve. Without `stop after 5 tries`, a vague goal can spend a long time deciding it is close enough. Run `/goal` with no arguments and it reports the current run's turn count and token usage, so you can see the cost as it accrues.

### Time-based loops (/loop and /schedule)

- **Triggered by:** a time interval.
- **Stops when:** you cancel it, or the work finishes (the PR merges, the queue empties).
- **Best for:** recurring work, or reacting to systems outside your project.
- **Manage cost by:** using longer intervals, or reacting to events instead of the clock.

Some work is the same task on new inputs: summarize the overnight Slack messages every morning. Other work depends on an external system that changes on its own, like a pull request that may pick up a review or fail CI. The simplest way to handle both is to check on an interval and react to what changed.

The [`/loop` command reruns a prompt on a timer](/blog/scheduled-tasks):

```
/loop 5m check my PR, address review comments, and fix failing CI
```

`/loop` runs on your machine. Turn the machine off and the loop stops. Omit the interval and Claude self-paces its own iterations instead of waiting on a clock. To move a recurring loop off your laptop, create a [cloud routine with `/schedule`](/blog/routines-guide), which runs on Anthropic's infrastructure and can fire on a cron schedule, an API call, or a GitHub webhook. `/schedule` is in research preview.

Reacting to events instead of the clock is cheaper still. That is what [the event-driven Monitor tool](/blog/monitor) does: it wakes the session only when a watched command emits a line, so a quiet system costs nothing.

### Proactive loops

- **Triggered by:** an event or schedule, with no human in the loop in real time.
- **Stops when:** each task exits when its goal is met; the routine runs until you turn it off.
- **Best for:** recurring streams of well-defined work: bug reports, issue triage, migrations, dependency upgrades.
- **Manage cost by:** routing routines to smaller, faster models and saving the most capable model for judgment calls.

The other three types compose into something that runs without you. A proactive loop chains a trigger, a goal, and orchestration so a stream of well-defined work gets handled start to finish. The pieces:

- `/schedule` (research preview) fires a routine on a cron schedule.
- `/goal` defines what done means, and skills document how to verify it.
- [Dynamic workflows](/blog/dynamic-workflows) (research preview) orchestrate the agents that triage each item, fix it, and review the fix.
- [Auto mode](/blog/auto-mode) lets the routine run without stopping to ask permission.

Put together for an incoming-feedback pipeline:

```
/schedule every hour: check the project-feedback channel for bug reports
/goal do not stop until every report found this run is triaged, actioned, and answered
```

When a fix is non-trivial, a dynamic workflow can explore three solutions in parallel worktrees and have a judge review them adversarially. This is the closest a human-in-the-loop AI agent gets to zero human in the loop, and it is also where an unbounded run costs the most. The goal and the model routing matter more here than anywhere else.

## Which loop to reach for

The four types map cleanly to what you are willing to hand off.

| Loop | You hand off | Use it when | Reach for |
| --- | --- | --- | --- |
| Turn-based | the check | you are exploring or deciding | custom verification skills |
| Goal-based | the stop condition | you know what done looks like | `/goal` |
| Time-based | the trigger | the work runs on a schedule or outside your project | `/loop`, `/schedule` |
| Proactive | the prompt | the work is recurring and well-defined | all of the above plus dynamic workflows |

Read the table top to bottom and you are handing off more each row: first the verification, then the finish line, then the trigger, then the prompt itself.

## Setting a stop condition that actually holds

Every loop above lives or dies on its stop condition. A loop with a vague finish line either quits early or runs forever, and both waste tokens.

The rule: make the condition something Claude can measure without your judgment. Compare these two:

- Weak: `make the tests better`. There is no line Claude can check, so it decides for you.
- Strong: `every test in the suite passes`. Claude runs the suite and reads the exit code.

Deterministic conditions that hold up well: a full test suite passing, a Lighthouse score at or above a number, a lint report with zero errors, a queue with zero items left, a PR in the merged state. Each is a fact Claude can read, not a feeling it has to have. When the finish line is a number or a state, `/goal` can enforce it and the evaluator has something concrete to check. When it is a vibe, you are back to being the loop yourself.

## Keeping quality high while looping

A loop's output is only as good as the system around it. Four things raise the floor:

- **Keep the codebase clean.** Claude follows the patterns it finds, so consistent existing code produces consistent new code.
- **Give Claude a way to verify its own work.** Encode what good looks like as a skill, with tools or connectors so it can see and measure the result.
- **Keep docs reachable.** Current framework and library docs in context beat the model guessing at an old API.
- **Use a second agent for review.** A reviewer with fresh context is less biased than the agent that wrote the change. The built-in [`/code-review`](/blog/code-review) skill runs that pass, and Code Review for GitHub does it on every PR.

One habit separates a loop that improves from one that repeats mistakes: when a result misses the bar, do not just fix that one instance. Encode the fix so every future iteration clears it. A loop that upgrades its own system is worth more than a loop that only runs.

## Managing token usage

Loops spend tokens whether or not they produce anything, so give every loop clear boundaries.

- **Pick the right primitive and model.** A small task does not need multiple agents or a goal loop. Some steps run fine on a cheaper, faster model; save the expensive one for judgment.
- **Define success and stop criteria explicitly.** This is the stop-condition discipline again, applied to cost.
- **Pilot before a large run.** A dynamic workflow can spawn hundreds of agents. Gauge the cost on a small slice first.
- **Use scripts for deterministic work.** Running a script is cheaper than reasoning through the same steps every iteration.
- **Do not run routines more often than the thing you watch changes.** Match the interval to reality.

Claude Code shows you where the tokens go. `/usage` breaks down recent usage by skills, subagents, and MCPs. `/goal` with no arguments reports the current run's turn count and token usage. `/workflows` shows each agent's token usage and lets you stop any agent mid-run. For the wider picture on cost, see our guide to Claude Code token optimization.

For the patterns behind the native loops, we have gone deep on two precursors: [thread-based autonomous loops](/blog/autonomous-agent-loops), which ship features overnight, and native task management, which gives a loop persistent, dependency-aware tasks to work through.

## Frequently asked questions

### What are the four types of loops in Claude Code?

Turn-based, goal-based, time-based, and proactive. They are sorted by what you hand off to the agent: the verification check, the stop condition, the trigger, or the whole prompt. Turn-based is every prompt you send. Goal-based runs to a target with `/goal`. Time-based reruns on an interval with `/loop` or `/schedule`. Proactive composes the others to run with no human in the loop.

### What is the difference between /loop and /schedule?

`/loop` runs on your machine and reruns a prompt on an interval; when your computer is off, it stops. `/schedule` moves the loop to the cloud as a routine that runs on Anthropic's infrastructure, so it keeps firing on its cron schedule whether or not your laptop is on. Reach for `/loop` for quick local polling and `/schedule` for recurring work that should outlive your session.

### How does a loop decide when to stop?

By checking a stop condition. In a turn-based loop, Claude decides the task is done or that it needs you. In a goal-based loop, an evaluator model checks your condition every time Claude tries to stop and sends it back if the condition is not met, until the goal is reached or a turn cap is hit. Deterministic conditions, like a passing test suite or a score threshold, are the most reliable.

### What is an agentic loop?

An agentic loop is an agent repeating cycles of work until a stop condition is met. The narrow, singular version is the agent loop that answers one prompt: Claude reads context, calls tools, checks the result, and repeats across turns until the task is done. The broader, plural version is the loop patterns you design around it, which is what this post covers.

## Getting started

Look at the work you already do. Find one task where you are the bottleneck and ask which piece you could hand off. Can you write the check that proves the work is done? Is the goal clear enough to state as a number or a state? Does the work arrive on a schedule? The answer points at a loop type.

Then pick that one task, write the verification or the stop condition, and run it. Watch where it stalls or overreaches, and tighten the condition. That loop is the first of many. The engineers pulling ahead right now are not writing better prompts. They are designing better loops.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
