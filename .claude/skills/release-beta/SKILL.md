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

## 1. Know what ships

```bash
git describe --tags --abbrev=0                    # last tag, e.g. v12.0.0-beta.53
git log --oneline <tag>..HEAD                     # everything that goes out
```

The next version is the tag's beta number + 1.

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

1. `cd qualitylayer && bun run test`: the full suite (~7 min). A one-off temp-folder cleanup race
   in `tests/cli/hook-prompt.test.ts` passes on rerun; anything else is real.
2. `bun run test:ui`: the whole Playwright suite, not only the specs you touched. Other sessions'
   site changes break `tests/frontend/website.spec.ts` (headings, axe contrast).
   *(2026-10-12: beta.54's first run was blocked by website checks left failing by a site redesign.)*
3. `cd docs/site && bun run test && bun run typecheck` when the site changed.
4. A **new browser e2e test** runs four times at once before it ships; CI's machines are
   slower and expose timing races a single local run hides:
   `for i in 1 2 3 4; do (bun test tests/e2e/<new>.test.ts > /tmp/run-$i.log 2>&1; echo "run $i $?") & done; wait`
   *(2026-10-12: the tour's ring lagged one stop behind its card on CI only.)*
5. Never run `bun run test` or `bun run build` while a release gate runs (they replace `dist/`).
   Run `bun run build --all` (the release build) once locally: it enforces guards the dev build
   skips, such as the memory engine's `releaseQualified` flag per target in
   `src/memory-engine/payloads/manifest.json`. *(2026-10-13: beta.56's first run failed in
   "Build QualityLayer (6 targets)" because no target was qualified; every local suite had passed.)*
   After `bun run test` in a fresh worktree, `bun run build` before `bun run test:ui`: the suite
   builds `dist/e2e`, the UI specs need `dist/qualitylayer`.
   Specs that drive the PTY host or CDP on iframes can fail on CI's Linux only (`/proc/<pid>/environ`
   EACCES, frames without their own CDP session); read the failure before calling it a flake.
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
(`gh run cancel <release-run-id>`), and push the fix; the new push starts a new run.

## 6. Done means published

`gh release view v12.0.0-beta.N` lists the assets, and the download page names the version.
Tell Max the version, what is in it, and anything left open. Install it on his Mac only when he
asks (memory: QualityLayer installed, clean-worktree recipe).
