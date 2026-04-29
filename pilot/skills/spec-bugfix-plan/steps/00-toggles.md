---

## Step 0: Read Toggle Configuration

**⛔ Run FIRST, before any other step.** Read all toggle env vars in a single Bash call:

```bash
echo "QUESTIONS=$PILOT_PLAN_QUESTIONS_ENABLED APPROVAL=$PILOT_PLAN_APPROVAL_ENABLED"
```

Reference these values throughout: Steps 3.1/3.5 (questions) and 7 (approval). Bugfix planning does not run Codex — adversarial review only runs once per `/spec` invocation, on the implementation in `spec-verify`.
