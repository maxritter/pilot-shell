---
title: "Claude Code Persistent Sub-Agents: Resume + Nest"
description: "Claude Code sub-agents are now resumable via SendMessage and nest 5 levels deep. The persistent sub-agent pattern, field data, and the gotchas."
slug: persistent-subagents
date: 2026-06-12
authors:
  - max-ritter
tags:
  - guide
  - agents
---

Claude Code sub-agents are now resumable via SendMessage and nest 5 levels deep. The persistent sub-agent pattern, field data, and the gotchas.

<!-- truncate -->

For two years the rule was simple: a sub-agent ran once, returned a summary, and was gone. You re-briefed a fresh agent for every follow-up, and you accepted that its context window was a throwaway you filled as full as possible before it closed. Two changes have quietly broken that model. Sub-agents are now **resumable** through `SendMessage`, and as of [nested sub-agents](/blog/nested-subagents) they can spawn their own children five levels deep. Put those two together and the right way to run Claude Code sub-agents inverts.

The new pattern is the **persistent sub-agent**: one warm, named specialist per domain that you keep alive across an entire session, feed new work through resume instead of fresh spawns, and let delegate its noisy collection to throwaway children. We have been running it in production, and the difference is not subtle. A frontend specialist we resumed eight times held every file it touched and every decision it made across the whole chain, and iteration latency dropped from cold builds of 12 to 40 minutes down to 4 to 7 minutes per warm round.

This guide is the field manual nobody has written yet. The mechanics of `SendMessage` resume, the version timeline that got us here, the persistence model and its 30-day expiry, the compaction caveat that silently degrades a long resume chain, the token ceiling and when to retire an agent, the fork-versus-resume decision, and the naming convention that keeps a resumable agent coherent. All of it is verified against the shipped binary and live session data, not the docs, which have not caught up.

## How Sub-Agents Became Resumable

The capability did not arrive in one release. It evolved across three, and knowing the timeline tells you why the old advice you have read is wrong.

| Version | What changed |
| --- | --- |
| v2.0.28 | Claude could first "choose to resume sub-agents." This was the `Task({resume})` era. |
| v2.1.63 | The Task tool was renamed the Agent tool. |
| v2.1.77 | The `resume` parameter was removed from the Agent tool. Resume now happens through `SendMessage({to: agentId})`, which auto-resumes a stopped agent in the background. |
| v2.1.172 | Sub-agents can spawn their own sub-agents, capped at depth 5. |

The critical line is v2.1.77. If you have copied a kit or a snippet that resumes an agent with `Task({ prompt: "...", resume: "abc123" })`, it fails today and has failed for roughly 95 releases. The old Task-tool resume parameter was removed; the syntax is dead. We caught this in our own framework, where the sub-agent skill still documented the v2.0.28 shape long after it stopped working. The mechanism that actually runs is `SendMessage`, and the distinction matters because the harness surfaces resume in three different places, none of which mention the old parameter.

For the running record of releases like this, we mirror Anthropic's official notes in our changelog.

## The SendMessage Resume Mechanic

When you spawn an agent, its result message ends with its `agentId`, a handle in the format `a...` followed by a note that you can use `SendMessage` with `to:` set to that ID to continue the agent. That is the whole interface. Names address agents that are still running; agentIds resume agents that have already completed. A fresh `Agent` call always starts from zero.

The harness behaves three different ways depending on the target agent's state, and these three branches are extracted verbatim from the client binary:

1. **The agent is still running.** Your message is queued "for delivery to the agent at its next tool round." You can pipe new instructions to a working agent and it picks them up between tool calls. We used this to course-correct an agent mid-iteration on copy without restarting it.
2. **The agent has completed.** The harness reports that the agent "had no active task; resumed from transcript in the background with your message," and tells you it will notify you when it finishes. The completed agent comes back to life, rehydrates its full transcript, does the new work, and re-reports exactly once.
3. **The handle is gone.** The harness returns "Agent has no transcript to resume. It may have been cleaned up." This is the failure mode you engineer around, covered below.

The practical upshot of branch 2 is the entire reason persistent sub-agents work: a resumed agent remembers everything. In one session a brand-fix specialist referenced its own prior collision decisions across eight separate rounds without being reminded of any of them. The context is not summarized down to a handoff note. The agent literally resumes with its prior window intact.

### What the Teams Flag Actually Gates

A correction worth stating plainly, because we published the opposite and the error spread into our own framework's skill file: **resuming a completed sub-agent through `SendMessage` does not require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.** In a default session, with no environment variable set, you spawn an agent, you get its `agentId` back, and `SendMessage({to: agentId})` wakes it from its transcript exactly as described above. Everything in this guide's resume mechanics is live for you right now.

What the flag gates is **agent-teams mode**, which is a different thing that happens to use the same tool name. Teams mode turns on the structured peer-to-peer protocol: named teammates addressable by name rather than handle, messages routed between agents that are not in a parent-child relationship, and a team lead coordinating peers. The GitHub issue asking Anthropic to ungate that (#42737) was closed "not planned," so teams stays experimental. Resume did not.

The distinction is not academic, because the two modes have **different delivery semantics**, and this is the part that bites. On the classic path, a sub-agent's final message returns to its caller automatically; you get the report whether or not anyone asks for it. In teams mode nothing returns automatically. A teammate's report reaches the lead only if the teammate sends it, and an idle notification is not a report. Same tool, opposite defaults. We cover the failure mode that produces in [why your subagent reports done without doing anything](/blog/subagent-reported-done).

The old advice attached to this section still holds, just not as a fallback. Write every resume message as if the reader were fresh: the repo state, the constraint, the acceptance criterion. Not because you might be locked out of resume, but because handles expire (see the persistence model below), and an agent you can boot from scratch at near-zero loss is a better-engineered agent regardless of whether you ever resume it.

## The Persistence Model: Handle vs Transcript

The most important and least understood part of resume is that there are two layers of persistence, and they expire on completely different schedules.

The **ephemeral layer** is the resume handle, the registry mapping that lets `SendMessage` find a completed agent and wake it up. This handle is session-state-scoped and perishable. It does not reliably survive a context-summarization boundary in your main conversation or an overnight gap between sessions. We watched a handle that worked perfectly at 11 PM return "no transcript to resume" the next morning, not because the data was gone but because the main thread had summarized in between and the registry mapping did not cross that boundary.

The **durable layer** is the transcript itself. Every sub-agent writes its full conversation to `~/.claude/projects/<project>/<session>/agent-<id>.jsonl`. When the handle above failed, that exact file was still sitting on disk at 6.4 MB, every decision intact. The data was never deleted. Only the live handle to it expired.

But durable does not mean permanent. The binary exposes a `cleanupPeriodDays` setting, described as "days to keep transcripts before automatic cleanup," defaulting to 30 with a minimum of 1. If you do not set it, transcripts age out after a month. Operators who rely on transcript rehydration as a recovery path should raise that value deliberately rather than assume the files live forever.

That gives you a clean fallback hierarchy. Resume by handle while it is warm. When the handle dies but you are inside the 30-day window, point a fresh agent at the predecessor's `agent-<id>.jsonl` and have it grep for the specific prior decisions it needs rather than ingesting the whole file. And underneath both, keep your real durable state where it belongs: in commits, written reports, and task files on disk. The agent's memory should survive the agent by design, not by luck. That principle is the heart of [thread-based engineering](/blog/thread-based-engineering), where the durable artifacts, not the live context, are the source of truth.

### The Compaction Caveat

Here is the subtle one. If a long-running sub-agent auto-compacted during a previous run, the transcript records a compaction boundary, and resume rehydrates the post-compaction summary as the operative context, not the full pre-compaction history. The complete history stays in the JSONL file, but it is not what the resumed agent wakes up holding.

This means a sub-agent you have resumed many times can quietly lose fidelity, replaying a summary of a summary rather than its original reasoning. It is the single strongest argument for the high-signal-window discipline in the next section: an agent that delegates its noisy work downward keeps its window high-signal, compacts later or never, and therefore keeps its resume chain high-fidelity for far longer than one that stuffed its own window full of raw tool output.

## The Tiered Context Economy

Resumability plus nesting forces a rewrite of the oldest piece of sub-agent advice: "fill the throwaway window, because unused capacity is wasted." That was correct when every agent was one-shot. It is now only half right, and applying it to the wrong tier is how you burn tokens and degrade quality at the same time.

The model we ship is three tiers, and the slogan is **Central AI conserves; persistent sub-agents maximize; throwaway sub-agents absorb the noise.**

**The main thread (T0) conserves.** It is a pure coordinator. It routes work, reviews results, talks to you, and delegates everything else. Nothing has changed here; the central thread has always run leanest.

**Persistent sub-agents (T1) maximize.** This is the one warm, named specialist per domain. It reads broadly, loads its skills, and gathers deep domain context, because that collection is an investment, not waste. The original reason to maximize collection was a guarantee against non-resumability: if the agent only ran once, you wanted it to have seen everything. Resumability now protects that investment instead of voiding it. The context is never lost, and every resume reuses the same compute, so the deep gather at spawn amortizes across every iteration that follows. The discipline that keeps this tier healthy is not "stay small." It is "keep the window high-signal by pushing work that does not belong in persistent context downward."

**Throwaway sub-agents (T2 and deeper) absorb the noise.** These are the one-shot scouts and nested children that a persistent specialist spawns when it needs something messy: fifteen web searches, a wide log grep, a bulk doc scan. The old maximize-everything doctrine lives here, exactly where it belongs. They burn disposable windows, over-collect freely, and return only the distilled verdict upward, keeping the persistent agent's context all signal. The depth cap is five, server-enforced, with no configuration knob, so the recursion has a hard floor.

The shift, stated plainly: the "maximize because the window is temporary" rule did not disappear. It moved down a tier, to the agents that are actually temporary. The agent you keep is the one you keep clean. For the deeper mechanics of how that downward delegation works layer by layer, [nested sub-agents](/blog/nested-subagents) is the companion to this post: nesting is the throwaway tier going deeper, resume is the persistent tier living longer, and together they force the tiering.

## Field Data: What a Real Resume Chain Looks Like

Doctrine is cheap. Here is what we actually measured running this pattern through a full visual rebuild.

Two specialists carried the bulk of the work as warm, resumed agents. The first chained a Tailwind v4 upgrade into a verbatim landing-page port into a Fumadocs blog port across three invocations, each one resuming the last. The second ran eight or more iteration rounds: logo fixes, naming changes, a homepage rework, a layout-variant swap, icon fixes, model chips, header and footer trims, and two passes on the hero copy. Every round resumed the same agent with its full prior context.

The token curve across that eight-round chain, measured per round, tells you both why the pattern works and where it ends: 199k, 186k, 214k, 231k, 241k, 255k, 272k, 324k. The window grows every resume because each resume replays the whole transcript. That is the cost of perfect memory, and it is monotonic. Two things follow. A high-signal T1 agent that delegated its noise downward is cheaper to resume than one bloated with raw tool output, and the saving compounds on every iteration. And there is a ceiling: around 300k of context, you finish the thread, write a handoff summary, and boot a successor agent rather than dragging an ever-heavier window through another ten rounds.

The latency payoff is the headline number. Cold-phase builds, where the agent was still discovering the codebase, ran 12 to 40 minutes and longer. Once warm, single-purpose iterations landed in roughly 4 to 7 minutes, because the agent never re-read the repo, never re-derived a decision, never re-loaded a skill. That collapse is the entire business case for keeping an agent warm instead of re-briefing a fresh one.

## The Warm Sub-Agent Iteration Loop

The pattern that ties all of this together is a loop, and it maps perfectly onto the most common real workflow: iterating on a UI while you watch it on localhost.

You review the running app, spot something to change, and type the feedback into your main thread. The main thread, which has stayed a lean coordinator the whole time, relays that feedback through `SendMessage` to the warm frontend specialist, the one that already knows every file it touched and every decision it made. The specialist executes, spawning a throwaway scout if it needs a noisy lookup, reports back, and you review again. Repeat.

## Naming a Resumable Agent

A one-shot agent does not need a careful name; you spawn it, it dies, the label never matters again. A persistent agent is the opposite. Its identity is frozen at spawn and has to stay true across every resume, including resume number eight when the task is nothing like the first one. Get this wrong and you end up resuming "the-hero-copy-fixer" to do footer work, which reads as nonsense in the transcript and in your own head.

The convention we ship is two fields:

- **`description`** = `<Agent Type> - <durable mission>`, a plain hyphen, never an em dash. For example, "Frontend Specialist - landing page UI." It names the domain, not the first task.
- **`name`** = a kebab-case, type-prefixed mirror of that mission, like `frontend-landing-ui`.

Per-task specifics, the actual thing you want done this round, live only in the prompt and in each resume message, never in the durable label. The test is one question: will this name still be true on resume #8? "Frontend Specialist - landing page UI" survives a logo fix, a hero rework, and a footer trim. "fix-the-hero-button" does not survive its own second invocation. Name the domain you will keep coming back to, not the task in front of you.

This is also why a self-contained resume prompt matters so much. If every resume message carries the repo state, the constraint, and the acceptance criterion as if the reader were fresh, then a dead handle costs you almost nothing: the same prompt boots a clean replacement that is productive immediately. We have done exactly that mid-session when a handle expired, and the replacement specialist picked up without a stumble.

## Resume or Fork or Fresh

Resume is not the only way to carry context between agents, and choosing wrong wastes the affordance. There are three options, and they trade off differently.

**Resume** gives you identity and history continuity. The same agent, its full transcript, its accumulated decisions. The cost is a cold prompt cache and a window that grows every time. Use it for iterative, same-domain work where the agent's memory of prior rounds is the whole point.

**Fork**, which has been default-on since v2.1.161, shares the parent's prompt cache. You get the parent's context inherited and cache warmth, but no identity continuity. Use it for one-shot work that needs to start from the parent's state but does not need to be the same ongoing agent.

**Fresh** is a clean slate with a self-contained prompt. Use it when the domain changes. A frontend specialist resumed to do database work carries stale, irrelevant context that actively hurts; a fresh backend agent beats it every time. Domain change means new agent, full stop. Related work in the same domain means resume.

The rule of thumb: same domain, iterating, resume. One-shot but needs parent context, fork. New domain, fresh. Match the tool to the continuity you actually need, not the one that feels most powerful.

## The Fable 5 Connection

One field observation kept recurring and is worth stating directly: the model override on the sub-agent mattered as much as the pattern. Setting `model: "fable"` on the frontend specialists produced a clear step-change in output quality over the default. In the rebuild that generated all the data above, every frontend round ran on a Fable sub-agent, and the one attempt that ran without the override was the one we rejected and redid.

That is not a coincidence of one session. [Fable 5](/blog/claude-fable-5-mythos-5), the first publicly available Mythos-class model, is the generation where the persistent sub-agent stops being a clever trick and becomes the default operating mode. A warm specialist running on a frontier model holds its accumulated context and applies frontier judgment to every resumed round, so the quality gain and the latency gain stack. The pattern was always going to be useful; on Fable 5 it is the way you should be working.

That recommendation sits on a different axis from the model-tier orchestration shape used elsewhere on this blog, where Fable plans and Sonnet sub-agents execute, and the two are easy to read as contradictory. They are not. Both are correct answers to different questions. **The selector is where the judgment is needed, not which model is better.**

| The sub-agent's bottleneck | Where Fable goes |
| --- | --- |
| Its own reasoning is the deliverable (copy, layout, visual judgment calls) | On the sub-agent, as in the rebuild above |
| It mostly absorbs volume (reading, searching, mechanical edits) while a plan directs it | At the coordinator, with Sonnet doing the executing |

The frontend rebuild above is the first row: the specialist's own judgment was the product, so paying frontier rates at the leaf was worth it. The cost case in Claude Code cost optimization is the second row: workers doing high-volume, low-judgment execution, coordinated by a plan that needs the frontier model's judgment once rather than on every file. Check which one describes the sub-agent in front of you before picking which end gets the expensive model.

You can assemble all of this by hand. Name your agents by the convention, resume them with self-contained prompts, watch the token ceiling, delegate noise to nested children, and keep durable state on disk. It works, and now you know how. But there is a real gap between knowing the pattern and having it run by default on every session without you thinking about it.

The before-and-after is stark. The manual path is reading this guide, getting the flag right, writing the convention into your own config, and remembering to resume instead of re-spawn every single time, on every project. The kit path is one drag-and-drop setup that encodes the doctrine, the skill, and the pipeline, so the first session you run already works the way this post describes. For the deeper version of that decomposition and how it pairs with collaborative execution, see how the kit handles [dynamic workflows and Agent Teams](/blog/ultracode-dynamic-workflows-agent-teams).

## Where This Goes

Treat the pace of the last few releases as a signal: this is new, and the surface will keep moving. Resume shipped ungated while teams mode stayed experimental, nesting is capped, the docs lag the binary by weeks, and the handle expires across boundaries you do not fully control. None of that is a reason to wait. The persistent sub-agent pattern is already the most efficient way we have found to run iterative work in Claude Code, and the field data backs it: warm beats cold by roughly an order of magnitude on latency, and a clean T1 window beats a stuffed one on both cost and fidelity.

The deeper trend is that the unit of work in Claude Code is shifting from the one-shot agent to the durable one. Orchestration used to mean spawning the right throwaway and filling it; increasingly it means keeping the right specialist warm and feeding it. Start with the agent fundamentals if the lifecycle is new to you, layer in [parallel and sequential dispatch](/blog/sub-agent-best-practices) for the work that fans out from the main thread, and read how task distribution decides what gets delegated where. Then keep one specialist warm per domain, name it for the mission and not the task, and let the throwaway children absorb the noise. That is the new way to run Claude Code sub-agents.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
