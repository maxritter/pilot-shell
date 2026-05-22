---
sidebar_position: 4
title: Rules & Standards
description: Production-tested rules and standards loaded into every Claude Code session — TDD enforcement, language standards, MCP routing, and project conventions.
---

# Rules & Standards

Production-tested best practices loaded into every session.

Rules load automatically at session start — they're enforced standards, not suggestions. Pilot ships 10 built-in rules plus 5 coding standards. Coding standards load conditionally by file type to keep context lean. Your project-level rules in `.claude/rules/` take precedence over Pilot's built-ins.

## Built-in Rule Categories

### Core Workflow (3 rules)

- `task-and-workflow.md` — Task management, /spec orchestration, deviation handling
- `testing.md` — TDD workflow with `Trivial:` escape, parsimony-first test design (reuse existing tests; max 1 unit + 1 functional test class when new coverage is needed), critical-path coverage review
- `verification.md` — Execution verification, completion requirements

### Development Practices (3 rules)

- `development-practices.md` — Project policies, systematic debugging, git rules
- `code-review-reception.md` — How to receive and act on code review feedback
- `documentation-sync.md` — Update affected docs (README, API docs, CLAUDE.md, AGENTS.md) in the same change as the code

### Tooling & Context (3 rules)

- `cli-tools.md` — Pilot CLI, Semble hybrid code search, RTK token optimization
- `browser-automation.md` — Browser automation for E2E UI testing (Chrome → Chrome DevTools MCP → playwright-cli → agent-browser)
- `mcp-servers.md` — MCP server reference and tool selection guidance

## Coding Standards — Activated by File Type

| Standard | Activates On | Coverage |
|----------|-------------|----------|
| Python | `*.py` | uv, pytest, ruff, basedpyright, type hints |
| TypeScript | `*.ts, *.tsx, *.js, *.jsx` | npm/pnpm, Jest, ESLint, Prettier, React patterns |
| Go | `*.go` | Modules, testing, formatting, error handling |
| Frontend | `*.tsx, *.jsx, *.html, *.vue, *.css` | Components, CSS, accessibility, responsive design |
| Backend | `**/models/**, **/routes/**, **/api/**` | API design, data models, query optimization, migrations |

:::tip Custom rules
Create `.claude/rules/my-rule.md` in your project. Add `paths: ["*.py"]` frontmatter to activate only for specific file types. Run `/setup-rules` to auto-discover patterns and generate project-specific rules.
:::

:::info Monorepo support
Organize rules in nested subdirectories by product and team (e.g. `.claude/rules/my-product/team-x/`). Team-level rules must use `paths` frontmatter to scope to the right files. `/setup-rules` generates a `README.md` in your rules directory to document the structure.
:::

## Testing posture: parsimonious by default

The default `testing.md` rule defines the agent's testing posture. Pilot's default is **parsimonious**:

- **Reuse existing behavioural tests first.** When a new public production class truly needs new tests, the ceiling is 1 unit test class + 1 functional test class (only when behaviour cannot be covered through unit tests). One test class per production class is the ceiling, not the floor — splitting tests per-method or mirroring code structure in tests is an anti-pattern (per Uncle Bob's *Test Contravariance* and Kent Beck's *Test Desiderata* "structure-insensitive" property).
- **Coverage gate scoped to critical paths** (business logic, security, data integrity, error handling). No blanket numeric threshold on glue code, configuration plumbing, simple CRUD, or trivial UI bindings. Coverage padding to push a number above a threshold is an anti-pattern.
- **TDD with documented escapes.** Red-green-refactor remains the default. The `Trivial:` plan-task field is the documented opt-out for changes ≤ 5 net new lines with no new branch, public symbol, or error path, and it must name an existing covering test or verification command. Bugfixes never qualify — a reproducing RED test is the bugfix lane's anti-regression guarantee.
- **Post-implementation enforcement.** The `changes-review` reviewer agent and the `spec-verify` Step 5 audit ("Test Parsimony Audit" + "Trivial: claim audit") verify the doctrine against the actual diff — the planner's claim is not authoritative.

### Why parsimony

User feedback (paraphrased): *"90% of the time, the agent tries to test too much, doing redundant tests that just add to the maintenance cost. It also tends to create one test class for each tiny part of the logic of a given class instead of 1 class = 1 unit test + 1 functional test (if needed)."* The default codifies that complaint as the rule.

### Override the testing posture

If your project wants strict TDD on every change, blanket 80 % coverage, or a different posture, create `.claude/rules/testing-project.md` in the repository — it shadows Pilot's global `testing.md`. The shadow file can be as small as a few overriding sections (the rest of the global rule still applies). Suggested structure:

```markdown
---
paths: ["**/*.py", "**/*.ts", "**/*.tsx"]
---

## Testing override

This project requires:
- Strict TDD on every code change (no `Trivial:` escape).
- 80 % minimum coverage across the entire codebase, not just critical paths.
- One test class per production class is acceptable; do not consolidate.
```

See `pilot/rules/testing.md` § Default Posture for the full doctrine that the shadow file overrides.

### Anti-patterns the parsimony rule rejects

| Anti-pattern | Why it's rejected |
|--------------|-------------------|
| One test class per method (e.g. `DoSomethingTests` for `Foo.DoSomething()`) | Couples test layout to implementation detail; refactor moves a method, all tests break. Reviewer flags as `must_fix`. |
| Mirroring code structure in tests | Behaviour-preserving refactor must not break the suite; structure-insensitive is a Test Desideratum. Flagged as `suggestion`. |
| Redundant assertions on the same path | Three tests asserting the same observable behaviour through three internal paths is one test, not three. Maintenance tax with no signal. Flagged as `should_fix`. |
| Test-per-trivial-helper | A one-line getter/formatter with no branches and no public-API exposure is covered by the test for the function that uses it. |
| Coverage padding to hit a threshold | Numbers are a side-effect of testing what matters, not the goal. Threshold-driven test creation is rejected. |
| `Trivial:` justification used to skip TDD on a non-trivial change | Post-implementation `Trivial:` claim audit verifies the field names an existing covering check and that the diff meets the four criteria (≤ 5 production lines, no new branch with non-trivial body, no new public symbol, no new error path). Mismatch → `must_fix`, remove `Trivial:`, write a real RED test. |
