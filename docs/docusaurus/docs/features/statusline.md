---
sidebar_position: 7
title: Status Line
description: Real-time session dashboard rendered below every Claude Code response — token usage, cost, model, branch, plan status, and savings at a glance.
---

# Status Line

:::warning Claude Code only
The status line is not available with Codex CLI. It uses a Claude Code-specific stdin API that Codex does not support.
:::

Three-line session dashboard rendered below every Claude Code response.

```
Opus 5 [1M] | █████░▓ 60% | 5h: 42% ⇡ 2h | 7d: 18% ⇣ 4d | +120 -38 | main ~5
Spec: my-feature feature [implement] ████░░░░ 3/6
Pilot 8.4.0 (Solo) · CC 2.1.80 (Max) · sessions 2 · memories 12
```

## Line 1 — Session Metrics

| Widget | What it shows |
|--------|---------------|
| **Model** | Active model (`Opus 5 [1M]`, `Sonnet 5`) |
| **Context** | Usage bar + percentage. Green < 80%, Yellow 80–95%, Red 95%+ |
| **5h / 7d usage** | Rate-limit percentage with pacing arrow and reset countdown. Shown on Pro/Max subscriptions. ⇡ = over pace (red), ⇣ = under pace (green) |
| **Lines / Git** | `+added -removed` and branch with staged/unstaged file counts. Shown on every plan (the compact file-changes view). |
| **Cost** | Session cost in USD. Shown on API/Enterprise only — suppressed on subscription plans. |

## Line 2 — Mode

**Quick Mode:** `Quick Mode · /spec for feature implementation and complex bugfixes`

**Spec Mode:** `Spec: my-feature feature [implement] ████░░░░ 3/6 iter:2`

Shows plan name, type (feature/bugfix), phase (plan/implement/verify), task progress bar, and iteration count.

During the **plan** phase (before tasks exist) the detail slot reads `models: auto` / `manual` / `off`, reflecting the Model Switching mode selected in your Console settings.

In `auto` mode it turns red and reads `models: auto ⚠ not-opus` (just `⚠` on a narrow line) when planning is running on something other than Opus. `opusplan` only upgrades the plan leg to Opus while the conversation fits Opus's effective 200K window — past it, Claude Code silently keeps serving Sonnet ([claude-code#65512](https://github.com/anthropics/claude-code/issues/65512), [#74325](https://github.com/anthropics/claude-code/issues/74325)). `/compact` or `/clear` before planning restores Opus; switching Model Switching to **Manual** lets you pick the planning model yourself.

## Line 3 — Version Info

`Pilot <version> (<tier>) · CC <version> (<subscription>) · sessions N · memories N`

## Configuration

Configured automatically during installation in `~/.claude/settings.json` — no manual setup required.
