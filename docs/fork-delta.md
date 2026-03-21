# Fork Delta: `canstralian/pilot-shell-devsecops` vs `maxritter/pilot-shell`

> **Status:** Active audit document — updated as divergence grows.
> **Constraint:** All security claims are untreated as untrusted until demonstrated by observable controls.

---

## Purpose

This document tracks every known point of divergence between this fork and the upstream
`maxritter/pilot-shell` repository. It serves as the authoritative diff ledger for reviewers,
contributors, and security assessors who need to understand the fork's current state without
reading every file.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fork has diverged (intentional change present) |
| ⚠️ | Partial divergence — upstream artifact still present |
| ❌ | No divergence — upstream value still in use |
| 🔒 | Target hardened state (not yet reached) |

---

## 1. Installer

| Field | Upstream | This Fork | Status |
|-------|----------|-----------|--------|
| `REPO` variable | `maxritter/pilot-shell` | `canstralian/pilot-shell-devsecops` | ✅ |
| Release download base URL | `github.com/maxritter/pilot-shell` | `github.com/canstralian/pilot-shell-devsecops` | ✅ |
| Binary download URL | `github.com/maxritter/pilot-shell/releases/…` | `github.com/canstralian/pilot-shell-devsecops/releases/…` | ✅ |
| Install confirmation prompt | References `pilot` and `ccp` commands | Unchanged from upstream | ❌ |
| Integrity verification | None (no checksum or signature validation) | None | 🔒 |
| TLS pinning or TOFU policy | Not present | Not present | 🔒 |

---

## 2. Claude / Pilot Settings (`pilot/settings.json`)

| Setting | Upstream value | This Fork | Status |
|---------|---------------|-----------|--------|
| `permissions.defaultMode` | `"bypassPermissions"` | `"default"` | ✅ |
| `skipDangerousModePermissionPrompt` | `true` | `false` | ✅ |
| `enableAllProjectMcpServers` | `true` | `false` | ✅ |
| Upstream star tip in spinner | `"Please star the repository: github.com/maxritter/pilot-shell"` | Removed | ✅ |
| `companyAnnouncements` branding | References upstream localhost console | Unchanged | ❌ |
| `statusLine` command | `~/.pilot/bin/pilot statusline` | Unchanged | ❌ |

---

## 3. Plugin Metadata (`pilot/plugin.json`)

| Field | Upstream | This Fork | Status |
|-------|----------|-----------|--------|
| `author.name` | `Max Ritter` | Unchanged | ❌ |
| `author.email` | `mail@maxritter.net` | Unchanged | ❌ |
| `repository` | `https://github.com/maxritter/pilot-shell` | Unchanged | ❌ |
| `license` | `Proprietary` | Unchanged | ❌ |

> **Note:** Attribution should be preserved per the upstream license. These fields require
> legal review before modification. Fork identity should be added as supplementary fields
> rather than overwriting upstream author attribution where that attribution is required.

---

## 4. MCP Configuration (`pilot/.mcp.json`)

| Setting | Upstream | This Fork | Status |
|---------|----------|-----------|--------|
| `context7` server enabled | Yes (`npx -y @upstash/context7-mcp`) | Unchanged | ❌ |
| `codebase-memory-mcp` enabled | Yes | Unchanged | ❌ |
| `grep-mcp` (external HTTP) | Yes (`https://mcp.grep.app`) | Unchanged | ❌ |
| `web-search` enabled | Yes | Unchanged | ❌ |
| `web-fetch` enabled | Yes | Unchanged | ❌ |
| Per-server trust review | Not present | Not present | 🔒 |
| MCP server allowlist policy | Not present | Not present | 🔒 |

---

## 5. Documentation

| File | Upstream | This Fork | Status |
|------|----------|-----------|--------|
| `README.md` | Upstream product README | Temporary fork README (intentional) | ✅ |
| `docs/fork-delta.md` | Does not exist | This file | ✅ |
| `docs/devsecops-fork-roadmap.md` | Does not exist | Created | ✅ |
| `docs/docusaurus/` | Full upstream docs site | Unchanged (upstream content) | ❌ |
| `CHANGELOG.md` | Upstream changelog | Unchanged | ❌ |

---

## 6. Workflows (`.github/workflows/`)

| Workflow | Upstream | This Fork | Status |
|----------|----------|-----------|--------|
| `release.yml` | Upstream release process | Unchanged | ❌ |
| `release-dev.yml` | Upstream dev release | Unchanged | ❌ |
| `deploy-website.yml` | Upstream docs deploy | Unchanged | ❌ |
| SAST / CodeQL | Not present | Not present | 🔒 |
| Dependency review | Not present | Not present | 🔒 |
| Secret scanning | Not present | Not present | 🔒 |
| SBOM generation | Not present | Not present | 🔒 |

---

## 7. Rules and Agents (`pilot/rules/`, `pilot/agents/`)

| Item | Upstream | This Fork | Status |
|------|----------|-----------|--------|
| All rule files | Upstream rules | Unchanged | ❌ |
| DevSecOps rules | Not present | Not present | 🔒 |
| Threat-model rule | Not present | Not present | 🔒 |
| Secret-handling rule | Not present | Not present | 🔒 |

---

## 8. Pyproject / Package Metadata

| Field | Upstream | This Fork | Status |
|-------|----------|-----------|--------|
| `pyproject.toml` package name | `pilot-shell` upstream content | Unchanged | ❌ |
| `console/package.json` name | Upstream | Unchanged | ❌ |
| `pilot/package.json` name | Upstream | Unchanged | ❌ |

---

## Upstream Artifacts Still Present

The following retain upstream identity without fork-specific modification. Each represents
either a deferred change, an item pending legal review, or a known gap:

- `pilot/plugin.json` — upstream author metadata
- `pilot/.mcp.json` — unreviewed MCP server list inherited wholesale
- `docs/docusaurus/` — full upstream documentation site
- `.releaserc.json` — upstream release pipeline config referencing upstream files
- `cliff.toml` — changelog header references "Pilot Shell"
- `CHANGELOG.md` — upstream history
- All files in `pilot/rules/` and `pilot/agents/`

---

## Attribution Note

This fork is built on top of `maxritter/pilot-shell`. Credit for the original workflow engine,
rules architecture, and tooling model belongs to that project. Changes in this fork are additive
and security-oriented and do not claim to replace or supersede the upstream work.

---

*Last updated: 2026-03-21*
