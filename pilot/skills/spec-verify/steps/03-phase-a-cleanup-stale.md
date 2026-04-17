---

## Step 3: Phase A — Finalize the Code

### Step 3: Clean Up Stale Spec-Review Findings

**⛔ ALWAYS run this step** — regardless of whether changes-review is enabled. Spec-review findings are stale artifacts from the planning phase that were already addressed during implementation.

```bash
rm -f ~/.pilot/sessions/$PILOT_SESSION_ID/findings-spec-review-*.json
```
