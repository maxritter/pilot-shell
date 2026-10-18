---
title: Project memory
description: Save project lessons, reuse them in later sessions and choose what travels through Git.
---

# Project memory

Keep decisions, fixes and constraints for later work. Your agents can search these lessons instead of rediscovering them.

<figure class="memory-flow" aria-label="How a saved lesson reaches an agent">
  <ol>
    <li><strong>Save a lesson</strong><span>A task or agent records something worth reusing.</span></li>
    <li><strong>Find it locally</strong><span>Search matches words and meaning in your project.</span></li>
    <li><strong>Use it in context</strong><span>Your agent receives the relevant lesson text.</span></li>
  </ol>
  <figcaption>Example lesson: “Keep database migrations short and retry busy locks.”</figcaption>
</figure>

## What your agents get

| How | What happens |
| --- | --- |
| **Session lessons** | With the installed hooks or plugins enabled, Claude Code, Codex, Pi and OpenCode can receive pinned lessons and matches for the first message in a repository. The block is at most 3 KiB. |
| **After compaction** | A supported client’s compaction hook can restore that lesson block. If hooks are disabled, unavailable or too slow, automatic delivery can be skipped. |
| **Search and save tools** | `memory_search`, `memory_read` and `memory_save` let an agent choose what to retrieve or save. Install registers the tools with Claude Code and Codex; Pi and OpenCode expose them through their plugins. Other agents use the [CLI](#command-line). |
| **Task lessons** | In Review, QualityLayer records decisions, fixed findings and plan amendments. Evidence stays with a lesson when available; missing or failed checks do not become passing evidence. A task’s **Memory** record in Files shows what each step used and saved. |

Lesson text is labelled as saved reference data. It does not replace your request or the agent’s instructions.

A specific lookup can return no results when nearby lessons do not fit the combined topic. Try concrete code terms or a shorter phrase. In JSON, `semantic: full` reports meaning-search index coverage. Read a returned lesson against the current code before using it.

## Manage your lessons

Open **Settings → Memory**.

| To | Use |
| --- | --- |
| Find a saved lesson | Search by a phrase or by what you need to do |
| Keep a lesson in session context | Open it and enable **Pin to every session**; up to five pins per project |
| Stop using an outdated lesson | **Retire**; its history stays available |
| Stop automatic session lessons | Turn off **Lessons in every session** |
| Pause capture and retrieval | Pause local memory; saved lessons stay |
| Choose repositories for Git exchange | **Manage projects** |

<details>
<summary>See Memory settings</summary>

![Memory settings with project sharing and saved lessons; illustrative project data](pathname:///img/app/memory-light.webp)
![Memory settings with project sharing and saved lessons; illustrative project data](pathname:///img/app/memory-dark.webp)

</details>

## What stays local

| Part | Where the text goes |
| --- | --- |
| **Storage and search** | Lessons and the search model stay on your computer. The bundled model finds meaning locally, without sending lessons to an embedding service. |
| **Your coding agent** | Lessons supplied to an agent become part of its context. A cloud-based agent may send that context to its provider under its own settings and terms. |
| **Git sharing** | Only repositories where you enable sharing exchange lesson files. This is separate from encrypted task sharing. |

## Share lessons through Git

1. Open **Manage projects** and turn sharing on for a repository. It starts off; the choice is local to this computer.
2. QualityLayer writes **eligible project lessons** to `.qualitylayer/memories/`. They can include lessons without recorded passing checks; available evidence stays attached.
3. Review the files, then commit and push them through your normal Git process. Memory exchange itself never commits or pushes.

Pilot imports and preference lessons stay private. A publication filter checks for credential patterns, email addresses, home paths, prompts and transcripts. Review the files before sharing: filtering is not a guarantee that a lesson contains no sensitive information.

Anyone who can read the repository can read these lesson files. Turning sharing off stops exchange; it does not erase files already committed.

## Import Pilot lessons

The Memory tab imports Pilot JSONL exports and Markdown knowledge files into a project you choose. Imported lessons stay private and unchecked. Importing the same file again adds no copies.

## Command line

Run project commands inside the repository. Any agent that can run shell commands can use them.

<details>
<summary>Search, save, pin and sync from your terminal</summary>

```sh
qualitylayer memory context "database migration locks" --json
qualitylayer memory store --title "Bound migration locks" --content "Keep migration locks short and retry busy migrations." --kind pattern --json
qualitylayer memory read <id> --json
qualitylayer memory pin <id> --json
qualitylayer memory import-pilot lessons.jsonl --json
qualitylayer memory share on --json
qualitylayer memory sync --json
```

`sync` exchanges lesson files with the checkout. See the [full command reference](reference/commands.md#memory) for search, retirement, imports and sharing controls.

</details>
