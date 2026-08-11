---
title: "Claude Code Dreams: Anthropic's New Memory Feature"
description: "Claude Code Auto Dream consolidates memory files, pruning stale notes and merging insights. Like REM sleep for your AI agent."
slug: auto-dream
date: 2026-03-24
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code Auto Dream consolidates memory files, pruning stale notes and merging insights. Like REM sleep for your AI agent.

<!-- truncate -->

Anthropic quietly shipped a feature to Claude Code that they haven't officially announced yet. It's called **Auto Dream**, and it solves the biggest problem with auto memory: decay over time.

**The problem**: Auto memory was a breakthrough. Claude finally took its own notes about your project. But after 20+ sessions, those notes become a mess. Contradictory entries pile up. Relative dates like "yesterday" lose meaning. Stale debugging solutions reference files that no longer exist. The notebook that was supposed to help Claude remember instead becomes noise that confuses it.

**Quick Win**: Check if Auto Dream is active on your setup. Run `/memory` inside any Claude Code session. Look for "Auto-dream: on" in the selector. If you see it, Claude is already consolidating your memory files in the background between sessions.

```
# Check your current memory state
/memory
 
# Look for:
# Auto-dream: on
```

If Auto Dream is available and toggled on, you're set. Claude periodically reviews every memory file in your project, prunes what's stale, resolves contradictions, and reorganizes the rest. If you don't see the toggle yet, keep reading. You can trigger it manually.

## Why "Dreaming"? The REM Sleep Parallel

The naming is deliberate, and the metaphor is surprisingly accurate.

During the day, your brain absorbs raw sensory input and stores it as short-term memories. During REM sleep, your brain replays the day's events, strengthens connections that matter, discards what doesn't, and organizes everything into long-term memory. People who don't get enough REM sleep struggle to form lasting memories. The information comes in, but it never gets consolidated.

[Auto memory](/blog/auto-memory) is Claude's daytime brain. It takes notes as it works: debugging patterns, build commands, architecture decisions, your preferences. Every session adds more entries. But without a consolidation step, those notes accumulate the same way unconsolidated short-term memories do. Contradictions persist. Outdated entries linger. The signal-to-noise ratio degrades with every session.

Auto Dream is the REM sleep cycle. It reviews what Auto Memory has collected, strengthens what's still relevant, removes what's outdated, and reorganizes the rest into clean, indexed topic files. Claude Code without Auto Dream was essentially sleep-deprived. It kept adding random notes without ever cleaning up.

## The Four Phases of Auto Dream

When Auto Dream runs, it follows a structured four-phase process. Each phase has a specific purpose, and together they transform scattered session notes into organized project knowledge.

### Phase 1: Orientation

Claude reads the current memory directory and takes stock of what exists. It opens MEMORY.md (the index file), scans the list of topic files, and builds a mental map of the current memory state.

This phase answers: "What do I already know, and how is it organized?"

### Phase 2: Gather Signal

This is where Auto Dream searches through your session transcripts (the JSONL files Claude stores locally for each session). It doesn't read every transcript end-to-end. That would be prohibitively expensive for projects with hundreds of sessions. Instead, it searches narrowly for specific patterns:

- **User corrections**: Moments where you told Claude it was wrong or redirected its approach
- **Explicit saves**: Times you said "remember this" or "save to memory"
- **Recurring themes**: Patterns that appeared across multiple sessions
- **Important decisions**: Architecture choices, tool selections, workflow changes

The narrow search is intentional. Exhaustively reading 500+ session transcripts would burn tokens and time for diminishing returns. Targeted grep-style searches extract the highest-value signals efficiently.

### Phase 3: Consolidation

The core phase. Claude merges new information into existing topic files and performs critical maintenance:

- **Converts relative dates to absolute dates.** "Yesterday we decided to use Redis" becomes "On 2026-03-15 we decided to use Redis." This prevents temporal confusion as memories age.
- **Deletes contradicted facts.** If you switched from Express to Fastify three weeks ago, the old "API uses Express" entry gets removed.
- **Removes stale memories.** Debugging notes about a file that was deleted during a refactor serve no purpose. They get pruned.
- **Merges overlapping entries.** If three different sessions noted the same build command quirk, those consolidate into one clean entry.

### Phase 4: Prune and Index

The final phase focuses on the MEMORY.md index file. This file is kept under 200 lines because that's the cutoff for what loads at startup. Phase 4 updates MEMORY.md to accurately reflect the current state of all topic files:

- Removes pointers to topic files that no longer exist
- Adds links to new topic files created during consolidation
- Resolves contradictions between the index and actual file contents
- Reorders entries by relevance and recency

Files that didn't need changes during consolidation are left untouched. Auto Dream doesn't rewrite everything on every run. It's surgical.

## The Full System Prompt

Here's the actual system prompt that powers Auto Dream. This is what Claude receives when a dream cycle kicks off:

```
# Dream: Memory Consolidation
 
You are performing a dream - a reflective pass over your memory files.
Synthesize what you've learned recently into durable, well-organized
memories so that future sessions can orient quickly.
 
Memory directory: `~/.claude/projects/<project>/memory/`
This directory already exists - write to it directly with the Write tool
(do not run mkdir or check for its existence).
 
Session transcripts: `~/.claude/projects/<project>/`
(large JSONL files - grep narrowly, don't read whole files)
 
## Phase 1 - Orient
 
- `ls` the memory directory to see what already exists
- Read `MEMORY.md` to understand the current index
- Skim existing topic files so you improve them rather than creating
  duplicates
- If `logs/` or `sessions/` subdirectories exist (assistant-mode layout),
  review recent entries there
 
## Phase 2 - Gather recent signal
 
Look for new information worth persisting. Sources in rough priority order:
 
1. **Daily logs** (`logs/YYYY/MM/YYYY-MM-DD.md`) if present - these are
   the append-only stream
2. **Existing memories that drifted** - facts that contradict something
   you see in the codebase now
3. **Transcript search** - if you need specific context (e.g., "what was
   the error message from yesterday's build failure?"), grep the JSONL
   transcripts for narrow terms:
   `grep -rn "<narrow term>" <project-transcripts>/ --include="*.jsonl"
| tail -50`
 
Don't exhaustively read transcripts. Look only for things you already
suspect matter.
 
## Phase 3 - Consolidate
 
For each thing worth remembering, write or update a memory file at the
top level of the memory directory. Use the memory file format and type
conventions from your system prompt's auto-memory section - it's the
source of truth for what to save, how to structure it, and what NOT
to save.
 
Focus on:
 
- Merging new signal into existing topic files rather than creating
  near-duplicates
- Converting relative dates ("yesterday", "last week") to absolute dates
  so they remain interpretable after time passes
- Deleting contradicted facts - if today's investigation disproves an old
  memory, fix it at the source
 
## Phase 4 - Prune and index
 
Update `MEMORY.md` so it stays under 200 lines. It's an **index**, not a
dump - link to memory files with one-line descriptions. Never write memory
content directly into it.
 
- Remove pointers to memories that are now stale, wrong, or superseded
- Demote verbose entries: keep the gist in the index, move the detail into
  the topic file
- Add pointers to newly important memories
- Resolve contradictions - if two files disagree, fix the wrong one
 
---
 
Return a brief summary of what you consolidated, updated, or pruned. If
nothing changed (memories are already tight), say so.
```

A few things worth noting about this prompt. It explicitly tells Claude to grep narrowly rather than reading full transcripts. It enforces the 200-line limit on MEMORY.md. And it instructs Claude to resolve contradictions at the source rather than just flagging them. The prompt is opinionated about how memory should be structured, which is why the output is consistently clean.

## When Auto Dream Runs

Two conditions must both be true before a consolidation cycle triggers:

1. **24 hours have passed** since the last consolidation
2. **More than 5 sessions have occurred** since the last consolidation

Both conditions are required. If you had one long session over two days, Auto Dream won't trigger (not enough sessions). If you ran 10 quick sessions in two hours, it won't trigger either (not enough time). This dual-gate prevents unnecessary consolidation runs on projects with light usage while ensuring active projects get regular cleanup.

For context on how heavy a consolidation can be: in one observed case, Auto Dream consolidated the memory from 913 sessions in roughly 8-9 minutes. Not trivial, but it runs in the background, so you won't notice the cost.

## Safety Guarantees

Auto Dream runs with meaningful constraints to prevent accidents.

**Read-only mode for project code.** During a dream cycle, Claude can only write to memory files. It cannot modify your source code, configuration, tests, or any other project file. The dream process is sandboxed to the memory directory.

**Lock file prevents concurrent runs.** If two Claude Code instances are open on the same project, only one can run Auto Dream. A lock file ensures no two consolidation processes operate simultaneously, preventing merge conflicts in your memory files.

**Background execution.** You can keep working in Claude Code while Auto Dream runs. It doesn't block your session or require you to wait. The consolidation happens in a separate process.

## How to Trigger a Dream Manually

You don't have to wait for the automatic trigger. If you know your memory files need cleanup (after a major refactor, for example), you can force a consolidation.

The `/dream` command exists but hasn't rolled out to everyone yet. In the meantime, you can manually trigger it by telling Claude directly:

```
"dream"
"auto dream"
"consolidate my memory files"
```

Claude recognizes the intent and runs through the same four-phase process. This is useful after big project changes when you want clean memory without waiting for the next automatic cycle.

## Before and After: What Consolidation Looks Like

Here's what a typical memory directory looks like before and after Auto Dream runs.

### Before (Messy, 30+ Sessions of Accumulation)

```
~/.claude/projects/<project>/memory/
├── MEMORY.md              # 280 lines, over the 200-line limit
├── debugging.md           # Contains 3 contradictory entries about API errors
├── api-conventions.md     # References Express (switched to Fastify 2 weeks ago)
├── random-notes.md        # Mix of stale and current info
├── build-commands.md      # "Yesterday" used 6 times with no dates
└── user-preferences.md    # Duplicates entries from MEMORY.md
```

### After (Consolidated)

```
~/.claude/projects/<project>/memory/
├── MEMORY.md              # 142 lines, clean index with links to topic files
├── debugging.md           # Deduplicated, only current solutions
├── api-conventions.md     # Updated to reflect Fastify migration
├── build-commands.md      # All dates absolute, no duplicates
└── user-preferences.md    # Merged with relevant MEMORY.md entries
```

The `random-notes.md` file is gone. Its contents were either merged into relevant topic files or pruned as stale. MEMORY.md dropped from 280 to 142 lines, bringing it back under the 200-line startup threshold. Contradictions were resolved. Relative dates were converted.

## Auto Memory vs Auto Dream: Two Layers of the Same System

These two features are complementary, not competing. Think of them as the collection layer and the maintenance layer of a single memory system.

| Aspect | **Auto Memory** | **Auto Dream** |
| --- | --- | --- |
| **Role** | Collects new information | Consolidates existing information |
| **When it runs** | During every session | Periodically (24h + 5 sessions) |
| **What it does** | Writes notes about patterns found | Prunes, merges, and reorganizes notes |
| **Trigger** | Automatic, continuous | Automatic or manual |
| **Output** | New entries in memory files | Cleaned, reorganized memory files |
| **Risk of skip** | Miss capturing useful information | Memory quality degrades over time |

Auto Memory without Auto Dream is a note-taker who never organizes their notebook. Auto Dream without Auto Memory has nothing to consolidate. You want both running.

## Four Memory Systems: The Complete Picture

With Auto Dream, Claude Code now has four distinct memory mechanisms. Here's how they all fit together, building on the comparison from our [auto memory deep-dive](/blog/auto-memory):

| Aspect | **CLAUDE.md** | **Auto Memory** | **Session Memory** | **Auto Dream** |
| --- | --- | --- | --- | --- |
| **Who writes it** | You | Claude (per session) | Claude (automatic) | Claude (periodic) |
| **Purpose** | Instructions and rules | Project patterns and learnings | Conversation summaries | Memory consolidation |
| **When it runs** | You edit manually | During each session | Background, every ~5K tokens | Every 24h + 5 sessions |
| **Scope** | Per-project or global | Per-project | Per-session | Per-project |
| **Loaded at startup** | Full file | First 200 lines of MEMORY.md | Relevant past sessions | N/A (runs between sessions) |
| **Storage** | `./CLAUDE.md` | `~/.claude/projects/<project>/memory/` | `~/.claude/projects/<project>/<session>/session-memory/` | Same as Auto Memory |
| **Best for** | Standards, architecture, commands | Build patterns, debugging, preferences | Continuity between sessions | Keeping memory clean and accurate |
| **Human analogy** | Instruction manual | Daytime note-taking | Short-term conversation recall | REM sleep consolidation |

The strongest setup uses all four. [CLAUDE.md](/blog/claude-md-mastery) provides authoritative rules you control. Auto Memory captures what Claude learns while working. [Session Memory](/blog/session-memory) maintains conversation continuity. Auto Dream keeps the accumulated knowledge clean, current, and organized.

## Practical Tips

**Let it run automatically for most projects.** The default trigger conditions (24h + 5 sessions) work well for active development. You don't need to babysit this.

**Force a dream after major refactors.** If you renamed half your codebase, migrated frameworks, or changed your API structure, trigger a manual dream cycle. The old memory entries will cause more confusion than clarity until they're consolidated.

**Review the output occasionally.** After a dream cycle runs, skim your MEMORY.md. Auto Dream is good, but it's not perfect. You might spot a consolidation choice you disagree with. The files are plain markdown. Edit them freely.

**Combine with context management practices.** Auto Dream keeps your memory files clean, but you still need to manage your active session context. Clean memory files mean Claude loads less noise at startup, which gives you more room in the [context window](/blog/context-buffer-management) for actual work.

## Next Steps

- Set up CLAUDE.md if you haven't already. Auto Dream consolidates Auto Memory, but CLAUDE.md remains the highest-priority source of truth.
- Understand [auto memory](/blog/auto-memory) to see what Claude captures during sessions, the raw material Auto Dream works with.
- Explore [Session Memory](/blog/session-memory) for conversation-level continuity between work sessions.
- Read about [context engineering](/blog/context-engineering) to understand how all these memory systems fit into a deliberate context strategy.
- Check the Claude Code changelog for the latest memory system updates, including when Auto Dream rolled out to your plan tier.
- New to Claude Code? Follow the installation guide to get set up on macOS, Windows, or Linux before configuring memory.

Auto Dream is the feature that turns Claude's memory from a growing pile of notes into an actively maintained knowledge base. Auto Memory captures the raw material. Auto Dream shapes it into something useful. The result is a Claude that doesn't just remember more over time, but remembers better.

[Auto Memory](/blog/auto-memory)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
