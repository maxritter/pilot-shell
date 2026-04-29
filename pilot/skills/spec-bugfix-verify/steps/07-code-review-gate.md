## Step 7: Code Review Gate (User Confirmation)

**⛔ MANDATORY before marking VERIFIED.**

**⛔ MUST use `AskUserQuestion`** — the stop guard only allows stopping when it detects this tool in the transcript. Plain text output will cause the stop guard to block session exit while waiting for user feedback.

1. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Verification Complete" "<plan-slug> — please review changes" --plan-path "<plan_path>" 2>/dev/null || true
   ```

2. Summarize what was done (brief: fix applied, tests passed, verification results), then ask:

   ```
   AskUserQuestion(
     question="All automated checks passed. Please review the code changes in the Console's **Changes** tab.\n\nYou can leave inline annotations using the **Review** mode toggle — annotations save automatically.\n\n[brief summary of fix]\n\nChoose an option when done:",
     options=["Approve — mark spec as verified", "Fix — address my annotations from the Console", "Manual — I'll test manually and report back"]
   )
   ```

3. Handle response — **match strictly, never auto-approve ambiguous input:**
   - **Approve:** Response is one of: "Approve", "approve", "lgtm", "looks good", "continue", "proceed" → proceed to Step 8
   - **Fix:** Response matches "Fix" or mentions annotations/console feedback → re-run Step 6 (check for code review annotations in JSON), fix issues, re-run tests, return to Step 7
   - **Manual / custom text:** Response matches "Manual" OR is ANY other free-text/custom input → the user wants to pause. **Do NOT mark VERIFIED. Do NOT change plan status.** Use `AskUserQuestion` again (required so the stop guard allows the user to exit while waiting):
     ```
     AskUserQuestion(
       question="Take your time testing. When you're done, choose an option or describe any issues you found:",
       options=["Approve — mark spec as verified", "Issues found — describe below"]
     )
     ```
     Then **stop and wait** for the user's next message.
   - **⛔ After Manual wait — re-evaluation of follow-up:** When the user responds after a Manual pause:
     - Explicit approval ("approve", "lgtm", "looks good") → proceed to Step 8
     - **Any other content** (error descriptions, screenshots, images, bug reports, or ANY non-approval text) → treat as **bug reports to fix**. Investigate the reported issues, implement fixes, re-run tests, then return to Step 7 (ask again).
   - **⛔ NEVER treat ambiguous or custom responses as approval.** Only the explicit keywords listed under "Approve" advance to Step 8.
