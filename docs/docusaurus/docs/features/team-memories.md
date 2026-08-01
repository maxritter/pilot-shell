---
sidebar_position: 2
title: Team Memories
description: Share a project's Pilot Console memories with your team by storing them in the project repository - decisions and discoveries flow to every contributor through git.
---

# Team Memories

Pilot Shell captures decisions, discoveries, and bugfixes as you work and re-injects them at the start of every session. By default they are yours alone, in a local database.

**Team Memories** stores a project's memories inside the project repository, so everyone who pulls the repo works from the same knowledge - the reasoning behind how the code works travels with the code instead of living on one laptop.

Available on the **Team** plan.

## How It Works

Memories are written as plain-text records under `.pilot/memories/`. Git is the transport: Pilot never stages, commits, pushes, or opens a remote on your behalf. It reads `git config user.email` to label who wrote a memory, and nothing else.

```
your-project/.pilot/
  memory.json                    # shareMemories: true
  memories/
    alice@example.com/2026-07-29.jsonl
    bob@example.com/2026-07-30.jsonl
```

One JSONL file per author per day, one memory per line. Because each teammate only ever writes files under their own folder, simultaneous exports cannot produce a merge conflict. File paths inside a record are repository-relative, so records are portable across checkouts.

## Enabling Sharing

Open the Console at `http://localhost:41777/#/memories` and click **Enable sharing** on the **Team Sharing** card.

That one click writes `"shareMemories": true` into `.pilot/memory.json`, exports every shareable memory you already have, and imports whatever your teammates have committed. Review the diff and commit it like any other change - including `.pilot/memory.json`, which is how the rest of the team turns sharing on.

## Staying In Sync

Once enabled, sharing keeps itself current in both directions:

- **Outgoing** - a session's memories are written when it ends. You still commit them.
- **Incoming** - teammates' new records are imported at the start of every session, before your context is assembled, so yesterday's decision is available to your agent today. Works on **both Claude Code and Codex CLI**.

Neither runs on a timer: a clock-driven job would drop files into your working tree mid-rebase or mid-review and make the diff you are reviewing a moving target. **Share memories** and **Import** on the card run either direction on demand.

Imported memories behave like your own - badged with their author in the Memories view, semantically searchable, and fed into the session-start context digest.

## What Gets Shared

**Shared:** observations of type `decision`, `discovery`, `bugfix`, `feature`, `refactor`, and `change` - the durable "how this works and why" knowledge.

**Not shared:** sessions, session summaries, and your prompts. Those are the noisiest and most personal part of the store and stay local. Other projects are never touched.

:::warning Review before you commit
Memories are written by a model reading your session. Treat `.pilot/memories/` like any other file you are about to commit and read the diff - Pilot does not scan record contents for secrets.
:::

:::warning Importing is a trust decision
Shared memories are loaded into your agent's context, so a repository you did not write can put text in front of your agent.

Enabling sharing yourself counts as that decision. But when you **clone a repo where `shareMemories` is already committed**, you have decided nothing, and the Console asks you to confirm before importing anything. The confirmation lives in `~/.pilot/memory/shared-memory-trust.json`, keyed by the repository's absolute path, so a different checkout must be confirmed on its own.
:::

## Turning It Off

**Disable sharing** on the card stops exporting and importing for that project. Nothing is deleted: committed records stay in the repository, imported memories stay in your database.

## Frequently Asked

**Do I have to re-export memories I already shared?**
No. Export appends only records the files do not already contain, so running it twice produces no diff.

**What happens if a teammate's licence lapses?**
The records are plain text in your repository and stay there. Without a Team licence the Console stops importing and exporting them.

**Can I share memories through a separate repository?**
Not today - the shared store lives in the project repo. Extensions (skills, rules, commands, agents) are the ones shared through a dedicated git remote; see [Extensions](./extensions.md#team-sharing-team-and-enterprise).
