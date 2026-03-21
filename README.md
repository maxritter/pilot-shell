<div align="center">

# pilot-shell-devsecops

**A security-oriented fork of Pilot Shell for AI-assisted engineering with explicit trust
boundaries, policy enforcement, and auditable workflows.**

</div>

---

## What this is

This is a fork of [`maxritter/pilot-shell`](https://github.com/maxritter/pilot-shell),
adapted for teams and individuals who need AI-assisted development with stronger security
controls, clearer governance, and verifiable delivery.

The upstream project builds a structured development workflow on top of Claude Code:
spec-driven planning, enforced verification, reusable rules, and lifecycle hooks. This fork
preserves that foundation and extends it with a security-first operating model.

---

## How this differs from upstream

| Area | Upstream | This fork |
|------|----------|-----------|
| Permission default | `bypassPermissions` | `default` (approval required) — *planned* |
| MCP server trust | Auto-trust all project servers | Explicit allowlist, pinned versions — *planned* |
| Install integrity | No checksum/signature checks | Binary verification via GitHub Attestation — *planned* |
| Security rules | Quality and workflow standards | Quality + security acceptance criteria — *planned* |
| Bash enforcement | None | Command policy hook — *planned* |
| SAST | None | `bandit`/`semgrep` on file write — *planned* |
| Audit trail | Memory system (convenience) | Structured session audit log — *planned* |
| SBOM | None | CycloneDX generation in CI — *planned* |

Items marked *planned* are in the roadmap but not yet implemented. See
[`docs/devsecops-fork-roadmap.md`](docs/devsecops-fork-roadmap.md) for the full plan with
effort and risk ratings.

For a detailed diff of current vs. target state, see
[`docs/fork-delta.md`](docs/fork-delta.md).

---

## Current status

This fork is in active restructuring. The workflow core (spec commands, hooks, rules) is
inherited from upstream and functional. Security-specific changes are being introduced
incrementally, with small reviewable commits.

**Do not treat this repository as a finished security platform.** The upstream defaults
(including `bypassPermissions`) are still present in some configuration files while
replacement work is in progress. Validate the actual configuration before use.

---

## What you get today (inherited from upstream)

- **Spec-driven development** — `/spec` command for structured planning, implementation,
  and verification with a mandatory plan approval gate
- **Lifecycle hooks** — 7 hook points (SessionStart, UserPromptSubmit, PreToolUse,
  PostToolUse, Stop, SessionEnd, PreCompact) for automated quality enforcement
- **Quality checks** — linting, type-checking, and TDD enforcement on every file write
  (Python, TypeScript, Go)
- **Pinned CI actions** — all GitHub Actions workflows reference commit SHAs, not floating
  tags
- **Trivy scanning** — vulnerability and secret scanning on every release path, blocking
  on CRITICAL/HIGH
- **Release approval gate** — manual approval required before any artifact is published
  (`environment: production`)
- **Build provenance attestation** — all release binaries attested via
  `actions/attest-build-provenance`

---

## What is being added (this fork)

The near-term implementation targets, in order:

1. **Fix permission defaults** (P1-PERM) — change `bypassPermissions` to `default`
2. **MCP trust lockdown** (P1-MCP) — disable auto-trust, pin versions, document data flows
3. **Binary integrity verification** (P1-INSTALL) — verify checksums and attestations at
   install time
4. **High-risk path guard hook** (P2-HOOK-PATH) — block/warn on writes to CI, shell, and
   secrets paths
5. **SAST on file write** (P2-HOOK-SAST) — run `bandit`/`semgrep` after every write
6. **Bash command policy hook** (P2-HOOK-BASH) — enforce a configurable command policy
7. **SBOM in CI** (P2-SBOM) — CycloneDX SBOMs for Python and Node.js components
8. **Security rules** (P3-RULES-SEC) — security acceptance criteria in spec workflows
9. **Session audit log** (P3-AUDIT) — structured per-session activity record
10. **Threat model** (P3-THREAT-MODEL) — documented trust boundaries and attack surface

---

## Constraints

- The `pilot` binary is **proprietary** and not open-source. This fork cannot audit or
  modify it. Security claims do not extend to binary internals.
- License validation connects to Gumroad at runtime (inherited from upstream).
- The installer currently still references the upstream GitHub repository for binaries.
  Until this fork publishes its own releases, the install script pulls from upstream.

---

## Contributing

Contributions are welcome in the following areas:

- Security rule authoring (OWASP-aligned, threat-model-grounded)
- Hook implementations for the roadmap items above
- Documentation of trust boundaries and data flows
- CI/CD improvements (SBOM, license scanning, provenance)
- Threat modeling

All contributions should be small and reviewable. No vague security claims without
supporting code or documentation.

---

## Repository layout

```
pilot/
  hooks/          Lifecycle hooks (quality, spec enforcement, memory)
  rules/          Always-loaded markdown rules for Claude Code
  commands/       On-demand slash commands (/spec, /setup-rules, etc.)
  agents/         Sub-agent definitions (plan-reviewer, spec-reviewer)
  settings.json   Claude Code plugin settings
  .mcp.json       MCP server configuration
installer/        Python installer (uv-based)
launcher/         Python launcher (wraps the pilot binary)
.github/          CI/CD workflows (release, deploy, claude)
docs/             Fork documentation (roadmap, delta, threat model)
```

---

<div align="center">

**Build with structure. Verify with rigor. Ship with evidence.**

</div>
