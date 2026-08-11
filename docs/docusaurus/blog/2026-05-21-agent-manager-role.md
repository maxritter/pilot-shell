---
title: "Claude Code Teams: Who Owns the Setup at Scale"
description: "Managing Claude Code teams needs one owner: the agent manager. The role, a DRI checklist, and a 90-day playbook for Claude Code at scale."
slug: agent-manager-role
date: 2026-05-21
authors:
  - max-ritter
tags:
  - guide
  - development
---

Managing Claude Code teams needs one owner: the agent manager. The role, a DRI checklist, and a 90-day playbook for Claude Code at scale.

<!-- truncate -->

Once more than a handful of developers run Claude Code, somebody has to own how the whole team uses it. Managing Claude Code teams is its own job, and in May 2026 Anthropic finally put a name on the person who does it: the **agent manager**, a hybrid PM/engineer function dedicated to the Claude Code ecosystem. If you have been running point on your team's AI tooling and nobody quite knew what to call you, this is the job title. To be clear, this post is about managing the people and setup of a team that uses Claude Code, not the Agent Teams multi-agent orchestration feature, which is a separate topic covered in our [Agent Teams guide](/blog/agent-teams).

The role exists because of a pattern Anthropic documented across its enterprise customers. The companies whose Claude Code rollouts went smoothly had something in common before any developer ran their first session. As Anthropic put it: "The rollouts that spread fastest had a dedicated infrastructure investment before broad access." That typically meant a small team, sometimes just one person, who wired up the tooling before broader access opened.

That small team or that one person is the agent manager. This post defines what managing Claude Code teams actually involves, what the single-owner version looks like for smaller orgs, and a realistic 90-day plan for someone stepping into the role for the first time. The framework draws on the harness vocabulary introduced in our [AI Layer pillar](/blog/the-ai-layer), which is the umbrella concept Anthropic now uses to describe everything that wraps the model. It pairs naturally with our guide to [running Claude Code on a large codebase](/blog/large-codebase-playbook), the strategy side of operating at scale.

## Why Managing Claude Code Across a Team Breaks Down

Without someone owning the harness, three failure modes surface within the first quarter of broad Claude Code access.

The first is tribal knowledge. Every developer evolves a personal AI layer. One engineer has a slick set of skills they wrote on a Saturday. Another wired up an MCP server nobody else knows about. A third built a stop hook that catches a class of bugs the team keeps shipping. None of it is shared. New hires get the bare default install and rediscover the same lessons from scratch.

The second is inconsistent results. Same model, same codebase, very different output quality across the team. Anthropic's framing is that the harness determines performance more than the model. Without standardization, the harness varies wildly per developer, and so does what Claude produces. The gap widens once developers start running [agent teams](/blog/agent-teams): a shared, well-built harness is what makes multi-agent runs reproducible instead of one engineer's lucky configuration. Code review surfaces problems that a hook should have prevented.

The third is security drift. Permissions get configured ad hoc. MCP servers connect to internal systems with whatever scope the developer happened to grant. Infosec finds out three months later that a credential is in plaintext inside an `.mcp.json` file checked into a personal fork. This is the failure mode that gets AI tools banned by the platform team.

Any one is fixable. All three together is the kind of mess that takes a quarter to clean up and a year to recover trust from. An agent manager is the standing answer.

## What an Agent Manager Actually Does

The job has five concrete areas of ownership. They map roughly onto the [seven pieces of the Claude Code harness](/blog/the-ai-layer), but with a governance lens layered on top. The agent manager is also the person who decides which [team orchestration](/blog/team-orchestration) patterns become the org default, so that scaling Claude Code across a team means scaling one proven workflow rather than fifty improvised ones.

### Owns the plugin marketplace

Plugins are how good harness configuration moves from one machine to the entire org. The agent manager curates which plugins are available, which versions developers should be on, and what gets retired. They run the marketplace the same way an internal package registry is run. New plugins go through review. Updates land on a schedule. Deprecations are announced.

### Curates approved skills

Skills are the workflow library. Without curation, every developer writes a personal `.claude/skills/` folder, and quality varies. The agent manager keeps a defined set of approved skills, decides what gets promoted from someone's personal fork into the org-wide bundle, and handles deprecation when a skill is replaced by a better one. Anthropic's recommendation here is direct: "starting with a defined set of approved skills, required code review processes, and limited initial access, and expand as confidence builds."

### Maintains CLAUDE.md conventions

Conventions evolve. The agent manager owns the canonical CLAUDE.md hierarchy and decides when subdirectory files get added or refactored. Our [self-improving CLAUDE.md pattern](/blog/self-improving-claude-md) is one tool here: a stop hook that proposes updates to the agent manager's review queue instead of letting rules go stale.

### Sets permissions policy

This is the infosec touchpoint. The agent manager decides what tools are allowed, what commands need approval, what gets denied at the settings level. The output is a `.claude/settings.json` that ships with the org-standard plugin, plus written policy for what developers can and cannot relax. Our permission management guide covers the mechanics; the agent manager is who decides org defaults.

### Runs the configuration review cadence

Anthropic suggests a meaningful configuration review every three to six months, and also after major model releases when performance feels like it has plateaued. The agent manager owns this cadence. They schedule the review, gather telemetry, retire rules that have become constraints rather than guardrails, and ship the updated harness.

## The Hybrid PM-Engineer Profile

The reason this role exists as a hybrid is that pure engineering and pure product management both fail at it.

A pure engineer builds beautiful internal tooling that nobody adopts because the rollout was never planned. A pure PM ships a glossy adoption plan but cannot debug a misconfigured hook on a Friday afternoon. The agent manager does both jobs.

The technical floor is real. You need to write a hook, read a settings.json, debug a silently failing MCP server, and reason about which skill should activate when. You need to read a Node stack trace and understand the difference between a permission rule and an MCP scope.

The product floor is also real. You define rollout phases, write developer-facing documentation, run office hours, gather feedback that does not turn into noise, and make calls on what gets prioritized when ten developers want ten incompatible features. You know when to say no.

## Minimum Viable Version: The DRI Pattern

Most orgs do not need a dedicated team for this on day one. Anthropic's minimum viable version is a single DRI: "one person with ownership over the Claude Code configuration, the authority to make calls on settings, permissions policy, the plugin marketplace, and CLAUDE.md conventions, and the responsibility to keep them current."

That sentence is your job description if you are the only person doing this. The DRI version works for orgs under fifty engineers, or as the starting point for a larger org that has not justified a dedicated headcount yet.

What the DRI specifically owns:

- The canonical CLAUDE.md and any subdirectory files
- The `.claude/settings.json` that ships with the org-standard repo template
- The approved skills list and the process for proposing additions
- The plugin marketplace, even if it is just a private git repo with three plugins in it
- The escalation path when a developer hits a permission or harness issue they cannot solve

What the DRI coordinates with but does not own: infosec policy review, vendor relationship with Anthropic, broad developer training. Those stay with their existing owners; the DRI is the interface.

## Where the Role Sits Organizationally

Anthropic's observation matches what teams have been reporting. The role sits "under developer experience or developer productivity, which is typically the function responsible for onboarding new engineers and building developer tooling."

DevEx is the natural home because the work is fundamentally about making developers faster and more consistent. Platform Engineering or Internal Tools are valid alternatives when DevEx does not exist as a function. Rarer but seen: a cross-functional working group that includes representation from engineering, infosec, and governance. Anthropic explicitly endorses this last pattern: "We've observed the smoothest deployments at organizations that establish cross-functional working groups early by bringing together engineering, information security, and governance representatives to define requirements together and build a rollout roadmap."

For most teams under a few hundred engineers, the working group is overkill on day one but worth standing up as access broadens.

## The First 90 Days

A realistic plan for someone stepping into the role. The shape repeats whether you are the DRI for a thirty-engineer startup or one of two engineers at a multi-thousand-engineer org.

### Days 1-30: Audit and baseline

The first month is not building. It is figuring out what already exists.

Inventory every personal Claude Code setup you can find. Ask the ten loudest Claude Code users to walk you through their `.claude/` folder. Note which patterns appear repeatedly, which feel idiosyncratic, which seem broken but the developer has stopped noticing. Pull telemetry if you have it: sessions per developer per week, which models, average context usage, common failure modes.

Talk to infosec. Get current concerns on the table before you ship anything. Ask what would have to be true for them to sign off on broader rollout. Ask platform engineering the same question if they own the tooling stack. Slack search "Claude Code" filtered to the last quarter is a high-signal exercise; the complaints are your roadmap.

By the end of week four you should have a written audit, a list of three to five problems worth solving first, a stakeholder map, and the start of a written charter for the role.

### Days 31-60: Build the v1 harness

Now you build. The output is a working harness you can ship to one team in days 61-90.

You are assembling [every component of the AI layer](/blog/the-ai-layer): a canonical CLAUDE.md (probably layered, with subdirectory files for the major services), a starter set of approved skills, the hooks that enforce the conventions the team keeps violating, the MCP servers that connect to internal tools developers actually use, and a plugin that bundles it for installation.

Write the docs too. Two pages, not twenty. One page is "how to install the harness." One page is "what changed and why." If you cannot fit it on two pages, the harness is too complicated for v1.

Pilot this version yourself before exposing it to anyone else. Eat the dogfood for a full week. Find the rough edges. Decide what gets fixed before launch and what gets deferred to v2.

### Days 61-90: Quiet rollout to one team

Anthropic's phrase is "before broad access." The discipline is to resist shipping to everyone at once.

Pick one team. Ideally one enthusiastic about AI tooling and willing to file detailed feedback. Roll out the v1 harness to them only. Be present in their Slack channel. Watch how they actually use it. Fix what breaks. Ship updates weekly.

By day 90 you should have a battle-tested v1 harness, a list of changes for v2 based on real usage, a rollout plan for the next two or three teams, and the start of a governance doc that codifies what is approved and what is in review.

## Governance Recommendations

A short list, drawn from what works in practice and what Anthropic explicitly recommends.

Start with limited initial access and expand as confidence builds. The pressure will be to give everyone access immediately. Resist it. Limited access is what lets you fix problems before they become company-wide incidents.

Maintain a defined set of approved skills with a written promotion process. Personal skills are fine; org-wide skills require review. The review process can be lightweight (a single reviewer plus a sanity check) but it has to exist.

Require code review on changes to anything in `.claude/` that ships with the org-standard repo. The harness is code. Treat it like code.

Stand up a cross-functional working group within the first six months: engineering, infosec, governance. Monthly cadence is fine. Document the escalation path so developers know where to go when they hit a problem they cannot solve themselves.

## Hiring or Promoting Internally

Most agent managers in 2026 are promoted internally. The role is too new for a deep external talent pool, and internal candidates already have the org context that makes the job possible.

Signals to look for in an internal candidate: writes good documentation unprompted, has a `.claude/` folder other engineers have asked to borrow from, runs informal office hours about AI tooling without being asked, has shipped at least one piece of internal infrastructure that other teams adopted.

If you hire externally, the rubric is closer to a senior platform engineer than a traditional PM. Ask them to walk through the harness they would ship on day one. Ask how they would handle a specific permissions request from infosec. Ask what they would prioritize between adding a new MCP server and standardizing the existing skills library. The answers reveal whether they understand both halves of the job.

Compensation lands between senior engineer and senior PM. Most orgs slot the role into an existing engineering ladder with a product-leaning level rather than inventing a new track.

## Where This Role Fits in the Harness

The seven pieces of the harness need an owner. Without one, the harness becomes the bottleneck instead of the leverage point. With one, the harness compounds. Every quarterly review removes a rule that has become a constraint and adds one that closes a gap. Every plugin update lifts the floor for every developer in the org. The work is real, the title is now named, and the orgs investing in it early are the ones whose Claude Code rollouts are quietly outperforming their peers.

The [large codebase playbook](/blog/large-codebase-playbook) covers the strategies the harness has to implement. The plugins distribution guide covers the mechanism agent managers use to ship the harness across the org. The [agentic engineering best practices](/blog/agentic-engineering-best-practices) post covers the developer-facing habits that the harness should reinforce.

## The Pattern Going Forward

Expect agent manager or an equivalent title to appear in tech-company org charts by the end of 2026. The companies that resist creating the role will end up creating it under a different name twelve months later, after the second or third incident that traces back to nobody owning the harness. The companies that create it early get to define what the role looks like for their org, rather than reverse-engineering it from a postmortem.

If you are the de facto agent manager today, the work is to make the role explicit. Write down what you own. Get your manager and infosec on the same page. Publish the charter. The role exists whether or not it is named, and named roles get the resourcing that unnamed work does not.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
