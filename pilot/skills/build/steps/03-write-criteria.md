## Step 3: Write the Criteria and the Rubric File

This is the artifact that matters. Everything downstream is measured against it.

### 3.1 Write 5–9 criteria

Each one:

- **Rules pass or fail, never a score.** Scores drift upward every round: "7/10" becomes "8/10" with no change to the work.
- **Is decidable from the output alone**, by someone who did not build it and does not know which artifact is ours.
- **Names the evidence that settles it**, so a lazy judge cannot pass it by default.
- **Resolves to "ours wins", never to "you cannot tell".** A criterion phrased as indistinguishable-from-the-bar, or as a viewer failing to spot which one is generated, passes on a tie — and a tie is the most common place this loop stops early. Parity with the bar was the starting assumption, not the finish line.

Include **at least one measurable criterion** when the goal has a measurable half — load time, bundle size, token cost, benchmark score, word count, pass rate, error rate. Taste plus a number beats taste alone.

Shape each one as **what is compared → how the judge obtains it → what passing looks like**:

| Weak | Strong |
|---|---|
| The hero section is compelling. | Our hero and Nike's, both screenshotted at 1440px and shown unlabelled: a viewer told nothing picks ours. |
| Good error handling. | Every failure mode the module documents has a test asserting the user-facing message, and the suite passes. |
| The writing is clear. | A reader new to the topic restates the core mechanism in one sentence after a single read. |
| Indistinguishable from Stripe's docs. | Shown unlabelled beside Stripe's docs, a reader who has used neither picks ours. |

**Write these before building.** Criteria written after a first draft describe that draft — the bar quietly becomes whatever you happened to make, which is the most common way this workflow produces nothing.

### 3.2 Create the rubric file

**Do this before any building** — the statusline and the Console pick it up immediately, and the stop guard starts holding the loop open.

1. **Filename:** `docs/plans/YYYY-MM-DD-<slug>.md` — slug from the first 3–4 words of the goal (lowercase, hyphens). If this session is already running inside a worktree checkout, use the worktree path as the base directory. `/build` never creates a worktree itself.

2. **Author email** (best-effort, omit the line if it fails):

   ```bash
   ~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
   ```

<!-- CC-ONLY -->
3. **Agent:** `Claude Code` if `$CLAUDE_CODE_ENTRYPOINT` is set, otherwise `Codex`.
<!-- /CC-ONLY -->
<!-- CODEX-START
3. **Agent:** `Codex`.
CODEX-END -->

4. **Write the file:**

   ```markdown
   # [Name] Build Rubric

   Created: [Date]
   Author: [email if available]
   Agent: [Claude Code|Codex]
   Status: PENDING
   Approved: No
   Rounds: 0
   Worktree: [Yes|No]
   Type: Build

   ## Summary

   **Goal:** [one line — what is being built]

   **Bar:** [named artifact]

   **Re-obtain the bar:** `[exact command, URL, or path from Step 2]`

   ## Criteria

   - [ ] Criterion 1: [what is compared] → [how the judge obtains it] → [what passing looks like]
   - [ ] Criterion 2: ...
   - [ ] Criterion 3: ...

   ## Out of Scope

   - [anything the user named that this build is deliberately not doing, or "none"]

   ## Round Log

   _No rounds yet._
   ```

   `Type: Build` is what makes the statusline render the loop and the Console badge the file as a build. `Status:` is a closed set — `PENDING` | `COMPLETE` | `VERIFIED`, bare keyword, no trailing prose. `Rounds:` starts at 0 and is incremented by the loop, never by hand.

   Every criterion is a `- [ ] Criterion N:` line at the top level of `## Criteria`. That exact shape is what the statusline counts — nested bullets and prose under a criterion are fine, but the criterion itself must be one of those lines.

5. **Register it:**

   ```bash
   ~/.pilot/bin/pilot register-plan "<rubric_path>" "PENDING" 2>/dev/null || true
   ```

### 3.3 Show the criteria to the user

Print the numbered list in the conversation. It is the one thing worth twenty seconds of their attention.

**Done when:** the rubric file exists, is registered, every criterion states its pass condition, and the user has seen the list.
