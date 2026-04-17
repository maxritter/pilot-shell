## Step 7: Approach Selection & Design Decisions

**⛔ Do NOT skip this step.** After exploration, always propose competing approaches before committing to a design. Even when one approach seems obvious, stating alternatives with trade-offs validates the choice and surfaces blind spots.

**Two parts — both mandatory:**

#### Part A: Overall Approach

Propose 2-3 implementation approaches based on exploration findings. For each approach:

- **Name** — short label (e.g., "Extend existing handler" vs "New dedicated service")
- **How it works** — 2-3 sentences
- **Trade-offs** — frame as **"X at the cost of Y"** — never recommend without stating what it costs
- **Recommendation** — mark your preferred approach with reasoning

If exploration also revealed scope ambiguity (gaps, optional features, multiple directions), include scope items as part of this step. `AskUserQuestion(multiSelect: true)` for scope items; unselected items go to "Out of Scope" or "Deferred Ideas."

#### Part B: Design Decisions

Within the chosen approach, resolve remaining design choices. Each decision gets 2-3 concrete options with trade-offs and your recommendation.

**Notify, then ask (Batch 2):**

```bash
~/.pilot/bin/pilot notify plan_approval "Design Decisions" "<plan_name> — architecture choices" --plan-path "<plan_path>" 2>/dev/null || true
```

Use `AskUserQuestion` — Part A (approach selection) and Part B (design decisions) can be combined into a single Batch 2 interaction when the decisions are related.

**When questions are disabled (`PILOT_PLAN_QUESTIONS_ENABLED=false`):** Still evaluate approaches and design decisions internally. Select the recommended approach, resolve design decisions with reasonable defaults, and document all choices with reasoning in the plan's "Autonomous Decisions" section.

Incorporate choices into plan design, proceed to Step 8.
