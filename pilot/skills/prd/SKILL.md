---
name: prd
description: "Generate Product Requirements Documents with optional research — brainstorm, challenge assumptions, define scope"
argument-hint: "<idea or feature description>"
user-invocable: true
effort: high
model: opus
---

# /prd - Generate Product Requirements Documents

**Strategic thought partner** — turns vague ideas into concrete Product Requirements Documents (PRDs) through one-on-one conversation, with optional research. Produces a PRD that can be handed off directly to `/spec` for implementation.

**Use `/prd` when:** You have an idea but aren't ready to spec it. Requirements are unclear. You need to explore trade-offs, challenge assumptions, or define scope before committing to a plan.

**Use `/spec` instead when:** Requirements are well-defined. You know what to build and roughly how. Skip straight to technical planning.

---

## Workflow

```
Understand → Research (optional) → Clarify → Propose → Converge → Write PRD → Hand off to /spec
```

The entire flow is conversational. One question at a time. No rushing to solutions.

---

## Phase 1: Understand the Idea

1. **Restate the idea** in your own words — confirm you understand what the user is thinking
2. **Explore the project context with CodeGraph** — start with `codegraph_context(task="<idea description>")` to discover relevant entry points, symbols, and existing code. Use `codegraph_search` + `codegraph_explore` for deeper understanding of specific areas. Use `codegraph_files` to understand project structure. Check docs and recent commits for additional context.
3. **Identify the core problem** — what problem does this solve? For whom? Why now?

Do NOT jump to solutions. Understand the problem space first.

---

## Phase 1.5: Research (Optional)

**After understanding the idea, ask the user which research tier they want.** Use `AskUserQuestion` with these options:

- **Quick (Recommended for simple ideas)** — "Skip research, go straight to brainstorming"
- **Standard** — "Quick web research: competitors, prior art, best practices (5-10 searches)"
- **Deep** — "Thorough parallel research: multiple angles, comprehensive findings (uses sub-agents, higher token cost)"

### Quick Tier

Skip this phase entirely. Proceed to Phase 2.

### Standard Tier

1. **Generate 5-8 search queries** based on the topic:
   - Competitor/alternative analysis ("alternatives to X", "X vs Y")
   - Prior art and existing solutions ("how companies solve X")
   - Technical approaches ("best practices for X")
   - User experience patterns ("UX patterns for X")
2. **Discover web-search tool:** `ToolSearch(query="+web-search search")`
3. **Execute searches sequentially**, gathering key findings from each
4. **Optionally fetch full pages** for promising results: `ToolSearch(query="+web-fetch fetch")` then `fetch_url(url="...")`
5. **Compile research summary:**
   - Key findings (3-5 bullet points)
   - Sources with links
   - Trade-offs and patterns discovered
   - Gaps or areas needing more exploration
6. **Present summary to user** before proceeding to brainstorming

### Deep Tier

1. **Generate a research outline** with 3-5 research angles based on the topic. Examples:
   - "Competitor landscape" — what exists, market positioning, pricing
   - "Technical approaches" — architectures, frameworks, implementation patterns
   - "User experience" — UX patterns, onboarding flows, common pain points
   - "Prior art" — academic papers, blog posts, case studies
2. **Launch 2-4 web-search-agent sub-agents in parallel:**

   For each research angle:
   ```
   Agent(
     subagent_type="web-search-agent",
     run_in_background=true,
     prompt="Research angle: <angle_name>\n\nTopic: <user_topic>\n\nFocus on: <specific questions for this angle>\n\nReturn findings in this format:\n## <Angle Name>\n### Key Findings\n- ...\n### Sources\n- [Link](url)\n### Trade-offs & Considerations\n- ...\n\nWrite your findings to: <output_path>"
   )
   ```

   Output path: `/tmp/prd-research-<angle-slug>.md`

3. **Wait for all agents to complete** (bash polling):
   ```bash
   for i in $(seq 1 120); do
     COUNT=$(ls /tmp/prd-research-*.md 2>/dev/null | wc -l)
     [ "$COUNT" -ge <expected_count> ] && echo "ALL_DONE" && break
     sleep 2
   done
   ```
4. **Read all output files** and synthesize into a comprehensive research summary
5. **Present synthesized findings to user** — organized by angle, with key insights highlighted
6. **Clean up temp files:** `rm -f /tmp/prd-research-*.md`

**Cap:** Maximum 4 parallel agents, each limited to 5 search queries.

### Research Output

When research was performed (Standard or Deep), the findings are embedded in the PRD under a `## Research Findings` section after Key Decisions.

---

## Phase 2: Ask Clarifying Questions

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

---

## Phase 3: Propose Approaches

After understanding the problem:

1. **Propose 2-3 approaches** with clear trade-offs
2. **Lead with your recommendation** and explain why
3. **Present approaches as context**, then use `AskUserQuestion` for selection
4. **Get the user's choice** before proceeding

Each approach should have:
- A short name
- How it works (2-3 sentences)
- Trade-offs framed as "X at the cost of Y"

**Selection:** After presenting approaches in text, use `AskUserQuestion` with each approach as an option. Mark your recommended approach clearly. The user selects — don't proceed without a choice.

---

## Phase 4: Converge on Scope

Based on the chosen approach:

1. **State what's in scope** — concrete deliverables
2. **State what's explicitly out** — and why (prevent scope creep later)
3. **Identify the core user flows** — step by step from the user's perspective
4. **Note any technical context** that `/spec` will need — constraints, integration points, existing patterns

**Confirm scope with `AskUserQuestion`:**
- "Yes, scope looks right — proceed to PRD"
- "No, I want to adjust scope" — let me specify what to add/remove
- "Let's discuss further" — I have questions about the scope

---

## Phase 5: Write the PRD

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

**Category selection:** During the conversation (Phase 2 or Phase 4), use `AskUserQuestion` to select the PRD category from the fixed set: Feature, Infrastructure, UX, API, Performance, Security, Documentation, Integration.

After writing:
1. **Self-review** — scan for placeholders, ambiguity, contradictions
2. **Set Status to Final** when user confirms
3. **Present to user** — summarize what the PRD covers
4. **Use `AskUserQuestion`** to confirm:
   - "Looks good — proceed to handoff" — PRD is ready
   - "I want to adjust something" — let me specify changes
   - "Start over on a section" — a section needs rethinking

---

## Phase 6: Hand Off to /spec

After the user confirms the PRD:

**Ask:** "Ready to hand this off to `/spec` for implementation planning?"

Use `AskUserQuestion` with options:
- **"Yes, start /spec now"** — invoke `/spec` immediately
- **"No, I'll run /spec later"** — just confirm the PRD path

### If yes — invoke /spec:

```
Skill('spec', args='<one-line-summary> — PRD: docs/prd/YYYY-MM-DD-slug.md — see PRD for full requirements')
```

**The args string must NOT end in `.md`** — the trailing text after the path prevents the `/spec` dispatcher from treating it as an existing plan file. The dispatcher only triggers plan-file mode when args end with `.md` AND the file exists.

### If no:

```
PRD saved to docs/prd/YYYY-MM-DD-slug.md

To implement later, run:
  /spec "Implement <summary> — PRD: docs/prd/YYYY-MM-DD-slug.md — see PRD for full requirements"
```

---

## Anti-Patterns

- **Free-form text questions** — never list numbered questions in plain text. Always use `AskUserQuestion` with predefined options
- **Rushing to solutions** — understand the problem first, always
- **Asking too many questions at once** — one at a time, each building on the last
- **Being a yes-man** — challenge assumptions, surface trade-offs
- **Over-specifying technically** — the PRD describes WHAT and WHY, `/spec` handles HOW
- **Skipping the conversation** — even "simple" features benefit from 2-3 clarifying questions. Unexamined assumptions cause the most wasted work.

---

## Key Principles

- **One question at a time** — don't overwhelm
- **Multiple choice preferred** — easier to answer than open-ended
- **Challenge assumptions** — be a strategic thought partner
- **YAGNI ruthlessly** — remove unnecessary scope
- **Explore alternatives** — always propose 2-3 approaches
- **Converge explicitly** — state the scope, get confirmation
- **Write for handoff** — the PRD is a contract between requirements and specification

ARGUMENTS: $ARGUMENTS
