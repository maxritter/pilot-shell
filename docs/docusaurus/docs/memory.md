---
title: Project memory
description: Reuse project lessons across agents and choose which repositories share them through Git.
---

# Project memory

Your agents reuse lessons from earlier tasks: decisions, fixes and constraints. This works with any coding agent you use with QualityLayer. The memory engine runs locally and needs no extra API key or service.

![Memory settings with project sharing and a searchable lesson list; illustrative project data](pathname:///img/app/memory-light.webp)
![Memory settings with project sharing and a searchable lesson list; illustrative project data](pathname:///img/app/memory-dark.webp)

Open **Settings → Memory** to search lessons, retire outdated ones or pause memory. Your agents' own memory settings stay as they are.

Search finds a lesson by its words and by its meaning. The model that reads meaning ships inside QualityLayer, so nothing is downloaded and no text leaves your computer.

## What your agents get

- **Lessons at the start.** A session in your repository receives its pinned lessons and the ones that match its first message, in one block of at most 3 KiB. It receives the block again after the agent compacts its context. Turn this off with **Lessons in every session** in Settings → Memory.
- **Pinned lessons.** Open a lesson and switch on **Pin to every session** to put it in every session's block. A project holds up to five pinned lessons.
- **Three tools.** `memory_search`, `memory_read` and `memory_save` let an agent look up, read and save lessons itself. `qualitylayer install` registers them with Claude Code and Codex, and says so when one of them is not installed. Pi and OpenCode reach the same tools through their QualityLayer plugins.
- **What a task learns.** While a task is in Review, QualityLayer saves the answers you gave, the review findings the agent fixed and the plan amendments it made. A lesson from a fix or amendment that did not pass its checks says so. Open the task's **Memory** record in Files to see which lessons each step used and saved.

A lesson text reaches an agent only inside a block marked as saved data, never as an instruction.

## Share lessons through Git

1. In **Manage projects**, turn sharing on for a repository. It starts off, and only you can turn it on.
2. QualityLayer writes lessons backed by recorded checks to `.qualitylayer/memories/`. Prompts, transcripts, credentials and personal preferences stay out.
3. Review and commit those files yourself. QualityLayer never commits or pushes.

Anyone who can read the repository can read its lessons, so keep team-only lessons in a private repository.

## Import Pilot lessons

The Memory tab imports Pilot JSONL exports and Markdown knowledge files into a project you choose. Imported lessons stay private and unchecked. Importing the same file again adds no copies.

## Command line

```sh
qualitylayer memory context "database migration locks" --json
qualitylayer memory store --title "Bound migration locks" --content "Keep the lock timeout short and retry busy migrations." --kind pattern --json
qualitylayer memory read <id> --json
qualitylayer memory import-pilot lessons.jsonl --json
qualitylayer memory share on --json
qualitylayer memory sync --json
```

Run them inside the repository. `sync` exchanges lesson files with the checkout; committing stays with you.
