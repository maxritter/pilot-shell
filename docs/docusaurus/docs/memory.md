---
title: Project memory
description: Reuse project lessons across agents and choose which repositories share them through Git.
---

# Project memory

:::info Next release
Project memory is being implemented on the development branch. It is not included in the current download.
:::

![Memory settings with project sharing and a searchable lesson list. The example project data is illustrative.](/img/app/memory-light.webp)

QualityLayer keeps useful project lessons between tasks. Claude Code and Codex can read the same local lessons: decisions, fixes and constraints worth remembering.

Open **Settings → Memory** to see your lessons, search them or pause memory. Settings applies to every project on this computer. **Manage projects** lets you find a repository and change its sharing setting without scrolling through every project.

The memory engine comes inside the QualityLayer command line used by the App and shell installer. It runs locally when needed. Search and storage need no additional API key, hosted service or runtime installation; your existing agent writes and uses the lessons.

## Share lessons through Git

Sharing starts off for each repository. Enable it for the repositories where you want your project lessons to travel with the code. This choice belongs to you on this computer; another person's Git changes cannot enable it for you.

QualityLayer writes eligible lessons under `.qualitylayer/memories/`. Review and commit those files with your normal Git workflow. QualityLayer imports shared changes before retrieving lessons. It does not make hidden commits or push them for you.

Only project lessons supported by recorded QualityLayer checks can be published. Personal preferences, prompts, transcripts, credentials and home-directory paths are excluded. Imported lessons carry their source and remain historical evidence: the agent must check them against the current code and approved plan.

Retire a lesson when it no longer applies. Retirement is recorded explicitly, so an older import cannot bring it back. Git retains earlier committed versions in its history.

## Keep native agent memories

Your Claude Code and Codex memory settings stay as you configured them. QualityLayer adds project lessons that both agents can query. It does not copy native memory stores back and forth or change required instructions in `AGENTS.md` or `CLAUDE.md`.

## Import Pilot lessons

The Memory tab accepts Pilot schema-v1 JSONL exports and Markdown knowledge files. Choose the destination project before importing. Repeating an import keeps the same lesson identity; malformed or unsupported records are reported.

Imported Pilot lessons stay private and unverified. They do not become team lessons merely because they were imported. The importer leaves the original files unchanged.

Markdown with an explicit lesson ID or a CLI concept path can update the same imported lesson. Browser files without a directory path use their content as identity: importing identical content again is skipped, while an edited file becomes a separate lesson. This preserves different documents that happen to share a filename.

## Use the command line

Agents use the same service as the App:

```sh
qualitylayer memory context "database migration locks" --json
qualitylayer memory store --title "Bound migration locks" --content "Keep the lock timeout short and retry busy migrations." --kind pattern --json
qualitylayer memory read <id> --json
qualitylayer memory import-pilot lessons.jsonl --json
qualitylayer memory share on --json
qualitylayer memory sync --json
```

Run project commands inside the repository. `share on` changes your local consent; `sync` exchanges eligible files with the checkout and leaves committing and pushing to you. `pause` stops capture and task retrieval while keeping your saved lessons available to browse.

## Engine updates

QualityLayer pins the engine and checks its bytes before running it. It never downloads an engine update in the background. Reviewed engine updates ship with a QualityLayer update, and ordinary updates preserve your lessons.
