---
sidebar_position: 5
title: Model Routing
description: Drive /model yourself by default, or hand opusplan routing to Claude Code.
---

# Model Routing

:::warning Claude Code only
Model Switching is a Claude Code feature. It is not available in Codex CLI -- on Codex, set the model via `codex --model <name>` or in `~/.codex/config.toml`, and `/spec` runs on whatever model is active.
:::

Opus reasons better; Sonnet is faster and cheaper. The cost-saving move is to plan on a stronger model, then drop to a cheaper one for the mechanical implementation and verification that follow. **Model Switching** controls how `/spec` handles that switch.

## The Three Modes

**Console -> Settings -> Model Switching** offers three mutually exclusive modes:

| Mode | What happens | Who switches |
|------|--------------|--------------|
| **Automated** | `/spec` runs on the `opusplan` model: Opus 5 plans (plan mode), Sonnet 5 executes everything else | Claude Code, natively |
| **Manual** (default) | `/spec` pauses once after plan approval so you can switch to your implementation model | You, via `/model` |
| **Off** | No model management, no prompts, no gates | Nobody -- the active `/model` choice runs everything |

Pilot does **not** remap model aliases behind the scenes in any mode -- your `/model` picker always means what it says.

## Manual (default)

New installs start here. You stay in control of the model at every phase:

1. Type `/spec <task>` on whatever model you want planning to run on (the Step-0 message reminds you -- switch with `/model` before planning starts if needed). Fable 5, Opus 5, anything.
2. Plan, review, approve as usual.
3. After you approve the plan, `/spec` finishes its turn with a switch prompt: *"switch to your implementation model now via `/model`, then send `continue`."* You get the input box back, run `/model sonnet` (or keep the current model), confirm Claude Code's dialog about carrying the conversation over to the new model, and type `continue` — implementation starts on your choice.

That's the whole contract -- one reminder, one pause. In fully-autonomous runs (Plan Approval disabled), the pause is skipped and a one-line notice is printed instead.

## Automated

`/spec` drives Claude Code's native `opusplan` model:

- Pilot sets `model: opusplan` (and the matching `ANTHROPIC_MODEL` env pin) in `~/.claude/settings.json` when you select Automated.
- The spec skills enter plan mode at planning start (Opus 5) and exit it after plan approval (Sonnet 5). Plan mode is purely the model lever here -- approval still happens at the AskUserQuestion gate.
- The `spec_mode_guard` hook blocks `/spec` when the session is not on `opusplan` and tells you to run `/model opusplan`.

**Know the boundary conditions.** Claude Code decides the plan-leg model, and it can silently keep serving Sonnet when Opus is not available for the request:

- **Conversation too large.** The Opus plan leg has an effective 200K window — and on current Claude Code versions the cap applies **even with the Opus 1M entitlement**: the v2.1.172 fix that gave entitled accounts a 1M plan leg has regressed upstream ([anthropics/claude-code#65512](https://github.com/anthropics/claude-code/issues/65512), [#74325](https://github.com/anthropics/claude-code/issues/74325)). Accounts without the entitlement, or with exhausted Max usage credits, were always capped at 200K. Once your conversation is bigger than that, plan mode silently stays on Sonnet. Pilot pre-flight-checks this at `/spec` submit and warns you to `/compact` / `/clear` first (or use Manual mode); a mid-planning check warns again if planning is observably not on Opus.
- **Opus usage limits.** Under `opusplan`, Claude Code serves Sonnet while your Opus pool is exhausted and switches back when it frees up (`/usage` shows the state).

## Off

Pilot stays out of model management entirely. `/spec`, `/fix`, and quick mode all run on the active `/model` choice with no reminders and no gates. Switching away from Automated heals a Pilot-written `opusplan` back to `opus[1m]`; any model you picked yourself -- including `opusplan` -- is left alone.

## Migration from earlier versions

The old boolean toggle (and the 9.12 configurable Plan/Execution model pair with its window-scoped alias pins) is gone:

| Old setting | New mode |
|-------------|----------|
| Model Switching ON (old default) | Automated |
| Model Switching OFF | Off |

Automated matches what ON-users were already getting, so upgrading never changes your mode; select Manual or Off in the Console if you'd rather. A fresh install is seeded Manual instead -- upgraders keep their existing behaviour, new users pick their own model from the start. Any leftover alias remaps an older Pilot wrote into `~/.claude/settings.json` are cleaned up on the next Pilot start (values you set yourself are left alone).

## The env var

Skills and hooks read the mode fresh from `~/.pilot/config.json` (`specWorkflow.modelSwitchMode`), so a Console change applies to the very next `/spec` -- no session restart needed. `PILOT_MODEL_SWITCH_MODE` (`automated` | `manual` | `off`) is exported for display and subagents.
