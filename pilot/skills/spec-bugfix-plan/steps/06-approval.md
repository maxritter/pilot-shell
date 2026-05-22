## Step 6: Get User Approval (and Model Switch Handoff)

### 6.0 Toggle interaction matrix

Pull `$PILOT_PLAN_APPROVAL_ENABLED` and `$PILOT_MODEL_SWITCH_ENABLED` from Step 0 and follow the matching row:

| `planApproval` | `modelSwitch` | What this step does |
|----------------|---------------|----------------------|
| true | true | AskUserQuestion → on Yes: set Approved, **write handoff sentinel, print short handoff message, end turn** (user runs `/model …`, then any prompt resumes implementation via `spec_handoff_resume` hook) |
| true | false | AskUserQuestion → on Yes: set Approved, **auto-invoke `Skill('spec-implement')`** |
| false | true | Silently set `Approved: Yes`, write sentinel, print short handoff message, end turn |
| false | false | Silently set `Approved: Yes`, auto-invoke `Skill('spec-implement')` (legacy behaviour) |

### 6.1 Notify (always)

```bash
~/.pilot/bin/pilot notify plan_approval "Bugfix Plan Ready" "<plan-slug> — annotate in Console or approve here" --plan-path "<plan_path>" 2>/dev/null || true
```

### 6.2 Approval

**⛔ If `PILOT_PLAN_APPROVAL_ENABLED` is `"false"`:** set `Approved: Yes` in the plan file immediately, then jump to **6.3 Handoff decision**.

**Otherwise — MANDATORY APPROVAL GATE:**

1. Summarize: symptom → root cause → fix approach → task structure
2. AskUserQuestion:
   - "Yes, proceed" — Approve as-is
   - "No, I have feedback" — I've annotated in the Console or edited the plan file; process my feedback

   The user can pause at this prompt, annotate in the Console's Specifications tab (auto-saves), or edit the plan file directly, then pick option 2. No "ready" handshake required.
3. **Yes:** Set `Approved: Yes`, then jump to **6.3 Handoff decision**.
   **No, I have feedback:** Re-run Step 5 (process Console annotations), re-read the plan file (in case the user edited it), then return to 6.2 and ask again.
   **Other free-text feedback:** Incorporate the changes into the plan, then re-ask with a fresh AskUserQuestion.

### 6.3 Handoff decision

**If `PILOT_MODEL_SWITCH_ENABLED` is `"true"` (default):** write the handoff sentinel and print the short model-switch message, then end the turn. Do NOT invoke `Skill('spec-implement')` — the user will resume after optionally switching models, and the `spec_handoff_resume` hook will route the next prompt straight to implementation.

```bash
mkdir -p "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-default}" && \
  touch "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-default}/spec-handoff-pending"
```

Then print this message **verbatim** (substitute the plan path):

```
Plan approved: <plan path>

Two ways to continue — pick what fits your context size:

  Option A — Fast (carries planning context):
    Run `/model <name>` to switch models (optional), then type any prompt
    (e.g. `continue`). Implementation resumes immediately with your full
    planning session still in context. Claude Code will ask you to confirm
    the model switch because the existing context is loaded into the new model,
    which incurs additional cost.

  Option B — Clean start (fresh context):
    Run `/clear`, then `/spec <plan path>`. Starts a new session with just
    the plan — lower token cost, useful if planning context is already large.

Model options (for either path):
  • `/model sonnet[1m]`  — Sonnet 1M context, cost-effective (recommended)
  • `/model sonnet`      — Sonnet 200K context
  • `/model opus[1m]`    — Opus 1M context (stay on same context size as planning)
  • `/model opus`        — Opus 200K context

Tip: turn off "Model Switching" in Console Settings → Automation to skip this pause next time.
```

After printing the message, end the turn — the stop guard's handoff sentinel will allow the stop, and the next user prompt will trigger `Skill('spec-implement', '<plan-path>')` automatically (Option A). For Option B the user runs `/clear` then `/spec <plan-path>`, which the dispatcher routes directly to implementation.

**If `PILOT_MODEL_SWITCH_ENABLED` is `"false"`:** do NOT write a sentinel. Invoke `Skill(skill='spec-implement', args='<plan-path>')` directly.
