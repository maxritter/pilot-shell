## Step 0: Setup, Process Overview, & Runtime Classification

### 0.1 Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read the reviewer toggle env vars:

```bash
echo "REVIEWER=$PILOT_CHANGES_REVIEW_ENABLED CODEX_CHG=$PILOT_CODEX_CHANGES_REVIEW_ENABLED"
```

Codex reviewers are controlled entirely by Console Settings — the env vars are authoritative.

Reference these values in Steps 1 (Launch Review), 3 (Collect Results — Codex collection).

### 0.2 Process Overview

```
Phase A — Finalize the code:
  Launch Reviewer → Automated Checks (tests + lint + verify commands) → Feature Parity (if migration) → Collect Review Results → Fix

Phase B — Verify the running program (depth depends on runtime profile):
  Build → Program Execution → Per-Task DoD Audit → E2E

Final:
  Regression check → Worktree sync → Post-merge verification → Update status
```

### 0.3 Classify Runtime Profile

**Determine verification depth based on what changed:**

| Profile | Criteria | Phase B Scope |
|---------|----------|---------------|
| **Minimal** | No server, no UI, no built artifacts (libraries, CLI tools, hooks, scripts) | Build check only |
| **API** | Server/API but no frontend changes | Build + program execution + DoD audit. Skip E2E. |
| **Full** | Frontend/UI changes or complex deployment | All Phase B steps |

Read the plan's Runtime Environment section (if present) and the changed file types to classify.
