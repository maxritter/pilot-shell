---
title: Designs
description: Create screen mockups, wireframes and diagrams with your agent, keep the ones every task builds on, and review, edit and share them in QualityLayer.
---

A design is an HTML page, or a folder of pages that clicks through like an app. A **draft** belongs to one task. A **lasting design** belongs to the project: every task starts from it and leaves it matching what shipped.

![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-light.svg)
![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-dark.svg)

## Create a design

Ask your agent, for example: "Show two layouts for the settings page." The design appears in **Files**.

| Made | Saved in |
| --- | --- |
| In a task | The task's `design/` folder |
| For the project | `.qualitylayer/designs/<name>/` in the repository |
| On this computer only | `docs/designs/`, out of git |

From the terminal:

```sh
qualitylayer design guide
qualitylayer design new settings --project
qualitylayer design show settings --project
```

All commands: [CLI reference](reference/commands.md#designs).

## The Designs place {#designs-place}

![The design Library: compact rows grouped by project, collapsible groups, search and sort, with previews opened on demand and Archived beside Library](pathname:///img/app/designs-light.webp)
![The design Library: compact rows grouped by project, collapsible groups, search and sort, with previews opened on demand and Archived beside Library](pathname:///img/app/designs-dark.webp)

**Designs** in the sidebar opens the reusable **Library**. Fold a project, search names and pages, or choose a project and sort order. Large groups reveal more rows as you need them; a preview loads when you open it. **New design** starts a reusable design. Working drafts stay in their task's **Files**, where their base design and the pages being changed are visible.

The row menu and full viewer offer rename, copy, show in another project, archive and delete. Renaming keeps existing links. A cross-project copy is independent; **Also show** adds a listing of the same original, and **Stop showing** removes that listing. **Archived** holds archived designs and a folded **Recently deleted** section for Restore. Deleting a source-backed entry keeps its application files.

## A lasting design open {#lasting}

![A reusable design open: page tabs, a return to the Library, a management menu and New task on this design, with current work and history in its sidebar](pathname:///img/app/designs-open-light.webp)
![A reusable design open: page tabs, a return to the Library, a management menu and New task on this design, with current work and history in its sidebar](pathname:///img/app/designs-open-dark.webp)

| Tab | What it holds |
| --- | --- |
| **Activity** | Open tasks changing the design, then every past change |
| **Comments** | Comment threads per page |
| **Details** | Its pages, where its files are, and any external reference you kept |

## A design of many pages {#folders}

A folder design is interactive: buttons, menus and links between pages work, and React with JSX is provided. Nothing loads from the network. Start one with `qualitylayer design new <name> --folder`.

## Draft on a lasting design {#draft-on}

Your agent changes a lasting design by drafting on it in the task:

```sh
qualitylayer design new <name> --on <design>[/<page>]
```

The lasting design stays as it is until you fold the draft in at Review. A draft's menu (right-click or **…**) also offers **Keep as a lasting design…**, **Compare with …** and **Share with the team**.

## Keep as a lasting design {#keep}

Choose **Keep as a lasting design…** on a draft, or run `qualitylayer design keep <name>`.

| Where it lives | Saved in | Who sees it |
| --- | --- | --- |
| **In the repository** | `.qualitylayer/designs/<name>/` | Anyone who can read the repository. It goes into pull requests like code |
| **Only on this computer** | `docs/designs/` | Only you; git does not see it |

## Fold in at Review {#fold-in}

When a task drafted on a lasting design, Review shows a card such as **This task changes App Model**.

1. Uncheck pages to leave out. **Compare** shows the lasting page beside the draft.
2. Click **Fold 3 pages in**. The pages become one revision, in the task's pull request.

If the lasting design changed since the draft began, the card asks you to compare first, then offers **Fold anyway**.

## Link a Claude Design file {#claude-design}

A lasting design can store its Claude Design link for **Open in Claude Design**. QualityLayer keeps only the link and does not sync changes.

## Review and comment {#full-size}

![A design open full size: Back to the Plan, the design's name and update time, Comment, zoom, Light and Dark, Desktop and Phone, Jump to and full screen; the Comments tab lists numbered spots with the agent's answers](pathname:///img/app/design-light.webp)
![A design open full size: Back to the Plan, the design's name and update time, Comment, zoom, Light and Dark, Desktop and Phone, Jump to and full screen; the Comments tab lists numbered spots with the agent's answers](pathname:///img/app/design-dark.webp)

*Example design in a fictional project.*

Press **C** (**Comment**), click a spot and say what should change. Your agent edits the page and answers in the thread. The toolbar also switches **Light**, **Dark**, **Desktop** and **Phone**; **F** goes full screen.

## Compare, edit and restore

**Open design canvas** shows artboards side by side. **Details** edits the HTML, renames, duplicates or restores a revision. Agents use `design inspect`, `push`, `pull` and `history`; a push cannot overwrite a newer version.

## Share a preview {#never-shared}

Designs stay on your computer until you choose **Share › Include designs** for a task. They then join its encrypted shared copy or link as previews that run no scripts; readers comment but cannot edit. Lasting designs in the repository travel with your pull requests instead.
