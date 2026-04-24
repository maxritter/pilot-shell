## Step 2b: Ideate (Optional — Skip if Concrete)

**Purpose:** When the input is vague ("I want better onboarding", "something for team updates"), riff with the user before locking into structured questions. This is the divergent phase — generate, react, refine.

**⛔ Skip this step entirely when:**
- The user's input already names a concrete thing to build ("Add OAuth login with Google", "Migrate the worker from cron to BullMQ")
- Step 1 found existing code that clearly answers what's being built
- Research (Step 2) already produced a chosen direction

**Run this step when:**
- The idea is a problem statement, not a solution ("users drop off after signup")
- The user used hedging language ("maybe", "something like", "I'm thinking")
- Multiple obviously-different shapes could satisfy the request

### How to Run It

Free-form prose, **no `AskUserQuestion`**. Each round:

1. **Pitch 3-5 directions.** Short, distinct angles — not variations of the same idea. Lead with one-line summaries; expand only on request. Example:
   > "A few directions I see for 'better onboarding':
   > - **Reduce surface area** — cut the signup form to email-only, defer everything else to first use
   > - **Guided first-run** — keep signup as-is, add a 3-step product tour after first login
   > - **Pre-fill from context** — detect the user's company/role from email domain, skip questions we can infer
   > - **Async setup** — let users start using the product immediately, complete profile in the background
   >
   > Which of these resonate, or where am I off?"

2. **Pressure-test what they pick.** When the user reacts, push back: where does this break? What does it cost? What did they implicitly assume? Surface the failure modes before they get baked in.

3. **Generate next round from their reaction.** Their answer reshapes the next pitch — don't run a fixed checklist. If they reject all 5 directions, ask what's missing rather than pitching 5 more.

4. **Stop when shape emerges.** Usually 1-3 rounds. The signal: the user starts saying "yes, and..." instead of "no, but...". When you can write a one-sentence summary of what they want and they nod, move on.

### Hand-off

End the ideation phase with an explicit transition:

> "OK, so we're building **<one-sentence summary>**. Switching to structured questions to nail down the details."

Then proceed to Step 3 (Clarify) with `AskUserQuestion`.

### Anti-Patterns

- **Pretending to ideate when the user already decided.** If they said "add Google OAuth", do not pitch alternatives — go to clarify.
- **Pitching variations of one idea.** Five flavors of "add a tour" is one idea, not five.
- **Endless rounds.** If round 3 hasn't converged, the problem is probably under-defined — ask the user what success looks like before pitching again.
- **Using `AskUserQuestion` here.** Structured forms collapse divergent thinking. Save them for Step 3.
