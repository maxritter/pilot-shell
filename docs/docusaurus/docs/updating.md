---
title: Updates and release notes
description: How the App finds and downloads updates once a day, what the release notes say, how Restart and update works, and how a command-line-only machine updates.
---

![Updating the App: it checks daily and downloads in the background, a line in the sidebar says an update is ready, and Restart and update reopens the App on the same page](pathname:///img/diagrams/update-light.svg)
![Updating the App: it checks daily and downloads in the background, a line in the sidebar says an update is ready, and Restart and update reopens the App on the same page](pathname:///img/diagrams/update-dark.svg)

## With the App

The App updates itself and its command line in one step. You never update them separately.

- **It checks once a day** and downloads the new version in the background. It checks the download against QualityLayer's signature before it shows anything.
- **It tells you quietly.** **Update ready · beta.14** appears above your name in the sidebar, on every page, until you update or choose **Later**. No dialog interrupts a review, and no system notification is sent for an update.
- **You choose when.** Click the line to see what's new and what will happen, then **Restart and update**, or **Later**. Nothing is installed until you choose.
- **You land where you were.** The App closes and opens again on the same page. A line says "Updated to 12.0.0-beta.14. You are back where you were." with **What's new**.

## What's new

The sheet shows the release notes in three groups:

| Group | What it holds |
| --- | --- |
| **New** | What you can do now |
| **Fixed** | What worked wrongly and now works |
| **Good to know** | Changes in behaviour and things to keep in mind |

It also says what will happen: the App closes and opens again on this page; agents keep working, because running commands finish on the old version and the next ones use the new one; skills, hooks and the Claude Code add-on update with it, so there is nothing to set up again. **Full release notes** opens the [changelog](reference/changelog.md).

**Settings › About** shows the same notes for the version you have or the one that is ready, the time of the last check, **Check now**, and an **Earlier releases** fold.

The notes have one source: each release's section of `CHANGELOG.md`. The App, the terminal, the GitHub release and the [changelog](reference/changelog.md) here all show the same words.

## While agents run

- **On macOS and Linux**, agent commands that are running finish on the old version, and new ones wait a few seconds while the App is replaced.
- **On Windows** a running command keeps its program file, so the update waits for running agent commands. The sheet says "Waiting for 2 agent commands to finish" and checks every 30 seconds. Nothing is stopped, and you can keep using the App. **Cancel the update** if you change your mind.

## If an update does not finish

If the download cannot be checked against QualityLayer's signature, nothing is changed and you keep the version you have. The sheet says so and offers **Try again** or **Download from qualitylayer.dev**.

## Command line only

On WSL2, a dev container or a server, update from the terminal:

```bash
qualitylayer update
```

It prints the same notes, grouped as New, Fixed and Good to know, then "Updated. Running agent commands finish on the old version; the next ones use the new." On a machine with the App, `qualitylayer update` hands over to the App's own updater. The browser App on a command-line-only machine shows the same sidebar line, with the command to run.

## Pilot Shell 11

Pilot Shell 11's own updater moves the machine to QualityLayer by the [install rule](install.md): the App on a machine with a screen, the command line elsewhere. See [Moving from Pilot Shell 11](moving-from-pilot-shell.md).
