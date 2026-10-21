# Artifact lessons from Claude artifacts (2026-10-20)

Source: Open Claude Design 1.8.0 mapped Claude Code 2.1.304's artifact protocol
(runtime contract 0.2.87). This plan applies the useful parts to QualityLayer's
local artifacts on `dev`. No visible App change is in scope, so the App Model
gate does not apply; every change is CLI, core, renderer, guide, skill or docs.

## The nine suggestions, checked against the code

| # | Suggestion | Finding in `dev` | Decision |
|---|---|---|---|
| 1 | Render matrix with console capture | `shot` draws one width/theme; `render.ts` records no console or exceptions | Build (S1) |
| 2 | Theme sets `data-theme` and `prefers-color-scheme` | `render.ts` emulates only the media feature; the guide carries a workaround | Build (S1) |
| 3 | Comment activation and attribution | Already covered: `for: agent/person`, person-note refusal, `delivered`, agent-actionable filter. Missing: anchor health | Build anchor health only (S2) |
| 4 | Per-file write hashes | Already covered: page writes are guarded per page revision (`workspace.ts`) | Drop |
| 5 | Design-token install record and drift | `new` seeds tokens but records nothing | Build (S2) |
| 6 | Shared-version pinning | Already covered: shares record their revision and update only on **Update shared preview** | Drop |
| 7 | Declared interactivity in shared previews | Shared previews run no scripts by design | Needs Max's security decision; not built |
| 8 | Publish to Claude through Open Claude Design | Only a stored link | Build CLI bridge (S3); App button later through the App Model |
| 9 | Versioned guides | One local guide, no record | Build with 5 (S2) |

## Slices

Each slice has exclusive files. `src/cli/commands/artifact.ts` is shared by S1
and S2 by region: S1 owns `shotCmd`, the `check` branch, `artifactArgs` and the
usage text; S2 owns `newCmd`, `listCmd` and `commentsCmd`. Re-read before every
edit. Never touch files another session has modified (`git status`).

### S1 Render matrix, runtime errors, theme signals

- `src/server/render.ts`: before navigation, set `document.documentElement.dataset.theme`
  through `Page.addScriptToEvaluateOnNewDocument`, next to the existing media emulation.
  Collect `Runtime.exceptionThrown`, `Runtime.consoleAPICalled` (error/assert),
  `Log.entryAdded` (error) and requests the policy blocked, per shot, through an
  optional `ShotSpec.onDiagnostics` callback. Existing callers stay unchanged.
- `artifact shot <name> --matrix`: four pictures (the artifact's width or 1280, and 390;
  light and dark) with per-picture `errors` and `blocked`. A single shot also reports them.
- `artifact check <name> --render`: source check plus the matrix; a runtime error is a
  `runtime-error` finding and makes the check invalid. Without Chrome it says so and
  stays source-only.
- Done when: a page that throws on load fails `check --render`; a page styled only by
  `[data-theme=dark]` draws dark under `shot --theme dark`; one `--matrix` call writes four
  pictures.
- Status: built. `artifact shot <name> --matrix`, `artifact check <name> --render`
  (`runtime-error`, `blocked-request`, `render-failed`).

### S2 Provenance and anchor health

- Record `ql:tokens` (digest of the project's design tokens used) and `ql:guide` (the
  authoring guide's version digest) as meta tags when `artifact new` creates a page.
- `artifact list` and `artifact inspect` report `tokens: current | drifted | unrecorded`
  and `guide: current | changed | unrecorded`; inspect adds the refresh step when drifted.
- `artifact comments <name>` marks each comment's anchor `missing` when its section no
  longer exists on the page, and `earlier` when it was written against an older revision.
- Done when: changing a project token marks an older artifact `drifted`, and a comment on a
  removed section is reported `missing`.
- Status: the stamp design above was built, then replaced (2026-10-20, Max asked to get it right;
  reviewed by the Artifacts page session and the Codex release owner). Reasons: a whole-text
  guide digest flags every artifact on any typo; a token digest flags tokens no page uses;
  only 18 of 465 real pages keep the template's `--ql-*` names, so stamps miss most artifacts.
- Replacement (S2b): direct comparison of the page's declared token values with the design file.
  - Colour names match `--ql-<name>` or `--<name>`; other tokens match their exact name.
  - Only root and theme blocks count: light and dark are compared separately, and the last
    declaration in each wins.
  - `var()`/`calc()`/`color-mix()` values are skipped; normalization is conservative.
  - A page with fewer than 3 matching design-file names is `n/a` ("uses its own palette").
  - The overview carries `tokens: {state, count}`, and the changed list is fetched on demand.
  - A per-artifact cache covers every consulted CSS file and the design file, with work and byte
    budgets per request. No watchers, timers or team backend involvement.
  - `artifact tokens <name> [--refresh --if-match]` guards every file it writes.
  - The guide stamp is dropped. Comment anchor health is kept.

### S3 Publish to Claude through Open Claude Design

- New `src/core/artifact/claude-publish.ts` and `src/cli/commands/artifact-claude.ts`:
  `artifact claude <name> status | publish | update | comments`.
- Lasting artifacts only. Packs the entry page like the App does, calls the installed
  `open-claude-design` (1.8.0 or later) with `--json`, and stores the returned artifact URL
  as the Claude Design link under the library revision guard. `update` re-publishes with
  the remote file hash from OCD as its `--if-match`. `comments` lists Claude threads and
  marks the ones sent to Claude as actionable; reply and resolve stay in OCD.
- Never reads, prints or stores Claude credentials; a missing or older OCD returns
  install guidance.
- Done when: a fake `open-claude-design` fixture round-trips publish, update and comments
  in a temp home.
- Status: built. `artifact claude <name> status | publish --if-match <revision> | update
  [--if-remote <sha256>] | comments [--open-only]`.

### S4 Guide, skill, docs, changelog (after S1–S3)

- `src/workflow/phases/artifact-authoring.md` and `artifact-check.md`: matrix shots,
  `check --render`, drop the `data-theme` workaround, provenance and Claude publishing.
- `src/skills/ql-artifact/SKILL.md`: route to the new commands without restating the guide.
- `docs/docusaurus/docs/artifacts.md` with the docs model (`copy.json`, `render.mjs --patch`).
- `CHANGELOG.md`: one entry per user-visible capability.
- Status: guide, review guide, skill and public docs are written (`artifacts.md`,
  `reference/commands.md` and the docs model). The changelog entries are added at release.

### S5 App data routes (non-visible), for the Artifacts page task

Agreed with the Artifacts page UX task (`2026-10-20-i-would-love-to-improve-the-artifacts-pa`):
it owns every visible App change, App Model first; this plan owns the data.

1. ~~`GET /api/artifacts`: each lasting row gains `tokens: { state, count?, reason? }`;
   `GET /api/artifacts/tokens?project=&name=` gives the changed list.~~
   Removed 2026-10-20 (Max): no token or script-error UI; agent-side only.
2. `GET /api/artifacts/claude?project=&name=` → `{ status: published|stale|none|unavailable, url?, reason?, install? }`;
   `POST` the same path `{ action: publish|update }`.
3. `GET /api/artifacts/claude/comments?project=&name=` → `{ threads: [{ id, author, text, sentToClaude, at }] }`.
4. ~~Shot records the server returns carry `diagnostics: { errors, blocked }`.~~
   Removed 2026-10-20 (Max): no token or script-error UI; agent-side only.
5. The artifact comments route marks each comment `anchor: missing|ok`.

## Ownership

- This plan: CLI, core, renderer, guide, skill, public docs, and the S5 routes.
- Artifacts page task: all App UI for 2, 3 and 5 (Publish to Claude, Claude threads,
  missing-anchor marker; the drift badge and runtime errors beside shots were removed
  2026-10-20 (Max): no token or script-error UI, agent-side only); team-shared editable artifacts with
  version history and restore, including their CLI (`artifact shared …`, dispatch line
  coordinated) and team service; interactive shared previews (Max's decision: sandboxed
  frame with scripts, no same-origin, no network). It sends doc text for the team-sharing
  CLI; this plan places it in the public docs.

## Verification

From `qualitylayer/`: `bun run typecheck`, `bun run lint`, focused `bun run test <files>`
per slice, then `bun run test:smoke`. Commit on `dev` through a private index with only
this plan's files.
