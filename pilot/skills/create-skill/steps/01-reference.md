## Step 1: Reference

### Quality Criteria

- **Reusable**: Will help future tasks, not just this instance
- **Non-trivial**: Required discovery or is a valuable workflow pattern
- **Verified**: Solution actually worked

**Do NOT extract:** Single-step tasks, one-off fixes, knowledge in official docs.

### Project Slug

Prefix ALL created skills with the project slug to avoid name collisions across repos.

```bash
SLUG=$(basename "$(git remote get-url origin 2>/dev/null | sed 's/\.git$//')" 2>/dev/null || basename "$PWD")
# Result: "pilot-shell", "my-api", "acme-backend"
```

**Skill scope:** Choose project or global based on reusability.

<!-- CC-ONLY -->
| Scope | When | Create in | After creating |
|-------|------|-----------|----------------|
| **Project** | Skill is specific to this repo | `.claude/skills/{slug}-{name}/SKILL.md` | Nothing needed |
| **Global** | Skill applies across projects | `~/.claude/skills/{slug}-{name}/SKILL.md` | Nothing needed |
<!-- /CC-ONLY -->
<!-- CODEX-START
| Scope | When | Create in | After creating |
|-------|------|-----------|----------------|
| **Project** | Skill is specific to this repo | `.agents/skills/{slug}-{name}/SKILL.md` | Nothing needed |
| **Global** | Skill applies across projects | `~/.agents/skills/{slug}-{name}/SKILL.md` | Nothing needed |

Codex project instructions belong in repo-root `AGENTS.md`; skill instructions belong in `.agents/skills/<name>/SKILL.md` or `~/.agents/skills/<name>/SKILL.md`. Do not put Codex skills in `AGENTS.md`.
CODEX-END -->

**Naming rules:** Lowercase with hyphens only. The slug provides context; the name should be 1-3 words max that are descriptive (not generic). Examples: `pilot-shell-lsp-cleaner`, `my-api-auth-flow`, `acme-deploy`. Never use generic names like "helper", "utils", "tools", "handler", "workflow".

### Use Case Categories

Identify which category your skill falls into — this guides the structure:

| Category | Used For | Key Techniques |
|----------|----------|----------------|
| **Document & Asset Creation** | Consistent output (reports, designs, code) | Embedded style guides, templates, quality checklists |
| **Workflow Automation** | Multi-step processes with consistent methodology | Step-by-step gates, validation, iterative refinement |
| **MCP Enhancement** | Workflow guidance on top of MCP tool access | Multi-MCP coordination, domain expertise, error handling |

### Skill Complexity Spectrum

**Move left whenever possible** — simpler skills are more reliable, cheaper to execute, and work across more models.

| Level | Style | Determinism | Best For |
|-------|-------|-------------|----------|
| **Passive** | Context only | N/A | Background knowledge, coding standards |
| **Instructional** | Rules + guidelines | Medium | Code review, style guides |
| **CLI Wrapper** | Calls a binary/script | **High** | Automation, integrations, data processing |
| **Workflow** | Multi-step with validation | Medium | Deploy pipelines, migrations |
| **Generative** | Asks agent to write code | Low | Scaffolding, code generation |

**Key insight:** A skill that says "run `eslint --fix`" works on any model. A skill that says "analyze the code and suggest improvements" requires expensive reasoning. Prefer commands over descriptions, scripts over instructions, explicit values over judgment.

**Problem-first vs tool-first:** Does the user describe an outcome ("set up a project workspace") or a tool ("I have Notion MCP connected")? Problem-first skills orchestrate tools for outcomes. Tool-first skills teach best practices for tools users already have.

### Skill Template

Before writing, answer these five questions:

1. **When should this skill activate?** (→ becomes `description`)
2. **What inputs does it need?** (arguments, files, environment state)
3. **What does success look like?** (specific output, files created, commands run)
4. **What should it NOT do?** (explicit exclusions prevent scope creep)
5. **How do you verify it worked?** (include a validation step)

### File Structure

```
your-skill-name/
├── SKILL.md              # Required — main skill file (case-sensitive, exactly SKILL.md)
├── scripts/              # Optional — executable code (Python, Bash, etc.)
├── references/           # Optional — detailed docs loaded as needed
└── assets/               # Optional — templates, fonts, icons used in output
```

**Critical rules:**
- File MUST be exactly `SKILL.md` (not SKILL.MD, skill.md, or Skill.md)
- No `README.md` inside the skill folder — all docs go in SKILL.md or `references/`
- Keep SKILL.md under 5,000 words — move detailed docs to `references/` and link

```markdown
---
name: {slug}-descriptive-kebab-case-name
description: |
  [What it does] + [When to use it] + [Key capabilities].
  Use when user asks to [specific trigger phrases]. Include trigger conditions, scenarios, exact error messages.
targets: [claude, codex]
tags: [category, domain]
license: MIT
allowed-tools: Grep Glob  # Optional — restrict which tools the skill can use
compatibility: Requires Python 3.12+    # Optional — environment requirements (1-500 chars)
metadata:                               # Optional — custom key-value pairs
  author: Your Name
  version: 1.0.0
  mcp-server: server-name               # If skill enhances an MCP server
---

# Skill Name

## Instructions

### Step 1: [First Major Step]
Clear explanation of what happens.

### Step 2: [Next Step]
[Continue with concrete, verifiable steps]

## Common Issues

### [Error message or symptom]
**Cause:** [Why it happens]
**Solution:** [How to fix — specific command or action]

## Examples

### Example 1: [Common scenario]
User says: "[typical request]"
Actions: [what the skill does]
Result: [expected outcome]

## When NOT to Use
[Explicit exclusions — prevents scope creep and misactivation]
```

### Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Kebab-case only, no spaces or capitals, must match folder name |
| `description` | Yes | Under 1024 chars, no XML tags (`<` or `>`). Include WHAT + WHEN + trigger phrases |
| `targets` | No | Restrict sync to specific CLIs (e.g., `[claude]`). Omit to sync everywhere |
| `tags` | No | Categories for hub search and filtering (e.g., `[debugging, python]`) |
| `license` | No | License identifier (e.g., `MIT`, `Apache-2.0`) |
| `allowed-tools` | No | Restrict which tools the skill can access (e.g., `Grep Glob`) |
| `compatibility` | No | Environment requirements (1-500 chars) |
| `metadata` | No | Custom key-value pairs: `author`, `version`, `mcp-server`, `category`, etc. |

**Security restrictions:** No XML angle brackets (`<` `>`) in frontmatter — frontmatter appears in the system prompt. Skills with "claude" or "anthropic" in the name are reserved.

### The Description Field

**Formula:** `[What it does, at capability level] + [When to use it] + [Key capabilities]`

**Capability, never process.** "What it does" means the outcome the skill delivers — "generates PRDs", "reviews a diff". It does NOT mean the ordered steps the body governs: "brainstorm, challenge assumptions, define scope" is the process, and naming it hands the agent a summary it will act on instead of reading the skill (see *The Description Trap* below). Test: if you can renumber your description's clauses into the skill's steps, cut them.

**Good descriptions:**

```yaml
# Specific and actionable — includes trigger phrases
description: Analyzes Figma design files and generates developer handoff
  documentation. Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".

# Clear value proposition with scope
description: End-to-end customer onboarding workflow for PayFlow. Handles
  account creation, payment setup, and subscription management. Use when
  user says "onboard new customer", "set up subscription", or "create
  PayFlow account".
```

**Bad descriptions:**

```yaml
# Too vague — won't trigger
description: Helps with projects.

# Missing triggers — the agent can't match user requests
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

**⚠️ The Description Trap:** If description summarizes the workflow, the agent follows the short description as a shortcut instead of reading SKILL.md. Always describe trigger conditions, not process.

**Make descriptions "pushy"** — agents tend to undertrigger skills (not use them when they'd help). Combat this by being explicit about when to activate. Instead of "How to build a dashboard for internal data", write "How to build a dashboard for internal data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard.'"

**One trigger per branch** — pushy means covering every *distinct* way the skill gets used, not restating one way in synonyms. "Build features using TDD … use when the user asks for test-first development" is one branch written twice; collapse it and spend the words on a genuinely different trigger instead.

### Progressive Disclosure

Three-level system — each level loads only when needed:

| Level | What | When Loaded | Context Cost |
|-------|------|-------------|--------------|
| **1. Frontmatter** | `description` in YAML | Always (system prompt) | ~100 tokens |
<!-- CC-ONLY -->
| **2. SKILL.md body** | Full instructions | When Claude thinks skill is relevant | ~1000+ tokens |
<!-- /CC-ONLY -->
<!-- CODEX-START
| **2. SKILL.md body** | Full instructions | When Codex thinks skill is relevant or the user invokes `$skill-name` | ~1000+ tokens |
CODEX-END -->
| **3. Linked files** | `scripts/`, `references/`, `assets/` | When the agent navigates to them | Only on demand |

**Rule of thumb:** "Is this line worth the context tokens it costs?" Don't explain what AI already knows. Only add your project's specific conventions, internal APIs, and domain rules.

**Size limits:** SKILL.md under 5,000 words / 500 lines. Move detailed docs to `references/` and link:

```markdown
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
- Error codes and handling
```

### Instructions Best Practices

**Be specific and actionable:**

```markdown
# Good
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)

# Bad
Validate the data before proceeding.
```

**Explain the why, not just the what** — Today's LLMs are smart. They have good theory of mind and respond better to reasoning than rigid commands. If you find yourself writing ALWAYS or NEVER in all caps, reframe and explain *why* the thing matters. "Use YYYY-MM-DD format because downstream parsers reject other formats" is more effective than "ALWAYS use YYYY-MM-DD format."

**Keep the skill lean** — Remove instructions that aren't pulling their weight. If test runs show the model wasting time on unproductive steps, cut the instructions causing it. The bar for "pulling its weight" is the sentence-level no-op test in *Steering the Agent* below.

**Include error handling** — anticipate what goes wrong and provide fixes in the skill.

**Put critical instructions at the top** — use `## Important` or `## Critical` headers. Repeat key points if needed — instructions buried at the bottom get ignored.

**Generalize, don't overfit** — Skills are used across many different prompts. If you're testing with specific examples, make sure instructions generalize beyond those examples. Fiddly, overly specific changes that only fix one test case make the skill worse overall.

**Bundle repeated patterns** — After test runs, review what the model did. If every test case independently wrote a similar helper script or took the same multi-step approach, that's a signal the skill should bundle that script in `scripts/`. Write it once — save every future invocation from reinventing the wheel.

### Steering the Agent

A skill exists to make agent behavior predictable — same *process* every run, not same output. Five levers serve that (adapted from mattpocock/skills' writing-great-skills).

**Match the form to the failure — pick this before picking a lever.** The form that bulletproofs one failure type measurably backfires on another, so classify the baseline failure first (Step 6.2 shows you what it actually is):

| Baseline failure | Right form | Wrong form |
|---|---|---|
| Knows the rule, skips it under pressure | Prohibition + Excuse→Reality table + red flags (Step 7's rationalization-resistant design) | Soft guidance ("prefer…", "consider…") |
| Complies, but the output has the wrong shape (bloated, buried verdict, restated spec) | Positive recipe: state what the output IS — its parts, in order | Prohibition list ("don't restate", "never narrate") |
| Omits a required element from something it already produces | Structural: a REQUIRED field or slot in the template it fills in | Prose reminders near the template |
| Behavior should depend on a condition | Conditional keyed to an observable predicate ("if the brief exists, reference it") | Unconditional rule plus exemption clauses |

Prohibitions backfire on *shaping* problems because an agent under a competing incentive negotiates with "don't X"; a recipe leaves nothing to negotiate — the output matches the stated shape or it doesn't. Two rules apply whichever form you pick:

- **No nuance clauses.** "Don't X unless it matters" reopens the negotiation. Express a real exception as its own conditional on an observable predicate.
- **Exemption clauses don't scope.** "This limit doesn't apply to code blocks" still suppresses code blocks. If part of the output must be exempt, restructure so the rule can't reach it.

**Leading words** — a compact concept already in the model's pretraining (*relentless*, *tight*, *tracer bullet*, *fog of war*) that the agent thinks with while running the skill. Repeated as a token, it anchors a whole region of behavior in the fewest tokens — in the body it anchors execution, in the description it anchors invocation. Prefer an existing pretrained word over a coined term: a made-up word recruits no priors, so you pay in definition tokens what a pretrained word gives free. Hunt for restatements a leading word retires: "fast, deterministic, low-overhead" → a *tight* loop.

**Prompt the positive** — the default lever for every failure type except the discipline row above, where the table sends you to a prohibition instead. Naming what NOT to do drags the forbidden behavior into context and makes it *more* available ("don't think of an elephant"). State the target behavior ("write one-line comments", not "never write verbose comments"), and when a prohibition is the right form, pair it with what to do instead.

**Negative space** — every decision a skill leaves unstated is delegated to the agent's priors, not left neutral. Read the draft for its silences: for each thing the skill doesn't say, decide deliberately — fill it, or leave it open as a real branch. Omission is a choice; make it on purpose.

**Completion criteria** — every step ends on a condition that tells the agent it's done. Make it *checkable* (the agent can tell done from not-done — "every modified file accounted for", not "until it looks good") and, where it matters, *exhaustive*. A vague bound invites the agent to declare done early and rush to the next step; when you observe that rush, sharpen the criterion first — it's cheaper than restructuring the skill.

**The no-op test, per sentence** — for each sentence ask: does it change behavior versus what the agent does by default? If not, delete the whole sentence, don't trim words from it. "Be thorough" is a no-op (the agent is already thorough-ish); "relentless" passes. Apply it sentence by sentence on every revision.
