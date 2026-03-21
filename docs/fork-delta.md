# Fork Delta: pilot-shell-devsecops vs. upstream pilot-shell

This document describes how this fork differs from the upstream `maxritter/pilot-shell`
project. It is maintained as a living record: sections are updated as changes are made.

---

## Purpose

The upstream project is a productivity-oriented AI-assisted development shell built on
Claude Code. It prioritizes developer experience, speed, and convenience.

This fork is a security-oriented reinterpretation of that foundation. The goal is to adapt
the same structured workflow mechanics (spec-driven development, hooks, rules, agents) into
a model that is appropriate for teams with explicit security, auditability, and compliance
requirements.

The fork is not a critique of the upstream project. It serves a different audience with
different constraints.

---

## Identity and Branding

| Area | Upstream | This Fork |
|------|----------|-----------|
| Project name | Pilot Shell | pilot-shell-devsecops |
| Author/org | maxritter / Max Ritter | canstralian |
| License | Proprietary | Under review (goal: OSS-compatible) |
| Repository reference | `maxritter/pilot-shell` | `canstralian/pilot-shell-devsecops` |
| `plugin.json` author | Max Ritter, mail@maxritter.net | canstralian |

### Remaining upstream references (to be cleaned up)

- `install.sh` line 5: `REPO="maxritter/pilot-shell"` — still pulls binaries from upstream
- `settings.json` spinner tips: two references to `github.com/maxritter/pilot-shell`
- `CHANGELOG.md`: all history reflects upstream release history

These are tracked in the roadmap as early cleanup targets.

---

## Permission Model

| Setting | Upstream default | This fork target |
|---------|-----------------|-----------------|
| `defaultMode` | `bypassPermissions` | `default` (require approval) |
| `skipDangerousModePermissionPrompt` | `true` | `false` |
| `enableAllProjectMcpServers` | `true` | `false` (explicit allow-list) |
| `DISABLE_INSTALLATION_CHECKS` | `true` | `false` |

**Current state:** The `pilot/settings.json` still reflects upstream defaults. Changing
these is a near-term priority. See roadmap item P1-PERM.

The upstream defaults trade off safety for zero-friction onboarding. For a DevSecOps
context, the appropriate default is to require explicit approval for dangerous actions and
to not auto-trust all MCP servers.

---

## Installation Security

| Area | Upstream | This Fork target |
|------|----------|-----------------|
| Install method | `curl ... \| bash` pipe-to-shell | Same shell script, but with integrity goals |
| uv install | `curl ... astral.sh/uv/install.sh \| sh` (no verification) | Pinned version + checksum verification |
| Binary download | No checksum or signature check | Require SHA-256 + optional sigstore verification |
| Binary source | `github.com/maxritter/pilot-shell/releases` | Fork's own releases |
| Provenance | GitHub attestation (upstream CI) | Inherit + document attestation verification |

**Current state:** `install.sh` still downloads binaries and the uv installer without any
integrity checking. The `download_file` function uses `curl -fsSL` with no `--checksum`
flag or post-download verification. This is tracked as P1-INSTALL.

The upstream CI does generate GitHub Attestations (via `actions/attest-build-provenance`),
which is a positive signal. This fork's goal is to surface that provenance to installers
and make verification a first-class step.

---

## MCP Server Trust Model

| Server | Type | Upstream posture | Fork assessment |
|--------|------|-----------------|-----------------|
| `context7` | `npx -y @upstash/context7-mcp` | Auto-install, unpinned | Medium risk: unpinned npm package |
| `codebase-memory-mcp` | Local binary via `sh -c` | Local | Low risk if binary is verified |
| `mem-search` | Local bun script | Local | Low risk |
| `web-search` | `npx -y open-websearch` | Auto-install, unpinned | Medium risk; data leaves machine |
| `grep-mcp` | `https://mcp.grep.app` (HTTP) | Remote HTTP MCP | High risk: all code queries leave machine |
| `web-fetch` | `npx -y fetcher-mcp` | Auto-install, unpinned | Medium risk |

**Key delta:** The fork should adopt a pinned, explicit MCP server allowlist with documented
data flow for each server. `grep-mcp` (remote HTTP) should be explicitly noted as
externalizing data. `npx -y` servers should have pinned versions and integrity hashes.

The `enableAllProjectMcpServers: true` setting (auto-trust all project MCP servers) should
be removed. See roadmap item P1-MCP.

---

## Hook Architecture

The upstream hook system is well-structured and covers 7 lifecycle events:

- `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`, `PreCompact`

This fork inherits this architecture unchanged. The hooks provide enforcement for spec
workflows, TDD, and code quality. These are a strong foundation for DevSecOps enforcement.

**Fork additions planned:**

- A `PreToolUse` hook for Bash that checks commands against a policy allowlist (P2-HOOK-BASH)
- A `PostToolUse` hook for Write/Edit that invokes static analysis (semgrep, bandit) (P2-HOOK-SAST)
- A `PreToolUse` hook for file writes to high-risk paths (secrets files, CI config) (P2-HOOK-PATH)
- A session-level audit log hook (P3-AUDIT)

---

## CI/CD Pipeline

The upstream CI/CD pipeline has several strong controls already in place:

- Pinned GitHub Actions to commit SHAs (all `uses:` lines use `@<sha>`)
- Trivy CRITICAL/HIGH vulnerability + secret scanning on release
- Manual approval gate (`environment: production`) before publishing
- Build provenance attestation via `actions/attest-build-provenance`
- `git-crypt` for encrypted content in the repo

**Fork delta:**

- The fork does not have its own secrets (`GIT_CRYPT_KEY`, `VERCEL_TOKEN`) — CI workflows
  will fail until these are configured or removed
- `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` in `release.yml` are upstream values and must be
  removed or replaced
- The `deploy-website.yml` workflow deploys to upstream Vercel infrastructure
- No SBOM generation (planned: P2-SBOM)
- No dependency license scanning (planned: P3-LICENSE)

---

## Rules and Standards

The upstream rules cover:

- `cli-tools.md`, `context-management.md`, `development-practices.md`
- `mcp-servers.md`, `playwright-cli.md`
- `standards-backend.md`, `standards-frontend.md`, `standards-golang.md`, `standards-python.md`, `standards-typescript.md`
- `task-and-workflow.md`, `testing.md`, `verification.md`, `code-review-reception.md`

These are workflow and quality standards, not security standards.

**Fork additions planned:**

- `rules/security-defaults.md` — threat modeling, input validation, secrets handling
- `rules/trust-boundaries.md` — explicit documentation of data flows and trust zones
- `rules/secure-review.md` — security acceptance criteria for spec workflows
- `rules/supply-chain.md` — dependency hygiene, version pinning, provenance

---

## Proprietary Components

The upstream `pilot` binary (distributed as a `.so` file, built from obfuscated Python) is
a proprietary component. It handles:

- License validation via Gumroad (`launcher/gumroad.py`)
- Tamper detection (`launcher/tests/unit/test_tamper_detection.py` references suggest
  the launcher detects modification)
- The `statusline` command
- Session and memory management internals

**Fork implications:**

- This fork cannot audit or modify the binary itself
- Any security claims about the binary cannot be verified from source
- The fork's security posture must not depend on guarantees from the proprietary binary
- Long-term: evaluate whether the binary should be replaced with open implementations

This is documented as a hard constraint in the roadmap.

---

## What is NOT changed (yet)

- Core hook logic (`pilot/hooks/`) — inherited unchanged, no security regressions added
- Spec workflow commands — inherited unchanged
- Agent definitions (`agents/`) — inherited unchanged
- Workflow rules — inherited unchanged (security rules are additive)
- Test suite — inherited unchanged

Changes to inherited functionality require a clear security justification and must not
break the underlying workflow model.

---

## Changelog

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-03-21 | Created `docs/fork-delta.md` | Establish audit baseline |
| 2026-03-21 | Updated `README.md` | Replace temporary placeholder with substantive fork identity |
| 2026-03-21 | Updated `pilot/plugin.json` | Remove upstream author attribution |
| 2026-03-21 | Created `docs/devsecops-fork-roadmap.md` | Publish prioritized implementation plan |
