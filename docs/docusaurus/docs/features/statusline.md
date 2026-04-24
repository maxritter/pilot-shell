---
sidebar_position: 7
title: Status Line
description: Real-time session dashboard rendered below every Claude Code response
---

# Status Line

Real-time session dashboard rendered below every Claude Code response.

Pilot Shell replaces the default Claude Code status line with a rich, three-line display. It receives JSON from Claude Code via stdin and renders model info, context usage, git state, costs, usage limits, spec progress, and version info — all color-coded and updated after every response.

## Layout

The status line has three lines:

**Subscription users** (Pro / Max — Claude Code emits `rate_limits` on stdin):
```
Line 1: Opus 4.7 [1M] | █████░▓ 60% | 5h: 42% ⇡ 2h | 7d: 18% ⇣ 4d | Savings: 65%
Line 2: Spec: my-feature feature [implement] ████░░░░ 3/6
Line 3: Pilot 8.2.1 (Solo) · CC 2.1.80 (Max) · sessions 2 · memories 12
```

**API / Enterprise users** (no `rate_limits` in stdin):
```
Line 1: Opus 4.7 [1M] | █████░▓ 60% | +156 -23 | main +2 ~3 | $1.45 | Savings: 65%
Line 2: Spec: my-feature feature [implement] ████░░░░ 3/6
Line 3: Pilot 8.2.1 (Solo) · CC 2.1.80 · sessions 2 · memories 12
```

The layout is symmetric: slots 3 and 4 swap between `5h | 7d` and `lines | git` based on what Claude Code provides on stdin. Cost is shown only for API / Enterprise users — on Pro / Max the subscription covers usage, so a dollar figure is noise and is suppressed. Savings always anchors the right side.

### Line 1 — Session Metrics

Widgets separated by `|`, from left to right:

| Widget | Description | Color coding |
|--------|-------------|--------------|
| **Model** | Active model in short form (`Opus 4.7 [1M]`, `Sonnet 4.6`). Legacy / pinned IDs such as `claude-opus-4-6`, `claude-sonnet-4-5-20250929`, or retired `claude-3-*` variants resolve to friendly labels (`Opus 4.6`, `Sonnet 4.5`, `Sonnet 3.7`, …). Unknown IDs display verbatim. | Cyan |
| **Context** | Effective context usage with progress bar and buffer indicator (`▓`). The session percentage alone is sufficient — no raw token count is shown. | Green < 80%, Yellow 80–95%, Red 95%+ |
| **Lines changed** | Session lines added/removed (`+156 -23`). Hidden when `rate_limits` is present. | Green for added, Red for removed |
| **Git** | Branch name with staged (`+N`) and unstaged (`~N`) counts. Shows worktree branch with `wt` suffix when in a spec worktree. Hidden when `rate_limits` is present. | Magenta branch, Green staged, Yellow unstaged |
| **Cost** | Session cost in USD. Hidden when `rate_limits` is present — on Pro / Max the subscription covers API usage, so the dollar figure is noise. | Green < $1, Yellow $1–5, Red $5+ |
| **5h usage** | 5-hour usage percentage with pacing arrow and reset countdown (`5h: 42% ⇡ 2h`). See pacing rules below. Only shown when `rate_limits` is available. | Green < 70%, Yellow 70–90%, Red 90%+ |
| **7d usage** | 7-day usage percentage with pacing arrow and reset countdown (`7d: 18% ⇣ 4d`). Only shown when `rate_limits` is available. | Same as 5h |
| **Savings** | Token savings percentage from RTK proxy (`Savings: N%`). Always shown when RTK has data, regardless of whether usage info is present. | Cyan |

:::info Usage Limits — Cross-Platform
Claude Code 2.1.80+ emits `rate_limits` directly on stdin for **subscription plans** (Pro / Max). Pilot reads these values with no network calls, no OAuth credentials, and no platform restrictions — it works identically on macOS, Linux, and Windows.

**API / Enterprise users** do not receive `rate_limits`, so the status line falls back to showing lines-changed, git branch, and RTK savings instead. No configuration needed — the display adapts automatically to whatever data Claude Code provides.
:::

#### Pacing Arrow

When a usage widget is shown, Pilot compares the used percentage to the *expected* percentage based on how much of the window has elapsed:

- **⇡** (red) — burning quota **faster** than the clock. On track to hit the limit before reset.
- **⇣** (green) — burning quota **slower** than the clock. Surplus budget available.
- *(no arrow)* — within ±3 percentage points of linear pace. On schedule.

Example: 150 minutes into the 5-hour window (half elapsed), used is 90% → `5h: 90% ⇡ 2h 30m` — clearly over pace and heading for the limit. Used 5% in the same situation → `5h: 5% ⇣ 2h 30m` — well under pace.

### Line 2 — Mode

**Quick Mode** (no active spec):
```
Quick Mode · /spec for feature implementation and complex bugfixes
```

**Spec Mode** (active `/spec` plan):
```
Spec: my-feature feature [implement] ████░░░░ 3/6 iter:2
```

| Field | Description |
|-------|-------------|
| **Name** | Plan name (date prefix stripped) |
| **Type** | `feature` (cyan) or `bugfix` (yellow) |
| **Phase** | `plan` (blue), `implement` (yellow), or `verify` (cyan) |
| **Progress bar** | Visual task completion (filled █ / empty ░) |
| **Count** | Completed/total tasks |
| **Iterations** | `iter:N` shown when verification has looped back (N > 0) |

### Line 3 — Version & Session Info

```
Pilot 8.2.1 (Solo) · CC 2.1.79 (Max) · sessions 2 · memories 12
```

| Field | Description |
|-------|-------------|
| **Pilot version** | Pilot Shell version with license tier in parentheses: `Solo` (green), `Team` (cyan), `Trial 5d` (yellow), or `pilot-shell.com/#pricing` (dim) |
| **CC version** | Claude Code version with subscription type in parentheses: `Max`, `Pro`, `Team`, `Enterprise`. Detected via `claude auth status` (cached 24h) |
| **Sessions** | Number of active Pilot Shell sessions |
| **Memories** | Observations saved to Pilot Console memory during this session (only shown when > 0) |

## Effective Context Display

Claude Code reserves ~16.5% of the context window as a compaction buffer, triggering auto-compaction at ~83.5% raw usage. Pilot rescales this to an **effective 0–100% range** so the progress bar fills to 100% right before compaction fires. The `▓` character at the end of the bar represents the reserved buffer zone.

For a 200K context window, compaction fires at ~167K tokens (83.5%). For a 1M context window, it fires at ~967K tokens (96.7%). The effective percentage normalizes both to 0–100%.

## Configuration

The status line is configured automatically during installation in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.pilot/bin/pilot statusline",
    "padding": 0
  }
}
```

No manual setup required — the installer handles this.
