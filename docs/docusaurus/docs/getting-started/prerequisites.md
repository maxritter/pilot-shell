---
sidebar_position: 1
title: Prerequisites
description: What you need before installing Pilot Shell
---

# Prerequisites

What you need before installing Pilot Shell.

## Claude Code

Install [Claude Code](https://code.claude.com/docs/en/quickstart) using the **native installer** before setting up Pilot Shell. If you have the `npm` or `brew` version installed, uninstall it first. If no Claude Code installation is detected, the Pilot installer will attempt to set it up for you.

## Claude Subscription

Pilot enhances Claude Code — it doesn't replace it. You need an active Claude subscription. Solo developers, teams, and enterprise organizations are all supported.

| Plan | Audience | Notes |
|------|----------|-------|
| **Max 5x** | Solo — moderate usage | Good for part-time or focused coding sessions |
| **Max 20x** | Solo — heavy usage | Recommended for full-time AI-assisted development |
| **Team Premium** | Teams | 6.25x usage per member + SSO, admin tools, billing management |
| **Enterprise** | Companies | For organizations with compliance, procurement, or security requirements |

## Codex Plugin (Included)

The [Codex plugin](https://github.com/openai/codex-plugin-cc) is installed automatically with Pilot. It provides adversarial code review powered by OpenAI Codex — an independent second opinion during `/spec` planning and verification phases.

**Setup:** Run `/codex:setup` once to authenticate with your OpenAI account, then enable the reviewers in Console Settings → Reviewers. Pilot auto-detects the plugin — Codex reviewer toggles appear grayed out until setup is complete.

A [ChatGPT Plus](https://chatgpt.com/#pricing) subscription ($20/mo) covers the Codex API usage needed for code reviews.

## System Requirements

Pilot installs once and works across all your projects. Each project can have its own `.claude/` rules and skills.

| Platform | Notes |
|----------|-------|
| **macOS** | 10.15 Catalina or later, Apple Silicon and Intel |
| **Linux** | Debian, Ubuntu, RHEL-based distros, and most others |
| **Windows** | WSL2 required — native Windows not supported |

:::tip Windows users
Install WSL2 first (`wsl --install -d Ubuntu`), then run the installer inside Ubuntu.
:::
