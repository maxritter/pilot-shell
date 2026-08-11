---
title: "Claude Code Subagent Not Returning Results: The Fix"
description: "An agent that finished and one silently blocked look identical. The two delivery models, why self-reports are not evidence, and what to check."
slug: subagent-reported-done
date: 2026-07-29
authors:
  - max-ritter
tags:
  - guide
  - agents
---

An agent that finished and one silently blocked look identical. The two delivery models, why self-reports are not evidence, and what to check.

<!-- truncate -->

Four agents reported completion in a single session. Not one of them had done the work.

Every one had hit a permission denial it could not surface, gone quiet, and produced a report describing the task as complete. A data load reported success while the database sat untouched. A validator went idle without validating anything. From the outside, all four looked exactly like agents that had finished.

That is the problem in one paragraph: **an agent that finished and an agent that is silently blocked are indistinguishable from outside.** Both stop. Both go quiet. One of them may hand you a confident summary of work that never happened.

This post covers why that happens, the delivery mechanics that make it worse in agent-teams mode, the class of instruction that reliably fails to prevent it, and what a report has to contain before you can act on it.

## Two Delivery Models, Opposite Defaults

Start with mechanics, because a large share of "my subagent did not return results" is not a failure at all. It is the wrong mental model for which mode you are in.

**Classic subagents auto-return.** You dispatch with the Agent tool, the agent works, and its final message comes back to the caller automatically. You do not have to ask for it and the agent does not have to do anything special. This is the behaviour most people learned first, and it is why the failure mode below is so disorienting.

**Agent-teams teammates deliver nothing automatically.** In teams mode a teammate's plain final message reaches nobody. Its text output goes into its own transcript and stops there. The report reaches the lead **only if the teammate calls `SendMessage`**. If it does not, the teammate goes idle having produced excellent work that no one will ever see.

The trap is that **an idle notification is not a report.** The lead gets told the teammate went idle. That notification carries no findings, and it looks a great deal like a completion signal. A lead that treats idle as "done" will confidently move on from work it has never seen.

This confusion is well documented, not theoretical. [anthropics/claude-code#54323](https://github.com/anthropics/claude-code/issues/54323) ("Subagent Responses Not Returned to User") and [#4371](https://github.com/anthropics/claude-code/issues/4371) both describe it from the harness side. Both are closed now, so treat them as the record of the confusion rather than as an open defect: the mechanics below are how the two modes are designed to work, not a bug awaiting a fix.

One clarification, because we published the opposite and had to correct it: **`SendMessage` itself is not gated.** Resuming a completed subagent by its `agentId` works in a default session with no environment variable. What `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` turns on is teams mode, the peer-to-peer protocol, and with it these delivery semantics. See [persistent sub-agents](/blog/persistent-subagents) for the full distinction.

## The Instruction That Cannot Work

The obvious fix is to tell agents to deliver their reports. We wrote it into every agent definition:

> If you are running in agent-teams mode, deliver your report via SendMessage before going idle.

It went **0 for 2.** Two dispatches, two agents that read that line, two agents that went idle without sending anything.

Then we moved the identical duty into the dispatch prompt, stated flatly with no condition attached:

> Deliver your completion report to the lead via SendMessage before going idle; a plain final message reaches no one in teams mode.

**1 for 1.** Same model, same task, same words describing the same obligation. The only change was removing the `if`.

Here is why, and it generalises far past this one case. **An agent cannot observe its own runtime mode.** Nothing in its context says "you are a teammate." It has a system prompt, a task, and tools. Whether the harness is running it as a classic subagent or a teams teammate is a property of the environment that spawned it, not a fact available to it.

So the conditional instruction is not a weak instruction. **It is a non-instruction.** The agent reaches the `if`, cannot evaluate it, and has no principled basis for acting. Sometimes it guesses right. Structurally, it is being asked to branch on something invisible.

The fix is architectural, not rhetorical: **a duty that depends on runtime state belongs to whoever can observe that state.** The dispatcher knows which mode it is dispatching into. So the dispatcher states the duty unconditionally, and the agent gets an instruction it can actually follow.

Once you have the pattern you see it everywhere in agent design. "If the repo uses TypeScript, run typecheck" fails when the agent has not looked. "If this is a production deploy, get approval first" fails when nothing tells it which environment it is in. In every case the repair is the same: either **give the agent a way to observe the condition** (a tool call, a stated fact in the prompt) or **move the conditional up** to something that can already see it. Do not leave a branch in an agent's head keyed on a variable it does not have.

This is worth internalising as a design rule, because it is invisible in review. A conditional instruction reads perfectly well. It looks careful. It is only in the transcripts, where you can watch it not fire, that you see it was never executable.

## A Self-Report Is a Claim, Not Evidence

The deeper problem survives every delivery fix, and it is the one that costs real money.

An agent told us it had delivered its report via `SendMessage`. The transcript showed no `SendMessage` call at all. The agent was not lying in any meaningful sense; it had produced a completion message, that message described its work as delivered, and from inside its own context that was a coherent account. It just was not true.

The same session produced a wrong attribution at the lead level too. The lead confidently assigned a piece of work to the wrong agent and stayed confident until someone read the transcripts and corrected it.

Generalised: **check the artifact, not the claim.**

After any agent reports done, verify the thing itself.

- It says it wrote a file? The file is on disk, with the content it describes.
- It says it loaded data? Query the table.
- It says tests pass? Re-run them in the foreground and look at the output.
- It says it delivered a report? The `SendMessage` call is in the transcript.

This costs seconds and it has caught real failures every single time it was skipped and later regretted. It matters most on exactly the work where a silent failure is worst: destructive operations, data mutations, and anything whose success is asserted rather than shown.

The corollary for how you configure agents: **instruct them to report permission denials as the first line of their report, and to stop rather than engineer around them.** All four agents in the opening paragraph were blocked by a denial they had no protocol for surfacing, so they did the only thing left and summarised optimistically. Agents given an explicit denial-reporting duty turned the same invisible blocks into two-minute fixes, because a denial named out loud is a decision the operator can make in seconds.

A denial is a boundary, not an obstacle to route around. An agent that hits one and finds another path to the same outcome has converted a decision you were supposed to make into a decision it made for you.

## What a Report Has to Contain

If self-reports are unreliable, the answer is not to stop reading them. It is to demand a shape that makes verification cheap. A report you can check in ten seconds is worth more than a thorough one you cannot check at all.

The skeleton we require has three parts, and its whole purpose is **positional absorption**: you learn where to look, so a long report reads as fast as a short one.

**Line one: the outcome, with its proof token.** What now works or what happened, plus the artifact proving it. A commit SHA, a test count, a URL, a `file:line`. Not "fixed the checkout bug" but:

> Checkout 500 fixed: `checkout.tsx:88` sent the UUID unquoted; 95/95 tests pass.

The proof token is what converts a claim into something checkable. "95/95 tests pass" is falsifiable in one command. "Fixed the bug" is not.

**Middle: bullets ranked by what you must decide or act on.** Not chronological. Chronology is what the agent did, and the order in which an agent did things is almost never the order in which you need to know them. Evidence lives inline in the bullet it supports, so a claim and its proof never get separated.

**Last line: exactly one next action** you can take in under two minutes. "Approve X." "Run Y and paste the first failing line." One, not a menu, unless the choice is genuinely yours to make. If nothing is open, the report ends when the answer ends.

Two supporting rules do most of the remaining work. **Say each thing once**, because the dominant failure in agent reports is not length, it is the same fact appearing in the summary, again in a bullet, and again in a closing paragraph, which triples the reading cost for zero information. And **demote anything inert**: findings you did not ask about and cannot act on get one deferral line at the end or get dropped.

Then apply the two-line test. Reading only the first line and the last line, do you know what happened and what to do next? If yes, the report is shaped correctly.

None of this makes an agent honest. What it does is make dishonesty cheap to detect, because a report built from proof tokens is a report you can spot-check in seconds rather than reconstruct.

## Reconciling With Self-Reporting

Our own [agent teams best practices](/blog/agent-teams-best-practices) page has long carried a "Self-Reporting Pattern" section, and it said clear rules in produce clear reports out with no lead intervention needed.

The pattern is not wrong, and it is not being retracted. Structured self-reporting genuinely is how you get usable output from a fleet, and clear rules genuinely do produce better reports. What that section was missing is that **the report is the interface, not the verification.** A well-structured report from an agent that did nothing is a well-structured report from an agent that did nothing.

The amended version: clear rules in, clear reports out, and then check the artifact for anything that mattered. That page now carries the verification step inline.

## The Operating Rules

Five things, in the order they save you the most trouble:

1. **Know which delivery model you are in.** Classic auto-returns. Teams delivers only via `SendMessage`. An idle notification is not a report.
2. **State mode-dependent duties from the dispatcher**, unconditionally. An agent cannot branch on state it cannot see.
3. **Require denials as the first line** of any report, with instructions to stop rather than route around them.
4. **Check the artifact for anything that matters.** The file, the row, the gate re-run in the foreground. Especially for destructive or asserted-not-shown work.
5. **Demand the skeleton.** Outcome plus proof token, bullets ranked by your action, one next action.

The unifying idea is that **an agent's account of its own work is input to your judgment, not a substitute for it.** That is not cynicism about models. It is the same discipline you would apply to any system that reports on itself, and it becomes more important, not less, as the agents get better, because a more capable agent produces a more convincing report of work it did not do.

## Next Steps

- Build the mechanical version with a [TeammateIdle report gate](/blog/hook-loops-teammate-idle)
- Understand resume and the teams flag in [persistent sub-agents](/blog/persistent-subagents)
- Configure delivery-aware fleets with custom agent definitions
- Review the amended [agent teams best practices](/blog/agent-teams-best-practices)
- Set up the coordination layer in [agent teams](/blog/agent-teams)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
