## Step 6: Approach Selection & Design Decisions

**⛔ Do NOT skip this step.** After exploration, always weigh competing approaches before committing. Even when one approach seems obvious, considering alternatives validates the choice and surfaces blind spots.

**Two parts — both mandatory in-process; the plan only records the chosen path:**

#### Part A: Overall Approach

Internally consider 2-3 implementation approaches based on exploration findings. For each candidate, evaluate:

- **Name** — short label, **referencing real symbols/files from the Step 3 Workspace Scan when available** (e.g., "Extend `OrderHandler` in `src/handlers/order.py`" vs "New `OrderService` module under `src/services/`"). Generic labels ("Extend existing handler") are a regression — only use them when `Greenfield?: yes` in the scan output.
- **How it works** — 2-3 sentences
- **Trade-offs** — frame as **"X at the cost of Y"** — never recommend without stating what it costs
- **Recommendation** — pick a preferred approach with reasoning

If exploration also revealed scope ambiguity (gaps, optional features, multiple directions), include scope items as part of this step. `AskUserQuestion(multiSelect: true)` for scope items; unselected items go to "Out of Scope" or "Deferred Ideas."

#### Part B: Design Decisions

Within the chosen approach, resolve remaining design choices. Each decision gets 2-3 concrete options with trade-offs and your recommendation.

**Notify, then ask (Batch 2):**

```bash
~/.pilot/bin/pilot notify plan_approval "Design Decisions" "<plan_name> — architecture choices" --plan-path "<plan_path>" 2>/dev/null || true
```

Use `AskUserQuestion` — Part A (approach selection) and Part B (design decisions) can be combined into a single Batch 2 interaction when the decisions are related.

**When questions are disabled (`PILOT_PLAN_QUESTIONS_ENABLED=false`):** Still evaluate approaches and design decisions internally. Select the recommended approach, resolve design decisions with reasonable defaults, and document all choices with reasoning in the plan's "Autonomous Decisions" section.

**What ends up in the plan (`## Approach` section, Step 9):** only the chosen approach's **Name** and **Why** (1-2 sentences capturing what it gives us and what it costs). Do NOT list rejected alternatives in the plan — they're decision exhaust, not implementer information. The only exception: if a user-rejected option is one an implementer might re-derive ("why aren't we just doing X?"), capture that rejection as a single sentence inside the `Why:` line.

Incorporate choices into plan design, proceed to Step 7.
