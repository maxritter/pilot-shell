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

```
Line 1: Opus 4.6 [1M] | █████░▓ 60% | +156 -23 | main +2 ~3 | $1.45 | saved 12.5K (65%)
Line 2: Spec: my-feature feature [implement] ████░░░░ 3/6 [plan-rev spec-rev wt]
Line 3: Pilot 8.2.1 (Solo) · CC 2.1.79 (Max) · sessions 2 · memories 12
```

### Line 1 — Session Metrics

Widgets separated by `|`, from left to right:

| Widget | Description | Color coding |
|--------|-------------|--------------|
| **Model** | Active model in short form (`Opus 4.6 [1M]`, `Sonnet 4.6`) | Cyan |
| **Context** | Effective context usage with progress bar and buffer indicator (`▓`) | Green < 80%, Yellow 80–95%, Red 95%+ |
| **Lines changed** | Session lines added/removed (`+156 -23`). Hidden when usage API data is available | Green for added, Red for removed |
| **Git** | Branch name with staged (`+N`) and unstaged (`~N`) counts. Shows worktree branch with `wt` suffix when in a spec worktree | Magenta branch, Green staged, Yellow unstaged |
| **Cost** | Session cost in USD | Green < $1, Yellow $1–5, Red $5+ |
| **5h usage** | 5-hour usage limit percentage with reset time (requires OAuth credentials) | Green < 70%, Yellow 70–90%, Red 90%+ |
| **7d usage** | Weekly usage limit percentage with reset time | Same as 5h |
| **RTK savings** | Token savings from RTK proxy (shown when no usage data available) | Cyan |

:::info Usage API
When OAuth credentials are present (`~/.claude/.credentials.json`), the Anthropic usage API provides 5-hour and weekly usage limits — these replace the lines-changed and RTK widgets. Without credentials, lines-changed and RTK savings are shown instead. This is credential-dependent, not platform-dependent.
:::

### Line 2 — Mode

**Quick Mode** (no active spec):
```
Quick Mode · /spec for feature implementation and complex bugfixes
```

**Spec Mode** (active `/spec` plan):
```
Spec: my-feature feature [implement] ████░░░░ 3/6 iter:2 [plan-rev spec-rev wt]
```

| Field | Description |
|-------|-------------|
| **Name** | Plan name (date prefix stripped) |
| **Type** | `feature` (cyan) or `bugfix` (yellow) |
| **Phase** | `plan` (blue), `implement` (yellow), or `verify` (cyan) |
| **Progress bar** | Visual task completion (filled █ / empty ░) |
| **Count** | Completed/total tasks |
| **Iterations** | `iter:N` shown when verification has looped back (N > 0) |
| **Config flags** | Spec workflow settings in brackets — green = on, dim = off |

**Config flags:**

| Flag | Setting | What it controls |
|------|---------|-----------------|
| `plan-rev` | Plan Review agent | Validates plans before implementation (~50k tokens) |
| `spec-rev` | Spec Review agent | Reviews code after implementation (~100k tokens) |
| `wt` | Worktree Support | Isolates changes in a git worktree |

Configure these in the [Pilot Console Settings](/docs/features/console#settings) tab or directly in `~/.pilot/config.json`.

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
