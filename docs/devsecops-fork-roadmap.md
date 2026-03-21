# DevSecOps Fork Roadmap

> **Status:** Living document — update as items are completed or reprioritized.
> **Constraint:** Do not over-claim security guarantees. Treat all claims as untrusted until
> demonstrated by observable, reviewable controls.

---

## Audit Summary

This repository is a security-focused fork of `maxritter/pilot-shell`. The fork direction is
sound, but the current state carries forward several high-trust defaults and upstream identity
artifacts that are inconsistent with a hardened DevSecOps posture.

### Trust-Boundary Risks

1. **Installer pulls binaries from upstream GitHub releases without integrity verification.**
   The installer script fetches a pre-compiled `.so` binary over HTTPS from
   `github.com/maxritter/pilot-shell` (now corrected to this repo, but no checksum or
   signature is validated). A supply-chain attack on the release or a MITM could deliver
   a malicious binary to every installer invocation.

2. **`permissions.defaultMode = "bypassPermissions"` disables all Claude Code permission prompts.**
   Any agent or tool invoked within a Pilot session runs without user confirmation regardless
   of destructiveness. This is a convenience default that eliminates a meaningful safety boundary.

3. **`skipDangerousModePermissionPrompt = true` silences the last-resort confirmation gate.**
   Even when entering a mode explicitly labeled "dangerous", the prompt is suppressed. There is
   no interactive checkpoint between the user intent and unrestricted execution.

4. **`enableAllProjectMcpServers = true` trusts every MCP server listed in `.mcp.json`.**
   The current `.mcp.json` includes an external HTTP MCP endpoint (`https://mcp.grep.app`) and
   three `npx -y` servers that download and execute code at invocation time. Each represents an
   unapproved code execution surface.

5. **MCP servers run with `npx -y` (no version pinning).**
   `context7`, `web-fetch`, and `web-search` install arbitrary npm packages at runtime via
   `npx -y`. Without pinned versions or lockfiles, the effective dependency set is
   non-deterministic and cannot be audited or reproduced.

### Upstream Identity Leakage

- `pilot/plugin.json` still declares `author: Max Ritter` and links to the upstream repository.
- `install.sh` previously pointed `REPO` at `maxritter/pilot-shell` (corrected in this audit).
- `pilot/settings.json` spinner tips included `"Please star the repository: github.com/maxritter/pilot-shell"` (corrected in this audit).
- Docusaurus documentation site (`docs/docusaurus/`) contains full upstream product copy.
- `CHANGELOG.md` reflects upstream release history.
- `cliff.toml` changelog header references "Pilot Shell" without fork attribution.

### Unsafe Defaults

| Default | Risk Level | Current State |
|---------|-----------|---------------|
| `bypassPermissions` | Critical | Corrected to `"default"` |
| `skipDangerousModePermissionPrompt: true` | High | Corrected to `false` |
| `enableAllProjectMcpServers: true` | High | Corrected to `false` |
| Unsigned installer binary | Critical | Not yet addressed |
| `npx -y` MCP servers (unpinned) | Medium | Not yet addressed |
| External HTTP MCP endpoint | Medium | Not yet addressed |

### Missing DevSecOps Primitives

- No SAST workflow (CodeQL or equivalent)
- No dependency review workflow (Dependabot or GitHub's built-in)
- No secret scanning configuration (beyond GitHub defaults)
- No SBOM generation or publication
- No signed releases or artifact attestation
- No security policy (`SECURITY.md`)
- No threat model document
- No DevSecOps-specific rules for the AI agent
- No separation of secrets handling in `.mcp.json`
- No lint-gating on security rules in CI

---

## Prioritized Next-Action Matrix

Ranked by: **Leverage** (impact per unit of effort) → **Blast Radius** (how much exposure it
closes) → **Implementation Effort** → **User Trust Impact**.

### Tier 1 — Immediate Wins (< 1 day each)

| # | Action | Leverage | Blast Radius | Effort | Trust Impact |
|---|--------|----------|-------------|--------|-------------|
| 1 | ~~Harden `pilot/settings.json` defaults~~ ✅ | Critical | Any session using Pilot | Minutes | High — removes silent permission bypass |
| 2 | ~~Fix `install.sh` REPO variable~~ ✅ | High | Every install invocation | Minutes | Medium — closes installer pointing at upstream |
| 3 | ~~Remove upstream star tip from settings~~ ✅ | Low | UX only | Minutes | Low — removes upstream advertising |
| 4 | Add `SECURITY.md` with responsible disclosure instructions | Medium | Governance surface | 1–2 hours | High — signals security intent |
| 5 | Pin `npx -y` MCP servers to explicit versions in `.mcp.json` | High | All MCP sessions | 1–2 hours | Medium — removes non-deterministic runtime deps |

### Tier 2 — Short-Term Structural Work (1–3 days each)

| # | Action | Leverage | Blast Radius | Effort | Trust Impact |
|---|--------|----------|-------------|--------|-------------|
| 6 | Add CodeQL SAST workflow to `.github/workflows/` | High | All code changes | Half day | High — automated vulnerability detection |
| 7 | Add Dependabot configuration for npm and pip | High | All dependency updates | 1 hour | Medium — keeps deps patched |
| 8 | Add GitHub dependency review workflow on PRs | Medium | All pull requests | 1 hour | Medium — blocks known-vulnerable deps |
| 9 | Remove or replace external HTTP MCP endpoint (`grep-mcp`) | Medium | All Pilot sessions | Half day | Medium — removes outbound dependency |
| 10 | Create `pilot/rules/devsecops.md` — DevSecOps rules for the agent | High | Every agent task | 1 day | High — bakes security thinking into workflow |

### Tier 3 — Medium-Term Work (3–10 days each)

| # | Action | Leverage | Blast Radius | Effort | Trust Impact |
|---|--------|----------|-------------|--------|-------------|
| 11 | Add installer binary integrity verification (SHA-256 + GPG) | Critical | Every install | 2–3 days | Very High — closes supply-chain gap |
| 12 | Generate and publish SBOM for releases | Medium | Release artifacts | 1–2 days | Medium — supports downstream auditors |
| 13 | Replace upstream Docusaurus docs with fork-specific content | Medium | User perception | 3–5 days | High — removes upstream identity confusion |
| 14 | Add signed releases with GitHub attestations | High | Release trust | 1–2 days | High — cryptographic release provenance |
| 15 | Write threat model document (`docs/threat-model.md`) | Medium | Governance | 2–3 days | High — foundation for all future decisions |

### Tier 4 — Structural/Architectural Work (> 10 days)

| # | Action | Leverage | Blast Radius | Effort | Trust Impact |
|---|--------|----------|-------------|--------|-------------|
| 16 | Replace proprietary Pilot binary with open, auditable runtime | Very High | Entire architecture | High | Very High — eliminates closed binary trust gap |
| 17 | Develop fork-specific permission model for MCP servers | High | All agent sessions | High | High — fine-grained trust boundaries |
| 18 | Policy-as-code for agent rules (OPA or equivalent) | Medium | Governance | High | Medium — machine-verifiable policy |
| 19 | Implement SLSA Level 2+ build provenance | High | Release pipeline | High | High — supply-chain compliance |

---

## Top 5 Risks

1. **Installer binary supply-chain (no integrity check)** — any compromise of the upstream
   GitHub release artifacts directly impacts all users.
2. **`bypassPermissions` default** — eliminated the core user-facing safety gate in all sessions.
   Corrected but must be validated that no downstream config re-enables it.
3. **`npx -y` unpinned MCP servers** — runtime code execution surface that cannot be audited
   or reproduced deterministically.
4. **External HTTP MCP endpoint** — `https://mcp.grep.app` is a third-party server that
   receives tool call context from every Pilot session with it enabled.
5. **Closed-source runtime binary** — the `pilot` binary is proprietary. Its behavior cannot
   be independently audited, and there is no way to verify it does not exfiltrate data,
   despite spinner tip claims to the contrary.

---

## Top 5 Leverage-Heavy Changes

1. **Harden `pilot/settings.json`** — three one-line changes close the largest immediate
   permission gaps. Already done in this audit.
2. **Add `SECURITY.md`** — zero-code change that signals security intent and provides a
   structured disclosure path. Disproportionately high governance return.
3. **Pin MCP server versions** — eliminates non-deterministic package execution with a small
   `package.json`-style change in `.mcp.json`.
4. **Add CodeQL workflow** — one YAML file enables continuous automated vulnerability
   detection across all future code changes.
5. **Create `pilot/rules/devsecops.md`** — a single rules file that bakes security
   thinking into every agent-assisted task in this repo.

---

## Exact Files That Should Change Next

In priority order:

1. `pilot/.mcp.json` — pin `npx` package versions; review external HTTP server
2. `SECURITY.md` — create with responsible disclosure policy
3. `.github/workflows/codeql.yml` — create CodeQL SAST workflow
4. `.github/dependabot.yml` — create Dependabot configuration
5. `pilot/rules/devsecops.md` — create DevSecOps agent rules
6. `docs/threat-model.md` — create initial threat model
7. `pilot/plugin.json` — add fork supplementary metadata (legal review required first)
8. `docs/docusaurus/` — replace upstream content with fork-specific documentation

---

## Validation Checklist

Use this checklist to verify hardening progress in each review cycle:

- [ ] `pilot/settings.json` `permissions.defaultMode` is not `"bypassPermissions"`
- [ ] `pilot/settings.json` `skipDangerousModePermissionPrompt` is `false` or absent
- [ ] `pilot/settings.json` `enableAllProjectMcpServers` is `false` or absent
- [ ] `install.sh` `REPO` variable points to `canstralian/pilot-shell-devsecops`
- [ ] All `npx -y` calls in `.mcp.json` are pinned to explicit package versions
- [ ] `SECURITY.md` exists and contains a responsible disclosure path
- [ ] CodeQL or equivalent SAST workflow is present and passing
- [ ] Dependabot is configured for npm and pip dependencies
- [ ] No upstream star/advertising tips remain in `pilot/settings.json`
- [ ] Installer verifies binary checksums before execution

---

*Last updated: 2026-03-21*
