# QualityLayer repository instructions

## Project

QualityLayer is a planning-first harness for any coding agent. One TypeScript
codebase in `qualitylayer/` compiles (`bun build --compile`) into a single
`qualitylayer` binary: the CLI that holds every task's state through one flow
(Discuss → Plan → Implement → Verify → Review), the App's server and its React
SPA, and the embedded phase texts, schemas and templates.
Installation drops the binary and agent skills, with Codex invocation-policy
metadata. The QualityLayer workflow requires explicit user opt-in.

The repository is public. Everything under `qualitylayer/` (and
`docs/site/api/`) is git-crypt encrypted; only `package.json`, `bun.lock`,
`tsconfig.json` and `biome.json` stay plaintext for supply-chain scanners.

## Commands

All in `qualitylayer/`:

- `bun run typecheck` · `bun run lint` (Biome) · `bun run lint:fix`
- `bun run test` — every test file in its own process (plain `bun test` leaks
  the test DOM between files); builds the binary first
- `bun run test tests/e2e` — a directory or single files
- `bun run build` — the development binary in `dist/qualitylayer`;
  `bun run build --all` — the six release targets with checksums
- `bun run release-gate --agent claude-code|codex` — a real agent carries the
  reference task (`tests/release/reference-task/`) to shipped: the Plan gate
  and the final review are approved through the App API, and the harness
  starts Implement with `/ql implement <task>` as the user would. `--plan-only`
  stops at the Implement stop. Uses the agent's own login; all QualityLayer
  state goes to a temp `QUALITYLAYER_HOME`. Costs real agent time.
- `bun run evals [--agent …] [--only discuss,plan]` — phase evals
  (`tests/evals/*.json`) judged on real runs of the flow; before releases, not
  per commit
- `bun scripts/transcript-cost.ts <session id | file | folder> [--json]` or
  `--gate <release-gate logs>` — what a run cost, from the agents' transcripts
  (estimates at list price)
- `bun run eval:activation [--agent claude-code|codex]` — real-client opt-in
  probes using the agent's own login, a temp HOME and a recording stub instead
  of the QualityLayer binary. `QUALITYLAYER_ACTIVATION_CODEX` and
  `QUALITYLAYER_ACTIVATION_CLAUDE` can select native executables when a local
  launcher depends on the real HOME.
- Do not run `bun run test` or `bun run build` while a release gate is running:
  both replace `dist/qualitylayer`, which the gate's agent is using
- Git hooks (`core.hooksPath=.github/hooks`, shared by every worktree) gate
  commits and pushes: `pre-commit` runs typecheck, lint, the Cockpit checks,
  cargo fmt and clippy for the App, shellcheck, actionlint and Trivy on what is
  staged; `pre-push` runs `.github/scripts/check_qualitylayer_encrypted.sh` over the
  pushed commits. Fix what they report; never bypass them with `--no-verify`

## Repository rules

- Preserve unrelated work in the dirty worktree. Do not reset, restore, or
  overwrite concurrent changes.
- Never move source, phase texts, schemas or fixtures out of `qualitylayer/`.
- Use the agent's native file tools for source edits. No bundled tooling (RTK,
  Semble, CodeGraph) is required or assumed.
- Tests never touch the real `HOME` or the network: they run the built binary
  against a temp git repository and a temp `HOME`, with Polar, the trial
  service and releases pointed at local fixtures or a closed port.
- Never run `install.sh`, `qualitylayer install`, the v11 upgrade or any
  uninstaller against the real `HOME` of a development machine; use a temp
  `HOME`.
- Never switch branches, commit, push, rebase, or force-update history
  without the corresponding user authorization.

## Layout

- `qualitylayer/src/core/` — task state machine, documents and validation,
  gates, recorded checks, the scaling rules (`scaling.ts`), cost, git, licence,
  telemetry, install. `advance()` is the only writer of a task's stage;
  `core/flow.ts` names the five steps for every surface.
- `qualitylayer/src/cli/` — argument parsing and output only.
- `qualitylayer/src/server/` and `src/ui/` — the App.
- `qualitylayer/src/workflow/` — phase texts, schemas, templates, the skill.
- `install.sh` — public, plaintext: download, verify the checksum, hand over
  to `qualitylayer install`.
- `docs/plans/` — QualityLayer's own task folders; local only, untracked and
  ignored.

## Cross-agent assets

- `AGENTS.md` is the shared repository core; `CLAUDE.md` must remain exactly
  `@AGENTS.md` plus a trailing newline.
