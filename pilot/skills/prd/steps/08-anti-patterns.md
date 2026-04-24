---

## Step 8: Anti-Patterns

- **Defaulting to free-form questions during the convergent phase** — once you're in Clarify/Converge (Step 3 onward), `AskUserQuestion` with predefined options is the default. Brief prose riffs are allowed when a question opens a genuinely new unknown (see Step 3), but don't drift back into open-ended chat for decisions that have a clean A/B/C shape.
- **Skipping ideation when the idea is vague** — if the user gave a problem statement instead of a solution, don't jump straight to structured questions. Brainstorm in prose first (Step 2b).
- **Pretending to ideate when the user already decided** — if the input is concrete, skip Step 2b. Don't pitch alternatives the user didn't ask for.
- **Rewriting the whole PRD when the user requests changes** — use `Edit` on specific sections so the user doesn't have to reload the file in their editor and re-read everything.
- **Rushing to solutions** — understand the problem first, always
- **Asking too many questions at once** — one at a time, each building on the last
- **Being a yes-man** — challenge assumptions, surface trade-offs
- **Over-specifying technically** — the PRD describes WHAT and WHY, `/spec` handles HOW
- **Skipping the conversation entirely** — even "simple" features benefit from 2-3 clarifying questions. Unexamined assumptions cause the most wasted work.
- **Letting one PRD swallow a whole platform** — if the request describes multiple independent subsystems, decompose in Step 1 before continuing.
