---
name: release-beta
description: Ship a QualityLayer beta from dev (CHANGELOG section, version bump, local gates, push, watch the Release workflow to a published GitHub release). Use when Max asks to "release", "kick off a release run", "ship a beta", or when a push to dev will release anyway (any feat:/fix:/perf: since the last tag).
---

# Release a beta

Any push to `dev` that carries a `feat:`, `fix:` or `perf:` commit since the last tag releases the
next beta (`.github/workflows/release.yml`). Max is fine with betas going out this way; a public
release on his approval only is an idea, not built. A run that fails costs ~15 minutes, so every
check below runs **before** the push. Each step names the mistake that taught it.

**Keep this skill current.** Whenever a release run fails or needs a workaround, add the lesson
here (the step, and the mistake in one line) before ending the turn. Max asked for this on
2026-10-12: the same release mistake must not happen twice.

## 0. CI on dev is green before anything else

```bash
gh run list --branch dev --workflow "QualityLayer CI" --limit 3 --json headSha,conclusion \
  --jq '.[] | "\(.headSha[0:9]) \(.conclusion)"'
gh run list --branch dev --workflow "QualityLayer source UI" --limit 3 --json headSha,conclusion \
  --jq '.[] | "\(.headSha[0:9]) \(.conclusion)"'
```

A red CI on dev blocks every release, and local suites do not see CI-only failures (Linux
runners, macos-14, slower machines, a fresh clone). Fix CI first, then prepare the release.
*(2026-10-13: CI had been red since 13:00; beta.56 needed six release runs over three hours.)*

- Prove CI fixes **without releasing**: push to a scratch branch and run
  `gh workflow run "QualityLayer CI" --ref <branch>` and `gh workflow run "QualityLayer source UI"
  --ref <branch>` (both take workflow_dispatch). Only a push to dev releases.
- A Linux-only failure reproduces locally in a container on the unlocked checkout:
  `docker run --rm -v "$PWD":/w -w /w/qualitylayer oven/bun:1.4.2 bun run test <file>`.
  *(The fake PTY agent's commands and /proc/<pid>/environ EACCES only failed on Linux.)*
- Read failures per job (`gh api …/actions/jobs/<id>/logs`); `gh run view --json jobs` can answer
  HTTP 502 for big runs, use `gh api "…/runs/<id>/jobs?per_page=50"` or wait a minute.
- Split real failures across helpers by area (process tests, build tools, browser e2e, UI units and
  site), each with exclusive files and the saved job logs; commit each group as it lands.

## 1. Know what ships

```bash
git describe --tags --abbrev=0                    # last tag, e.g. v12.0.0-beta.53
git log --oneline <tag>..HEAD                     # everything that goes out
```

The next version is the tag's beta number + 1. Everything on dev ships (Max, 2026-10-13: "do not
leave anything behind from dev"); a half-finished file in the shared checkout is named to Max, not
shipped.

## 2. Notes and version, in the same commit

- `CHANGELOG.md` (repo root) gets `## 12.0.0-beta.N` on top with `### New`, `### Fixed`,
  `### Good to know` as needed. Plain words for users; no internal names, no file paths.
  `bash .github/scripts/changelog-section.sh 12.0.0-beta.N >/dev/null` must pass.
  *(2026-10-12: a run failed in Prepare Release, "CHANGELOG.md has no section".)*
- `qualitylayer/package.json` `"version"` moves to the same version.
  `tests/core/update.test.ts` checks the newest CHANGELOG version equals it.
  *(2026-10-12: the section went in without the bump; CI failed on three shards.)*

## 3. Local gates, before the push

The Release workflow reuses CI's results and waits for the **whole** source UI run, website
checks included, so a failure anywhere blocks it.

1. `cd qualitylayer && bun run test --all`: the full suite (`bun run test` alone is the fast
   working tier and skips every file over 3 s). A one-off temp-folder cleanup race
   in `tests/cli/hook-prompt.test.ts` passes on rerun; anything else is real.
2. `bun run test:ui`: the whole Playwright suite, not only the specs you touched. Other sessions'
   site changes break `tests/frontend/website.spec.ts` (headings, axe contrast).
   *(2026-10-12: beta.54's first run was blocked by website checks left failing by a site redesign.)*
3. `cd docs/site && bun run test && bun run typecheck` when the site changed.
4. A **new browser e2e test** runs four times at once before it ships; CI's machines are
   slower and expose timing races a single local run hides:
   `for i in 1 2 3 4; do (bun test tests/e2e/<new>.test.ts > /tmp/run-$i.log 2>&1; echo "run $i $?") & done; wait`
   *(2026-10-12: the tour's ring lagged one stop behind its card on CI only.)*
5. Freeze the source and build a private candidate with `bun run build --out <absolute-path>`.
   Supply it as `QUALITYLAYER_TEST_BINARY` for the full Bun and UI checks, from the same source
   directory as its development trial key. Run heavy suites sequentially on this Mac; overlapping
   Bun, browser, Rust and docs builds caused native stop/replay, crash-recovery and HTTP timing
   failures in beta.57 qualification. The unchanged cases passed in the controlled full rerun.
   Record the frozen source commit, private candidate path and hash, and matching development
   trial key before starting. Keep that candidate/key pair together throughout qualification.
   Never replace a gate's binary or signer while it runs.
   Run `bun run build --all` (the release build) once locally: it enforces guards the dev build
   skips, such as the memory engine's `releaseQualified` flag per target in
   `src/memory-engine/payloads/manifest.json`. *(2026-10-13: beta.56's first run failed in
   "Build QualityLayer (6 targets)" because no target was qualified; every local suite had passed.)*
   Without an explicit candidate, both test launchers build privately. The UI launcher removes
   its own temporary folder after success or failure; it preserves caller-supplied candidates.
   Specs that drive the PTY host or CDP on iframes can fail on CI's Linux only (`/proc/<pid>/environ`
   EACCES, frames without their own CDP session); read the failure before calling it a flake.
   Before a real Claude turn, prepare its configured account method in the private profile.
   A working `apiKeyHelper` takes precedence over an expired OAuth copy. Copy only that helper
   and the fixture's required hooks; preserve personal settings and credentials. Without a
   helper, keep the refreshable private OAuth copy. A failed login preflight spends no model turn.
   Real App-start checks preserve the selected **Own settings** and the user's existing
   permissions. A stricter automatic permission mode is unverified until its actual consent
   prompt is handled. Retain a bounded native startup trace on failure; change trust-prompt
   recognition only for the observed prompt, preserving consent and session ownership.
6. **The shipped binary is a different program.** Only `--release`/`--all` builds obfuscate the
   licence, team, gate, install and server code, and every other suite drives the development
   build. `tests/release/protection.test.ts` › "a new user's first minutes" runs the trial, a key
   in the terminal and a key or the trial in the App's Setup on a real release binary, from an
   empty home. A change to the licence code, the server's gate or `OBFUSCATION` in
   `scripts/build.ts` adds its journey there, and proves the test fails without the fix.
   *(2026-10-12: beta.53's obfuscator setting `transformObjectKeys` made `activate` throw on every
   machine without a licence; a customer could not enter his key, and no test ran that path.)*
7. A browser test checks what a person sees after the page settles: poll with
   `page.waitFor(expr, 3000)`, never one instant read of a position.
   *(2026-10-12: the tour's ring was checked the instant its card changed; on CI's Linux the part
   was still moving into place, and two release runs failed on it.)*

## 4. Commit and push

- Commit through a private index (AGENTS.md): `GIT_INDEX_FILE=<scratch> git read-tree HEAD`,
  `git add` only your files, `git commit -F <msg>`, then `git reset -q HEAD -- <your files>` so the
  shared index matches. Never `--no-verify`. The shell is zsh: keep the file list in an array,
  `FILES=(a b c); git add "${FILES[@]}"`; a plain `$FILES` is one word, adds nothing, and the
  commit silently does not happen. Check `git log --oneline -1` before pushing.
- The releasing subject is `feat:` or `fix:`. A site-only change can ride as `fix(site):`.
- `git fetch origin && git log HEAD..origin/dev` must be empty, then `git push origin HEAD:dev`.

## 5. Watch it to the end

```bash
gh run list --branch dev --limit 8 --json databaseId,workflowName,status,conclusion,headSha \
  --jq '.[] | select(.headSha | startswith("<sha>")) | "\(.databaseId) \(.workflowName) \(.status) \(.conclusion)"'
gh run watch <release-run-id> --exit-status --interval 60   # in the background
```

Release jobs, in order: Check Release Trigger → Prepare Release (CHANGELOG) → Reuse CI results
(needs QualityLayer CI green) + Source UI Gate (waits up to 20 min for the source UI run) →
builds, App packages for six targets, native Windows → publish.

Tauri parses `CI` as a boolean: set `CI=true` or `CI=false`, never `CI=1`.
*(2026-10-15: a native App qualification build stopped before startup on `CI=1`.)*

Restore any publishing workflows paused for candidate qualification before final publication,
then verify that the release's required gates and publish jobs are enabled.

**Diagnose a failure while the run is still going.** `gh run view --log-failed` is empty until the
whole run ends; read each failed job instead:

```bash
gh run view <ci-run-id> --json jobs --jq '.jobs[] | select(.conclusion=="failure") | .databaseId'
gh api --allow-escape-sequences repos/maxritter/pilot-shell/actions/jobs/<job-id>/logs \
  | sed 's/\x1b\[[0-9;]*m//g' | grep -E "FAIL |✗ |error:"
```

A failed **App package** job whose log ends in `xcrun stapler staple … failed (68)` with
"The network connection was lost" (Apple's ticket service, `api.apple-cloudkit.com`) is Apple's
outage, not ours: `gh run rerun <release-run-id> --failed` reruns that package and what depends
on it; no new push. *(2026-10-12: beta.55's macos-x64 package.)* The same goes for
`error running bundle_dmg.sh` on `macos-15-intel` after notarization was Accepted: the DMG script
hides its own output, and the build's one retry can fail too; rerun the failed job again.
*(Same day, beta.55's second attempt.)* Since 1f2428733 `scripts/app.ts` staples five times
with a growing pause; if a package still fails three times, the runner's link to Apple is bad
for the day: say so to Max instead of rerunning on.

**Never push to dev while a Release run is still going.** release.yml has no concurrency
group: a second run computes the same next version and races the first for its tag. Commit
locally, wait for the run to end, then push. A `ci:`/`docs:`/`chore:` commit after the new tag
releases nothing.

A file marked `FLAKY … passed on retry` (e.g. `command-speed` a few ms over on CI) did not fail
the run; look for `FAIL` twice (the retry failed too). Read the failure's numbers before
choosing a cause: identical coordinates in two runs mean a layout fact, not a race.

Then fix, rerun that test locally (step 3.4 for timing), cancel the doomed run
(`gh run cancel <release-run-id>`), and push the fix; the new push starts a new run. Batch: wait
for the doomed run's CI to finish so every failure goes into one push, not one push per failure.

A **cancelled** source UI shard hit its 15-minute limit: the suite outgrew its shards. Add shards
in `qualitylayer-ui.yml` (8 since 2026-10-13) rather than raising the limit.
*(Two runs lost to 4 shards that had been taking 13-15 minutes.)*

A commit that changes no CI path starts no CI run; "Reuse CI results" then waits 20 minutes and
runs its fallback suite. That still releases; it is just slow (since 2026-10-14 CI also runs on
release.yml and workflow-script changes).

`tests/e2e/design-page.test.ts` skips its <=820 px viewer and Escape-dialog cases on macOS CI
(`macRunner`) since the macos-14 Chrome hang; e2770b1b2 keeps hidden pages running. After the
next CI run, remove the skip if those cases pass with it lifted on a scratch branch.

## 6. Done means published, deployed and checked live

- `gh release view v12.0.0-beta.N` lists the assets (39 for beta.56).
- The site and the database ship inside **Publish Release**, not the Deploy Website workflow
  (that one skips scoped subjects like `chore(release):`): its log shows
  `db-migrate: applied migration <n>` (or nothing to apply), and `vercel inspect qualitylayer.dev`
  names a deployment created minutes ago.
- Live checks: `curl -s https://qualitylayer.dev/api/app/latest` names the new version; `/`,
  `/download`, `/docs/changelog` answer 200; `/api/licence/entitlement` POST without a key
  answers 400 "Missing key".
- The installed App against the live backend: with the token from `~/.qualitylayer/cockpit.lock`
  as `x-qualitylayer-token`, `GET /api/licence`, `/api/team`, `/api/team/instructions` and
  `/api/memory/overview` answer `ok: true`.
- Close the feedback issues the release fixes, with the version and how to update.
Tell Max the version, what is in it, and anything left open. Install it on his Mac only when he
asks (memory: QualityLayer installed, clean-worktree recipe).
