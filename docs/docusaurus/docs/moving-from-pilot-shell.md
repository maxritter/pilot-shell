---
title: Moving from Pilot Shell 11
description: What carries over from Pilot Shell 11, what is removed, and the two choices you make.
---

Pilot Shell is now QualityLayer. One step moves a machine over: Pilot Shell's own updater, the App, or the terminal installer. On a machine with a screen you get the App; elsewhere, the command line.

![Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell's own parts are removed; you choose about the tools it installed and its memories](pathname:///img/diagrams/move-light.svg)
![Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell's own parts are removed; you choose about the tools it installed and its memories](pathname:///img/diagrams/move-dark.svg)

## What carries over

- **Your licence.** A paid Pilot Shell licence keeps working. A Pilot Shell trial does not carry over; a 7-day QualityLayer trial starts instead.
- **Your plans.** Every task folder in `docs/plans/` stays where it is.
- **Your own settings, skills and files.** Only what Pilot Shell added is touched.

## What is removed

- Pilot Shell's own files in `~/.claude`.
- Its entries in your agent settings, restored from Pilot's own baselines, so your values stay.
- Its block in your shell profile, its Codex parts and its runtime in `~/.pilot`.

In a terminal you confirm this list first, or nothing is changed.

## What you choose

1. **Which tools Pilot Shell installed should go.** Only the tools Pilot recorded as its own are listed, and you tick the ones to remove. rtk, semble and codegraph start ticked: our benchmarks show today's models gain nothing from them. General tools such as typescript, prettier or ruff, and design tools such as Impeccable, start unticked, because your projects may use them. A tool you leave unticked stays installed and is yours.
2. **Whether to delete your Pilot Shell memories** (`~/.pilot/memory`). QualityLayer does not use them, and the answer is no unless you say otherwise. To keep what is in them, ask Claude Code or Codex to move them into its own memory first. Sessions, logs and configuration in `~/.pilot` stay either way.

The terminal installer asks both questions. After Pilot Shell's updater moved a desktop machine, the App asks them on its first open, under "Pilot Shell is now QualityLayer". Pilot Shell's updater itself asks nothing: Pilot's own parts go, and every tool and memory stays until you choose.

Next: [your first task](first-task.md).
