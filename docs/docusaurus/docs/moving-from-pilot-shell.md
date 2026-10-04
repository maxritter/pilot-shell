---
title: Moving from Pilot Shell 11
description: What carries over from Pilot Shell 11, what is removed, what stays, and that the move asks nothing.
---

Pilot Shell is now QualityLayer. The move asks you nothing. One step moves a machine over: Pilot Shell's own updater, the App, or the terminal installer. On a machine with a screen you get the App; elsewhere, the command line.

![Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell's own parts are removed; the tools it installed and its memories stay](pathname:///img/diagrams/move-light.svg)
![Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell's own parts are removed; the tools it installed and its memories stay](pathname:///img/diagrams/move-dark.svg)

## What carries over

- **Your licence.** A paid Pilot Shell licence keeps working. A Pilot Shell trial does not carry over; a 7-day QualityLayer trial starts instead.
- **Your plans.** Every task folder in `docs/plans/` stays where it is.
- **Your own settings, skills and files.** Only what Pilot Shell added is touched.

## What is removed

- Pilot Shell's own files in `~/.claude`.
- Its entries in your agent settings, restored from Pilot's own baselines, so your values stay.
- Its block in your shell profile, its Codex parts and its runtime in `~/.pilot`.

## What stays

- **The tools Pilot Shell installed**, such as rtk, semble, codegraph, typescript, prettier or Impeccable. QualityLayer does not need them, and your projects may. The install report lists each one with the command that removes it.
- **Your Pilot Shell memories** (`~/.pilot/memory`). QualityLayer does not use them. To keep what is in them, ask Claude Code or Codex to move them into its own memory.
- **Sessions, logs and configuration** in `~/.pilot`.

To remove what you no longer need, ask Claude Code or Codex.

## What you see

The terminal installer prints three lines once: what happened, what stayed, and that `/spec` is now `/ql` and the Console is the QualityLayer App. Your licence line follows in the install report. After Pilot Shell's updater moved a desktop machine, the App shows the same note on its first open, under "Pilot Shell is now QualityLayer", and goes on to setup or Home when you press **Continue**. It is the same on every path: the terminal, the App and Pilot Shell's updater.

Next: [your first task](first-task.md).
