---

## Step 0: Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read the reviewer toggle env vars:

```bash
echo "REVIEWER=$PILOT_CHANGES_REVIEW_ENABLED CODEX_CHG=$PILOT_CODEX_CHANGES_REVIEW_ENABLED"
```

Codex reviewers are controlled entirely by Console Settings — the env vars are authoritative.

Reference these values in Steps 4, 7, and 8.
