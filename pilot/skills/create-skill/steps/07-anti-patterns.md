---

## Step 7: Anti-Patterns & Troubleshooting

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
