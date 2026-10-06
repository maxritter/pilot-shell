---
title: Designs
description: Ask your agent to draw a page, open it full size in the App, and point at what should change. Designs stay on your computer.
---

A design is one page your agent draws for you: a screen, a flow, a diagram of how something fits together. You see it full size in the App, comment on a spot, and your agent changes the same page. It works at any step, inside a task or outside one.

![What a design is: you ask your agent, it draws one HTML page in your project, the App lists it under Designs; you open it full size and comment on a spot, the agent changes the same page and the App shows the update; a design is never shared](pathname:///img/diagrams/designs-light.svg)
![What a design is: you ask your agent, it draws one HTML page in your project, the App lists it under Designs; you open it full size and comment on a spot, the agent changes the same page and the App shows the update; a design is never shared](pathname:///img/diagrams/designs-dark.svg)

## Ask for one

Say it in your own words: "mock up the settings page", or "draw how the five files map to the App". Your agent writes one self-contained page and the App lists it under **Designs**, with what it is for and when it was last updated. A dot marks a design you have not opened yet.

- **In a task**, the page goes into the task's `design/` folder.
- **Outside a task**, it goes into `docs/designs/` and belongs to the whole project.

## The Designs tab {#designs-tab}

![A step shows the design its Plan names as a preview with Open full size; the Designs tab of the right sidebar lists this task’s designs and the project’s; designs are only on this computer and never shared](pathname:///img/diagrams/designs-tab-light.svg)
![A step shows the design its Plan names as a preview with Open full size; the Designs tab of the right sidebar lists this task’s designs and the project’s; designs are only on this computer and never shared](pathname:///img/diagrams/designs-tab-dark.svg)

The right sidebar's **Designs** tab holds them in two groups, **This task** and **In this project**, each with its open comments. On Home, with no task open, it shows the project's designs. When the Plan is about a design, its Interface section shows a preview with **Open full size**, and the review asks you whether it looks right.

## Open it full size {#full-size}

![A design open full size: one thin bar with Back to the Plan, its name, when it was updated, the status pill, Comment, zoom, Jump to and full screen; a comment pinned to a spot with the agent’s answer; and a quiet notice when the page was updated](pathname:///img/diagrams/design-open-light.svg)
![A design open full size: one thin bar with Back to the Plan, its name, when it was updated, the status pill, Comment, zoom, Jump to and full screen; a comment pinned to a spot with the agent’s answer; and a quiet notice when the page was updated](pathname:///img/diagrams/design-open-dark.svg)

A design takes the whole content area under one thin bar: **Back**, its name and when it was updated, the status pill, **Comment** (C), zoom and **Fit**, **Jump to** a section of the page, **Full screen** (F) and **Open in browser**.

**Comment** lets you click a spot and say what should change. The comment shows under the design in the **Comments** tab, with **Jump to the spot**, and reaches your agent like any other comment.

## When it changes

Your agent changes the same page and says in one line what changed. The App shows a quiet notice, "Settings page was updated · Open", and the dot comes back. You always see the latest; there is nothing to compare or pick between.

## Never shared {#never-shared}

A design stays on your computer. It is never on a share link, on qualitylayer.dev or in a pull request, and QualityLayer keeps the design folders out of Git for you. A share link shows only a still picture of the design the Plan names, marked as a picture.

Your agent can look at its own work too: `qualitylayer design shot` takes a picture of a design. See the [command reference](reference/commands.md#designs).
