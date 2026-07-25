# Spec Workflow Model-Switching Smoke Test

Dry-run of `/spec` (plan → implement → verify) with no real product work, to observe
automated model switching between the planning and execution legs.

## Observed models per phase (Automated mode — the default)

| Phase | Model | How switched |
|-------|-------|---------------|
| Planning (`spec-plan`) | Opus 5 (plan mode) | `EnterPlanMode` called at start of planning (opusplan → Opus, native) |
| Implementation (`spec-implement`) | Sonnet 5 (`claude-sonnet-5`) | `ExitPlanMode` called after plan approval (opusplan → Sonnet) |
| Verification (`spec-verify`) | Sonnet 5 (`claude-sonnet-5`) | Same session as implementation — no further switch needed |

## Why the switch happens

With `modelSwitchMode: "automated"` (`PILOT_MODEL_SWITCH_MODE=automated`), Claude Code
runs on the `opusplan` model alias: plan mode resolves to Opus and non-plan-mode to
Sonnet — natively. `/spec` calls `EnterPlanMode`
before planning and `ExitPlanMode` right after plan approval, so the model flip is
automatic. Boundary condition worth testing: with the conversation above the Opus plan
leg's effective window (~200K — currently even with the Opus 1M entitlement, a known
Claude Code regression, anthropics/claude-code#65512), Claude Code silently keeps
serving Sonnet — the `spec_mode_guard` pre-flight and the `plan_mode_tracker`
mid-planning check must both surface it.

## Contrast: Manual mode

With `modelSwitchMode: "manual"`, no plan mode is used: `/spec` prints a planning-model
reminder at Step 0 and pauses once after plan approval (AskUserQuestion) for the
`/model` switch. The whole workflow otherwise runs on the active `/model` choice.

## Contrast: Off

With `modelSwitchMode: "off"`, the whole `/spec` workflow (plan, implement, verify)
stays on the active `/model` choice with no prompts and no `EnterPlanMode`/`ExitPlanMode`
calls at all.
