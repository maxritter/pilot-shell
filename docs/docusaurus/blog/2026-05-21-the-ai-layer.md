---
title: "The Claude Code Harness: 7 Components Explained"
description: "Claude Code is a model plus a harness. The AI layer of skills, hooks, agents, and MCPs matters more than the model. Here is how it works."
slug: the-ai-layer
date: 2026-05-21
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code is a model plus a harness. The AI layer of skills, hooks, agents, and MCPs matters more than the model. Here is how it works.

<!-- truncate -->

A coding agent is two things, not one. The first is the model: the weights, the reasoning, the raw capability Anthropic ships every few months. The second is what surrounds it: the files Claude reads on startup, the hooks that fire at the right moment, the skills it pulls in on demand, the sub-agents it spawns to keep its main context clean. Anthropic calls this second thing the **Claude Code harness**. Cole Medin, in his recent video and reference repo, calls it the **AI Layer**. Same idea, different name. Both terms are starting to stick because they explain something every team eventually notices.

The same model, with two different harnesses, produces wildly different outcomes on the same codebase.

That is the premise of [Anthropic's recent post on how Claude Code works in large codebases](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start), and it matches what every team running Claude Code at scale has been quietly learning. Performance is not just about the model. The ecosystem you build around it determines whether Claude grep-searches into a wall of irrelevant hits or jumps straight to the function you meant. Whether it follows your conventions or freelances. The harness is the leverage point, and most teams underinvest in it for months before the same realization lands: the model was never the bottleneck.

This post is the map. We will walk through each of the seven AI layer pieces, show how they compose, and explain the mental model that turns "where does this go?" from a judgment call into a quick test. By the end you should be able to look at any Claude Code setup and say, with reasonable confidence, what is missing and what to build next.

## Why the Harness Matters More Than the Model

Anthropic's point is unusually direct: the ecosystem around the model, the harness, determines how Claude Code performs more than model choice alone. Strong claim from the company that makes the model. It also matches what teams keep reporting after they ship their first serious internal rollout.

The reason traces back to a deliberate architectural choice. Claude Code does not pre-index your codebase. No RAG pipeline silently embedding your files, no vector store waiting to be queried. Claude navigates your repo the same way you do: walks the filesystem, runs grep, reads files, follows imports. Anthropic's framing for the alternative is blunt: "embedding pipelines can't keep up with active engineering teams." A vector index that was right an hour ago is wrong by the time CI finishes. Agentic search dodges that failure mode entirely. The price is that context curation becomes your job, not the indexer's.

On a 5,000-line side project, this is invisible. Claude reads almost everything and the conversation moves on. On a 200,000-line monorepo, it is the whole game. A naive grep for `handlePayment` returns three thousand string matches across services that have nothing to do with your actual change. Each hit eats tokens. Each irrelevant file shoulders the relevant one out of context. Without a harness, the model never gets the chance to be smart because it never gets the right inputs.

The harness is how you fix that. It is the layer of configuration, hooks, skills, sub-agents, and tool access that decides what Claude sees, when, and in what shape. Same weights, same prompts. Different layer underneath. Different outcomes.

## The Seven Pieces of the AI Layer

Anthropic identifies five extension points, then adds LSP integrations and sub-agents as two additional capabilities that round out the setup. Cole's [helpline reference repo](https://github.com/coleam00/helpline) demonstrates the pattern as working code in a single Python project. Together they form the surface area of the harness. Each plays a distinct role, each loads at a different time, and each has a common failure mode you should know about before you build with it.

| Component | Loads When | Best For | Common Confusion |
| --- | --- | --- | --- |
| CLAUDE.md | Every session | Project conventions | Putting reusable expertise here vs. Skills |
| Hooks | Event-triggered | Automating behavior | Prompting instead of automating |
| Skills | On demand | Reusable expertise | Loading into CLAUDE.md |
| LSP | Always (once configured) | Symbol navigation | Assuming it is automatic |
| MCP Servers | Always (once configured) | Internal tool access | Building before basics work |
| Sub-agents | When invoked | Exploration vs. editing split | Same-session exploration plus editing |
| Plugins | Always (once configured) | Org-wide distribution | Letting good setups stay tribal |

Read the table once, then keep going. Each row gets a section.

### Component 1: CLAUDE.md (Persistent Conventions)

Anthropic calls these "context files that Claude reads automatically at the start of every session." Think of them as the always-on briefing.

A root CLAUDE.md describes the big picture: stack, top-level layout, conventions that apply everywhere. Subdirectory CLAUDE.md files describe local conventions: the test command for that service, the naming pattern for that folder, the gotcha that bit someone last quarter. Claude walks up the tree from wherever you initialize the session and loads everything it finds.

The day-one mistake is treating CLAUDE.md as a dumping ground for everything Claude might ever need. Bloated rules degrade performance because every token is paid for on every turn. Keep CLAUDE.md lean and push anything workflow-shaped (a process, a procedure, a "how we do X") into a Skill instead.

For the depth on what belongs there, [the CLAUDE.md mastery guide](/blog/claude-md-mastery) covers the rules-vs-documentation distinction. For the layered pattern, [our subdirectory CLAUDE.md walkthrough](/blog/subdirectory-claude-md) shows the walk-up loading rules.

```
# Root CLAUDE.md (lean, big picture)
Stack: Next.js 15 + tRPC + Postgres
Run tests: pnpm test
Conventions: no em dashes, prefer named exports

# packages/api/CLAUDE.md (local, specific)
This service handles billing. All money values in cents.
Run tests for this package only: pnpm --filter api test
Migrations live in db/migrations and are timestamped.
```

### Component 2: Hooks (Event-Driven Automation)

Hooks are scripts that fire on lifecycle events. Anthropic describes them as "scripts that run at key moments." They are how you bolt deterministic behavior onto an otherwise probabilistic agent.

A start hook runs when a session opens. Cole uses one to drop git status, the recent commit log, and the current branch into the session so Claude knows the repo state before the first prompt. A stop hook runs when Claude finishes its turn. The standout pattern in Cole's helpline repo is a stop hook that spawns a separate headless Claude session, has it review the recent changes against the current CLAUDE.md files, and writes a proposed diff to a review file. Your CLAUDE.md self-improves while you sleep instead of slowly going stale.

The common mistake is prompting your way through work that should be automated. If you type "run the formatter" three times a session, that is a hook. [The hooks primer](/blog/hooks-guide) covers all twelve lifecycle events, and [our self-improving CLAUDE.md walkthrough](/blog/self-improving-claude-md) details the headless reviewer pattern.

```
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/review-claudemd.mjs\""
      }
    ],
    "SessionStart": [
      {
        "type": "command",
        "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-context.mjs\""
      }
    ]
  }
}
```

### Component 3: Skills (On-Demand Workflows)

Skills are the workhorse of the harness. Anthropic frames them as "offloading specialized workflows and domain knowledge, loading them only when the task calls for it." They are markdown files with a frontmatter description Claude reads at session start; the body content only loads when the description tells Claude the skill is relevant.

This progressive disclosure is why a harness can grow large without context bloat. Fifty skills, but you pay the token cost of one or two per turn. Skills can also be scoped to file paths via a `paths:` parameter in the frontmatter (accepts a single glob or a list), so the API-route-creation skill only enters the discovery set when Claude is actually working under `packages/api/`. [Path-scoped skills](/blog/path-scoped-skills) gives the full pattern.

```
---
name: api-add-route
description: Add a new tRPC route with input validation and tests
paths: packages/api/**
---
 
(skill body loads only when paths match and description is relevant)
```

### Component 4: Language Server Protocol (Symbol Navigation)

LSP gives Claude what every modern IDE has been giving you for years. Anthropic's framing: it "gives Claude the same navigation a developer has in their IDE." Go-to-definition. Find-all-references. Symbol-level search that understands scope, types, and imports instead of pattern-matching on raw strings.

Without it, Claude reaches for grep, which is fine on small codebases and falls apart past about 50,000 lines. A grep for `monthly_total_cents` in a six-figure-LOC repo returns dozens of false positives: comments, log lines, test fixtures, unrelated string concatenations. Each costs tokens. With an LSP MCP server like Cole's helpline build, the same query returns one definition and two references.

Anthropic cites one enterprise that "deployed LSP integrations org-wide before their Claude Code rollout, specifically to make C and C++ navigation reliable." That is the level of forethought serious teams put into this. The common mistake is assuming LSP is automatic. It is not. You need a code intelligence plugin plus the language server binary for your stack. Our LSP MCP server walkthrough covers the build pattern and the token math against grep.

### Component 5: MCP Servers (Tool and Data Access)

MCP, the Model Context Protocol, is the standard way Claude talks to anything outside the filesystem. Anthropic describes it as "how Claude connects to internal tools, data sources, and APIs." Postgres, GitHub, Linear, an internal docs system, your analytics warehouse: all MCP servers.

LSP is itself an MCP server. So is a codebase-search server exposing structured AST queries. The pattern is consistent: a small server exposes typed tools, Claude calls them when relevant. Anthropic's enterprise example is a retail org that "built a skill connecting Claude to their internal analytics platform so that business analysts could pull performance data" without writing SQL.

The MCP mistake is the inverse of the CLAUDE.md one: teams build elaborate custom servers before the basics are working. Get CLAUDE.md, hooks, and skills right first. MCP earns its place once you know which tool would have saved Claude a wasted exploration. The MCP basics guide is the right starting point.

### Component 6: Sub-agents (Context-Window Multiplication)

A sub-agent is "an isolated Claude instance with its own context window," as Anthropic puts it. The parent invokes the sub-agent with a task, the sub-agent runs in a clean context, returns a result, exits. The parent never sees the sub-agent's full transcript, only the final answer.

This is the single most underused component in most setups. The canonical pattern is exploration vs. editing: send a read-only sub-agent to map a subsystem, have it write findings to disk, then let the main agent edit with those findings in hand. Done in one session, you exhaust the context grepping. Split across agents, the main thread stays sharp because the spelunking happened elsewhere. Cole's helpline ships a read-only `explorer` sub-agent that does exactly this.

### Component 7: Plugins (Distribution and Standardization)

A plugin, in Anthropic's words, "bundles skills, hooks, and MCP configurations into a single installable package." It is the answer to the question every Agent Manager eventually asks: how do I get this harness onto forty laptops without an hour of setup each?

The fastest enterprise rollouts have an answer ready on day one. A small team builds the harness as a plugin, publishes it to an internal marketplace, new engineers install with two commands. Cole's helpline ships its full AI layer this way:

```
/plugin marketplace add /path/to/helpline/tooling
/plugin install helpline-ai-layer@helpline-tooling
```

The mistake is letting good setups stay tribal. Every team that ships strong Claude Code work eventually builds a great `.claude/` directory. Without plugin distribution, that directory lives in one repo, gets copied unevenly into others, and the conventions diverge. With plugins, the same harness ships everywhere, and improvements ship everywhere when you update the package. Our plugins distribution guide covers marketplace setup.

## How the Components Compose

The seven harness pieces fire on very different schedules, and that asymmetry is the point. CLAUDE.md sits as the persistent base, loaded once per session and present in every turn. Hooks fire at lifecycle moments, mostly invisible. Skills load on demand, lighting up only when their description matches the task. LSP and MCP are always available but only called when Claude reaches for them. Sub-agents spawn occasionally, do their work in their own context, and return one tidy answer.

This composition is what makes the harness scalable. If every component loaded every turn, you would burn your entire context window on plumbing before Claude saw the actual code. Progressive loading is what lets a fifty-skill, ten-MCP, five-hook setup feel as lean as a single CLAUDE.md.

## Rules vs. Workflows (The Mental Model)

The most useful distinction Cole introduces is two words: rules vs. workflows.

Rules are things Claude must always follow. Conventions. Constraints. "Money values in cents." "Always run the formatter before committing." Rules go in CLAUDE.md because they need to be present on every turn.

Workflows are repeatable processes for specific task types. "To add a new API route, do these eight steps." "To run a security review, check these patterns and write a report in this shape." Workflows go in Skills because they only matter during that specific work.

The test is mechanical: if Claude needs to know it before you ask the question, rule. If Claude only needs to know it once you ask for that specific kind of work, workflow. Most "should this go in CLAUDE.md or a skill?" debates dissolve the moment you apply that test.

Both can be path-scoped. The `packages/api/CLAUDE.md` rules only load when you initialize there or below. The `api-add-route` skill only enters discovery under the API service. Right context, right scope, nothing more.

## When Do You Need a Harness This Elaborate?

Not every project needs every component. Match the harness to the codebase.

**Solo project, under 5,000 lines.** A lean CLAUDE.md is usually enough. Claude can read most of the repo in a single session. Add hooks once you find yourself typing the same command repeatedly.

**Team project, 30,000 to 100,000 lines.** This is where the harness starts paying for itself. Lean root CLAUDE.md plus subdirectory files. Hooks for formatting and the self-improving rule reviewer. A handful of skills for the team's most common workflows. One or two MCP servers for the tools you actually reach for daily.

**Enterprise monorepo, 100,000+ lines.** Every component matters. Layered CLAUDE.md. LSP non-negotiable. Sub-agents for exploration. Plugins for distribution. An Agent Manager owning it all. [Our large codebase playbook](/blog/large-codebase-playbook) walks through the eight specific strategies that make Claude Code workable at this scale.

There is a known limit. Anthropic notes the hierarchical CLAUDE.md model breaks down on "codebases with hundreds of thousands of folders and millions of files" or non-git version control. Those cases need additional architecture beyond the standard harness, and the team should plan for that upfront rather than discover it the hard way.

## Build It Yourself, or Use a Pre-Built Harness

Building this stack from scratch takes months. Not because any single component is hard, but because the right shape only emerges after you live with it for a few projects. The first CLAUDE.md is too long. The first skill set is too generic. The first hook fires on the wrong event. You iterate, you discover the rules-vs-workflows distinction the hard way, you rewrite, and three months in you have something that works.

Honest tradeoff: build yourself if you want the learning, use a pre-built harness if you want the months back.

## Maintaining the Harness Over Time

A harness is not a one-time investment. Anthropic recommends "a meaningful configuration review every three to six months," and also after every major model release. What was a good rule for an older model can constrain a newer one.

The example Anthropic gives: a CLAUDE.md rule enforcing single-file refactors made sense when models reliably broke cross-file edits. A newer model handles cross-file refactors well, so that rule now leaves capability on the table. Same for hooks: one team had a hook intercepting file writes for Perforce, redundant the moment Claude Code shipped native Perforce support. Rules and hooks age. Review them on a cadence.

The self-improving CLAUDE.md pattern keeps this from being manual work. The harness corrects itself between scheduled reviews, so the scheduled review becomes a sanity check rather than an archaeology dig. [The self-improving walkthrough](/blog/self-improving-claude-md) shows the full setup.

## Who Owns the Harness?

Someone has to. Anthropic is explicit: the fastest enterprise rollouts had dedicated investment before broad access. "A hybrid PM/engineer function dedicated to managing the Claude Code ecosystem" is the role that has started to emerge. Plugin marketplace curation, CLAUDE.md conventions, permissions policy, the approved skill set: all lives with one person or a small team.

Most companies do not need a full team. A single DRI with authority over configuration, settings, and the plugin marketplace is the minimum viable version. The role usually lives under Developer Experience or Developer Productivity. [Our breakdown of the Agent Manager role](/blog/agent-manager-role) goes deeper on what that person actually does.

## Next Steps

Three reading paths from here, depending on where you are.

If you are setting up your first project, start with [CLAUDE.md mastery](/blog/claude-md-mastery) to get the foundation right, then [the skills primer](/blog/claude-skills-guide) for the second layer.

If you are running into limits on a large codebase, jump straight to [the large codebase playbook](/blog/large-codebase-playbook) for the eight specific strategies that fix the most common failures.

If you are planning an enterprise rollout, read [the agent manager role breakdown](/blog/agent-manager-role) first, then our plugins distribution guide for the standardization piece.

## The Harness Is the Leverage Point

The model will keep getting better. Anthropic ships, your competitors ship, the field moves. What does not move on the same cadence is the layer underneath: the CLAUDE.md files you wrote, the hooks you configured, the skills you built, the sub-agents you scoped, the MCP servers you wired in. That layer is yours, and it compounds. Every model release lands on top of a harness you already own, and a strong harness amplifies the new model's gains in a way a weak harness never can.

That is the strategic case for taking the AI layer seriously. It is also why teams that win at Claude Code at scale look different from teams that just use it. The winning teams treat the harness as a product. They own it, review it on a cadence, distribute it through plugins, and have one person accountable for it. The other teams treat it as a config file that someone wrote once and nobody updates.

The shape of where this is going is already visible. The Agent Manager role is real now. Plugin marketplaces are real now. Path-scoped skills are real now. The AI layer is starting to look less like a junk drawer of dotfiles and more like a platform engineering surface inside every serious codebase. Treating it that way is the move.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
