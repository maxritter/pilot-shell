---
title: "Claude Code Source Leak: Everything Found (2026)"
description: "Full breakdown of the Claude Code npm source map leak. 512K lines, 44 feature flags, Undercover Mode, KAIROS, and model codenames revealed."
slug: claude-code-source-leak
date: 2026-04-01
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Full breakdown of the Claude Code npm source map leak. 512K lines, 44 feature flags, Undercover Mode, KAIROS, and model codenames revealed.

<!-- truncate -->

**Problem**: On March 31, 2026, someone at Anthropic forgot to add `*.map` to `.npmignore`. That one missing line exposed the entire Claude Code codebase: 512,000+ lines of TypeScript, 44 hidden feature flags, an always-on background agent called KAIROS, and a stealth mode designed to hide Anthropic employee contributions to open-source projects. The Claude Code source code leak is the most significant accidental disclosure in AI tooling history, and it happened because the Bun runtime generates source maps by default.

**What this means for you**: If you use Claude Code, this leak reveals what's coming next, how the tool actually works under the hood, and several features that Anthropic hasn't announced yet. If you build with AI tools in general, this is a masterclass in what a $2.5 billion ARR product looks like from the inside: the architecture decisions, the security tradeoffs, and the engineering culture that produces both brilliant systems and basic packaging mistakes.

## How the Leak Happened

Security researcher **Chaofan Shou** ([@shoucccc](https://x.com/shoucccc) on X), an intern at Solayer Labs, discovered that version 2.1.88 of the `@anthropic-ai/claude-code` npm package shipped with a 59.8 MB JavaScript source map file (`cli.js.map`). He posted the download link to X at approximately 4:23 AM ET. The post went viral, reaching between 16 and 21 million views.

The root cause was mundane. Claude Code uses the Bun runtime for its build process, and Bun generates source maps by default. Someone needed to add `*.map` to the `.npmignore` file. Nobody did.

Boris Cherny, Anthropic's head of Claude Code, confirmed it was a "plain developer error." He also shared a quote that tells you everything about their development culture: "100% of my contributions to Claude Code were written by Claude Code."

This was not the first time. A similar leak occurred in February 2025, making this at minimum the second such incident in 13 months. And it came just 5 days after the "Mythos" model spec leak, where a CMS misconfiguration exposed roughly 3,000 internal files, including draft blog posts about unreleased models.

Two leaks in one week. For a company that brands itself as the safety-first AI lab, that's a rough look. And for everyone asking "is Claude Code open source?" after seeing the GitHub repository: the answer is more nuanced than ever.

## The Scale of What Was Exposed

The source map file decompressed into approximately 1,900 TypeScript source files. Here's the scale:

| Metric | Value |
| --- | --- |
| Total source files | ~1,900 TypeScript files |
| Total lines of code | 512,000+ |
| Main entry point | 785KB (`main.tsx`) |
| Registered tools | 40+ |
| Hidden feature flags | 44, covering 20+ unshipped features |
| Context compaction strategies | 5 distinct approaches |
| Event hooks | 25+ hook system |

The architecture is a custom React terminal renderer using React and Ink with game-engine-style optimization. The query engine alone spans 46,000 lines. The base tool definition is 29,000 lines. If you've used Claude Code's context management system, you've felt the effects of those 5 compaction strategies without knowing they existed.

Three subagent execution models were found: Fork, Teammate, and Worktree. If you've been following our coverage of [sub-agent best practices](/blog/sub-agent-best-practices), this confirms the architectural patterns we've described, with the added context that Claude Code internally uses three distinct delegation strategies depending on task complexity.

The tool also includes prompt caching with 14 tracked cache-break vectors, meaning the system actively monitors 14 different conditions that could invalidate its prompt cache. And `bashSecurity.ts` contains 23 numbered security checks that gate every shell command Claude Code executes. For more on how those permission checks work in practice, see our permission management guide.

## Undercover Mode: The Most Controversial Discovery

The most debated finding lives in a file called `undercover.ts`, approximately 90 lines of code. Undercover Mode activates when an Anthropic employee (`USER_TYPE === 'ant'`) uses Claude Code on a non-internal repository.

When active, it injects this system prompt:

```
You are operating UNDERCOVER in a PUBLIC/OPEN-SOURCE repository.
Your commit messages, PR titles, and PR bodies MUST NOT contain
ANY Anthropic-internal information. Do not blow your cover.
```

The mode does the following:

- **Strips all `Co-Authored-By` attribution** from commits, removing any trace that Claude Code generated the code
- **Forbids mentioning** internal codenames, Slack channels, internal repo names, or even the phrase "Claude Code" itself
- **Blocks references to unreleased models** like Opus 4.7 and Sonnet 4.8 (more on those codenames below)
- **Provides no force-OFF mechanism** for external users

In external builds shipped to regular users, the entire undercover function is dead-code-eliminated. You will never encounter it. But the existence of the mode raises genuine questions about AI companies contributing anonymously to open-source projects.

As one Hacker News commenter summarized: the Buddy system is "adorable" and Undercover Mode is "unethical." Whether you see it as corporate stealth or responsible information security depends on your perspective. The technical reality is that Anthropic employees use Claude Code on open-source projects, and this mode prevents internal details from leaking through commit metadata. The ethical concern is that AI-generated code enters open-source repositories without attribution to either the AI or the company.

The deep irony was not lost on the community. They built Undercover Mode specifically to prevent leaking internal secrets through code contributions. Then they leaked the entire source code through a file they forgot to exclude from the npm package.

## KAIROS: The Always-On Background Agent

KAIROS is referenced over 150 times in the source code. Named after the Ancient Greek concept of "the right moment" (the opportune time to act), it represents a fully built but unshipped autonomous daemon mode for Claude Code.

Here's what the code reveals:

- **Autonomous operation**: KAIROS receives periodic `<tick>` prompts and decides independently whether to act
- **Persistence**: Continues running even when your laptop is closed, maintaining session state across restarts
- **15-second blocking budget**: Prevents the agent from monopolizing system resources during any single decision cycle
- **Append-only logging**: Daily log files that the agent cannot self-erase, creating an audit trail of all autonomous actions
- **Three exclusive tools**: Push notifications, file delivery, and PR subscriptions, none of which are available to the standard Claude Code session
- **GitHub webhook subscriptions**: Autonomous monitoring of repository events without user intervention

KAIROS represents the next step beyond what we currently describe as [autonomous agent loops](/blog/autonomous-agent-loops). Where current Claude Code sessions require you to be present and approving, KAIROS would operate in the background indefinitely, watching your repositories and taking action when it determines the moment is right.

The name choice is deliberate. In Greek rhetoric, kairos means recognizing and acting at the perfect moment, contrasted with chronos (sequential time). The agent doesn't run on a schedule. It decides when to engage based on context.

The feature remains gated behind flags, and there's no indication of a launch timeline. But the 150+ references suggest this is not a prototype. It's a finished feature waiting for a green light.

## autoDream: When Claude Literally Dreams

The `services/autoDream/` directory contains a memory consolidation system that runs during idle time. Claude literally "dreams," reorganizing and compressing accumulated session knowledge.

The system uses a three-gate trigger:

1. At least 24 hours since the last dream cycle
2. At least 5 sessions completed since last consolidation
3. A consolidation lock (preventing concurrent dream processes)

When all three conditions are met, the dream cycle runs four phases:

1. **Orient**: Assess current memory state and what needs consolidation
2. **Gather Recent Signal**: Collect insights from recent sessions
3. **Consolidate**: Merge new knowledge with existing memory
4. **Prune and Index**: Remove redundancies and keep MEMORY.md under 200 lines / approximately 25KB

If you've used Claude Code's [auto-memory system](/blog/auto-memory), you've seen the results of this process. If you want to understand how [auto-dream](/blog/auto-dream) works in practice, we covered the user-facing behavior in detail. The leaked source code confirms the four-phase architecture and adds the specific thresholds that trigger it.

## Anti-Distillation: Poisoning Competitor Training Data

The source code reveals a two-layer anti-distillation system designed to prevent competitors from training on Claude Code's outputs.

**Layer 1: Fake Tools**

The feature flag `anti_distillation: ['fake_tools']` tells the server to inject decoy tool definitions into responses. This is gated behind a GrowthBook flag called `tengu_anti_distill_fake_tool_injection`. Any competitor attempting to distill Claude Code's tool-calling behavior would learn from deliberately incorrect tool schemas.

**Layer 2: CONNECTOR_TEXT**

The server returns only cryptographically signed summaries rather than full reasoning chains. This approach withholds the detailed chain-of-thought that would be most valuable for competitor model training. The CONNECTOR_TEXT layer is scoped to `USER_TYPE === 'ant'` only, meaning it runs for Anthropic employees but not external users.

Together, these systems mean that Anthropic has been actively thinking about, and building defenses against, model distillation attacks targeting their agentic coding tool.

## ULTRAPLAN: 30-Minute Remote Planning Sessions

ULTRAPLAN offloads complex planning tasks to a remote Cloud Container Runtime running Opus 4.6 with a planning window of up to 30 minutes. Your local terminal polls every 3 seconds for updates, and a browser UI allows live monitoring where you can approve or reject the plan in progress.

If you've used Claude Code's planning modes, ULTRAPLAN represents the extreme version: a remote instance with a 30-minute thinking budget, running on hardware far more capable than your laptop.

## Penguin Mode and Internal Codenames

"Penguin Mode" is the internal name for what users know as [Fast Mode](/blog/fast-mode). The API endpoint is `/api/claude_code_penguin_mode`, and it has a kill-switch flag called `tengu_penguins_off`. The codename pattern extends throughout the codebase.

### Model Codenames Revealed

| Codename | Maps To |
| --- | --- |
| Tengu | Claude Code's internal project codename |
| Capybara | New model family (possibly the leaked "Mythos" model). References to capybara, capybara-fast, capybara-fast[1m], capybara-v2-fast |
| Fennec | Opus 4.6 (migration function `migrateFennecToOpus` found in source) |
| Numbat | Unreleased model ("Remove this section when we launch numbat") |
| Opus 4.7 | Referenced in Undercover Mode's forbidden strings list |
| Sonnet 4.8 | Referenced in Undercover Mode's forbidden strings list |

The capybara codename is especially interesting because it also appears as a [Claude Buddy](/blog/claude-buddy) species name, hex-encoded to bypass Anthropic's own `excluded-strings.txt` build scanner. They encoded all 18 pet species names uniformly so that hiding one codename wouldn't look suspicious.

## The Code Quality Debate

The leaked source sparked a separate conversation about code quality at a company billing $2.5 billion annually from this product.

**The `print.ts` file**: 5,594 lines of code containing a single function that spans 3,167 lines. That one function alone is longer than many entire applications.

**Frustration detection**: The codebase includes a regex-based system that scans user input for profanity and emotional distress signals. The community reaction was immediate: "An LLM company using regexes for sentiment analysis? That's like a truck company using horses to transport parts."

**187 spinner verbs**: The loading spinner cycles through 187 different action verbs. Community members went through the entire list checking for "reticulating" (the famous SimCity 2000 loading message). They found it.

**Nested callbacks**: One Hacker News commenter described the extensive use of nested `.then()` callback chains as "a defining work of the 'just vibes' era." Given that the head of Claude Code has stated the tool wrote its own codebase, this means the AI's coding style is now a matter of public record.

**Native client attestation**: The security layer for client verification has been pushed below the JavaScript layer entirely, into Bun's Zig-level HTTP stack. This is more sophisticated than what most developer tools implement and suggests Anthropic takes API security seriously even if npm packaging is an afterthought.

## Community Reaction

The community response moved fast.

**Mirrors and forks**: One mirror repository accumulated over 41,500 forks. The code was also mirrored to a decentralized platform with a clear statement: "Will never be taken down."

**Clean-room rewrites**: Korean developer Sigrid Jin created "claw-code" (instructkr/claw-code), a clean-room Python rewrite that hit 75,000 GitHub stars in approximately 2 hours, possibly the fastest-growing repository in GitHub history.

**DMCA takedowns**: Anthropic filed DMCA notices against GitHub mirrors, a standard response but one that drew criticism given that the code was accidentally published through their own packaging error.

**Memecoins**: Someone launched $Nebulynx on Solana, based on the rarest possible Claude Buddy variant (Shiny Legendary). Because of course they did.

**Concurrent chaos**: By coincidence, the same day saw a supply-chain attack on an unrelated npm package via Axios, creating a surreal 24 hours where the npm ecosystem was simultaneously dealing with an accidental corporate leak and a deliberate security attack.

**Coverage**: The leak was covered by CNBC, Fortune, Gizmodo, VentureBeat, Axios, The Register, Decrypt, Cybernews, and The Hacker News, among others.

## What This Means for the AI Industry

### For Anthropic

Anthropic sits at $19 billion annualized revenue, with Claude Code alone generating $2.5 billion ARR. The company is reportedly preparing for an October IPO at approximately $380 billion valuation. Two leaks in one week (source code plus the Mythos model spec) undermine the "safety-first" narrative that is core to their brand and valuation story.

AI security firm Straiker warned that attackers can now study the data flow through Claude Code's four-stage context management pipeline, potentially identifying attack vectors that weren't visible before. Feature flags and the product roadmap are now visible to competitors like GitHub Copilot, Cursor, and every other AI coding tool.

### For Developers Using Claude Code

The leak confirms that Claude Code's architecture is genuinely sophisticated. Five context compaction strategies, 14 cache-break vectors, 23 security checks on bash commands, and three subagent execution models. This is not a wrapper around an API. It's a deeply engineered system.

The upcoming features (KAIROS, ULTRAPLAN, autoDream refinements) suggest Claude Code is heading toward always-on, autonomous operation rather than the session-based model most users experience today. If you're building workflows around Claude Code, designing for eventual autonomous operation is worth considering now.

### For the Open-Source Debate

One of the most searched questions after the leak: is Claude Code open source? Technically, the source code has been visible on GitHub since Anthropic chose to publish the repository. But "source available" is not the same as "open source." The license does not permit redistribution or modification, which is why Anthropic could file DMCA takedowns against mirrors. The npm leak made the full codebase more accessible, including source maps that reverse-engineer the compiled output to readable TypeScript, but it did not change the licensing.

Anthropic's official statement: "No sensitive customer data or credentials were involved. Release packaging issue caused by human error, not a security breach." They initially used the npm `deprecated` flag instead of actually unpublishing the package, which drew additional criticism for a slow response. No formal post-mortem has been published.

## Frequently Asked Questions

### What was the Claude Code source code leak?

On March 31, 2026, version 2.1.88 of the `@anthropic-ai/claude-code` npm package shipped with a 59.8 MB source map file (`cli.js.map`) that exposed the complete TypeScript source code. The file contained approximately 1,900 source files and 512,000+ lines of code, revealing hidden features, internal codenames, and unshipped capabilities like the KAIROS background agent and Undercover Mode.

### Is Claude Code open source?

Claude Code's source is available on GitHub, but it is not open source in the licensing sense. The license does not permit redistribution or modification. The npm leak made the full source more accessible through source maps, but Anthropic retains copyright and filed DMCA takedowns against unauthorized mirrors.

### What is Claude Code Undercover Mode?

Undercover Mode is a feature that activates for Anthropic employees when they use Claude Code on non-internal repositories. It strips Co-Authored-By attribution, forbids mentioning internal details in commits, and prevents references to unreleased models. It has no effect on external users as it is dead-code-eliminated from public builds.

### What is KAIROS in Claude Code?

KAIROS is an unshipped autonomous daemon mode referenced over 150 times in the Claude Code source. Named after the Greek concept of "the right moment," it's a background agent that persists across sessions, receives periodic tick prompts, and can independently decide to take actions like sending notifications or monitoring GitHub webhooks. It remains behind feature flags with no announced launch date.

### What model codenames were found in the leak?

The leak revealed several internal codenames: Tengu (Claude Code's project codename), Capybara (a new model family, possibly the leaked Mythos model), Fennec (Opus 4.6), and Numbat (an unreleased model). References to Opus 4.7 and Sonnet 4.8 were found in Undercover Mode's list of forbidden strings, confirming these models are in development.

### How did the Claude Code leak happen?

The Bun runtime generates source maps by default during the build process. Someone at Anthropic failed to add `*.map` to the `.npmignore` file, causing the source map to be included in the published npm package. Boris Cherny, head of Claude Code, confirmed it was a "plain developer error." This was at least the second such incident, following a similar leak in February 2025.

---

*Already using Claude Code? Make sure you understand the [context engineering techniques](/blog/context-engineering) that power the system, or explore our complete guide to Claude Code if you're just getting started.*
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
