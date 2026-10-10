# QualityLayer repository instructions

## Project

QualityLayer is a planning-first harness for any coding agent. One TypeScript
codebase in `qualitylayer/` compiles (`bun build --compile`) into a single
`qualitylayer` binary: the CLI that holds every task's state through one flow
(Discuss → Research → Plan → Outline → Implement → Verify → Review, one
Markdown file per step), the App's server and its React SPA, and the embedded phase texts, schemas and templates.
Installation drops the binary and agent skills, with Codex invocation-policy
metadata. The QualityLayer workflow requires explicit user opt-in.

The repository is public. Everything under `qualitylayer/` (and
`docs/site/api/`) is git-crypt encrypted; only `package.json`, `bun.lock`,
`tsconfig.json` and `biome.json` stay plaintext for supply-chain scanners.

## Commands

All in `qualitylayer/`:

- `bun run typecheck` · `bun run lint` (Biome) · `bun run lint:fix`
- `bun run dev:ui` — source-backed App demo on loopback with Vite reload;
  `bun run test:ui` — one-worker Playwright desktop/phone light/dark checks
  with semantic interactions, geometry and axe. Both Claude Code and Codex
  use these commands. Read `qualitylayer/TESTING.md` for setup and evidence.
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
- Several sessions can share one worktree, and its index too. Commit by hand
  through a private index, the way `qualitylayer commit slice` does: set
  `GIT_INDEX_FILE` to a temporary file, `git read-tree HEAD`, add only your
  files (`git update-index` or `hash-object --path`, which runs the git-crypt
  filter), then commit. Never stage, unstage or reset paths in the shared index
  that are not yours.
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
- Resource budget: any change to the server, its polls, watchers, hooks or
  background CLI paths keeps `tests/e2e/resource-budget.test.ts` green. Git and
  `gh` calls are cached on what changes their answer, children are reaped, and
  idle is near 0% CPU. Files that grow in the QualityLayer home carry a cap
  (`core/home-caps.ts`); the server's own check is `server/resource-guard.ts`.

## Design changes

- Show a design change before building it, unless it is as small as a single
  button or switch. This covers the App, the Cockpit, the website and the docs.
- Outside a QualityLayer run: mock the change with Open Claude Design
  together with Impeccable (its context, craft floor and critique), and show
  it to the user before touching the source.
- Inside a QualityLayer run: the Plan's mockup shows it (`ui: true`, one
  mockup per changed surface). Use the same two tools for its check pass and
  to sync it to Claude Design.
- Use the approved unified App Model and current `qualitylayer/PRODUCT.md`
  and `qualitylayer/DESIGN.md`: only genuine human choices, full documents
  with approval in the shared header, quiet future steps, and the four Home
  areas. Activity belongs in its header chip panel, with no duplicated status.
- Start frontend iteration with the source demo and focused browser checks.
  Demo fixtures do not prove the real API/session path or installed App.
  Before release, verify the actual installed final candidate and record its
  source commit, command results, artifact hash and installed version. Never
  accept visual reference changes automatically or bypass existing gates.

## Layout

- `qualitylayer/src/core/` — task state machine, documents and validation,
  gates, recorded checks, the scaling rules (`scaling.ts`), cost, git, licence,
  telemetry, install. `advance()` is the only writer of a task's stage;
  `core/flow.ts` names the seven steps for every surface.
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

<!-- antislop:start -->
## Anti-slop review

Use the installed `antislop` plugin for UI and reader-facing copy work in both
Claude Code and Codex. Read its core skill, then `antislop-ui`,
`antislop-human`, `antislop-layoutmobile` or `antislop-copywriting` as relevant.
Reuse the user-level installation; do not vendor a second copy into this repo.

For implementation, apply the filter during the work and keep the approved
App Model and `qualitylayer/DESIGN.md` as the visual direction. Explicit user
instructions take precedence. A review-only request remains read-only.
Check controls, loading/empty/error states, keyboard use, contrast, responsive
layout, duplicated UI and unsupported claims. Record concrete evidence and
unverified states in the task's QA report; a source scan is not a browser pass.
Use the delivery checklist alongside Impeccable and the checks in
`qualitylayer/TESTING.md`, without adding duplicate installations or review loops.
<!-- antislop:end -->
