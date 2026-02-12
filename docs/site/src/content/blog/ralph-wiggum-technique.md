---
slug: "ralph-wiggum-technique"
title: "Claude Code Ralph Wiggum: Run Autonomously Overnight"
description: "The complete guide to Ralph Wiggum loops. Learn stop hooks, completion promises, and verification-first workflows that ship features overnight."
date: "2026-01-14"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 8
keywords: "autonomously, claude, code, overnight, ralph, run, technique, wiggum"
---

Mechanics

# The Ralph Wiggum Technique: How to Run Claude Code Autonomously While You Sleep

The complete guide to Ralph Wiggum loops. Learn stop hooks, completion promises, and verification-first workflows that ship features overnight.

> **Update (Jan 2025)**: Anthropic shipped native [task management](/blog/guide/development/task-management) with dependencies, blockers, and multi-session coordination via `CLAUDE_CODE_TASK_LIST_ID`. Many Ralph workarounds are now built-in. The core principles below still apply - the new system just makes the plumbing native.

You give an agent a list of tasks. It picks one, implements it, tests it, commits the code. Then it picks the next one. And the next. All night while you sleep.

That's Ralph Wiggum. Not the Simpsons character. The autonomous AI coding loop that's changing how engineers ship software.

## [What Makes Ralph Different](#what-makes-ralph-different)

Most developers use Claude Code like a conversation. Prompt. Wait. Review. Prompt again. That's fine for small tasks. But for building features? You're the bottleneck.

Ralph flips the model. Instead of you driving each interaction, you set up a loop that keeps Claude working until the job is done. The key insight: Claude Code's stop hooks let you intercept when the agent tries to finish and redirect it back to work.

Here's the core pattern:

1. Claude works on a task
2. Claude tries to stop (outputs completion)
3. A stop hook intercepts and checks: is the work actually done?
4. If not, feed the prompt back and continue
5. If yes, let it complete

The magic is in step 4. Your agent doesn't quit when it thinks it's done. It quits when the work is verified.

## [The Completion Promise](#the-completion-promise)

Ralph uses a "completion promise" - a specific word or phrase that signals genuine completion. When Claude feels the task is truly finished, it outputs this promise (commonly the word "complete").

```p-4
// In your Ralph loop configuration
completion_promise: "complete"
max_iterations: 25
```

The stop hook checks for this promise. If it's not there, the loop continues. If it is, the loop ends. This prevents Claude from quitting prematurely while also providing a clean exit when work is done.

**Critical rule**: Until Claude outputs the promise, it doesn't stop. This forces the agent to keep iterating until it genuinely believes the work is complete.

## [Verification: The Non-Negotiable Core](#verification-the-non-negotiable-core)

Boris Cherny, the creator of Claude Code, has one rule he never breaks: **always give Claude a way to verify its work**.

This is the foundation that makes Ralph reliable. Without verification, you get a loop that runs forever or stops too early. With verification, you get a loop that knows when it's done.

Three verification approaches work well with Ralph:

### [1. Test-Driven Verification](#1-test-driven-verification)

Write tests before implementation. Claude runs the tests, sees failures, implements code, runs tests again. The loop continues until all tests pass.

```p-4
Workflow:
1. Run all tests in /tests/feature-x/
2. If tests fail, implement code to make them pass
3. Run tests again
4. Repeat until all tests pass
5. Output "complete" only when test suite is green
```

This is the most reliable approach. Tests are objective. They either pass or fail. No ambiguity.

### [2. Background Agent Verification](#2-background-agent-verification)

Spawn a separate agent to verify the main agent's work. This is Boris's approach for long-running tasks:

```p-4
After completing work, use a background agent to:
1. Review all changed files
2. Run the full test suite
3. Check for regressions
4. Report any issues found
```

The background agent provides an independent check. If it finds problems, the main loop continues.

### [3. Stop Hook Validation](#3-stop-hook-validation)

The stop hook itself can run validation commands. Check a progress file, run linting, verify build status. If validation fails, block the stop and continue iterating.

```p-4
// Stop hook pseudocode
if (agent_trying_to_stop) {
  validation_result = run_tests();
  if (validation_result.failed) {
    return { decision: "block", reason: "Tests failing, continue work" };
  }
  return { decision: "allow" };
}
```

## [The Two-Phase Workflow](#the-two-phase-workflow)

Here's where many developers make their first mistake: they try to plan and implement in the same context window.

Separate them.

**Phase 1: Planning Session**

- Generate specifications through conversation
- Review and edit by hand
- Create an implementation plan with explicit file references
- Keep the spec as a "pin" that prevents invention

**Phase 2: Implementation Session**

- Fresh context (clear the previous conversation)
- Feed only the plan document
- Run the Ralph loop
- Let the agent iterate until complete

Why separate? Context window degradation is real. After enough back-and-forth, Claude starts making assumptions based on earlier messages that are no longer relevant. A fresh start with just the plan means sharper focus.

The plan becomes your anchor. Every loop iteration references it. Instead of drifting, the agent stays aligned with what you actually wanted.

## [Practical Implementation: The PRD Approach](#practical-implementation-the-prd-approach)

Ryan Carson's approach breaks down like this:

1. **Start with a PRD** (Product Requirements Document)

   - What are we building?
   - What's in scope?
   - What's explicitly out of scope?
2. **Convert to user stories with acceptance criteria**

   - Each story is a small, testable unit
   - Acceptance criteria define "done"
3. **Structure for agent consumption**

   - JSON or markdown format
   - Clear checkboxes for progress tracking
   - Links to relevant code locations
4. **Run the loop**

   - Agent picks the next uncompleted story
   - Implements it
   - Runs verification (tests)
   - Marks it complete
   - Moves to the next

The beauty: you can walk away. Come back in the morning to find completed features, passing tests, and committed code.

## [UI Verification: The Hidden Trap](#ui-verification-the-hidden-trap)

Here's a gotcha that catches everyone: functional tests pass, but the UI is broken.

The problem: Ralph can verify that code runs correctly while completely ignoring visual bugs. A component renders, tests pass, but the button is off-screen or text is truncated.

The solution: **screenshot-based verification protocol**.

```p-4
After implementing UI changes:
1. Take screenshots of affected components
2. Rename each with "verified_" prefix after review
3. Do NOT output completion promise yet
4. Let the next iteration confirm all files are verified
5. Only then output "complete"
```

This forces at least two loop iterations for UI work. The first implements and captures screenshots. The second verifies all screenshots were reviewed. Claude can't skip the visual check.

**The key insight**: Tell Claude that after renaming screenshots, it should NOT output the promise yet. Let the next iteration confirm completion. This prevents premature exits.

## [Economics: Why This Changes Everything](#economics-why-this-changes-everything)

Running a coding agent continuously costs approximately **$10.42 USD per hour** with Sonnet (measured over 24-hour burn rate).

That's less than minimum wage in most places. For a machine that can:

- Clear backlogs overnight
- Run multiple features in parallel
- Never get tired or distracted
- Scale with more compute

The constraint shifts from "how much can I afford to run?" to "how much reliable work can I define?"

Teams that can run reliable loops will dramatically outpace those that can't. The gap is widening.

## [Common Failures and Fixes](#common-failures-and-fixes)

### [Loop Never Ends](#loop-never-ends)

**Cause**: Impossible task or missing completion criteria
**Fix**: Set a max iteration count (e.g., 25). Add explicit completion criteria to your prompt.

### [Loop Ends Too Early](#loop-ends-too-early)

**Cause**: Claude outputs the promise before work is done
**Fix**: Strengthen your verification. Add tests. Use the screenshot protocol for UI. Make "done" objectively measurable.

### [Quality Degrades Over Iterations](#quality-degrades-over-iterations)

**Cause**: Context window filling with failed attempts
**Fix**: Implement checkpoint state. Mark completed work in an external file. Let the loop resume cleanly if context fills.

### [Agent Invents Features](#agent-invents-features)

**Cause**: Spec is vague or missing
**Fix**: Your spec is the "pin" that prevents invention. Make it specific. Include explicit references to existing code. Tell Claude what NOT to do.

## [Setting Up Your First Ralph Loop](#setting-up-your-first-ralph-loop)

Start simple. Pick a well-defined feature with existing tests.

1. **Install the Ralph plugin** (or implement the stop hook pattern yourself)
2. **Create your prompt file**:

```p-4
Study the implementation plan in /docs/plan.md
Pick the single most important incomplete task
Implement it following existing patterns
Run tests with: npm test
On pass: mark task complete in plan.md, commit changes
On fail: fix the issue and run tests again
Output "complete" only when all tasks are done and tests pass
```

3. **Set constraints**:

   - Max iterations: 25
   - Completion promise: "complete"
   - Quality gates: tests must pass, linting must pass
4. **Watch the first run**. Don't walk away yet. Cancel if behavior looks wrong. Adjust your prompt. Re-run.
5. **Gradually increase autonomy** as trust builds.

## [The Ralph Philosophy](#the-ralph-philosophy)

Ralph isn't about removing humans from coding. It's about removing humans from the tedious iteration loop.

You still design the system. You write the specs. You define what "done" looks like. You review the final result.

But the 2 AM debugging? The repetitive test-fix-test cycles? The context switching between features? That's what Ralph handles.

Boris's philosophy remains at the core: **verification drives everything**. Give Claude a way to verify its work, and it can run reliably for hours. Without verification, you're just hoping.

Start with verification. Build your loops around it. The autonomous coding future isn't about smarter prompts. It's about better feedback systems.

## [Next Steps](#next-steps)

- Try [native task management](/blog/guide/development/task-management) for built-in persistence and multi-session coordination
- Learn about [hooks](/blog/tools/hooks/hooks-guide) to implement custom stop behaviors
- Explore [async workflows](/blog/guide/agents/async-workflows) for running multiple loops
- Read about [thread-based engineering](/blog/guide/mechanics/thread-based-engineering) for scaling your autonomous workflows
- Check [feedback loops](/blog/guide/development/feedback-loops) for verification patterns

The developers who master Ralph aren't just using Claude Code. They're building systems that ship while they sleep.

Last updated on

[Previous

Output Formatting](/blog/guide/mechanics/output-formatting)[Next

Thread-Based Engineering](/blog/guide/mechanics/thread-based-engineering)
