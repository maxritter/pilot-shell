# DevSecOps Control Plane

> Secure delivery architecture for the Pilot Shell DevSecOps fork.

## 1. Purpose

This document defines the **secure delivery workflow** governing how code moves from a developer's local machine through Claude Code-assisted development, automated gates, and CI/CD pipelines to production release. It establishes the control plane: who can approve what, at what stage, and with what evidence.

---

## 2. Guiding Principles

| Principle | Meaning |
|-----------|---------|
| **Policy over prompt** | Behaviour is defined in files and hooks, not model memory |
| **Evidence before merge** | No merge without verifiable artefacts (tests, scans, plans) |
| **Minimal blast radius** | Each action is scoped to the narrowest necessary permission |
| **Explicit trust** | Trust is granted by configuration, not inferred from context |
| **Auditability first** | Every gate produces a structured, machine-readable record |

---

## 3. Delivery Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE                                                              │
│                                                                             │
│  Developer ──► /spec (plan phase)                                          │
│                     │                                                       │
│                     ▼                                                       │
│              spec_plan_validator.py  ──── GATE: plan quality               │
│                     │                                                       │
│                     ▼                                                       │
│           /spec-implement (code phase)                                      │
│                     │                                                       │
│                     ▼                                                       │
│         file_checker.py + checker plugins  ── GATE: syntax / types        │
│                     │                                                       │
│                     ▼                                                       │
│            /spec-verify (proof phase)                                       │
│                     │                                                       │
│                     ▼                                                       │
│          spec_stop_guard.py  ──── GATE: tests must pass                    │
│                     │                                                       │
│                     ▼                                                       │
│         .githooks/pre-commit  ──── GATE: Trivy + unit tests + typecheck   │
│                     │                                                       │
│                     ▼                                                       │
│              git push origin                                                │
└───────────────────────────────────────┬────────────────────────────────────┘
                                        │
                ┌───────────────────────▼────────────────────────┐
                │  CI / GITHUB ACTIONS                           │
                │                                                │
                │  PR opened                                     │
                │       │                                        │
                │       ▼                                        │
                │  claude.yml (delta review)  ── GATE: review   │
                │       │                                        │
                │       ▼                                        │
                │  Policy check workflow      ── GATE: policy   │
                │  (secret scan, dep audit)                      │
                │       │                                        │
                │       ▼                                        │
                │  Human review approval      ── GATE: required │
                │       │                                        │
                │       ▼                                        │
                │  Merge to main                                 │
                │       │                                        │
                │       ▼                                        │
                │  release.yml  ──── GATE: semantic-release     │
                │                    version + changelog         │
                │       │                                        │
                │       ▼                                        │
                │  GitHub Release + artefacts                    │
                └────────────────────────────────────────────────┘
```

---

## 4. Gate Inventory

Each gate produces evidence. Evidence is required before the next stage proceeds.

### 4.1 Local Gates

| Gate | Trigger | Implementation | Evidence Produced |
|------|---------|----------------|-------------------|
| **Plan quality** | `/spec` plan phase | `spec_plan_validator.py` | Structured validation output in `.claude/specs/<feature>/plan.md` |
| **Code syntax/types** | PostToolUse (Write/Edit) | `file_checker.py` + checkers | Pass/fail per file, logged to session |
| **TDD enforcement** | PostToolUse | `tdd.py` checker | Failing tests required before implementation |
| **Test passage** | `/spec-verify` | `spec_stop_guard.py` | All tests green; no merge without this |
| **Security scan** | pre-commit | Trivy (CRITICAL+HIGH) | Exit 1 on violations; exceptions in `.trivyignore` |
| **Unit tests** | pre-commit | pytest (launcher, installer, hooks) | Exit 1 on failure |
| **Type check** | pre-commit | TypeScript + basedpyright | Exit 1 on error |

### 4.2 CI Gates

| Gate | Trigger | Implementation | Evidence Produced |
|------|---------|----------------|-------------------|
| **Delta code review** | PR open/update | `claude.yml` action | Sticky review comment with findings |
| **Secret scan** | PR open | _to be implemented_ | Scan report as PR check |
| **Dependency audit** | PR open | _to be implemented_ | Dependency report as PR check |
| **Policy check** | PR open | _to be implemented_ | Policy compliance status |
| **Human approval** | PR ready | GitHub branch protection | Approval record on PR |
| **Release validation** | Merge to main | `release.yml` | Semver tag + CHANGELOG entry + GitHub Release |

---

## 5. Minimum Evidence Before Merge

A pull request **must not merge** unless all of the following are present:

```
[ ] Passing pre-commit hook (security scan + tests + typecheck)
[ ] Green CI checks (all required status checks passing)
[ ] Delta code review from Claude Code action (no open blockers)
[ ] Secret scan clean (no detected secrets in diff)
[ ] Dependency audit (no new CRITICAL/HIGH CVEs introduced)
[ ] At least one human reviewer approval
[ ] Spec verification record (for feature work): .claude/specs/<feature>/verify.md
[ ] Changelog entry drafted (conventional commit triggers this automatically)
```

For **releases**, additionally:

```
[ ] All merge evidence above applied to every included PR
[ ] Semantic version tag created by release.yml
[ ] GitHub Release artefact published
[ ] CHANGELOG.md updated via cliff.toml
```

---

## 6. Extension / Rules / Skills / Agent Trust Model

Extensions to the control plane are themselves subject to the control plane.

### 6.1 Rules (`pilot/rules/`)

- Rules are **policy documents** read by Claude Code at session start.
- They constrain behaviour but are **not enforced code**; hooks enforce.
- Changes to rules require the same PR + review process as code.
- Rules files must not grant permissions beyond what `pilot/claude.json` allows.
- New rules require a corresponding hook or checker if they assert executable behaviour.

### 6.2 Skills (`pilot/commands/`, `.claude/skills/`)

- Skills are **task templates** invokable by developers.
- Skills that perform file writes, shell execution, or network calls are **Tier 2** actions (see `risk-tiers.md`).
- Skills sourced from third parties require review before installation.
- Auto-loaded skills (ambient discovery) must be explicitly allowlisted in `settings.json`.

### 6.3 Hooks (`pilot/hooks/`)

- Hooks run **as the local user** with local filesystem and subprocess access.
- Hooks are **the enforcement layer**; all policy must flow through hooks or CI.
- New hooks undergo full spec + review before activation.
- Hook timeouts must be set; unbounded hooks are disallowed.
- Hooks must not make outbound network calls without explicit policy approval.

### 6.4 MCP Servers (`pilot/.mcp.json`)

- MCP servers run with the permissions of the Claude Code process.
- Each server is a **trust boundary crossing** (see `trust-boundaries.md`).
- Servers must be pinned to specific versions/commit refs where possible.
- Servers that execute arbitrary shell commands are **Tier 3** actions.
- New MCP server additions require a PR with documented threat model.

### 6.5 Agents / Sub-agents

- Sub-agents (e.g., `spec-reviewer.md`, `plan-reviewer.md`) operate within the same session permissions.
- Agent-generated code is treated identically to human-generated code: same gates apply.
- Agents must not be granted permissions exceeding those in `claude.json`.
- Agent spawning by other agents (recursive agent chains) is **Tier 3** and requires explicit allowlisting.

---

## 7. Autonomous vs. Approval-Gated Actions

See `risk-tiers.md` for the full taxonomy. Summary:

| Autonomous (no human gate) | Approval-Gated |
|---------------------------|----------------|
| Read files, search code | Write to files outside the working directory |
| Run linters and formatters | Execute shell commands not in allowlist |
| Run unit tests | Modify CI/CD workflows |
| Generate plans and specs | Add/modify MCP servers |
| Create draft PRs | Push to main/protected branches |
| Fetch public documentation | Release artefact publication |
| Secret scanning | Modify hook definitions |
| Dependency audit reads | Install new dependencies |

---

## 8. Deviation Protocol

When a gate fails or is bypassed:

1. **Record** the bypass reason in the PR description or commit message.
2. **Reference** the exception in `.trivyignore` or equivalent with expiry date.
3. **Open a follow-up issue** tagged `security-debt` within 24 hours.
4. **Reviewer acknowledgment** required in approval comment for any gate bypass.

Bypasses to pre-commit (`--no-verify`) are **prohibited** except in break-glass scenarios with post-incident review.

---

## 9. Secrets Management

- Secrets are **never committed**, including in `.env` files, test fixtures, or documentation.
- Environment variables for CI are stored in GitHub Actions encrypted secrets.
- `git-crypt` protects encrypted paths (`launcher/`, `console/`, `docs/site/api/`).
- Local `.env` files are listed in `.gitignore`; presence is checked by the secret scan hook.
- Rotation procedure: rotate in secrets manager → update GitHub Actions secret → no code change required.

---

## 10. Feedback Loops

| Signal | Consumer | Action |
|--------|---------|--------|
| Pre-commit failure | Developer | Fix before push |
| CI check failure | Developer + Reviewer | Block merge |
| Claude review finding | Developer | Address or explicitly dismiss |
| CVE in dependency audit | Developer | Patch or document exception |
| `security-debt` issue backlog | Team | Sprint triage |
| Release failure | On-call | Roll back tag, investigate |
