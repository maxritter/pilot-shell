---
title: Designs
description: Ask your agent to draw a page, open it full size in the App, and point at what should change. Designs stay on your computer.
---

A design is one page your agent draws for you: a screen, a flow, a diagram of how something fits together. You see it full size in the App, comment on a spot, and your agent changes the same page. It works at any step, inside a task or outside one.

![Ask your agent for a design, open its compact entry in Files, comment on a spot and see the same page update; the interactive page stays local](pathname:///img/diagrams/designs-light.svg)
![Ask your agent for a design, open its compact entry in Files, comment on a spot and see the same page update; the interactive page stays local](pathname:///img/diagrams/designs-dark.svg)

## Ask for one

Say it in your own words: "mock up the settings page", or "draw how the seven files map to the App". Your agent writes one self-contained page and the App lists it as a compact entry in **Files**, with what it is for and when it was last updated. A dot marks a design you have not opened yet.

- **In a task**, the page goes into the task's `design/` folder.
- **Outside a task**, it goes into `docs/designs/` and belongs to the whole project.

## Designs in Files {#designs-tab}

![Design entries in Files; choosing one opens its preview](pathname:///img/diagrams/designs-tab-light.svg)
![Design entries in Files; choosing one opens its preview](pathname:///img/diagrams/designs-tab-dark.svg)

The right sidebar's **Files** tab lists only designs owned by the open task, with their open comments. On Home, with no task open, it lists the project's designs. A question about a design shows the relevant preview. Read the design with the complete Plan and approve the Plan from its header; the agent asks a separate design question only when it needs your judgement.

## Open it full size {#full-size}

![A design open full size: one thin bar with Back to the Plan, its name, when it was updated, the status pill, Comment, zoom, Jump to and full screen; a comment pinned to a spot with the agent’s answer; and a quiet notice when the page was updated](pathname:///img/diagrams/design-open-light.svg)
![A design open full size: one thin bar with Back to the Plan, its name, when it was updated, the status pill, Comment, zoom, Jump to and full screen; a comment pinned to a spot with the agent’s answer; and a quiet notice when the page was updated](pathname:///img/diagrams/design-open-dark.svg)

A design takes the whole content area. Its bar shows **Back**, the design's name, when it was updated and the agent's status. Use **Comment** (C) to mark a spot, zoom or **Fit** to see the page, and **Jump to** to find a section. **Full screen** (F) and **Open in browser** give it more room.

**Comment** lets you click a spot and say what should change. The comment shows under the design in the **Comments** tab, with **Jump to the spot**, and reaches your agent like any other comment.

## When it changes

Your agent changes the same page and says in one line what changed. The App shows a quiet notice, "Settings page was updated · Open", and the dot comes back. You always see the latest; there is nothing to compare or pick between.

## Kept on your computer {#never-shared}

The interactive design and its comments stay on your computer, and QualityLayer keeps the design folders out of Git for you. A share link can show a still picture of the design the Plan names, marked as a picture. It cannot open the interactive page.

Your agent can look at its own work too: `qualitylayer design shot` takes a picture of a design. See the [command reference](reference/commands.md#designs).
