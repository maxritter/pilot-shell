---
title: "Dynamic Workflows vs Agent Teams (Claude Code)"
description: "Claude Code Dynamic Workflows vs Agent Teams: a side-by-side comparison and a clear rule for when to use each. Where ultracode fits."
slug: ultracode-dynamic-workflows-agent-teams
date: 2026-06-03
authors:
  - max-ritter
tags:
  - guide
  - development
---

Claude Code Dynamic Workflows vs Agent Teams: a side-by-side comparison and a clear rule for when to use each. Where ultracode fits.

<!-- truncate -->

**Dynamic Workflows vs Agent Teams** is the choice that trips people up most in Claude Code, because the two look like flavors of the same thing and are not. A dynamic workflow fans out across dozens of isolated agents that never talk to each other. An Agent Team is a small set of peers that message each other and renegotiate the plan live while they build. Pick wrong and you cap your scale, burn 2 to 4x the tokens, or ship a worse result. There is also ultracode, a session toggle that sits on top of dynamic workflows rather than competing with them, and this guide places it precisely.

The short version: dynamic workflows are a deterministic harness of isolated agents, Agent Teams are a small set of peers that negotiate live, and ultracode is the session-wide policy that hands those workflows to you automatically. The rest of this post draws the lines, puts the two execution models side by side, and gives you a decision rule you can apply task by task. If you want the standalone deep dives, see [Dynamic Workflows](/blog/dynamic-workflows), the [Agent Teams guide](/blog/agent-teams), and the [ultracode guide](/blog/ultracode); this page is the one that compares them and tells you which to pick.

## The Three, Defined Plainly

Start with clean definitions, because most of the confusion comes from treating these as three flavors of the same thing. They are not. One is a setting, one is an execution shape, and one is a coordination model.

### Ultracode: the always-on workflow toggle

Ultracode is a Claude Code setting, not a model effort level. It does two jobs at once: it sends `xhigh` reasoning effort to the model, and it has Claude auto-orchestrate dynamic workflows for substantive tasks. Leave it on and any sufficiently big request gets fanned out across verifying subagents without you ever typing the word "workflow." It applies to the current session only and resets when you start a new one.

Think of ultracode as the switch that says "treat every meaty task in this session as workflow-worthy and act accordingly." That is powerful for an audit-grade session and expensive for routine edits, because the workflow layer applies to every substantive task whether it needed one or not. The full effort-ladder breakdown and the token-cost reality check live in the [ultracode guide](/blog/ultracode).

### Dynamic Workflows: a deterministic harness of isolated agents

A dynamic workflow is a real JavaScript file that Claude writes on the fly and then runs. The file orchestrates many separate Claudes, each with a clean context window and one focused job. It is deterministic (same script plus same args resumes from cache), resumable, and saveable as a reusable artifact. The agents inside it never talk to each other. Structure is fixed in code before anything runs.

Workflows exist to defeat three failure modes a single context window hits on hard work: agentic laziness (quitting a fifty-item task after thirty-five), self-preferential bias (a model grading its own answer too kindly), and goal drift (losing the original objective across a long, compacted conversation). Isolation fixes all three by construction. The mechanics, the six patterns, and the harness API are covered in the [dynamic workflows deep dive](/blog/dynamic-workflows).

### Agent Teams: a small set of peers that negotiate live

Agent Teams are a handful of named teammates (roughly two to five) that coordinate through a shared task list and direct peer-to-peer messaging. A frontend teammate can discover the API shape is wrong, message the backend teammate, who revises it, and both re-sync. Orchestration is LLM-driven and turn by turn. The contract between the pieces is negotiated live, mid-build.

That live negotiation is the entire point, and it is the one thing the other two cannot do. The setup, patterns, and examples are in the [Agent Teams guide](/blog/agent-teams).

## The Core Difference

Everything downstream flows from a single distinction:

- **Agent Teams talk to each other while they work.** The interface between the pieces can change during the build, and the pieces renegotiate it in real time.
- **Workflow agents never talk to each other.** Each is isolated with one job, and the structure is fixed when the harness is written. There is no live renegotiation.

Ultracode is not a third member of that pair. It is the auto-pilot for dynamic workflows, so it inherits the workflow side of the line: isolated agents, deterministic structure, no live negotiation. When you reason about ultracode, you are reasoning about dynamic workflows that Claude triggers for you instead of on request.

## Side by Side

This is the comparison to bookmark. It contrasts the two execution models that actually compete (Agent Teams and dynamic workflows); ultracode rides on the workflow column.

|  | Agent Teams | Dynamic Workflows |
| --- | --- | --- |
| **Orchestration** | LLM-driven, turn by turn (lead plus teammates decide as they go) | Code-driven, deterministic (a JS file decides) |
| **Communication** | Peer-to-peer messaging plus a shared task list | None between agents (isolated by design) |
| **Adaptation** | High: teammates renegotiate the contract live | Low: the shape is fixed when the harness is written |
| **Scale** | About 2 to 5 teammates | Up to 16 concurrent, 1,000 lifetime |
| **Determinism and reuse** | Non-deterministic, not a reusable artifact | Deterministic, resumable, saveable, shareable |
| **Defends the 3 failure modes?** | Not structurally (a teammate can still grade its own work) | Yes, by construction (isolation plus adversarial verify) |
| **Token cost** | 2 to 4x | High and data-dependent; capped by an explicit budget |
| **Best unit shape** | Few units, deeply interdependent | Many units, independent |

### When to Use Each: The 10-Second Answer

If you only read one thing, read this:

- **Use Dynamic Workflows** when the work is many independent units, when it is verification-heavy, when its size is unknown, or when you need a reproducible run. Audits, fact-checks, migrations across hundreds of call sites, ranking large candidate pools.
- **Use Agent Teams** when the work is a few (2 to 5) deeply interdependent pieces whose interface is still changing and the parts need to renegotiate it live. A new authenticated feature where schema, API, and UI are designed together.
- **Use ultracode** when you want every substantial task in a whole session to get workflow-grade treatment automatically, then drop back to `/effort high` for routine edits. It is a policy, not a third execution model.

The one-line test: if the pieces need to talk to each other mid-build, reach for an Agent Team; if they do not, reach for a dynamic workflow. Everything below is the reasoning behind that rule.

### Where each wins, and where it hurts

**Agent Teams** win when the work is a few deeply interdependent pieces whose interface is still in flux. They coordinate on a shared, evolving contract in real time, adapt to surprises that were not in the plan, and stay alive across the build accumulating context. They hurt past a handful of pieces: orchestration quality depends on LLM messaging that can drift or miss a message, there is no structural defense against a teammate preferring its own work, and the runs are neither deterministic nor reusable. The coordination itself is overhead and a failure point.

**Dynamic Workflows** win when the work is many independent units, when it is verification-heavy, when its size is unknown, or when you need the run to be reproducible. They scale far past a team, defeat the three failure modes by construction, express data-dependent shapes a fixed team cannot (tournament, loop-until-done, generate-and-filter), and bound cost with an explicit budget. They hurt when units are deeply interdependent and the contract keeps changing, because isolated agents cannot push back on each other. There is also no live human input mid-run, and authoring a correct harness is genuinely harder because it is code that fails in code ways.

## The Three-Way Decision Guide

The clearest way to choose is to treat plain `/build`, dynamic workflows, and Agent Teams as three answers to "how should we run this?"

**Reach for plain isolated sub-agents (the everyday `/build` baseline) when:**

- You just want to parallelize a few independent tasks and conserve the main session's context.
- This is the default. Neither workflows nor teams replace it; they are what you escalate to when one window or a chatty handful of agents is the wrong shape.

**Reach for Dynamic Workflows when ANY of these hold:**

- Many independent units (per file, per claim, per row, per rule, per resume).
- The task is verification-heavy or adversarial and you want N skeptics, not self-grading.
- The size of the work is unknown (find ALL the bugs, broken links, recurring corrections).
- You need to rank or sort more candidates than fit reliably in one prompt (use a tournament).
- You want the run to be deterministic, resumable, and reusable.
- Example: audit the whole codebase for a class of bug, fact-check every claim in a doc, rank eighty resumes, migrate two hundred call sites.

**Reach for Agent Teams when ALL of these hold:**

- The work is a small number of deeply interdependent pieces (2 to 5).
- The interface between them is uncertain and will likely change during the build.
- You want the pieces to negotiate and adapt to each other in real time.
- Example: build a new authenticated feature where the DB schema, the API contract, and the UI are all being designed at once and influence each other.

**And ultracode sits above this as a session policy.** Turn it on when you want every substantive task in a session to get workflow-grade treatment automatically (a long audit-and-migration session), and drop back to `/effort high` the moment you return to routine edits. It is the dial that says "this whole session earns workflows," not a separate execution model.

## The Six Workflow Patterns, Briefly

Dynamic workflows are not freeform. Almost every one is a composition of six named patterns. Prompting Claude with the right pattern by name produces a sharper harness than a vague "use some subagents." Here they are in one line each; the [dynamic workflows deep dive](/blog/dynamic-workflows) covers each in full.

1. **Classify-and-act.** A classifier reads the task, decides its type, and routes each kind to the right downstream agent.
2. **Fan-out-and-synthesize.** Split into many small steps, run one agent on each, then merge at a barrier into one result.
3. **Adversarial verification.** For each finding, spawn a separate skeptic whose only job is to refute it. Survivors are the findings the skeptic could not knock down.
4. **Generate-and-filter.** Generate many noisy candidates, then a separate pass filters, dedupes, and keeps only what holds up.
5. **Tournament.** Agents each attempt the same task differently, then a judge compares them pairwise until a winner emerges.
6. **Loop-until-done.** When the size is unknown, keep spawning agents until a stop condition is met (no new findings two rounds running).

A real migration might compose three at once: fan out one agent per fix, pair each with an adversarial reviewer, and loop until the build is clean.

## The Honest Bottom Line

Agent Teams are not obsolete, but their territory is narrower than it first looks. Their genuine, irreplaceable niche is **small-N, high-interdependence, evolving-contract feature builds that need live negotiation.** A workflow can imitate contract-first execution (phase one produces the schema, phase two's agents are handed that schema), and that covers a large share of what people use teams for today. What a workflow cannot replace is the iterative back-and-forth: frontend builds against the API, finds it wrong, pushes back, backend revises, both re-sync. That live loop is the Agent Teams core, and isolated workflow agents cannot push back on each other.

For most "do this same thing across many items" or "verify, discover, or rank at scale" work, a dynamic workflow is the better tool. It scales further, bounds cost with a budget, produces reproducible results, and structurally fights the failure modes that a chatty team does not. Ultracode is simply the policy that hands those workflows to you automatically for a whole session, which is exactly why it is worth turning on for an audit and turning off for a typo.

So the map is short enough to keep in your head. Parallelize a few independent tasks: plain isolated sub-agents. Same work across many items, or verify, discover, and rank at scale: a dynamic workflow, and ultracode if the whole session is that shape. A few interdependent pieces whose contract is still moving: an Agent Team. The theory underneath all three (how parallel and long-running threads compose) is in [thread-based engineering](/blog/thread-based-engineering), and for the scale where workflows truly earn their keep, the [large codebase playbook](/blog/large-codebase-playbook) covers migrations and audits across thousands of files.

## Making the Right Call Automatic

Here is the part the comparison table does not solve for you. Knowing the rule is the easy half. Applying it correctly on every task, under deadline, when the request is ambiguous and you are three hours into a session, is the hard half. The decision is not a one-time read. It repeats on every meaningful task you start, and each miss costs you the same way: pick a team for many-independent-units work and you cap your scale and burn 2 to 4x tokens; pick isolated sub-agents for an evolving-contract feature and you get pieces that cannot renegotiate and a build that fights itself. The framework is sound. The discipline to run it every single time is what slips.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
