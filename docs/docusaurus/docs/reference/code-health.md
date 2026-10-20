---
title: Code health
description: Review structure, complexity and duplication with local Qlty checks.
---

# Code health

QualityLayer uses local Qlty checks to help your agent review complexity and code structure. Install and update prepare a separate, pinned binary and verify it before use. Your project configuration and personal agent settings stay yours.

Installed hooks collect the files a session edits. At the end of its turn, a short structure check covers a bounded batch of those files. Findings reach the agent with its next prompt or tool result; the check does not start another turn. The `ql-quality` skill helps your agent inspect the findings without starting a workflow.

## Check and review

Run these commands inside your repository:

| To | Run |
| --- | --- |
| Tool status | `qualitylayer quality status --json` |
| Retry setup | `qualitylayer quality setup --json` |
| Edited files | `qualitylayer quality check [paths...] --json` |
| Duplication | `qualitylayer quality check --all --duplication --json` |
| Metrics | `qualitylayer quality metrics [paths...] --json` |
| Linters | `qualitylayer quality lint [paths...] --json` |
| Review a finding | `qualitylayer quality acknowledge <id> --reason "<evidence>"` |
| Pause / resume | `qualitylayer quality off` / `qualitylayer quality on` |

With no paths, `check` selects changed source files. Use `--all --duplication` for a deliberate project-wide comparison.

Read each finding against its source. Fix relevant problems and run the affected tests. For an intentional pattern or deferred improvement, record the evidence and repair boundary. Acknowledging it retains the finding; it does not fix the code. `known` means seen before, not reviewed. Changed source, analyzer settings, duplication counterparts or increased metrics require review again.

Checks are advisory. Add `--fail-on-new` to `quality check` only when you want unreviewed findings to fail the command. Your tests, security checks and release requirements still apply. `quality off` pauses checks for this project; run `quality on` before checking again.

## Availability

Automatic structure checks run locally without model calls or plugin downloads. Manual linting uses the project's enabled Qlty plugins and may need their tools or runtimes. Failed, skipped or unavailable checks provide no passing evidence.

QualityLayer acknowledgments cover built-in structure and duplication findings. Review plugin findings with your project linter’s own controls; their policies can depend on configuration beyond the checked files.

Native Qlty builds cover macOS and Linux on x64 and ARM64, and Windows x64. Windows ARM64 reports unavailable. If setup fails, check download access and archive tools, then retry `quality setup`.
