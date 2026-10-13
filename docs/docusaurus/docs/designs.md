---
title: Designs
description: Create screen mockups, wireframes and diagrams with your agent, keep the ones every task builds on, and review, edit and share them in QualityLayer.
---

A design is an HTML page you review with your coding agent in QualityLayer, or a folder of pages that clicks through like an app. Use one to try a screen layout, compare alternatives or explain a flow. A design made for one task is a **draft**. One you keep for the whole project is a **lasting design**: every later task starts from it and leaves it matching what shipped.

![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-light.svg)
![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-dark.svg)

## Create a design

Ask your agent to mock up a screen or draw a flow, for example: "Show two layouts for the settings page." It writes a self-contained page with local styles and images. The App lists it in **Files**; a dot marks one you have not opened.

| Asked | Saved in | Listed |
| --- | --- | --- |
| In a task | The task's `design/` folder | **Files** of that task, with its open comments, and in the [Designs place](#designs-place) under **Drafts in open tasks** |
| Kept for the project | `.qualitylayer/designs/<name>/` in the repository | The Designs place, and **Files** of every task in the project |
| Outside a task, or kept only on this Mac | `docs/designs/`, out of git | The Designs place, under **On this Mac** |

At the **Product** level, Discuss also draws a grey wireframe of each screen that changes, and two side by side when you have a layout to choose. The Plan's finished design is a separate page, approved with the Plan.

To start a project design from the terminal:

```sh
qualitylayer design guide
qualitylayer design new settings --project
qualitylayer design show settings --project
```

`new` creates the page for you or your agent to edit. `show` tells the App to display its latest version. The [CLI reference](reference/commands.md#designs) covers the full command list.

## The Designs place {#designs-place}

**Designs** sits in the sidebar after Home and Team. It lists every project's designs, grouped like the sidebar: the same order, tiles and names.

| Control | What it does |
| --- | --- |
| **Show** | **Everything**, **Lasting**, or **Drafts in tasks** |
| **Thumbnails**, **List** | Cards with a picture, or one line each. Your choice is remembered |
| Find | Filters by design or project name |
| **New design** | Starts a lasting design in a project you pick, with a name and what it shows |

Each lasting design shows its name, what it shows, its pages, when it last changed and which task changed it. **Changing in 2 open tasks** names the tasks that are drawing on it now, each with its status mark. Under the lasting designs, **Drafts in open tasks** lists the task, the draft's name, what it drafts on, the task's step and **Open**. Drafts of shipped tasks drop out. A design you made before and kept only on this Mac sits under **On this Mac**.

## A lasting design open {#lasting}

Open a lasting design to see it full size. A design of several pages has a tab for each; a dot marks a page that an open task is changing. **Comment** works as on any design, per page. The right sidebar has three tabs:

| Tab | What it holds |
| --- | --- |
| **Activity** | The open tasks changing the design and which pages, then every change from its history, named after the task when a task made it |
| **Comments** | The comment threads on the page |
| **Details** | What it shows, its pages, where its files are, its Claude Design link and the other projects that list it |

**Open in Claude Design** appears when the design has a link. **New task on this design** starts a task with the design in mind.

## A design of many pages {#folders}

A design can be a folder: pages, scripts, styles, fonts and pictures. It opens interactive, so a design made like the App itself behaves like it. Buttons, menus and screen changes work, and a link to another page of the same design switches the page. Scripts can use JSX, and React is provided. Nothing loads from the network. The page keeps no storage between visits, so state lives only while it is open.

Your agent starts a folder with `qualitylayer design new <name> --folder` and adds pages as more `.html` files beside the first. Comments and thumbnails work per page.

## Draft on a lasting design {#draft-on}

In a task, **Files** shows the task's drafts. A draft of a lasting design says what it drafts on, such as "Draft on App Model › Sidebar". Below the drafts, a **Lasting designs** group named after the project lists its lasting designs, with **All designs** to open the Designs place.

Your agent reads the lasting design a change touches and drafts on it: `qualitylayer design new <name> --on <design>[/<page>]` copies the design, or one page, into the task and remembers where it came from. The lasting design itself does not change until you fold the draft in at Review. You can start a draft yourself with **Draft on it in this task** from a lasting design's menu.

Right-click a draft, or use its **…**, for **Open**, **Keep as a lasting design…**, **Add as a page of …**, **Compare with …**, **Rename…**, **Copy path**, **Share with the team** and **Delete…**. On a lasting design, the menu offers **Open**, **Draft on it in this task** and, when it has a link, **Open in Claude Design**.

## Keep as a lasting design {#keep}

Choose **Keep as a lasting design…** on a draft. The dialog asks for:

| Field | What it decides |
| --- | --- |
| **Name** and **What it shows** | How the design is listed |
| **Project** | The task's project. **Also show in another project** lists it under others too, on this computer |
| **Where it lives** | **In the repository**, or **Only on this Mac** |
| **Claude Design link** | Optional. Available for a design in the repository |

**In the repository** saves it in `.qualitylayer/designs/<name>/`. It goes into your pull requests like code, and every worktree and teammate sees the same pages. Anyone who can read the repository can read the design, so the dialog says so before you keep it. **Only on this Mac** saves it in `docs/designs/`, which git does not see. The draft in your task stays as it is.

Your agent does the same with `qualitylayer design keep <name>`.

## Fold in at Review {#fold-in}

When a task has drafts on a lasting design, its Review page shows a card, **This task changes App Model**. Each page the drafts changed has a row with a check, its name, **Changed** or **New page**, and the page before and after. Uncheck a page to leave it out.

The card warns you before it folds when:

- the lasting design changed since the draft began;
- a page the draft uses was removed from, or added to, the lasting design;
- another open task changes the same page. Whichever task ships second compares its page first.

**Compare** shows a page as the lasting design has it beside the draft's. **Not now** closes the card. **Fold 3 pages in** writes the checked pages into the lasting design as one revision named after the task, and they go into the task's commits and its pull request. When a page changed in the lasting design since the draft began, the first click folds nothing; the card asks you to compare, and the button then reads **Fold anyway**. If the lasting design is gone, the card offers to keep the draft as a new lasting design.

## Link a Claude Design file {#claude-design}

A lasting design can record the link of its Claude Design file. **Open in Claude Design** then opens it from the design, its menu and its Details. QualityLayer only keeps the link. It does not copy changes between the two.

## Review and comment {#full-size}

![A design open full size: Back to the Plan, the design's name and update time, Comment, zoom, Light and Dark, Desktop and Phone, Jump to and full screen; the Comments tab lists numbered spots with the agent's answers](pathname:///img/app/design-light.webp)
![A design open full size: Back to the Plan, the design's name and update time, Comment, zoom, Light and Dark, Desktop and Phone, Jump to and full screen; the Comments tab lists numbered spots with the agent's answers](pathname:///img/app/design-dark.webp)

*Example design in a fictional project.*

Open the design's compact entry in **Files** to give it the whole content area. Its toolbar lets you change the view:

| Control | What it does |
| --- | --- |
| **Comment** (C) | Click a spot and say what should change |
| Zoom, **Fit** | Size the page |
| **Light**, **Dark**, **Desktop**, **Phone** | Switch how the page shows |
| **Jump to** | Find a section of the design |
| **Full screen** (F), **Open in browser** | Give it more room |

A pinned comment appears in **Comments** with **Jump to the spot**. Your agent reads it, edits the same page and answers in the thread. The App shows when the design changes.

## Compare, edit and restore

Choose **Open design canvas** to compare artboards side by side. Search by name, choose which to show, then zoom or pan around them.

Open **Details** to edit the HTML source, change the title, duplicate or rename a design, or restore a saved revision. A failed save keeps your edits. If someone else has changed the same design, QualityLayer asks you to reload before saving over it.

Agents can use `design inspect`, `push`, `pull` and `history` for the same work. Updates require the revision returned by `inspect`, so an agent cannot silently overwrite a newer version.

## Share a preview {#never-shared}

Designs stay on your computer until you choose **Share › Include designs** for a task. This adds them to that task's encrypted Team copy or external link, with the same access as its documents. Lasting designs kept in the repository travel with your pull requests instead. Designs on this Mac in `docs/designs/` are separate from the task's shared copy.

Shared previews disable scripts and navigation. Readers can comment or request improvements; they cannot edit your local source. Turning **Include designs** off removes the designs from existing shared copies.

For agent authoring, start with `qualitylayer design guide` and `qualitylayer design context`. Use `design check` for source checks and `design shot` to inspect the rendered page.
