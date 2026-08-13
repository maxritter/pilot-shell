## Step 6: Code Review Gate (User Confirmation)

**⛔ MANDATORY before marking VERIFIED.**

<!-- CC-ONLY -->
**⛔ MUST use `AskUserQuestion` whenever you can emit it** — the stop guard reads this tool from the transcript to recognise an answer-wait turn, so plain text alone would leave it blocking session exit while the user is being asked.

⛔ **When you cannot emit it** — as a Claude Code subagent running this bugfix as an orchestration lane, where the tool is absent from the toolset entirely — asking in plain text is then the *correct* move, not a violation, but it must be paired with a yield or the question is passed by momentum. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/agent-gate-protocol.md` and follow it, supplying `GATE_NAME` = `Code review gate`, `OPTIONS` = the three below, `SENTINEL_PATH` = `verify-gate-pending`:

```bash
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$SESS_DIR" && touch "$SESS_DIR/verify-gate-pending"
```

Then **end your turn**; the guard honours the sentinel once for an approved plan at `Status: COMPLETE`. Treat the user's NEXT message as their answer, delete the sentinel on resume (`rm -f "$SESS_DIR/verify-gate-pending"`), and **re-touch it** each time you return here and ask again — it is consumed when honoured. Step 7's precondition is satisfied by this prose ask exactly as it is by the form; what it tests is that the gate was asked and answered, never which tool asked it.

**⛔ Resume / compaction / idle:** if you wake into a session where the previous Step 6 is unresolved (no in-turn approve keyword received from the user), **re-ask** — via `AskUserQuestion`, or via the prose ask + yield above when you cannot emit it. Do NOT infer approval from "checks all passed," empty annotations, or a long quiet gap. Silence is never approval.
<!-- /CC-ONLY -->
<!-- CODEX-START
**⛔ Present options as numbered text and wait for user response.** Do NOT infer approval from "checks all passed" or silence. Explicit approval keywords required.

Presenting the options is only half of it: the turn must also END so the answer can arrive. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/agent-gate-protocol.md` and follow it, supplying `GATE_NAME` = `Code review gate`, `OPTIONS` = the three below, `SENTINEL_PATH` = `verify-gate-pending`:

```bash
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$SESS_DIR" && touch "$SESS_DIR/verify-gate-pending"
```

The guard honours it once for an approved plan at `Status: COMPLETE`. Treat the user's NEXT message as their answer, `rm -f "$SESS_DIR/verify-gate-pending"` on resume, and re-touch it each time you ask again.
CODEX-END -->

1. Notify:
   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Bugfix Verification Complete" "<plan-slug> — please review changes" --plan-path "<plan_path>" 2>/dev/null || true
   ```

2. Summarize what was done (brief: fix applied, tests passed, verification results), then ask:

   ```
   AskUserQuestion(
     question="All automated checks passed. Please review the code changes in the Console's **Changes** tab.\n\nYou can leave inline annotations using the **Review** mode toggle — annotations save automatically.\n\n[brief summary of fix]\n\nChoose an option below, or type your feedback directly into the input box (free text works the same as picking 'Manual'):",
     options=["Approve — mark spec as verified", "Fix — address my annotations from the Console", "Manual — I'll test manually and report back"]
   )
   ```

3. Handle response — **match strictly, never auto-approve ambiguous input:**
   - **Approve:** Response is one of: "Approve", "approve", "lgtm", "looks good" → proceed to Step 7. (Do NOT treat a bare "continue"/"proceed" as approval — those are routine resume nudges, not a verification sign-off.)
   - **Fix:** Response matches "Fix" or mentions annotations/console feedback → re-run Step 5 (check for code review annotations in JSON), apply fixes, re-run tests, return to Step 6
   - **Manual / custom text:** Response matches "Manual" OR is ANY other free-text/custom input → the user wants to pause. **Do NOT mark VERIFIED. Do NOT change plan status.** Use `AskUserQuestion` again (required so the stop guard allows the user to exit while waiting):
     ```
     AskUserQuestion(
       question="Take your time testing. When you're done, choose an option or describe any issues you found:",
       options=["Approve — mark spec as verified", "Issues found — describe below"]
     )
     ```
     Then **stop and wait** for the user's next message.
   - **⛔ After Manual wait — re-evaluation of follow-up:** When the user responds after a Manual pause:
     - Explicit approval ("approve", "lgtm", "looks good") → proceed to Step 7
     - **Any other content** (error descriptions, screenshots, images, bug reports, or ANY non-approval text) → treat as **bug reports to fix**. Investigate the reported issues, implement fixes, re-run tests, then return to Step 6 (ask again).
   - **⛔ NEVER treat ambiguous or custom responses as approval.** Only the explicit keywords listed under "Approve" advance to Step 7.
