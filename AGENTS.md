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
  `bun run test:ui` — Playwright checks with semantic interactions, geometry
  and axe, in desktop light while working; `bun run test:ui --all` adds dark
  (CI runs `--all`); `--project desktop-small` checks a 1024 × 720 window. Nobody uses the App on a
  phone: there are no phone checks. Both Claude Code and Codex
  use these commands. Read `qualitylayer/TESTING.md` for setup and evidence.
- `bun run test` — the working run: every test file recorded within 3 seconds, each
  in its own process (plain `bun test` leaks the test DOM between files); builds the
  binary first. A couple of minutes
- `bun run test tests/e2e/x.test.ts` — a directory or single files, whatever their
  time: the slower files that cover what you changed
- `bun run test --all` — every file: once before a push; CI runs it on every push
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
  filter), then commit. Afterwards bring your own paths in the shared index up
  to the new commit (`git reset -q HEAD -- <your paths>`); otherwise it keeps
  their old blobs and the next commit from it reverts yours. Never stage,
  unstage or reset paths in the shared index that are not yours.
- Never move source, phase texts, schemas or fixtures out of `qualitylayer/`.
- Read committed encrypted paths with `git cat-file --filters HEAD:<path>`.
  `git show HEAD:<path>` returns git-crypt ciphertext and cannot be linted as source.
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

## Test cost

- Tests are budgeted: `qualitylayer/scripts/test-tiers.ts` and
  `tests/scripts/test-budget.test.ts`. A file over ten seconds needs its reason
  there; the working run and the full suite stay within their minutes. Raising a
  budget needs the person's approval, never a way to make a run pass.
- Test at the cheapest level that proves the behaviour (TESTING.md): unit and
  component tests first, an in-process server for the API, and the built binary, a
  browser or the native App only for what only they show, one flow per journey.
- No fixed sleeps to wait for something; share a fixture per file; tests for
  retired behaviour leave with the code.
- While working run `bun run test` plus the slower files you touched; run
  `--all` once before a push, never several full runs at once.

## Bigger workflow changes are measured

- The bench is on demand: run it for a bigger change to how a task runs (a
  new or reshaped step, helpers, gates, scaling rules, settings defaults,
  several phase-text changes at once), or when the person asks. Not for every
  release or small wording fix: a run costs real time and tokens. `bun run
  bench` (skill `ql-bench`, design `qualitylayer/design/bench.md`) runs
  Claude Code **and** Codex; take the baseline on the same cells.
- Quality first: keep a measured change only when acceptance and test
  strength are not worse on any cell and agent; then time, cost and fresh
  tokens decide. A verdict with `?` needs more repeats before it is claimed.
- Put the compare's headline in the commit body and in
  `qualitylayer/design/bench-log.md`. Compare QualityLayer with its own
  earlier version only; the plain agents calibrate the acceptance checks.

## Design changes

- Before every user-visible UI change, update the canonical lasting design:
  the App Model for the App, the website design for the website, or the
  corresponding design for the Cockpit and docs. Show and review that change
  in QualityLayer before changing production UI source. This includes a
  single button, switch, wording, interaction state or motion change. Keep
  the model and implementation aligned; revise the model first when the UI
  needs to change during implementation.
- Outside a QualityLayer run: use QualityLayer's local Designs workspace
  and the `ql-design` skill together with Impeccable (context, craft and
  critique). Start from the existing lasting design and show the prototype
  before changing production UI source. Design commands do not start a workflow.
- Inside a QualityLayer run: the Plan's mockup shows it (`ui: true`, one
  mockup per changed surface). Use the local design guide and Impeccable for
  its check pass; review and comments stay in QualityLayer. Use Claude Design
  only for an explicit request or a supplied remote project/artifact.
- Use the approved unified App Model and current `qualitylayer/PRODUCT.md`
  and `qualitylayer/DESIGN.md`: only genuine human choices, full documents
  with approval in the shared header, quiet future steps, personal attention
  and running work on Home, and teammate asks in Team. Reusable designs live in
  the compact Library and working drafts in task Files. Activity belongs in its
  header chip panel, with no duplicated status.
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
