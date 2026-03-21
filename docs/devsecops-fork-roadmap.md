# DevSecOps Fork Roadmap

**Repository:** `canstralian/pilot-shell-devsecops`
**Base version audited:** 7.7.1 (upstream `maxritter/pilot-shell`)
**Audit date:** 2026-03-21
**Status:** Active development

---

## Audit Summary

This roadmap is grounded in a hands-on audit of the inherited upstream codebase. The
following findings shaped the prioritization below.

### Critical findings

| ID | Finding | Location | Risk |
|----|---------|----------|------|
| F-01 | `defaultMode: bypassPermissions` — all Claude Code permission guardrails disabled | `pilot/settings.json` | Critical |
| F-02 | `skipDangerousModePermissionPrompt: true` — dangerous mode prompt suppressed | `pilot/settings.json` | Critical |
| F-03 | `install.sh` downloads and executes `uv` installer via `curl \| sh` with no integrity check | `install.sh:130` | High |
| F-04 | `install.sh` downloads `.so` binaries and `chmod +x`s them with no checksum or signature verification | `install.sh:278-337` | High |
| F-05 | `REPO="maxritter/pilot-shell"` — fork still pulls release artifacts from upstream author's GitHub | `install.sh:5` | High |
| F-06 | `enableAllProjectMcpServers: true` — auto-trusts all project-scope MCP servers | `pilot/settings.json` | High |
| F-07 | `DISABLE_INSTALLATION_CHECKS: "true"` — disables runtime installation integrity checks | `pilot/settings.json` | Medium |
| F-08 | `grep-mcp` MCP server routes all code queries to `https://mcp.grep.app` (external HTTP) | `pilot/.mcp.json` | Medium |
| F-09 | `npx -y` used for `context7`, `web-search`, `web-fetch` MCP servers — unpinned, auto-install | `pilot/.mcp.json` | Medium |
| F-10 | `plugin.json` author/repo still references upstream author and repository | `pilot/plugin.json` | Low |
| F-11 | Spinner tips in `settings.json` reference `github.com/maxritter/pilot-shell` | `pilot/settings.json` | Low |
| F-12 | Vercel project IDs and org ID (upstream infra) hardcoded in CI workflow | `.github/workflows/release.yml` | Low |

### Positive controls (inherited from upstream)

- GitHub Actions workflows pin all `uses:` references to commit SHAs — no floating tags
- Trivy vulnerability + secret scanning runs on every release path (CRITICAL/HIGH, exit-code 1)
- Manual approval gate (`environment: production`) before any artifact is published
- Build provenance attestation via `actions/attest-build-provenance` for all release binaries
- `git-crypt` encrypts sensitive content in-repo (launcher, docs/site/api)
- Hook system provides enforcement at 7 session lifecycle points
- Spec workflow enforces plan → approval → implement → verify loop
- `verification.md` rule explicitly requires evidence before completion claims

### Constraints

- The `pilot` binary is proprietary and distributed as a compiled `.so` — source not auditable
- License validation connects to Gumroad at runtime — external network dependency
- The fork cannot make security claims about binary internals without source access
- Any security guarantees must be grounded in the open-source portions (hooks, rules, installer,
  launcher Python, CI/CD)

---

## Roadmap

Items are grouped into priority tiers. Each item includes an effort estimate (S/M/L) and a
risk rating for the change itself (low/medium/high — risk of breaking things or introducing
regressions).

### P0 — Prerequisite: Identity and Baseline Integrity

These are cleanup tasks that must happen before any security claims are credible.

| ID | Task | Effort | Change risk | Status |
|----|------|--------|-------------|--------|
| P0-BRAND-01 | Update `pilot/plugin.json`: replace author name, email, repository URL | S | Low | Done |
| P0-BRAND-02 | Remove upstream repository reference from spinner tips in `settings.json` | S | Low | Pending |
| P0-BRAND-03 | Update `install.sh` REPO variable to fork's own release path (or document the dependency explicitly until fork has its own binary releases) | S | Medium | Pending |
| P0-BRAND-04 | Remove or replace Vercel project/org IDs in `release.yml` | S | Low | Pending |
| P0-DOC-01 | Replace upstream README with fork-oriented version (initial version done) | S | Low | Done |
| P0-DOC-02 | Create `docs/fork-delta.md` documenting divergence from upstream | S | Low | Done |
| P0-DOC-03 | Create this roadmap document | S | Low | Done |

---

### P1 — High-Impact Security Defaults

These directly address the most critical findings. Changing permission defaults affects
day-to-day UX — communicate changes clearly.

#### P1-PERM: Fix permission defaults

**Problem:** `defaultMode: bypassPermissions` disables all user approval prompts for
Claude Code actions. `skipDangerousModePermissionPrompt: true` suppresses the secondary
warning. Together, these mean the AI can write files, run bash commands, and call external
tools without any human checkpoint.

**Target state:**
```json
{
  "permissions": {
    "defaultMode": "default"
  },
  "skipDangerousModePermissionPrompt": false
}
```

For workflows that genuinely need reduced friction (CI environments, automated pipelines),
the appropriate pattern is to explicitly set `bypassPermissions` in that context rather than
as a global default.

**Effort:** S | **Change risk:** Medium (breaks zero-friction UX, requires user acknowledgment)

---

#### P1-MCP: Lock down MCP server trust

**Problem:** `enableAllProjectMcpServers: true` auto-trusts any MCP server defined in
`.mcp.json`. Combined with unpinned `npx -y` servers, this means arbitrary npm packages
are installed and executed automatically.

**Steps:**
1. Set `enableAllProjectMcpServers: false` in `settings.json`
2. Pin `npx`-based MCP servers to specific versions: `npx -y @upstash/context7-mcp@<version>`
3. Add integrity expectations (consider `npx --integrity` or switch to local installs)
4. Document the data flow for each enabled MCP server — especially `grep-mcp` (external HTTP)
5. Add a `docs/mcp-trust-register.md` listing each server, its trust level, what data it
   receives, and whether it externalizes data

**Effort:** M | **Change risk:** Low (additive, behavioral change limited to MCP auto-trust)

---

#### P1-INSTALL: Add binary integrity verification to `install.sh`

**Problem:** The installer downloads `.so` binaries and the `uv` installer from external
sources with no checksum or signature verification. A compromised CDN, MITM, or GitHub
release could substitute malicious binaries undetected.

**Steps:**
1. For `uv` install: pin to a specific version and verify the SHA-256 hash
   ```bash
   UV_VERSION="0.5.x"
   UV_EXPECTED_SHA="..."
   curl -LsSf "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-installer.sh" -o /tmp/uv-install.sh
   echo "${UV_EXPECTED_SHA}  /tmp/uv-install.sh" | sha256sum -c -
   sh /tmp/uv-install.sh
   ```
2. For pilot binaries: verify GitHub Attestation using `gh attestation verify` before
   executing the downloaded binary
3. Add `--fail-with-body` flag to `curl` calls to surface error content on failure
4. Consider offering a `--verify-only` mode that checks integrity without installing

**Effort:** M | **Change risk:** Medium (adds verification step that can break on hash mismatch)

---

### P2 — Enforcement Hooks

These add security-aware enforcement into the existing hook architecture. The hook system
is the right place to enforce policy — it fires at lifecycle boundaries and already gates
spec workflows.

#### P2-HOOK-BASH: Bash command policy hook

**Problem:** No hook currently validates Bash commands against a policy. The `tool_redirect.py`
hook exists in `PreToolUse` for Bash but its purpose is tool routing, not security policy.

**Proposed hook:** `pilot/hooks/bash_policy.py` — fires on `PreToolUse` for `Bash`

Behavior:
- Block or warn on high-risk patterns: `rm -rf`, `curl | sh`, `wget | sh`, `sudo` without
  justification, writes to `/etc/`, `chmod 777`, `export ... KEY`, `export ... TOKEN`
- Log all Bash commands to a per-session audit trail (see P3-AUDIT)
- Configurable via a `pilot/config/bash-policy.yaml` allowlist/denylist

**Effort:** M | **Change risk:** Medium (can break legitimate workflows — needs test coverage)

---

#### P2-HOOK-SAST: Static analysis on file write

**Problem:** The existing `file_checker.py` PostToolUse hook runs language-specific quality
checks (linting, type checking). It does not run security-focused analysis.

**Proposed extension:** Add a security analysis pass to `file_checker.py` or a parallel
`security_checker.py` hook:
- Python: `bandit -r <file>` for common security issues (hardcoded credentials, SQL injection,
  subprocess misuse, eval/exec)
- JavaScript/TypeScript: `semgrep` with the `javascript.security` ruleset
- General: `semgrep` with `generic.secrets` ruleset for accidental credential writes
- Only block on `ERROR` severity findings; warn on others

**Effort:** M | **Change risk:** Low (additive, non-blocking by default)

---

#### P2-HOOK-PATH: High-risk path guard

**Problem:** No hook protects writes to high-risk file paths (CI workflows, shell configs,
secrets files, sudoers).

**Proposed hook:** `pilot/hooks/path_guard.py` — fires on `PreToolUse` for `Write`, `Edit`, `MultiEdit`

Block or require explicit acknowledgment for writes to:
- `.github/workflows/` — CI pipeline modification
- `~/.bashrc`, `~/.zshrc`, `~/.profile`, `~/.ssh/` — shell/SSH config
- `/etc/`, `/usr/` — system paths
- Files matching `*.env`, `*secret*`, `*credential*`, `*private_key*`

**Effort:** S | **Change risk:** Low

---

#### P2-SBOM: Software Bill of Materials generation

**Problem:** No SBOM is generated for releases. Consumers cannot audit what dependencies
are included in release artifacts.

**Steps:**
1. Add `cyclonedx-python` to generate a Python SBOM during the release workflow
2. Add `cdxgen` or `syft` for the Node.js console component
3. Upload SBOM as a release artifact alongside the binaries
4. Store SBOM in `docs/sbom/` in the repo for the latest release

**Effort:** S | **Change risk:** Low (additive CI step)

---

### P3 — Auditability and Policy Infrastructure

These build the audit trail, policy documentation, and governance layer.

#### P3-AUDIT: Session audit log

**Problem:** There is no durable audit trail of what actions were taken in a session. The
`mem-search` MCP server stores observations, but this is a convenience feature, not an
audit log.

**Proposed:** A `SessionEnd` hook writes a structured JSON log to `~/.pilot/audit/` containing:
- Session ID, start/end time
- All tool calls (tool name, inputs summary, exit code)
- All Bash commands executed
- Files written/modified
- Spec plan ID if a spec workflow was active

This does not capture file contents (privacy constraint) but creates a verifiable activity
record. Log rotation and retention policy should be configurable.

**Effort:** M | **Change risk:** Low

---

#### P3-RULES-SEC: Security rules for spec workflows

**Problem:** Spec workflow planning and verification (`spec-plan.md`, `spec-verify.md`)
have no security acceptance criteria. A plan can be approved and verified without any
security requirements being checked.

**Proposed new rules:**
- `pilot/rules/security-defaults.md` — OWASP-aligned defaults for new code: input
  validation, output encoding, authentication patterns, secret management
- `pilot/rules/trust-boundaries.md` — require explicit documentation of trust zones in
  any design that touches external input, network, or storage
- `pilot/rules/secure-review.md` — add security acceptance criteria to spec plan templates;
  require a threat model for any feature involving authentication, authorization, or data
  handling

**Effort:** M | **Change risk:** Low (additive rules, no behavior change)

---

#### P3-LICENSE: Dependency license scanning

**Problem:** No CI step checks that dependency licenses are compatible with the fork's
intended license. This matters if the fork moves toward open-source distribution.

**Steps:**
1. Add `pip-licenses` to the Python CI step to generate a license report
2. Add `license-checker` or `licensee` for Node.js
3. Flag any GPL or AGPL dependencies that would impose copyleft requirements

**Effort:** S | **Change risk:** Low (informational, non-blocking initially)

---

#### P3-THREAT-MODEL: Threat model document

**Problem:** There is no threat model for the system. Without one, security decisions are
reactive and incomplete.

**Deliverable:** `docs/threat-model.md` covering:
- Trust boundaries: local filesystem, Claude API, MCP servers (local vs. remote), CI/CD, release infra
- Assets: source code, session memory, API keys, session state, release binaries
- Threat actors: malicious MCP server, compromised upstream dependency, prompt injection via
  file content, exfiltration via MCP web-fetch/grep-mcp
- Existing controls mapped to threats
- Gaps (open threats with no current control)

**Effort:** L | **Change risk:** Low (documentation only)

---

#### P3-POLICY-GATE: Policy-as-code gate for spec workflows

**Problem:** The spec workflow's `spec_plan_validator.py` and `spec_verify_validator.py`
hooks validate workflow state but not security posture. A spec can complete without any
security review step.

**Proposed extension:** Add a configurable policy gate to `spec_stop_guard.py` that checks
whether a security review step was completed before allowing the session to end. The policy
can start as a lightweight checklist:
- Does the plan include a threat assessment section? (required for P2-P3 risk features)
- Did verification include at least one SAST run?
- Were no `ERROR`-level findings suppressed without documented justification?

**Effort:** M | **Change risk:** Medium (blocks workflows until policy conditions are met)

---

## Implementation Order Summary

| Priority | ID | Description | Effort | Risk |
|----------|----|-------------|--------|------|
| 1 | P0-BRAND-* | Branding/identity cleanup | S | Low |
| 2 | P1-PERM | Fix bypassPermissions default | S | Medium |
| 3 | P1-MCP | Lock down MCP trust model | M | Low |
| 4 | P1-INSTALL | Binary integrity verification | M | Medium |
| 5 | P2-HOOK-PATH | High-risk path write guard | S | Low |
| 6 | P2-HOOK-SAST | SAST on file write | M | Low |
| 7 | P2-HOOK-BASH | Bash command policy | M | Medium |
| 8 | P2-SBOM | SBOM generation in CI | S | Low |
| 9 | P3-RULES-SEC | Security rules for spec | M | Low |
| 10 | P3-AUDIT | Session audit log | M | Low |
| 11 | P3-LICENSE | Dependency license scanning | S | Low |
| 12 | P3-THREAT-MODEL | Threat model document | L | Low |
| 13 | P3-POLICY-GATE | Policy gate for spec workflows | M | Medium |

---

## Definition of Done

A roadmap item is complete when:

1. The change is implemented and committed with a clear commit message referencing the item ID
2. Any new behavior has test coverage
3. `docs/fork-delta.md` is updated to reflect the change
4. If the item changes defaults or workflow behavior, a note is added to the README

---

## Out of Scope

The following are explicitly not goals for this fork:

- Replacing or re-implementing the proprietary `pilot` binary
- Building a competing commercial product
- Adding features unrelated to security, auditability, or governance
- Maintaining compatibility with commercial Gumroad license checks beyond what the binary requires
