## Step 1: Fix the Scope and Baseline

1. Resolve the repository root without modifying it. Preserve any user-supplied repository-relative scope. If no scope is supplied, choose the smallest source roots supported by current project configuration; do not silently treat vendored, generated, build, cache, dependency, or fixture trees as production source.
2. Read the nearest repository instructions and the configuration that owns lint, type-check, compiler, and package commands.
3. Capture the initial worktree exactly with `git status --short --untracked-files=all` when Git is available. Record the current branch and relevant diff so pre-existing changes are not attributed to this audit.
4. Inventory configured candidate generators without installing or downloading anything:
   - package scripts and the repository's existing package manager;
   - compiler unused-symbol settings;
   - configured linter or dead-code analyzer rules;
   - locally available binaries already named by those configurations.
5. Reject commands that can mutate or fetch: formatter/fixer modes, code generation, migrations, `npx` without a local binary guarantee, `uvx`, package installation, CodeGraph init/index/sync, or tools absent from the project configuration.

Write down before continuing:

- production scope and explicit exclusions;
- test/fixture/example scopes kept separate;
- candidate limit (default 100 unless the user supplied a smaller bound);
- exact initial worktree snapshot;
- configured candidate generators that are locally runnable.

If no project-native candidate generator is configured and available, continue only far enough to report that gap. Do not synthesize candidates from search, CodeGraph, LSP, or intuition.

**Completion:** scope, exclusions, candidate limit, worktree baseline, and eligible analyzer commands are known.
