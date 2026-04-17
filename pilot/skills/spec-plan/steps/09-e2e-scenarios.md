### Step 9: E2E Test Scenarios (Conditional)

**Skip when:** Runtime profile would be Minimal (no UI, no server, no user-facing entry points). Use the same classification logic as `spec-verify` Step 3.0 — if Phase B would be skipped entirely, skip this step too.

For features with UI or user-facing workflows, create structured E2E scenarios describing exactly how a user verifies the feature works. These become the verification contract for Phase B in `spec-verify` — the verifier executes them step by step rather than improvising.

**Format — add as `## E2E Test Scenarios` section in the plan:**

```markdown
### TS-001: [Scenario Name]
**Priority:** Critical | High | Medium
**Preconditions:** [Required state — e.g., "logged in as admin", "no existing items"]
**Mapped Tasks:** Task 1, Task 3

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [Navigate / click / fill — concrete browser automation action] | [What user sees] |
| 2 | [Next action] | [Expected UI response] |
```

**Guidelines:**
- 3–8 scenarios typical — focus on user-visible workflows, not unit-level behavior
- **Critical** = must pass before deployment; **High** = essential UX; **Medium** = edge cases / error states
- Every task that changes UI or user-visible behavior must be covered by at least one scenario
- Steps must be executable via browser automation — Claude Code Chrome, playwright-cli, or agent-browser (concrete: navigate, click, fill, read page — no "observe manually")
- Test what users see, not internal implementation — same observable inputs and outputs

When scenarios are written, update Goal Verification truths to reference them (e.g., "TS-001 passes end-to-end").
