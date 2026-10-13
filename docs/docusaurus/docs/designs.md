---
title: Designs
description: Create screen mockups, wireframes and diagrams with your agent. Review, edit and share them in QualityLayer.
---

A design is an HTML page you review with your coding agent in QualityLayer. Use one to try a screen layout, compare alternatives or explain a flow. You can work on designs during a task or keep them with the project.

![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-light.svg)
![Ask your agent for a design, open its compact entry in Files and comment on a spot. Designs stay local until you include them in an encrypted shared task](pathname:///img/diagrams/designs-dark.svg)

## Create a design

Ask your agent to mock up a screen or draw a flow, for example: "Show two layouts for the settings page." It writes a self-contained page with local styles and images. The App lists it in **Files**; a dot marks one you have not opened.

| Asked | Saved in | Listed |
| --- | --- | --- |
| In a task | The task's `design/` folder | **Files** of that task, with its open comments |
| Outside a task | `docs/designs/` | **Files** on Home |

At the **Product** level, Discuss also draws a grey wireframe of each screen that changes, and two side by side when you have a layout to choose. The Plan's finished design is a separate page, approved with the Plan.

To start a project design from the terminal:

```sh
qualitylayer design guide
qualitylayer design new settings --project
qualitylayer design show settings --project
```

`new` creates the page for you or your agent to edit. `show` tells the App to display its latest version. The [CLI reference](reference/commands.md#designs) covers the full command list.

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

Designs stay on your computer until you choose **Share › Include designs** for a task. This adds them to that task's encrypted Team copy or external link, with the same access as its documents. Project designs in `docs/designs/` are separate from the task's shared copy.

Shared previews disable scripts and navigation. Readers can comment or request improvements; they cannot edit your local source. Turning **Include designs** off removes the designs from existing shared copies.

For agent authoring, start with `qualitylayer design guide` and `qualitylayer design context`. Use `design check` for source checks and `design shot` to inspect the rendered page.
