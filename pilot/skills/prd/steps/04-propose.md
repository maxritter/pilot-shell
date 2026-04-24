---

## Step 4: Propose Approaches

**Not the same as Step 2b (Ideate).** Ideate is divergent — pitching distinct *directions* when the problem itself is vague. Propose is convergent — once the problem is clear, pitching 2-3 concrete *implementation approaches* for that known problem. If you already did Ideate and the user picked a direction, Step 4 narrows that direction into approaches. If the input was concrete and you skipped Ideate, Step 4 is the first place options get presented.

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
