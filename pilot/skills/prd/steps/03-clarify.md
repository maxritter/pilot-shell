---

## Step 3: Ask Clarifying Questions

**⛔ ALWAYS use the `AskUserQuestion` tool** — never list numbered questions in plain text. Each question gets its own entry with 2-4 predefined options users can select. This provides a structured form UI that is much easier to answer than freeform text.

**One question at a time, building on previous answers.** Each `AskUserQuestion` call focuses on a single decision point, and the next question must follow from what the user just said — not from a fixed checklist. If the user's answer exposes a new assumption or constraint, pivot there instead of marching through pre-planned topics.

**⛔ Skip obvious questions.** Do not ask anything already answered by the one-line idea, the codebase exploration in Step 1, or earlier answers in this conversation. The goal is to surface what the user hasn't thought about yet, not to collect a standard intake form.

Coverage areas (ask only where genuinely unclear):
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
- Typically 3-6 questions total, depending on complexity — stop asking once you have 90% of the spec
