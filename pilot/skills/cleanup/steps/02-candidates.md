## Step 2: Generate Candidates with Project-Native Checks

Run the narrowest already-configured checks that can report unused code. Use the repository's locked package manager and existing environment. Examples are illustrative, not commands to invent:

- TypeScript/JavaScript: an existing Knip script/configuration, or configured TypeScript/ESLint unused-symbol checks.
- Python: configured Ruff, Pyright/basedpyright, Vulture, deadcode, or repository wrapper scripts.
- Go: configured compiler, vet, staticcheck, or repository lint targets.
- Rust: configured compiler or Clippy targets.
- Other stacks: only the project's existing compiler/linter/dead-code configuration.

For each command:

1. Record the command exactly as executed, its exit status, selected scope, and the candidate-bearing output.
2. Distinguish a successful finding exit from a tool/configuration/runtime failure. Do not reinterpret a failure as “no candidates.”
3. Normalize candidates by symbol, declaration path, and line. Deduplicate multiple diagnostics from the same analyzer family.
4. Split production declarations from declarations inside test, fixture, example, benchmark, generated, vendored, and build trees.
5. Bound follow-up to the configured limit. If output exceeds it, sort deterministically by repository-relative path, line, and symbol; report truncation.

Do not promote compiler warnings that concern imports, variables, dependencies, unreachable branches, or files into symbol-deletion claims without retaining their actual category. “Unused dependency” and “dead production symbol” are different cleanup classes.

**Completion:** every candidate came from a named, configured, freshly executed project-native analyzer, or the reportable absence/failure of such a generator is established.
