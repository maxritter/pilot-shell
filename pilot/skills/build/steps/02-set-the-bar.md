## Step 2: Set the Bar

If the user named a reference, use it — no question needed. If not, offer **2–3 candidates**, one line each, and stop for their pick. Do not proceed on a bar you chose alone.

<!-- CC-ONLY -->
Use `AskUserQuestion` for the pick — it renders a structured form; don't fall back to plain-text numbered questions. Skip the question entirely when `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"`: take the hardest candidate you can genuinely reach, name it in the rubric, and say in one line which one you took and why.
<!-- /CC-ONLY -->
<!-- CODEX-START
Present 2–3 plain-text numbered candidates with their trade-offs and wait for the user's answer. Skip the question entirely when `PILOT_PLAN_QUESTIONS_ENABLED` is `"false"`: take the hardest candidate you can genuinely reach, name it in the rubric, and say in one line which one you took and why.
CODEX-END -->

### A bar passes three tests

- **Named.** A specific thing. "Stripe's pricing page" works; "award-winning SaaS sites" does not.
- **Obtainable.** You can fetch it, screenshot it, read it, run it, or open it — and in Step 1 you already did.
- **Comparable.** Both artifacts can sit side by side and someone can pick one. If you cannot picture the A/B, it is not a bar.

| Goal | Bar that works |
|---|---|
| Website, app, UI | A named product's live page, screenshotted at the same viewport |
| Game, 3D, visual | Footage or stills from a named shipped title |
| Writing | A named author's published piece, same length and format |
| Code, tooling | A named repo's implementation, plus its benchmark or test suite |
| Research, analysis | A named report, or a paper's methods section |
| Deck, doc, deliverable | A real artifact from a firm known for it, same page count |
| A rewrite or migration | The **existing** artifact, captured before you touch it, plus one external reference |

**Prefer the hardest bar you can genuinely reach.** A soft bar makes the loop exit on round one, which is the same as not running it.

### Capture the bar so later rounds cannot drift

Recalling the bar is how the comparison quietly becomes "whatever we already made". Pin it to something re-openable and record *how* in the rubric:

- A URL plus the exact fetch or screenshot command.
- A file path under the project (a screenshot, a saved page, a reference doc).
- A command that reproduces it (`git show <ref>:<path>`, a benchmark invocation, a binary to run).

For a rewrite, capture the "before" **now** — once you start editing, the old version stops being obtainable.

**Done when:** the bar is named, obtained, the re-obtain command is written down, and the user has not objected.
