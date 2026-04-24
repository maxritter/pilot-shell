---

## Step 6: Write the PRD

**Save to:** `docs/prd/YYYY-MM-DD-<slug>.md`

Generate the filename from the first 3-4 words of the idea (lowercase, hyphens). Create the `docs/prd/` directory if it doesn't exist:

```bash
mkdir -p docs/prd
```

### PRD Format

```markdown
# [Feature Name]

Created: YYYY-MM-DD
Author: [user email from pilot status]
Category: [one of: Feature, Infrastructure, UX, API, Performance, Security, Documentation, Integration]
Status: Draft
Research: [Quick | Standard | Deep | None]

## Problem Statement

[Concise paragraph: what problem, for whom, why now. This is the north star.]

## Core User Flows

[Step-by-step from the user's perspective. How does the primary user accomplish the core outcome?]

### Flow 1: [Name]
1. User does X
2. System responds with Y
3. ...

### Flow 2: [Name] (if applicable)
1. ...

## Scope

### In Scope
- [Concrete deliverable 1]
- [Concrete deliverable 2]

### Explicitly Out of Scope
- [What's excluded] — [why]
- [What's excluded] — [why]

## Technical Context

[Lightweight technical notes for the implementer. NOT a full technical design — that's /spec's job.]

- **Relevant architecture:** [existing patterns, integration points]
- **Constraints:** [technical limitations, dependencies]
- **Existing code:** [files/modules that relate to this feature]

## Key Decisions

[Trade-offs and decisions made during the conversation, with reasoning.]

| Decision | Choice | Why |
|----------|--------|-----|
| [What was decided] | [The choice] | [Reasoning] |
```

**Fetch author email** (best-effort):

```bash
~/.pilot/bin/pilot status --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email',''))" 2>/dev/null
```

If the command returns a non-empty email, include `Author: <email>` in the header. If empty or fails, omit the Author line.

**Category selection:** During the conversation (Step 3 or Step 5), use `AskUserQuestion` to select the PRD category from the fixed set: Feature, Infrastructure, UX, API, Performance, Security, Documentation, Integration.

After writing:

1. **Self-review (4-point scan)** — read the file with fresh eyes and fix issues inline:
   - **Placeholders:** any `TBD`, `TODO`, bracketed `[...]` left from the template, or vague "etc." lists?
   - **Internal consistency:** do scope, user flows, and decisions agree with each other? Does anything contradict?
   - **Scope:** focused enough for one `/spec` plan, or did decomposition slip? If it grew during writing, split or trim.
   - **Ambiguity:** could any requirement be read two different ways? Pick one and make it explicit.

   **Calibration — only flag what would actually cause problems during `/spec`.** A missing section, a contradiction, or a requirement so ambiguous it could be built two different ways → fix it. Minor wording improvements, stylistic preferences, sections that are less detailed than others, or "this paragraph could be tighter" → leave it alone. The goal is a PRD that produces a correct plan, not a perfect document.

2. **Tell the user the file is ready and ask them to read it.** Do NOT jump straight to a confirmation form — give them a chance to actually open the file first:

   > "PRD written to `docs/prd/YYYY-MM-DD-<slug>.md`. Please open it in your editor and read it through, then let me know if anything needs to change before we hand off to `/spec`."

   Wait for the user's response. They may reply with edits in chat ("change scope item 3 to ...") or confirm it's good.

3. **Apply any requested changes** with `Edit` directly on the file — don't rewrite the whole document. Then re-run the 4-point scan and ask the user to re-read **only the changed sections**.

4. **Set Status to Final** once the user approves.

5. **Confirm next step with `AskUserQuestion`:**
   - "Looks good — proceed to handoff" — PRD is ready
   - "I want to adjust something else" — let me specify changes
   - "Start over on a section" — a section needs rethinking
