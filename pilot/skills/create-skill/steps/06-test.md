## Step 6: Test & Iterate

**When to use:** Complex workflow and generative skills benefit from testing. Simple passive/instructional skills can skip this phase.

### Step 6.1: Write Test Prompts

Create 2-3 realistic prompts — things a real user would actually say. Be specific and include context, not abstract requests.

```
# Bad — too clean, too obvious
"Create a chart from this data"

# Good — realistic, with context and personality
"ok so my boss sent me Q4_sales_final_v2.xlsx and wants me to add a profit
margin column. Revenue is in column C, costs in D i think"
```

Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?"

### Step 6.1a: Micro-Test the Wording First

Full A/B runs are the final gate, but they are slow per iteration. When you are writing behaviour-shaping wording — a rule, a rationalization row, a dispatch-prompt instruction — verify the wording itself first with cheap one-shot samples:

1. **One fresh-context sample per call.** System prompt = the realistic context the guidance will live in (the whole skill or prompt, not the guidance in isolation); user message = a task that tempts the failure.
2. **Always run a no-guidance control.** If the control does not exhibit the failure, there is nothing to fix — stop, and do not author the guidance.
3. **5+ reps per variant.** Single samples lie.
4. **Read every flagged match yourself.** Score programmatically if you like, but template echoes and quoted counter-examples masquerade as hits and inflate both failure and success counts.
5. **Treat variance as a metric.** When guidance lands, reps converge on the same shape. Five different interpretations across five reps means the wording is not binding — tighten the form (Step 1's *Match the form to the failure*) before adding words.

Micro-tests verify wording. They do not replace the with-skill vs baseline runs below for discipline skills.

### Step 6.2: Run Tests

<!-- CC-ONLY -->
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
<!-- /CC-ONLY -->
<!-- CODEX-START
For each test prompt, run `codex exec` in isolated sandbox directories — one with the skill installed, one without. Save outputs to a workspace directory.

```
Workspace structure:
<skill-name>-workspace/
└── iteration-1/
    ├── test-1-descriptive-name/
    │   ├── with-skill/      # Output from codex exec with skill installed
    │   └── without-skill/   # Baseline output (no skill)
    └── test-2-descriptive-name/
        ├── with-skill/
        └── without-skill/
```

**With-skill run** — create a temp directory with the skill installed under `.agents/skills/<name>/SKILL.md`, then:
```bash
cd <workspace>/iteration-N/test-ID/with-skill/
codex exec "Complete this task: [test prompt]. Save outputs to the current directory."
```

**Baseline run** — same prompt, but in a directory without the skill installed.

Run all test cases sequentially (Codex does not support parallel subagents).
CODEX-END -->

### Step 6.3: Evaluate Results

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

### Step 6.4: Iterate

Based on feedback:

1. **Identify patterns** — What went wrong across test cases? Is it a structural issue or a wording issue?
2. **Improve the skill** — Apply changes, focusing on generalizable fixes (not overfitting to test cases)
3. **Rerun all tests** into `iteration-N+1/` — compare with previous iteration
4. **Repeat** until the user is satisfied or feedback is all positive

**Stop when:** User says it's good, all feedback is empty (everything looks fine), or improvements plateau.

### Step 6.5: Description Optimization

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

**How skill triggering works:** Skills appear to the target agent with their name + description. The agent decides whether to consult a skill based on that description alone. Important: agents only consult skills for tasks they can't easily handle on their own — simple one-step queries like "read this file" won't trigger a skill even if the description matches, because the agent can handle them directly. Your test queries should be substantive enough that the target agent would actually benefit from consulting a skill.

**Test triggering accuracy:**

<!-- CC-ONLY -->
```bash
# For each query, test if Claude would trigger the skill
# Run in a new session or use claude -p (pipe mode)
echo "<test query>" | claude -p "Would you use the [skill-name] skill for this request? Answer only YES or NO."
```
<!-- /CC-ONLY -->
<!-- CODEX-START
```bash
# For each query, test if Codex would trigger the skill
# Run in a new session or use codex exec
codex exec "Would you use the [skill-name] skill for this request? Answer only YES or NO. Request: <test query>"
```
CODEX-END -->

**Iterate on the description** based on mismatches:
- Should-trigger but didn't → add relevant trigger phrases/scenarios to description
- Shouldn't-trigger but did → add "Do NOT use for..." exclusions, narrow the scope

Run 2-3 iterations. If available, split queries 60/40 into train/test sets — optimize on train, validate on test to avoid overfitting the description to your specific queries.
