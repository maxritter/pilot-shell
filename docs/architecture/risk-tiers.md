# Risk Tiers

> Action classification system for Pilot Shell DevSecOps. Defines which actions Claude Code and automation may take autonomously, which require approval, and what evidence is required.

## 1. Tier Definitions

| Tier | Name | Autonomous? | Gate Required | Evidence |
|------|------|------------|---------------|---------|
| **T0** | Read-only / Observe | Yes | None | None |
| **T1** | Local write / Test | Yes | Post-action validation | Test results, lint pass |
| **T2** | State change / Deploy-adjacent | No — but auto-approved with pre-conditions | Pre-conditions met | Spec plan, scan results |
| **T3** | Privileged / Irreversible | No — human approval required | Explicit approval | PR approval + evidence chain |

### Decision Rule

```
Is the action reversible with a single git operation?
  YES ──► Can it affect shared state (CI, release, remote services)?
            NO  ──► T1 (autonomous with validation)
            YES ──► T2 (pre-conditions required)
  NO  ──► T3 (human approval required)

Is the action read-only with no persistent side effects?
  YES ──► T0 (fully autonomous)
```

---

## 2. Tier 0 — Read-Only / Observe

**Autonomous.** No gate. No evidence required.

These actions can be taken at any time, by Claude Code, hooks, MCP servers, or CI, without human review.

### Action Classes

| Category | Examples |
|---------|---------|
| **File system reads** | Read source files, configs, docs, logs |
| **Codebase search** | Grep, glob, AST traversal, Probe queries |
| **Test execution (read results)** | Run tests, read output — no file changes |
| **Type checking** | Run basedpyright, TypeScript compiler — diagnostic only |
| **Linting (read mode)** | Ruff check, eslint — no auto-fix |
| **Memory reads** | Read session memory, CLAUDE.md, specs |
| **MCP reads** | Query codebase-memory-mcp, context7 docs |
| **Git status/log** | `git status`, `git log`, `git diff` — read only |
| **Dependency reads** | Read lock files, `pip list`, `npm ls` |
| **Security scan (report)** | Trivy scan — report only, no blocking |
| **Public documentation fetch** | `web-fetch` for official docs |
| **Web search** | `web-search` for public information |

### Threat Note

Even read operations can carry risk if they pull untrusted content into context (prompt injection). MCP reads from remote/external sources are T0 by default but should be treated with input-awareness by downstream actions.

---

## 3. Tier 1 — Local Write / Test

**Autonomous, with post-action validation.** No human approval, but a gate must run after.

These actions modify local files or execute local processes but are:
- **Reversible** via git
- **Contained** to the local working directory
- **Validated** by an automated gate immediately after

### Action Classes

| Category | Examples | Post-Gate |
|---------|---------|----------|
| **Source file writes** | Write/Edit `.py`, `.ts`, `.go`, `.md` files in project | `file_checker.py` + language checker |
| **Test file writes** | Write test files, fixtures | Test run (must pass or fail expectedly for TDD) |
| **Config file writes** | `.env.example`, `pyproject.toml`, `package.json` (non-CI) | Lint + format check |
| **Documentation writes** | Write docs within `docs/` | No executable gate; visual review |
| **Auto-formatting** | `ruff format`, `prettier`, `gofmt` | Typecheck must still pass |
| **Spec plan writes** | Write `.claude/specs/<feature>/plan.md` | `spec_plan_validator.py` |
| **Spec verify writes** | Write `.claude/specs/<feature>/verify.md` | `spec_stop_guard.py` (tests green) |
| **Git staging** | `git add` specific files | Pre-commit hook (on commit) |
| **Local build** | `bun build`, `vite build` — local only | Build exit code 0 |
| **Linting (auto-fix)** | `ruff --fix`, `eslint --fix` | Typecheck must still pass |

### Conditions for Autonomous T1 Execution

1. Action is within the current working directory or explicitly scoped project path.
2. No credentials, secrets, or tokens are involved.
3. A spec plan (`plan.md`) exists for the feature being implemented.
4. Post-action validation hook is registered and will run.

---

## 4. Tier 2 — State Change / Deploy-Adjacent

**Requires pre-conditions to be met, then may proceed.** No direct human approval needed if pre-conditions are verified by automation, but a human can always intervene.

These actions change state that may affect other developers, CI pipelines, or downstream consumers.

### Action Classes

| Category | Examples | Pre-Conditions | Gate |
|---------|---------|---------------|-----|
| **Git commit** | `git commit` with staged changes | Pre-commit hook passes | Pre-commit (Trivy + tests + typecheck) |
| **Git push (feature branch)** | `git push origin feature/*` | Commits pass pre-commit | CI checks on PR open |
| **PR creation** | Open a GitHub PR | Branch passes CI | Review workflow triggered |
| **Dependency addition** | Add to `pyproject.toml`, `package.json` | Audit clean; no new HIGH/CRITICAL CVEs | CI dependency audit check |
| **Lock file update** | `uv lock`, `bun install` | Updated lock file committed | Dependency audit in CI |
| **New MCP server** | Add entry to `pilot/.mcp.json` | Documented threat model; PR review | PR approval required |
| **New hook registration** | Add entry to `pilot/hooks/hooks.json` | Implementation reviewed; timeout set | PR approval required |
| **New skill install** | Add to `.claude/skills/` | Reviewed content; no shell-exec without allowlist | PR approval required |
| **Rules file change** | Modify `pilot/rules/*.md` | Change reviewed for safety constraint removal | PR approval required |
| **Environment config change** | Modify `pilot/claude.json` permissions | Change reviewed for scope expansion | PR approval required |
| **New CI workflow (non-privileged)** | Add `.github/workflows/*.yml` (no secrets access) | Workflow reviewed; actions pinned | PR approval + workflow policy check |

### Pre-Conditions for T2 Actions

```
[ ] Active spec plan exists for the change (feature work)
[ ] All T1 local validations have passed
[ ] No open HIGH/CRITICAL security findings in current working set
[ ] Secret scan has run and is clean
[ ] Dependency audit is clean for introduced packages
```

---

## 5. Tier 3 — Privileged / Irreversible

**Requires explicit human approval before execution.** Automation may prepare and propose, but cannot execute.

These actions are irreversible, affect shared production state, grant elevated permissions, or carry high blast radius.

### Action Classes

| Category | Examples | Approval Required From |
|---------|---------|----------------------|
| **Merge to main** | Merge PR into `main`/`master` | ≥1 human reviewer approval + all CI checks |
| **Release publication** | Tag + push release, publish artefact | Release workflow success + maintainer approval |
| **CI workflow with secrets** | Modify workflows accessing `GITHUB_TOKEN`, deploy secrets | Code owner approval (CODEOWNERS) |
| **Branch protection changes** | Modify required reviewers, status checks | Repository admin |
| **Hook script modification** | Edit `pilot/hooks/*.py` | PR review + spec-verify passing |
| **`claude.json` permission expansion** | Add new allowed tools or expand filesystem scope | PR review + explicit justification |
| **MCP server with exec capability** | MCP server that runs shell commands | PR review + threat model doc |
| **New agent definition** | Add agent to `pilot/agents/` | PR review |
| **`git-crypt` key rotation** | Rotate encryption key | Repository admin + all holders notified |
| **Secret rotation** | Rotate API keys, tokens, credentials | Admin + rotation runbook |
| **Force push to any branch** | `git push --force` | Explicit maintainer decision; documented reason |
| **Production infrastructure change** | Cloud config, DNS, deployment targets | Admin + change management |
| **Recursive agent spawning** | Agent spawns further agents outside current spec | Explicit user permission in session |

### Approval Protocol for T3 Actions

1. **Propose**: Claude Code or automation creates a PR with full evidence chain.
2. **Review**: Human reviewer(s) assess the change against the evidence.
3. **Approve**: ≥1 approval in GitHub PR with explicit confirmation.
4. **Gate**: All CI checks green before merge is permitted.
5. **Record**: GitHub audit log captures approval. PR description records rationale.
6. **Execute**: Merge or deployment only after all above complete.

---

## 6. Risk Tier Assignment for Existing Components

### Hooks (`pilot/hooks/`)

| Hook | Tier | Rationale |
|------|------|-----------|
| `context_monitor.py` | T0 | Read-only token counting |
| `tool_redirect.py` | T3 | Modifying this removes enforcement |
| `tool_token_saver.py` | T1 | Local optimization, no state change |
| `file_checker.py` | T1 | Post-write validation, no side effects |
| `spec_mode_guard.py` | T2 | Guards commit path; modification is T3 |
| `spec_stop_guard.py` | T3 | Removing exit-1 silently enables bad merges |
| `spec_plan_validator.py` | T1 | Validates plan quality, no external state |
| `spec_verify_validator.py` | T1 | Validates verify phase, no external state |
| `session_clear.py` | T1 | Local session cleanup |
| `session_end.py` | T1 | Local cleanup |
| `pre_compact.py` | T1 | Context management, local |
| `python.py` checker | T0/T1 | Runs linters, no persistent write |
| `typescript.py` checker | T0/T1 | Runs linters, no persistent write |
| `tdd.py` checker | T0 | Read-only enforcement check |

### CI Workflows (`.github/workflows/`)

| Workflow | Tier | Rationale |
|---------|------|-----------|
| `claude.yml` (review) | T2 | PR comment, no merge gate bypass |
| `release.yml` | T3 | Creates release artefacts, tags main |
| `release-dev.yml` | T3 | Pre-release; still creates artefacts |
| `deploy-website.yml` | T3 | Deploys to public service |

### MCP Servers (`pilot/.mcp.json`)

| Server | Tier | Rationale |
|--------|------|-----------|
| `context7` | T0 | Read-only public docs |
| `codebase-memory-mcp` | T1 | Reads + writes local memory store |
| `mem-search` | T0 | Read-only memory search |
| `web-search` | T0 | Read-only, external, untrusted content |
| `grep-mcp` | T0 | Read-only, public repos |
| `web-fetch` | T0* | Read-only but highest prompt-injection risk; treat responses as untrusted |

### Configuration Files

| File | Tier for Changes |
|------|-----------------|
| `pilot/claude.json` | T3 (permission additions); T2 (non-permission changes) |
| `pilot/settings.json` | T2 |
| `pilot/.mcp.json` | T2 (existing servers); T3 (new server additions) |
| `pilot/hooks/hooks.json` | T3 |
| `pyproject.toml` | T2 (dependency changes); T1 (tool config) |
| `package.json` | T2 (dependency changes); T1 (script changes) |
| `.githooks/pre-commit` | T3 |
| `.releaserc.json` | T3 |
| `.github/workflows/*.yml` | T2-T3 (see CI Workflows above) |

---

## 7. Autonomous Action Boundaries

### What Claude Code may do without asking:

```
T0: All read operations
T1: Write source files within project root
T1: Write test files
T1: Run formatters (with post-typecheck)
T1: Write spec plan/verify files
T1: Stage files with git add (specific paths)
T2: Commit staged changes (pre-commit gate must pass)
T2: Push to feature branch
T2: Open draft PR
```

### What requires human confirmation before proceeding:

```
T2: Add dependencies to lock files
T2: Add new MCP server to .mcp.json
T2: Modify rules files
T2: Modify claude.json (non-permission)
T3: Merge PR (human clicks merge)
T3: Modify any hook script
T3: Modify claude.json permissions
T3: Modify CI workflows (especially with secrets)
T3: Trigger release workflow
T3: Force push
T3: Recursive agent spawning
```

---

## 8. Evidence Chain per Tier

### T0 — No evidence required

### T1 — Automated evidence

```
evidence/
  lint_pass: true|false (language checker output)
  typecheck_pass: true|false
  test_result: pass|fail|N/A
  spec_plan_exists: true|false
```

### T2 — Pre-condition record

```
evidence/
  t1_evidence: <all T1 above>
  secret_scan: clean|violations (list)
  dependency_audit: clean|findings (list)
  spec_verify: pass (if feature work)
  pre_commit: passed (exit 0)
```

### T3 — Full evidence chain

```
evidence/
  t2_evidence: <all T2 above>
  pr_number: <int>
  approvals: [{ reviewer: str, approved_at: iso8601 }]
  ci_checks: [{ name: str, status: passed }]
  review_comments_resolved: true
  rationale: <text in PR description>
```

---

## 9. Escalation Path

When an action's tier is ambiguous:

1. **Default to the higher tier** — if unsure whether an action is T2 or T3, treat it as T3.
2. **Ask before acting** — Claude Code must use `AskUserQuestion` to confirm before T2+ actions where pre-conditions cannot be automatically verified.
3. **Surface the evidence** — Claude Code must show the evidence chain before proposing a T3 action.
4. **Do not bypass** — If a human declines a T3 action, do not reattempt with equivalent effect via a different path.

---

## 10. Future Tier Controls (Roadmap)

| Control | Target Tier | Notes |
|---------|------------|-------|
| Secret scanning hook (`PreToolUse`) | T2 pre-condition | Block commits with secrets |
| Dependency audit hook (`PreToolUse`) | T2 pre-condition | Block if new CVE introduced |
| Policy check CI workflow | T2-T3 gate | OPA/Rego policy for PR validation |
| Workflow policy validator | T3 gate | Check generated workflow files for safe patterns |
| Skills manifest + provenance check | T2 pre-condition | Verify skill origin before auto-load |
| Prompt injection scanner | T0 enhancement | Warn on suspicious MCP response content |
| Artefact signing | T3 evidence | Sign release artefacts for integrity |
