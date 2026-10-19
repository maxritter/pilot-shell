# QualityLayer repository instructions

QualityLayer is an opt-in planning/build harness. The TypeScript code in
`qualitylayer/` compiles into the CLI, server and App. Running a design command
alone does not start the full workflow.

## Invariants

- Preserve unrelated working changes and the shared index. Git writes require the
  corresponding user authorization. Before committing in a shared checkout,
  read `docs/agents/operations.md` for the private-index procedure.
- Keep source, phase texts, schemas and fixtures under `qualitylayer/`.
  `advance()` owns task-stage writes; `core/flow.ts` owns the seven workflow steps.
- Source under `qualitylayer/` and `docs/site/api/` is git-crypt encrypted, except
  the declared package/lock/TypeScript/Biome files. Read committed encrypted source
  with `git cat-file --filters HEAD:<path>`.
- Tests use temporary homes/repositories and fixture services. Never run an
  installer, upgrade or uninstaller against the real home. Never install Pilot
  Shell on this Mac.
- Keep the resource-budget contract when changing polls, watchers, hooks or
  background work; read `docs/agents/operations.md` for its checks.

## Verification

From `qualitylayer/`, use `bun run typecheck`, `bun run lint` and focused
`bun run test <files>` for the affected behavior. Plain `bun test` can leak DOM
state. Read `docs/agents/verification.md` for the checkout's test tiers, browser
matrix, release gates and workflow benchmark; package scripts are executable truth.
Git commit/push hooks remain mandatory. Do not build or run the building test
runner while a release gate is using `dist/qualitylayer`.

## Product and visible changes

Use `qualitylayer/PRODUCT.md`, `qualitylayer/DESIGN.md` and `ql-design`.
Each surface has one lasting design in local QualityLayer Designs; change it first, show
and review it there, then implement, so design and code never drift:

- App Model (`qualitylayer/design/app/app-model`): every visible App change, including
  wording or one control.
- Website (`qualitylayer/design/site/website-model`): the site and the docs guides.
- Team Model (`qualitylayer/design/collaboration-data-model`): the team backend's
  tables, lifetimes, storage and API authority.
- Workflow (`qualitylayer/design/app/workflow`): the steps, what a step page shows, the
  sections and order of each step's Markdown file, its schemas and phase texts, and
  what the person is asked or approves.

Keep code and its design aligned. Claude Design is not a workspace for
this repository; Claude Code may provide a second opinion. Inside a QualityLayer
build the independent visual critique is Polish's, once per build, not each
slice's.

Read `docs/agents/design.md` for design authoring/review, composition checks,
model ownership and release evidence. Use Impeccable and the user-level Anti-slop
plugin for relevant UI/copy work; reuse their installations and effective hooks.
Mechanical checks and matching tokens do not establish visual approval.
For shared UI, inspect the production consumers at their actual content widths,
with long labels, paths and requests in both themes. Focused Plan previews reuse
the real design components and open the exact page and stable section; do not
approve simplified redraws in their place. Record the visual critique and fix
clipping before local installation or release.

## Ownership

`AGENTS.md` is the shared source; `CLAUDE.md` stays exactly `@AGENTS.md` plus a
newline. A workflow bench runs only when Max asks for one; then read the
benchmark section in `docs/agents/verification.md`. For delegated QualityLayer findings, use
`ql-feedback` before edits and cite the shared inbox heading and evidence.
