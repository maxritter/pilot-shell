## Step 8: Hand Off to /spec

This is the single terminal confirmation — Step 7 already settled the PRD content, so do NOT ask "does anything need to change?" again here.

**⛔ Never auto-invoke `/spec` or `Skill('spec')`.** The user MUST type the command themselves (global rule in `task-and-workflow.md`). This skill's terminal action is to PRINT the command, then stop and wait.

**Ask** (`AskUserQuestion`, or plain-text numbered options on Codex):
- **"Show me the `/spec` command"** — print the ready-to-run command below
- **"I'm done for now"** — just confirm the PRD path

Either way, print the hand-off command for the user to run (do not run it yourself):

```
PRD saved to docs/prd/YYYY-MM-DD-slug.md

To start implementation planning, run:
  /spec "Implement <one-line-summary> — PRD: docs/prd/YYYY-MM-DD-slug.md — see PRD for full requirements"
```

**The command's argument must NOT end in `.md`** — the trailing text after the path prevents the `/spec` dispatcher from treating it as an existing plan file (dispatcher plan-file mode triggers only when the argument ends with `.md` AND the file exists).

ARGUMENTS: $ARGUMENTS
