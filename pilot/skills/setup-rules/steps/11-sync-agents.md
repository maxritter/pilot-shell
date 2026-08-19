## Step 11: Install and Verify Cross-Agent Synchronization

The final repository contract is:

- `AGENTS.md` is the user-editable shared core.
- `CLAUDE.md` contains exactly `@AGENTS.md` plus a trailing newline.
- `.agents/skills/` is the user-editable canonical tree for tracked project skills.
- Tracked `.claude/skills/` content is generated and must never be edited directly.
- Pilot's shared hook synchronizes on SessionStart, supported edits made through either agent, and Stop as a Code Mode backstop.
- `scripts/sync-agent-assets.mjs` is the standalone recovery writer and CI drift checker.

Untracked or ignored local agent-only extensions are outside this repository contract. Preserve them; they neither become canonical project assets nor make CI fail.

### Step 11.1: Confirm Destructive Reconciliation — CONDITIONAL

Reuse the migration decision from Step 7. Ask again only if Step 10 found a new conflict, a tracked mirror-only skill, or generated files that would overwrite unique tracked content.

AskUserQuestion: "The generated Claude Code assets differ from their canonical sources. Which content should become canonical before I regenerate the mirror?"

- **"Preserve all unique content (Recommended)"** — copy unique instructions/skill files into `AGENTS.md`, scoped rules, or `.agents/skills/` as appropriate, then regenerate
- **"Use `.agents/skills/` and `AGENTS.md`"** — replace generated counterparts from the documented canonical sources
- **"Review each conflict"** — show each conflicting file and choose its canonical content
- **"Skip synchronization"** — leave assets untouched and report the failed parity gate

Never run generation across an unresolved tracked mirror-only edit.

### Step 11.2: Install the Repository Checker

Resolve the bundled script relative to this skill's loaded `SKILL.md` (its source path is `scripts/sync-agent-assets.mjs`). Run it from the target repository:

```bash
mkdir -p .agents/skills
# If the repository has no canonical skills yet, keep .agents/skills/.gitkeep tracked.
node <setup-rules-skill-dir>/scripts/sync-agent-assets.mjs --install --repo .
```

`--install` writes the standalone `scripts/sync-agent-assets.mjs` into the repository and performs the initial convergence of the root import and project skill mirror. Commit the installed script so recovery and CI use the same implementation without requiring Pilot Shell.

The checker requires `.agents/skills/` even when it is empty. In that case, add `.agents/skills/.gitkeep` so a fresh clone preserves the canonical directory.

If the bundled script cannot be resolved, stop this step before changing `CLAUDE.md` or `.claude/skills/` and report the installation gap.

### Step 11.3: Confirm Automatic Hook Coverage

Pilot installs one shared agent-asset hook through both its Claude Code and Codex adapters. Do not add repository-specific hooks. Confirm the installed adapters provide these behaviors:

1. **SessionStart:** detect prepared repositories and converge `CLAUDE.md` plus tracked skill mirrors before work begins.
2. **Canonical edit:** after either agent emits a supported edit to `AGENTS.md` or `.agents/skills/`, run the repository synchronizer automatically.
3. **Generated edit:** when either agent targets tracked `.claude/skills/` content, redirect the edit when supported or block it, and return the exact canonical `.agents/skills/` path to edit instead.
4. **One-way authority:** copy `.agents/skills/` to `.claude/skills/` only. Never infer canonical content from the generated tree.
5. **Stop:** run a read-only check and repair drift only when needed. This covers Code Mode when nested edits emitted no PreToolUse/PostToolUse event.

This makes the active agent irrelevant to authoring: Claude Code and Codex both edit the same canonical filesystem paths. If either adapter lacks the shared hook, report that Pilot installation needs repair; do not compensate with a second project hook.

The hook must execute only Pilot's installed bundled checker. Treat the repository copy as an enrollment marker, update target, and CI/manual recovery command; never execute that repository-controlled copy from a trusted global hook.

### Step 11.4: Add the Check to Existing CI

When the repository has CI, add this command to an existing required validation, lint, or documentation job:

```bash
node scripts/sync-agent-assets.mjs --check
```

Choose the cheapest existing job that already checks out the complete repository. Do not create a new workflow or job for this check. Preserve the workflow's package-manager and step conventions. If no CI exists, document the local command instead of introducing a CI system.

### Step 11.5: Prove Automatic Parity

The shared hook normally performs every write. After all source edits and CI wiring, run the read-only backstop:

```bash
node scripts/sync-agent-assets.mjs --check
```

If `--check` reports drift, fix the canonical source or hook installation, run `node scripts/sync-agent-assets.mjs --write` once as recovery, then rerun `--check`. Users should not need `--write` during normal Claude Code or Codex work.

The check must exit zero. Then capture evidence for the summary:

1. `AGENTS.md` exists and retains every approved user-authored shared section.
2. `CLAUDE.md` is byte-for-byte `@AGENTS.md\n`.
3. All tracked project skill names have canonical entries and generated mirrors; local untracked/ignored agent-only extensions are listed as out of scope.
4. Every tracked file under each canonical `.agents/skills/<name>/` is byte-identical to its `.claude/skills/<name>/` mirror.
5. `scripts/sync-agent-assets.mjs --check` exits zero without modifying the worktree.
6. Pilot's shared hook covers SessionStart, canonical edits, generated-edit redirection/blocking and Stop for both agents.
7. An existing CI job invokes `--check`, or the repository has no CI and the local-only status is recorded.

Do not hand-edit the generated mirror. Its only supported authority is the canonical source, whether convergence came from the automatic hook or a recovery `--write`.
