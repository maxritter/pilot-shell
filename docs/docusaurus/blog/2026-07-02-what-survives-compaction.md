---
title: "What Survives /compact in Claude Code"
description: "What Claude Code /compact keeps and loses, straight from Anthropic's docs. The full survival table plus how to make rules and skills persist."
slug: what-survives-compaction
date: 2026-07-02
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

What Claude Code /compact keeps and loses, straight from Anthropic's docs. The full survival table plus how to make rules and skills persist.

<!-- truncate -->

**Problem**: You gave Claude Code a rule twenty messages ago. The session compacted. Now Claude ignores it, and you're left wondering whether the model got dumber or the instruction was never really followed. Neither. The instruction got summarized away, and where you put it is what decided whether it came back.

**Quick answer**: After compaction, anything Claude loaded from disk at startup gets re-injected, and anything that arrived through the conversation gets folded into a summary. Your project-root CLAUDE.md survives. A rule scoped to a file path does not, until Claude reads a matching file again. Anthropic [documented the exact rules](https://code.claude.com/docs/en/context-window), and once you know them you stop losing instructions to compaction by accident.

This is a spoke of our context management guide. Read that for the broader strategy; this post is the specific mechanics of what `/compact` keeps.

## The Full Survival Table

When a session compacts, whether you triggered it with `/compact` or Claude Code fired it automatically near the limit, it summarizes your conversation history to reclaim space. The fate of each piece of context depends only on how it was loaded, not on how important it is. Here is every mechanism:

| Mechanism | After compaction |
| --- | --- |
| System prompt and output style | Unchanged; they were never part of the message history |
| Project-root CLAUDE.md and unscoped rules | Re-injected from disk |
| Auto memory (`MEMORY.md`) | Re-injected from disk |
| Rules with `paths:` frontmatter | Lost until a matching file is read again |
| Nested CLAUDE.md in a subdirectory | Lost until a file there is read again |
| Invoked skill bodies | Re-injected, capped at 5,000 tokens per skill and 25,000 total, oldest dropped first |
| Hooks | Not applicable; they run as code, not context |

The pattern is worth saying out loud: **loaded from disk at startup means it comes back; loaded through the conversation means it gets summarized.** Your project-root CLAUDE.md, your unscoped `.claude/rules/` files, and your [auto memory](/blog/auto-memory) all reload from disk after compaction, so instructions you keep there are effectively permanent. Everything else is negotiable. (Auto memory here means Claude's `MEMORY.md` notes, not [Session Memory](/blog/session-memory), which is the separate background summary Claude loads when a session compacts.)

## Why Path-Scoped Rules and Nested CLAUDE.md Disappear

The two entries that trip people up are path-scoped rules and nested CLAUDE.md files, because both feel like configuration but behave like conversation.

A rule with `paths:` frontmatter in `.claude/rules/` does not load at startup. It loads the moment Claude reads a file matching its glob, which means it enters your message history mid-session, right alongside the file contents. Compaction summarizes message history. So the rule gets compressed into the summary and its specifics are gone, until Claude next reads a matching file and the rule re-triggers. A [nested CLAUDE.md](/blog/subdirectory-claude-md) in a subdirectory works the same way: it loads on demand when Claude works in that folder, not at launch, so compaction treats it like any other in-conversation content.

The fix is a placement decision. If an instruction must survive a mid-task compaction, it belongs in your project-root CLAUDE.md or an unscoped rule, both of which reload from disk. If it is genuinely local to one part of the codebase, a [path-scoped rule](/blog/rules-directory) is still the right call. Just know it reloads lazily rather than persisting, and it will be absent in the window right after a compaction fires. Anthropic's [memory documentation](https://code.claude.com/docs/en/memory) confirms it: nested CLAUDE.md files are not re-injected automatically and reload the next time Claude reads a file in that directory.

## How Skills Survive: The Token Caps

Invoked skills come back after compaction, but not for free. Re-injection is capped at 5,000 tokens per skill and 25,000 tokens total, and when the total budget is exceeded, the oldest invoked skills are dropped first. A large skill gets truncated to fit its per-skill cap, and truncation keeps the start of the file.

That last detail is an instruction to you, not a curiosity: **put the load-bearing parts of every `SKILL.md` near the top.** If your critical steps live at the bottom of a 6,000-token skill, they are the first thing lost when the file is truncated after a compaction.

Two more skill behaviors matter here. First, the skill descriptions listing, the one-line summaries Claude reads at startup to know what it can invoke, is the single startup element that does *not* reload after `/compact`. Only skills you actually invoked are preserved; the rest of the catalog is gone from that window. Second, a skill marked `disable-model-invocation: true` costs zero context until you call it with `/name`, because it never appears in the startup listing at all. That makes it the right setting for side-effect skills like commit, deploy, or send, which you want out of context entirely until the moment you use them. For the mechanics of the listing and how it gets throttled, see our guides on [Claude skills](/blog/claude-skills-guide) and the [skill listing budget](/blog/skill-listing-budget).

## Steer and Verify Compaction

You are not stuck with whatever the automatic pass decides to keep. Four commands give you control:

- `/compact focus on X` runs compaction with your instructions, so the summary preserves the thread you name (`/compact focus on the auth refactor`) instead of what the automatic pass guesses is important.
- `/clear` wipes the conversation entirely. Use it between unrelated tasks, since stale conversation both crowds out the files you need next and costs tokens on every message.
- `/context` shows the live breakdown of what is using your window right now, by category.
- `/memory` lists the CLAUDE.md and rules files loaded this session and links to your auto memory folder, so you can confirm what will survive a compaction before one happens.

Running `/memory` and `/context` before a long task is the fastest way to catch a rule that *won't* persist, or a memory file quietly eating your window.

## Structure Your Instructions So the Right Things Survive

Put it together and a simple placement policy falls out:

- **Must survive every compaction?** Project-root CLAUDE.md or an unscoped rule. Keep it lean, because it reloads in full and bloat here taxes every session.
- **Only relevant to one directory or file type?** A path-scoped rule or nested CLAUDE.md. Accept that it reloads lazily and is absent right after compaction.
- **A multi-step workflow?** A skill, with the critical steps top-loaded so truncation can't cut them.
- **A skill with side effects?** Add `disable-model-invocation: true` so it stays out of context until you invoke it.

## The Takeaway

Compaction is not lossy by accident; it is lossy by design, and Anthropic told you exactly where the seams are. Loaded-from-disk survives, in-conversation gets summarized. Once that rule is in your head, "Claude forgot my instruction" stops being a mystery and becomes a placement bug you can fix in one move: put the instruction where it reloads. For the buffer mechanics behind when compaction actually fires, see the [context buffer guide](/blog/context-buffer-management); for the full strategy of working within the window, start at the context management hub.

Context Management
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
