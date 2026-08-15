## Step 0: Permission Mode + Model Switching Pre-Flight

<!-- CC-ONLY -->
**0a. Permission mode.** Check if the spec_mode_guard hook injected a permission mode note. If you see a system-reminder containing "Current permission mode is", briefly warn the user:

> "Your current permission mode is **{mode}**. For uninterrupted `/spec` execution, **Bypass Permissions** mode is recommended (Shift+Tab to cycle). Proceeding — the workflow may pause for permission prompts."

Do not stop or wait for the user to switch. The user's mode choice is respected — bypass permissions is recommended, not required.

**0b. Model Switching mode info (show the matching message verbatim to the user).** Read the mode FRESH from config.json (session env is startup-frozen; a Console change must steer this /spec):

```bash
MODE=$(python3 -c "import sys,os;sys.path.insert(0,os.path.expanduser('~/.pilot/hooks'));from _lib.util import read_model_switch_mode;print(read_model_switch_mode())" 2>/dev/null || echo "automated")
echo "MODE=$MODE"
```

- **If `MODE` is `manual`:**

  > ℹ️ Manual model switching — planning runs on your current `/model` choice (see the status bar). Switch now with `/model` if you want a different planning model; after plan approval you'll be prompted once to switch to your implementation model. Prefer automation? Console → Settings → Model Switching → Automated (requires `opusplan`).

- **If `MODE` is `automated`:**

  > ℹ️ Automated model switching — `/spec` runs on the **opusplan** model: **Opus** plans, **Sonnet** executes, switched automatically. This requires `/model opusplan` (Pilot sets it for you; if your status bar shows something else, run `/model opusplan` now). Prefer picking models yourself? Console → Settings → Model Switching → Manual.

- **If `MODE` is `off`:**

  > ℹ️ Model management is off — the whole workflow runs on your active `/model` choice.

Also relay any `PRE-FLIGHT CONTEXT CHECK` note the spec_mode_guard hook injected (Automated mode with a large conversation): tell the user planning may stay on Sonnet at this context size and how to fix it, then continue on their call.

We can only see the resolved model — this is guidance, not a hard check. After showing the message, continue with the workflow.
<!-- /CC-ONLY -->
<!-- CODEX-START
**Skip** — permission mode and model switching are not applicable in Codex CLI. Proceed directly to Step 1.
CODEX-END -->
