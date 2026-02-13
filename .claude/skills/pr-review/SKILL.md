---
name: pr-review
description: |
  Comprehensive PR review: analyze bot comments, check CI pipeline failures,
  and verify code changes against project rules. Use when: (1) user shares a PR
  URL and wants it reviewed, (2) user says "review PR #X", (3) PR has failing
  checks or bot comments to address. Covers: bot feedback (CodeRabbit, Claude),
  CI/CD failures (fetch logs, fix issues), workflow sync, and rules compliance.
author: Claude Code
version: 2.0.0
---

# PR Review

End-to-end PR review: bot comments, CI pipelines, and code quality.

## Trigger Conditions

- User shares a GitHub PR URL
- User says "review PR #X" or "check PR"
- PR has failing checks or unaddressed bot comments
- User wants PR ready for merge

## Workflow Overview

```text
1. Gather        → Fetch comments, CI status, changed files
2. Triage        → Validate each issue against actual code, assign verdict
3. CI Analysis   → Check failures, fetch logs, identify root causes
4. Recommend     → Present actionable summary with fix/dismiss per issue
```

**Key principle:** Don't just list what bots said — validate each claim, dismiss
noise, and tell the user exactly what's worth fixing.

---

## Phase 1: Gather All Inputs

Run all of these in parallel to collect raw data:

```bash
# PR metadata
gh pr view <number> --json title,body,state,headRefName,baseRefName

# CI check status
gh pr checks <number>

# PR-level comments (issue comments)
gh api repos/{owner}/{repo}/issues/<number>/comments \
  --jq '.[] | {user: .user.login, body: .body, created_at: .created_at}'

# Inline review comments (code-level)
gh api repos/{owner}/{repo}/pulls/<number>/comments \
  --jq '.[] | {user: .user.login, body: .body, path: .path, line: .line, diff_hunk: .diff_hunk}'

# Formal reviews (approve/request changes)
gh api repos/{owner}/{repo}/pulls/<number>/reviews \
  --jq '.[] | {user: .user.login, state: .state, body: .body}'

# Changed files list
gh pr diff <number> --name-only
```

### Identify Comment Sources

| Source | Pattern | Treatment |
|--------|---------|-----------|
| CodeRabbit | `coderabbitai[bot]` | Triage each suggestion |
| Claude | `claude[bot]` | Triage each issue by severity |
| Vercel | `vercel[bot]` | Skip — deployment status only |
| GitHub Actions | `github-actions[bot]` | Handle in CI phase |
| Human reviewers | Any non-bot | Always surface — highest priority |

**Skip noise:** Vercel deployment summaries, CodeRabbit walkthrough summaries,
and bot meta-comments (help text, checkboxes) are informational only. Don't
include them in the triage table.

---

## Phase 2: Triage Each Issue

For every substantive issue raised by a bot or reviewer, validate it:

### 2.1 Extract Issues

Parse each bot comment into discrete issues. A single bot comment often contains
multiple issues — split them. For each issue, capture:

- **Source**: Who raised it (CodeRabbit, Claude, human)
- **Severity**: What the bot claimed (critical, warning, minor, nitpick)
- **File**: Which file is affected
- **Claim**: One-sentence summary of what the bot says is wrong

### 2.2 Validate Against Code

**For each issue, check the actual code before assigning a verdict:**

```text
Can you read the file?
├─ YES (plaintext) → Read the file, check if the issue is real
│   ├─ Issue is valid     → Verdict: FIX (with specific action)
│   ├─ Issue is wrong     → Verdict: DISMISS (explain why bot is wrong)
│   └─ Already fixed      → Verdict: DISMISS (fixed in later commit)
├─ NO (encrypted/binary)  → Verdict: UNVERIFIABLE (note why)
└─ File doesn't exist     → Verdict: DISMISS (stale reference)
```

**Validation rules:**

- **Security claims**: Read the actual code. Check if input validation exists,
  if command execution uses safe patterns (execFile with args array, not string
  interpolation). Don't accept "might be vulnerable" without evidence.
- **Missing feature claims**: Check if the feature exists elsewhere or is
  intentionally omitted. Search the codebase for related patterns.
- **Performance claims**: Only flag if there's a concrete bottleneck, not
  theoretical concerns.
- **Style/naming claims**: Dismiss unless they violate project rules in
  `.claude/rules/` or `~/.claude/rules/`.
- **"Question" comments**: Bots sometimes phrase issues as questions ("Was this
  intentional?"). Investigate and answer the question — don't pass it through
  as an issue.

### 2.3 Cross-Reference with CI

If CI already catches an issue (e.g., type error flagged by bot AND caught by
tsc in CI), note it as "caught by CI" to avoid duplicate work.

### 2.4 Assign Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **FIX** | Issue is valid, needs addressing before merge | Describe the specific fix |
| **DISMISS** | Issue is invalid, already fixed, or not applicable | Explain why |
| **UNVERIFIABLE** | Can't check (encrypted file, missing context) | Note what's needed |
| **DEFER** | Valid but low-priority, can be a follow-up | Suggest when to address |

---

## Phase 3: CI Pipeline Analysis

### Check Status

```bash
gh pr checks <number>
```

### For Failed Checks

```bash
# Find the run ID from the checks output URL
gh run view <run-id> --log-failed
```

### Categorize Failures

| Type | Detection | Blocking? |
|------|-----------|-----------|
| Unit test failure | `FAILED` in pytest/jest output | Yes |
| Type check error | basedpyright/tsc errors | Yes |
| Lint error | ruff/eslint output | Usually yes |
| Build failure | Non-zero exit | Yes |
| Flaky test | Passes on retry | No — note as flaky |
| Unrelated failure | Fails on main too | No — pre-existing |

### Check If Failure Is Pre-existing

```bash
# Compare: does the same check fail on main?
gh run list --branch main --limit 3 --json conclusion,name \
  --jq '.[] | "\(.name): \(.conclusion)"'
```

If the same check fails on main, it's pre-existing — note it but don't block.

---

## Phase 4: Present Actionable Summary

**This is the output the user sees. Make it decision-ready.**

```markdown
## PR #X Review Summary

### CI Status
| Check | Status | Notes |
|-------|--------|-------|
| Python Tests | pending/pass/fail | [details if failed] |
| Console Tests | pass | — |
| Build | pass | — |

### Issues Triage

| # | Source | Severity | File | Issue | Verdict | Action |
|---|--------|----------|------|-------|---------|--------|
| 1 | Claude | High | routes.ts | Command injection risk | FIX | Add strict date regex |
| 2 | CodeRabbit | Nitpick | .gitattributes | Broad encryption scope | DISMISS | Intentional |
| 3 | Claude | Medium | spec-plan.md | Retry logic vague | DEFER | Follow-up PR |

### Recommended Actions
1. **Must fix before merge:** [list FIX items]
2. **Can defer:** [list DEFER items]
3. **Dismissed:** [count] issues dismissed (invalid or already addressed)

### Dismissed Issues (for reference)
| # | Issue | Why Dismissed |
|---|-------|---------------|
| 2 | Broad git-crypt scope | Intentional — encrypts proprietary source |
```

### Presentation Rules

- **Lead with what matters**: FIX items first, then DEFER, then dismissed
- **Be specific**: "Add `/^\d{8}$/` regex in UsageRoutes.ts:L42" not "fix validation"
- **Show your work**: For each DISMISS, explain why the bot was wrong
- **Don't repeat bot text verbatim**: Summarize in one sentence
- **Group related issues**: If 3 bot comments are about the same root cause, merge them
- **End with a recommendation**: "I recommend fixing #1 and #3, deferring #5, rest is noise"

---

## Quick Commands Reference

```bash
# PR overview
gh pr view <number>

# Check status
gh pr checks <number>

# Failed run logs
gh run view <run-id> --log-failed

# PR diff
gh pr diff <number>

# Bot comments (PR-level)
gh api repos/{owner}/{repo}/issues/<number>/comments

# Inline review comments
gh api repos/{owner}/{repo}/pulls/<number>/comments

# Formal reviews
gh api repos/{owner}/{repo}/pulls/<number>/reviews
```
