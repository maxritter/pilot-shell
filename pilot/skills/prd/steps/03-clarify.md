---

## Step 3: Ask Clarifying Questions

**⛔ ALWAYS use the `AskUserQuestion` tool** — never list numbered questions in plain text. Each question gets its own entry with 2-4 predefined options users can select. This provides a structured form UI that is much easier to answer than freeform text.

**One question at a time.** Each `AskUserQuestion` call should focus on a single decision point.

Focus on understanding:
- **Purpose** — what's the core outcome the user wants?
- **Users** — who benefits from this? What's their workflow today?
- **Constraints** — timeline, technical limitations, existing architecture
- **Success criteria** — how will we know this works?
- **Scope boundaries** — what's explicitly NOT included?

**Question format:** Every question must have 2-4 concrete options with trade-offs. Use `multiSelect: true` when choices aren't mutually exclusive. Include an "Other" option when the user might have a direction you haven't considered.

**Principles:**
- Challenge assumptions — "You mentioned X. Have you considered Y?"
- Surface trade-offs — "That's possible, but it comes at the cost of Z"
- Be constructive but strategic — don't be a yes-man
- If the idea has red flags or scope creep risks, raise them now
- Typically 3-6 questions total, depending on complexity
