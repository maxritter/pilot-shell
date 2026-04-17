---

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

| Scope | When | Create in | After creating |
|-------|------|-----------|----------------|
| **Project** | Skill is specific to this repo | `.claude/skills/{slug}-{name}/SKILL.md` | Nothing needed |
| **Global** | Skill applies across projects | `~/.claude/skills/{slug}-{name}/SKILL.md` | Nothing needed |

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
targets: [claude]
tags: [category, domain]
license: MIT
allowed-tools: Bash(python:*) WebFetch  # Optional — restrict which tools the skill can use
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
| `allowed-tools` | No | Restrict which tools the skill can access (e.g., `Bash(python:*) WebFetch`) |
| `compatibility` | No | Environment requirements (1-500 chars) |
| `metadata` | No | Custom key-value pairs: `author`, `version`, `mcp-server`, `category`, etc. |

**Security restrictions:** No XML angle brackets (`<` `>`) in frontmatter — frontmatter appears in the system prompt. Skills with "claude" or "anthropic" in the name are reserved.

### The Description Field

**Formula:** `[What it does] + [When to use it] + [Key capabilities]`

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

# Missing triggers — Claude can't match user requests
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

**⚠️ The Description Trap:** If description summarizes the workflow, Claude follows the short description as a shortcut instead of reading SKILL.md. Always describe trigger conditions, not process.

**Make descriptions "pushy"** — Claude tends to undertrigger skills (not use them when they'd help). Combat this by being explicit about when to activate. Instead of "How to build a dashboard for internal data", write "How to build a dashboard for internal data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard.'"

### Progressive Disclosure

Three-level system — each level loads only when needed:

| Level | What | When Loaded | Context Cost |
|-------|------|-------------|--------------|
| **1. Frontmatter** | `description` in YAML | Always (system prompt) | ~100 tokens |
| **2. SKILL.md body** | Full instructions | When Claude thinks skill is relevant | ~1000+ tokens |
| **3. Linked files** | `scripts/`, `references/`, `assets/` | When Claude navigates to them | Only on demand |

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

**Keep the skill lean** — Remove instructions that aren't pulling their weight. If test runs show the model wasting time on unproductive steps, cut the instructions causing it. Every line should earn its context tokens.

**Include error handling** — anticipate what goes wrong and provide fixes in the skill.

**Put critical instructions at the top** — use `## Important` or `## Critical` headers. Repeat key points if needed — instructions buried at the bottom get ignored.

**Generalize, don't overfit** — Skills are used across many different prompts. If you're testing with specific examples, make sure instructions generalize beyond those examples. Fiddly, overly specific changes that only fix one test case make the skill worse overall.

**Bundle repeated patterns** — After test runs, review what the model did. If every test case independently wrote a similar helper script or took the same multi-step approach, that's a signal the skill should bundle that script in `scripts/`. Write it once — save every future invocation from reinventing the wheel.
