## Step 4: Create or Edit the Canonical Skill

### Project Scope

The repository must already have the checker installed by `/setup-rules`. Verify that before authoring:

```bash
test -f scripts/sync-agent-assets.mjs
node scripts/sync-agent-assets.mjs --check
```

If the script is absent, run `/setup-rules` to migrate existing content and install it. Do not invent another copy command or edit `.claude/skills/` directly; setup must resolve possible legacy conflicts before generation.

Create or edit only the canonical directory:

```bash
mkdir -p .agents/skills/{slug}-{name}
# Write .agents/skills/{slug}-{name}/SKILL.md and any supporting files
```

Pilot's shared hook converges on SessionStart and regenerates the complete mirror for canonical skills under `.claude/skills/` after edits from either Claude Code or Codex, while preserving untracked/ignored agent-only extensions. Users normally do not run `--write`.

If a task or tool presents a tracked `.claude/skills/<name>/...` path, do not edit that generated file. Follow the hook's redirect when supported; otherwise use the canonical `.agents/skills/<name>/...` path reported by the blocking message. Never copy changes from `.claude/skills/` back into `.agents/skills/`.

### Global Scope

Global skills are outside the repository sync contract:

<!-- CC-ONLY -->
```bash
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills/{slug}-{name}
# Write SKILL.md
```
<!-- /CC-ONLY -->
<!-- CODEX-START
```bash
mkdir -p ~/.agents/skills/{slug}-{name}
# Write SKILL.md
```
CODEX-END -->

If a global skill should ship to both agents or other users, promote it through Pilot's skill library rather than maintaining two user-level copies by hand.

Edit the created `SKILL.md` with the template from Step 1.

**Cross-agent portability checklist:**

- Describe capabilities (read files, search text, execute commands, launch a bounded agent) rather than assuming one tool namespace or parameter schema.
- Prefer common shell commands and repository-relative paths when exact execution is needed.
- Provide a capability-based fallback for optional agent, browser, and web tools.
- Avoid Claude-only or Codex-only instructions in a project skill. If behavior must differ, key it to an observable capability in the current session.
- Never reference Pilot-only services such as Semble or Pilot MCP servers unless the skill declares them as prerequisites and has a portable fallback.
- Keep `targets: [claude, codex]` when both agents are supported; narrow it only when the workflow truly cannot run on one target.
- Rely on Pilot's shared hook for normal mirroring. Keep manual `--write` as recovery, not a required authoring step.

**Determinism checklist:**

- Prefer exact commands over descriptions (`run prettier --write .` not "format the code")
- Prefer scripts over multi-step instructions (reference `scripts/deploy.sh` not five prose steps)
- Use explicit values over judgment (`block files > 100KB` not "block large files")
- For high-risk operations: include exact commands, validation steps, and rollback plan
- For low-risk work: use general guidelines and let the agent apply judgment

**One skill = one purpose.** Split review, testing, and deployment when they are independent workflows.

**Security:** Skills must not contain malware, exploit code, credentials, or surprising data access. Use environment variables for secrets.
