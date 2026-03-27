---
description: Create a well-structured skill — provide a topic to explore the codebase and build a skill interactively, or capture a workflow from the current session
user-invocable: true
effort: max
model: opus
---

# /create-skill — Skill Creator

**Create a reusable skill.** Provide a topic or workflow description, and this command explores the codebase, gathers relevant patterns, and builds a well-structured skill interactively with you. If no topic is given, it evaluates the current session for extractable knowledge.

---

## Phase 0: Reference

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

---

## Phase 1: Understand the Topic

**Start here — clarify what skill to build.**

If the user provided a topic or description, work with it. If not, evaluate the current session (see Session Mode below).

### Topic-Driven Mode (Primary)

1. Restate the topic in your own words — what workflow, pattern, or problem does this skill address?
2. Ask clarifying questions if needed:
   - What triggers this workflow? (specific error, specific task type, specific file pattern)
   - What does success look like? (a command runs successfully, a file is created, a pattern is consistently applied)
   - Is this specific to this project or reusable across projects?
3. **Explore the codebase for relevant patterns:**
   ```bash
   # Find existing patterns related to the topic
   probe search "<topic keywords>" ./ --max-results 5 --max-tokens 2000
   # Extract concrete examples
   probe extract <relevant-file>:<line>
   ```
   Or use `Grep`/`Glob` if Probe is not available.
4. Review any existing documentation or onboarding notes that cover this topic
5. Build understanding of the current state: what works, what's tricky, what's non-obvious

### Session Mode (Fallback — when no topic provided)

Ask yourself:

1. "What did I learn that wasn't obvious before starting?"
2. "Would future-me benefit from having this documented?"
3. "Was the solution non-obvious from docs alone?"
4. "Is this a multi-step workflow I'd repeat?"
5. "Did I query an external service the user will ask about again?"

**If NO to all → Skip, nothing to extract.** External service queries are almost always worth extracting.

---

## Phase 2: Check Existing

```bash
# Project skills
ls .claude/skills/ 2>/dev/null
rg -i "keyword" .claude/skills/ 2>/dev/null
# Global skills (user + Pilot defaults)
ls ~/.claude/skills/ 2>/dev/null
ls ~/.claude/pilot/skills/ 2>/dev/null
rg -i "keyword" ~/.claude/skills/ ~/.claude/pilot/skills/ 2>/dev/null
```

| Found | Action |
|-------|--------|
| Nothing related | Create new |
| Same trigger/fix | Update existing (bump version) |
| Partial overlap | Update with new variant |

---

## Phase 3: Create Skill

**Create the skill directory and SKILL.md:**

```bash
# Project scope — skill lives in this repo's .claude/skills/
mkdir -p .claude/skills/{slug}-{name}
# Write SKILL.md (see template in Phase 0)

# Global scope — skill applies across all projects
mkdir -p ~/.claude/skills/{slug}-{name}
# Write SKILL.md
```

Skills in `.claude/skills/` (project) or `~/.claude/skills/` (global) are automatically available to Claude — no sync step needed.

Edit the created `SKILL.md` with the skill content using the template from Phase 0.

**Portability checklist** — skills are shared with users who may NOT have Pilot Shell:

- **Only use built-in Claude Code tools** in skill instructions: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `Agent`, `WebFetch`, `WebSearch`, `Notebook`, `LSP`, `TodoRead`/`TodoWrite`
- **Never reference Pilot-specific tools:** `probe search/extract/query`, `agent-browser`, `pilot` CLI, Pilot MCP servers (`mem-search`, `context7`, `grep-mcp`, `web-fetch`, `web-search`)
- **Substitute with built-in equivalents:** `probe search` → `Grep`/`Glob`, `agent-browser` → `Bash` with `npx agent-browser`, web fetch → `WebFetch`
- If a skill genuinely requires a non-standard tool, document it as a prerequisite in the skill body (not silently assume it exists)

**Determinism checklist** — maximize reliability:

- Prefer exact commands over descriptions (`run prettier --write .` not "format the code")
- Prefer scripts over multi-step instructions (reference `scripts/deploy.sh` not 5 prose steps)
- Use explicit values over judgment (`block files > 100KB` not "block large files")
- For high-risk operations (DB migrations, deploys): exact commands, validation steps, rollback plan
- For low-risk operations (code review, docs): general guidelines, let AI use judgment

**One skill = one purpose.** If the skill handles review AND testing AND deployment, split it.

**Security:** Skills must not contain malware, exploit code, or content that could compromise system security. A skill's contents should not surprise the user in their intent. Don't create skills designed to facilitate unauthorized access or data exfiltration.

---

## Phase 4: Quality Gates

### Structure Checklist

- [ ] Folder named in kebab-case
- [ ] `SKILL.md` file exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, no spaces, no capitals, matches folder name
- [ ] `description` includes WHAT and WHEN (under 1024 chars, no XML tags)
- [ ] No `README.md` inside the skill folder
- [ ] SKILL.md under 5,000 words

### Content Checklist

- [ ] Instructions are clear and actionable (commands > descriptions)
- [ ] Error handling included (Common Issues section)
- [ ] Examples provided (concrete input/output)
- [ ] "When NOT to Use" section with explicit exclusions
- [ ] Verification step (how to confirm it worked)
- [ ] No sensitive information (API keys, passwords → use env vars)
- [ ] No hardcoded paths (use relative paths or environment variables)
- [ ] References clearly linked (to `references/` or external docs)

### Triggering Test

Before finalizing, verify the description will activate correctly:

```
Should trigger:
- "[exact phrases a user would say]"
- "[paraphrased version of the request]"
- "[related but different phrasing]"

Should NOT trigger:
- "[unrelated topic that sounds similar]"
- "[general request the skill shouldn't handle]"
```

**Debug approach:** Ask Claude "When would you use the [skill name] skill?" — Claude will quote the description back. Adjust based on what's missing.

---

## Phase 5: Test & Iterate

**When to use:** Complex workflow and generative skills benefit from testing. Simple passive/instructional skills can skip this phase.

### Step 1: Write Test Prompts

Create 2-3 realistic prompts — things a real user would actually say. Be specific and include context, not abstract requests.

```
# Bad — too clean, too obvious
"Create a chart from this data"

# Good — realistic, with context and personality
"ok so my boss sent me Q4_sales_final_v2.xlsx and wants me to add a profit
margin column. Revenue is in column C, costs in D i think"
```

Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?"

### Step 2: Run Tests with Subagents

For each test prompt, spawn a subagent that has access to the skill and ask it to complete the task. Save outputs to a workspace directory.

```
Workspace structure:
<skill-name>-workspace/
└── iteration-1/
    ├── test-1-descriptive-name/
    │   ├── with-skill/      # Output from agent using the skill
    │   └── without-skill/   # Baseline output (no skill)
    └── test-2-descriptive-name/
        ├── with-skill/
        └── without-skill/
```

**With-skill run** — subagent prompt:
```
Complete this task using the [skill-name] skill at [path]:
Task: [test prompt]
Save outputs to: [workspace]/iteration-N/test-ID/with-skill/
```

**Baseline run** — same prompt, but tell the subagent to NOT use the skill. This reveals what value the skill actually adds.

Launch all runs in parallel (with-skill AND baseline for each test case) to save time.

### Step 3: Evaluate Results

**Qualitative review:** Present outputs to the user side-by-side (with-skill vs baseline). Ask: "How do these compare? Anything the skill should do differently?"

**Quantitative assertions (optional):** For skills with objectively verifiable outputs, define assertions:

```json
{
  "test_id": 1,
  "test_name": "quarterly-report-margins",
  "prompt": "...",
  "assertions": [
    {"text": "Output file contains profit margin column", "type": "file_check"},
    {"text": "Margins calculated as (revenue - cost) / revenue", "type": "correctness"},
    {"text": "Handles negative margins without crashing", "type": "edge_case"}
  ]
}
```

Grade each assertion as pass/fail with evidence. Prefer programmatic checks (run a script) over eyeballing — scripts are faster, more reliable, and reusable across iterations.

**Don't force assertions on subjective skills** — writing style, design quality, and creative output are better evaluated qualitatively by the user.

**Blind comparison (optional):** For more rigorous evaluation, spawn an independent subagent that receives both outputs (with-skill and baseline) WITHOUT knowing which is which. Let it judge quality. This removes bias from the evaluation — if the independent judge consistently prefers the with-skill output, the skill is adding real value.

### Step 4: Iterate

Based on feedback:

1. **Identify patterns** — What went wrong across test cases? Is it a structural issue or a wording issue?
2. **Improve the skill** — Apply changes, focusing on generalizable fixes (not overfitting to test cases)
3. **Rerun all tests** into `iteration-N+1/` — compare with previous iteration
4. **Repeat** until the user is satisfied or feedback is all positive

**Stop when:** User says it's good, all feedback is empty (everything looks fine), or improvements plateau.

### Step 5: Description Optimization

After the skill works well, optimize its triggering accuracy.

**Generate 16-20 diverse trigger queries** — a mix of should-trigger and should-not-trigger:

**Should-trigger queries (8-10):**
- Different phrasings of the same intent (formal, casual, terse)
- Cases where the user doesn't name the skill but clearly needs it
- Uncommon use cases and edge cases
- Queries where this skill competes with another but should win

**Should-not-trigger queries (8-10):**
- **Near-misses** — queries that share keywords but need something different
- Adjacent domains with ambiguous phrasing
- Queries that touch on something the skill does but in a context where another approach is better

**Make queries realistic** — include file paths, personal context, abbreviations, typos, casual speech, varying lengths. Bad: `"Format this data"`. Good: `"i have this csv from marketing (campaigns_q4.csv) and need to pivot it so each campaign type is a column with spend as values, can you also add a total row at the bottom"`.

**How skill triggering works:** Skills appear in Claude's `available_skills` list with their name + description. Claude decides whether to consult a skill based on that description alone. Important: Claude only consults skills for tasks it can't easily handle on its own — simple one-step queries like "read this file" won't trigger a skill even if the description matches, because Claude can handle them directly. Your test queries should be substantive enough that Claude would actually benefit from consulting a skill.

**Test triggering accuracy:**

```bash
# For each query, test if Claude would trigger the skill
# Run in a new session or use claude -p (pipe mode)
echo "<test query>" | claude -p "Would you use the [skill-name] skill for this request? Answer only YES or NO."
```

**Iterate on the description** based on mismatches:
- Should-trigger but didn't → add relevant trigger phrases/scenarios to description
- Shouldn't-trigger but did → add "Do NOT use for..." exclusions, narrow the scope

Run 2-3 iterations. If available, split queries 60/40 into train/test sets — optimize on train, validate on test to avoid overfitting the description to your specific queries.

---

## Anti-Patterns & Troubleshooting

| Anti-Pattern | Fix |
|--------------|-----|
| **Kitchen sink** — skill does too many things | One skill = one purpose. Split it. |
| **Vague instructions** — "properly format the code" | Name the specific tool and command |
| **Explaining AI knowledge** — "React is a JavaScript library..." | Only add what AI doesn't know: YOUR conventions |
| **Too many options** — "use pdfplumber, PyMuPDF, or camelot..." | Give one default, mention alternatives only if needed |
| **No verification** — "deploy to staging" (how do you know it worked?) | Always include a verification command |
| **Hardcoded paths** — `/Users/john/projects/my-app/...` | Relative paths or environment variables |
| **Ambiguous language** — "Make sure to validate things properly" | `CRITICAL: Before calling create_project, verify: project name non-empty, at least one team member assigned` |

### Iteration Signals

| Signal | Symptom | Fix |
|--------|---------|-----|
| **Undertriggering** | Skill doesn't load when it should, users manually enabling it | Add more detail and trigger keywords to description |
| **Overtriggering** | Skill loads for irrelevant queries, users disabling it | Add negative triggers ("Do NOT use for..."), be more specific |
| **Instructions not followed** | Claude loads skill but ignores steps | Instructions too verbose (condense), buried (move critical to top), or ambiguous (use exact commands) |
| **Large context issues** | Skill seems slow or responses degraded | Move detailed docs to `references/`, keep SKILL.md under 5,000 words |

---

## Example

**Scenario:** User asks to create a skill for finding dead code using LSP.

**Result:** `.claude/skills/my-project-lsp-cleaner/SKILL.md`

```yaml
name: my-project-lsp-cleaner
description: |
  Find dead/unused code using LSP findReferences. Use when: (1) user asks
  to find dead code, (2) cleaning up codebase, (3) refactoring. Key insight:
  function with only 1 reference (definition) or only test refs is dead code.
targets: [claude]
tags: [refactoring, code-quality]
license: MIT
author: Claude Code
version: 1.0.0
```
