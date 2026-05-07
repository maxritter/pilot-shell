# Pilot Shell — Supply-Chain Audit Guide

How to review, monitor, and respond to upstream changes that Pilot Shell installs.

## 1. How to audit upstreams

The single source of truth is **`installer/upstreams.yaml`**. Every entry pins exact version + sha256/commit + last-audited date.

```bash
# Full pin history (every change to any entry, with commit message + reviewer):
git log -p installer/upstreams.yaml

# Changes to a specific entry id (substring match):
git log -p installer/upstreams.yaml | grep -A 5 "id: codegraph"

# Date range:
git log -p --since="2026-01-01" --until="2026-06-30" installer/upstreams.yaml
```

A bump PR is recognisable by:
- `version:` and (for curl entries) `sha256:` updates on the same hunk
- `last_audited:` bumped to the merge date
- Renovate or maintainer signature on the commit

If a bump lacks an updated `last_audited`, it should be rejected in review — that's the maintainer's signature that they actually audited the diff.

## 2. CI gates

`.github/workflows/supply-chain.yml` runs on every PR + nightly + on demand:

- **Manifest schema validation** — `installer/manifest.py:validate()` rejects malformed entries (missing sha256 on curl, `latest` on npm, allow-without-justification, soft-pin without reason, duplicate ids, etc.).
- **Drift check** — `scripts/check_manifest_drift.py` greps installer code for `@latest`, `master/install.sh`, unversioned `npm install -g`/`npx`/`uv run --with`, hardcoded versions outside the manifest, and unmonitored MCP packages.
- **Nightly cron** opens a `security` + `supply-chain` GitHub issue if either gate fails.

The release workflows (`release.yml`, `release-dev.yml`) include a `supply-chain-gate` job that uses the GitHub Checks API to verify `supply-chain` succeeded for the release SHA. **No release tag can be cut while supply-chain is red** — even without branch-protection set up.

## 3. Response process for retroactive flags

When the nightly cron opens a `security` + `supply-chain` issue:

1. **Triage within 24 h.** Read the issue body — it includes a link to the workflow run.
2. **Classify** the finding:
   - **Drift check failed** — bisect to the offending commit; revert or pin around it.
   - **Schema validation failed** — a manifest edit broke the contract; fix the YAML.
3. **Decide**: pin around the issue (downgrade in manifest), replace the upstream (separate PRD), or accept-and-document with `# noqa: drift-check  # <reason>`.
4. **Hotfix**: if user-facing, follow the soft-pin SLA below for vendor-managed upstreams or open a regular PR for hard-pinned ones.

## 4. Renovate coverage gap (non-GitHub curl entries)

Renovate's `github-tags` datasource only matches curl `source_url`s hosted at `github.com` or `raw.githubusercontent.com`. Three current entries are **outside Renovate automation** and must be re-pinned manually:

- `claude-code-installer` (`https://claude.ai/install.sh`)
- `uv-installer` (`https://astral.sh/uv/install.sh`)
- `bun-installer` (`https://bun.sh/install`)

`.github/renovate.json` adds the `needs-manual-bump` label to these entries so they show up in dashboards. Re-pin cadence: same as the soft-pin SLA below for `claude-code-installer`; quarterly audit for the other two unless the upstream publishes a security advisory sooner. Run the one-line `sha256` recompute from §5 against the current bytes, update `version`/`sha256`/`last_audited`, and ship the bump PR yourself.

## 5. Soft-pin re-pin SLA

Some upstreams (notably `claude-code-installer` → `https://claude.ai/install.sh`) cannot be hard-pinned: Anthropic redeploys the script at any time. These entries have `soft_pin: true` in the manifest. Behaviour:

- **Hash mismatch in production** logs a warning *and the new hash* via `_thread_local.last_retry_stderr`, then proceeds (vs hard-pin which refuses to execute).
- **Maintainer audits the new script within 24 h**: read the diff between the cached pinned bytes and the new bytes. Look for new domain calls, sudo escalation, suspicious env vars.
- **Maintainer re-pins within 48 h**: edit the manifest entry, update `version`, `sha256`, `last_audited`, and ship a Pilot Shell patch release.

Compute the new hash with one of:

```bash
# Linux:
curl -fsSL https://claude.ai/install.sh | sha256sum

# macOS:
curl -fsSL https://claude.ai/install.sh | shasum -a 256
```

## 6. V1 explicit non-goals

The following are intentionally out of scope for V1 and tracked in the PRD's deferred section. Do **not** open issues claiming these as bugs.

- **OpenSSF Scorecard scoring loop** — adds CI complexity and helps least where the threat is highest (single-author npm packages without public repos). Revisit if attacks materialize.
- **Socket.dev real-time scanning** — requires external account + API key. Optional bolt-on if needed; the GitHub App can be installed independently without this PR.
- **Branch-protection required check** — the release-workflow `supply-chain-gate` job is the gate that matters; an extra merge-time gate is duplicative for a single-maintainer repo.
- **Pull-through artifact proxy** (Verdaccio, S3 mirror) — strongest possible defense, revisit at enterprise scale.
- **Customer-facing security page** + public SBOM publication — separate PRD.
- **Emergency hotfix runbook** / auto-rollback / launcher push notifications — manual hotfix is V1.
- **Replacing `claude.ai/install.sh`** with `@anthropic-ai/claude-code@<version>` (npm hard-pin) — separate PRD, individual replacement decision.
- **Dedicated `docs/security/audit-log.md` written by CI on merge** — V1 uses git history.
- **AST-based drift checker** — V1 regex is sufficient; graduate if false-positives appear.
