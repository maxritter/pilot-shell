---
name: release-beta
description: Prepare, qualify and publish a QualityLayer beta from dev. Use when Max asks to release or ship a beta, or when preparing a dev push that stages a release candidate.
---

# Release a beta

A push to dev stages a private candidate. Publication requires an explicit
promotion of that successful run after installing and verifying its exact
artifacts. The current authority is `.github/workflows/release.yml`,
`qualitylayer-candidate.yml` and `qualitylayer/scripts/release-candidate.ts`.
A staged candidate is not a published release.

Use the person's existing authorization for commits, pushes, installation and
publication. Do not infer missing authorization from this skill. Keep the
release checklist current, retain failures and distinguish source tests,
development builds, installed candidates and public readback.

## Source and version

- Read the last tag, the full range since it, the dirty worktree and active
  peer claims. Preserve other sessions' work and coordinate commits by named
  paths through a private index. Never bypass hooks.
- Keep package version and the top CHANGELOG section aligned. Stage an
  unpublished version; do not silently reuse an existing tag.
- Read the actual workflow inputs before dispatching. The stage version is
  selected from current source and tags; flags and older notes can be stale.
- For public copy, use Deslop, Anti-slop and Impeccable. Preserve the existing
  website and README design. Update the canonical local QL design before
  visible changes, then inspect the implemented screens.

## Qualification

Run the required gates on fixed source: the working tier and changed slow
files while iterating, then the full suite and supported desktop UI matrix
before pushing. Run site tests and typechecks when the site changes. Use
semantic browser expectations and actual rendered geometry; preserve original
failures and investigate their causes before repeating tests.

Heavy suites run sequentially on this Mac. Do not overlap Bun, browser, Rust
and docs builds with resource measurements. Freeze the source commit, binary
hash and matching development trial key for native workflow tests; never
replace a running gate's executable. A development trial key is not a
production signing credential.

For bigger workflow changes, use ql-bench on the matching baseline and both
primary agents. Quality comes before time or cost. Binary comparisons need
each side's own installed skills and bridges, isolated native profiles and
pinned tools. Record failed and unrun attempts; do not retry, void or regrade
an unfavorable run to manufacture acceptance.

Before native turns, verify the intended existing account in an isolated
profile. Preserve native permission policy, personal settings and credentials.
App fixture bypass flags do not prove production Own settings behavior.
Use an explicit temporary HOME, CODEX_HOME, CLAUDE_CONFIG_DIR and XDG paths.

Release builds are separate programs from development builds: obfuscation,
signing and embedded payload bytes need their own checks. The candidate graph
qualifies six native Memory payload and distribution targets, signing policy,
notarization where required, upgrade/migration behavior and installation
notices. Never flip releaseQualified flags in lieu of those receipts.

CI and the complete source UI run must pass for the exact candidate SHA.
A scratch branch can verify CI changes without staging a dev candidate.
Read failed job logs before attributing a failure to the platform. Retrying
an infrastructure failure creates a new run attempt whose artifacts and
receipts must be qualified separately.

## Stage, install and promote

1. Commit with normal hooks and verify the source/index are coherent. Fetch
   origin, reconcile remote changes and push only with the person's authority.
   Avoid overlapping release runs; keep their source and attempt identities
   distinct.
2. Watch the Release stage through its candidate jobs. Download the recorded
   candidate manifest and exact assets/catalog artifacts from the successful
   run and attempt. Verify their identities, hashes and existing signatures
   with release-candidate.ts before running executables.
3. Install that candidate locally when authorized, preserving live native
   sessions. Record the actual installed App, CLI and engine hashes, source
   commit/tree, version and check outcomes in the installed-candidate receipt.
   Test actual App launch, memory readback and the required native journeys.
   An ad-hoc development install cannot stand in for this receipt.
4. Dispatch Release with operation=promote on the same source SHA, using the
   exact version, candidate_run_id, candidate_run_attempt,
   candidate_source_sha and installed_receipt. Supply structured inputs or
   an input file, not interpolated multiline shell text. The workflow validates
   the successful run, immutable artifacts and installed hashes before its
   environment authorization and publish job. Promotion reuses those bytes;
   it does not rebuild or resign them.
5. If source or artifact bytes change, stage and qualify a new candidate.
   Never fabricate an installation receipt or promote an earlier candidate
   as though it covers the new source.

Tauri accepts CI=true or CI=false, not CI=1. Inspect actual workflow jobs and
logs rather than assuming a prior release's job order or asset count.

## Publication readback

Verify the new GitHub release and complete expected assets, public download
checksums/signatures, /api/app/latest and updater alignment. Check the website,
download page and changelog after deployment. A successful upload or alias
command alone does not establish the live result.

Website-only publication uses the repository's deploy-website skill and its
local Vercel path when authorized. Do not assume that an App promotion also
published every later website edit.

Close only feedback items whose fixes and verification shipped. Tell Max the
published version, meaningful changes, installed version and any remaining
unverified behavior. Keep this guide aligned when the release protocol changes.
