---
title: "Claude Code TeammateIdle Hook: Loop-Safe Exit 2"
description: "Exit code 2 blocks an agent and feeds it a correction. Building a real TeammateIdle gate exposed three loop-safety rules the docs do not carry."
slug: hook-loops-teammate-idle
date: 2026-07-29
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Exit code 2 blocks an agent and feeds it a correction. Building a real TeammateIdle gate exposed three loop-safety rules the docs do not carry.

<!-- truncate -->

Exit code 2 is the documented way to block an agent and hand it a correction. A `Stop` hook exits 2 and Claude keeps working. A `PreToolUse` hook exits 2 and the tool call dies. A `TeammateIdle` hook exits 2 and the teammate does not go idle. Every hooks guide, [ours included](/blog/hooks-guide), teaches this and stops there.

Stopping there is fine right up until you build a gate that fires more than once. We built one designed to push back at most twice. It pushed back five times, then kept going, and the reason it kept going was not a bug in the logic. It was three separate assumptions about how transcripts and state behave, each of which was wrong in a way that only shows up under repetition.

This is that gate, the three rules, and the debugging method that found them.

## What the Gate Was For

Some context on why a `TeammateIdle` gate is worth building at all, because it exposes a real gap.

Claude Code has two delivery models and they behave oppositely. With a **classic subagent**, the final message returns to the caller automatically; you get the report whether or not anyone asked for it. In **agent-teams mode**, nothing returns automatically. A teammate's plain final message reaches nobody. The report only arrives if the teammate calls `SendMessage`, and if it does not, the teammate simply goes idle looking exactly like one that finished successfully.

That is a silent failure with a real cost, covered fully in [why your subagent reports done without doing anything](/blog/subagent-reported-done). The mechanical fix is a hook: when a teammate is about to go idle, check whether it actually delivered, and if not, exit 2 to keep it working with instructions to deliver.

`TeammateIdle` is the event, it is blockable, and this is exactly what it is for. The naive version is about fifteen lines. The naive version is also what fired five times.

## Rule 1: Skip Your Own Feedback When Reading the Transcript

The gate needs to answer one question: did this teammate send a report **since its last real assignment?** The obvious implementation walks the transcript, finds the last user-role message (the assignment), finds the last `SendMessage` tool call, and compares positions.

The trap: **your own pushback lands in the transcript as a user-role message.**

So the sequence goes like this. The teammate finishes, does not send. The gate fires, exits 2, and injects feedback. That feedback is written to the transcript as a user-role entry. The teammate complies and sends the report. The gate fires again, walks the transcript, and finds that the most recent user-role message is *its own feedback*, which sits after the assignment. The report it just successfully extracted now appears to predate the latest "assignment," so the gate concludes no report was delivered and pushes back again. On a report it already got.

The hook resets its own marker every time it succeeds. That is the five-times behaviour, and it is self-sustaining: every pushback creates the evidence for the next one.

The fix is a sentinel. Tag your injected text with a known prefix and exclude it when identifying assignments:

```
const FEEDBACK_PREFIX =
  "Deliver your completion report to the lead via SendMessage";
 
if (role === "user") {
  const isToolResult = content.some((b) => b && b.type === "tool_result");
  const isOwnFeedback = entryText(msg, content).startsWith(FEEDBACK_PREFIX);
  if (!isToolResult && !isOwnFeedback) lastAssignment = i;
}
```

Note the second exclusion alongside it. **Tool results are also user-role entries.** A teammate that ran twenty tool calls has twenty user-role messages that are not assignments, and counting them produces the same false negative from a different direction.

The general principle, and it applies to any hook that both reads and writes a conversation: **a hook that injects into the transcript it later parses is in a feedback loop with itself.** Make your own writes identifiable, and skip them on read.

## Rule 2: The Transcript Lags the Turn

Second failure, and this one is intermittent, which makes it worse.

Sometimes the gate fired on a teammate that had *definitely* just sent its report. Not always. Maybe one time in four. Same code, same conditions, different outcome, which is the signature of a race.

The transcript file is written asynchronously. When `TeammateIdle` fires, the teammate's most recent turn, including the `SendMessage` you are looking for, may not have been flushed to disk yet. You read the file, the call is not there, and you correctly conclude from stale data that no report exists.

The fix is unglamorous:

```
const FLUSH_DELAY_MS = 750;
await new Promise((r) => setTimeout(r, FLUSH_DELAY_MS));
```

750ms is what we measured as reliable here; treat it as a starting point rather than a constant, since it will vary with transcript size and disk. Because `TeammateIdle` fires once per teammate at the end of its work, the delay costs nothing anyone notices. Do not copy this pattern into a `PreToolUse` hook, where it would tax every single tool call.

The broader lesson generalises past hooks entirely: **when a snapshot contradicts what you know happened, check when the snapshot was taken before concluding anything from it.** We have watched two agents reach opposite conclusions about the same file, both reading real data, purely because one read before a write and one after.

## Rule 3: Mark Exhausted, Do Not Clear the Counter

Third failure, and the most subtly wrong.

You want a limit. Two pushbacks is plenty; if a teammate has ignored the instruction twice, a third is not going to land, and an unbounded gate can trap an agent forever. So you count pushbacks in a state file and stop at the cap.

The natural implementation is to clear the counter when you stop:

```
// Do NOT do this
if (pushbacks >= MAX_PUSHBACKS) {
  delete state[key]; // give up
  process.exit(0);
}
```

That gives up exactly once. `TeammateIdle` can fire again for the same teammate, and now the state is clean, so the counter starts at zero and the gate re-arms. Your cap of two silently becomes a cap of two per idle event, unbounded in total.

The counter needs three states, not two: never pushed back, pushed back N times, and **done pushing back**. A sentinel value carries the third:

```
const pushbacks = state[key] || 0;
if (pushbacks === -1) process.exit(0); // exhausted earlier; stay silent
 
if (pushbacks >= MAX_PUSHBACKS) {
  state[key] = -1; // remember that we gave up
  writeFileSync(statePath, JSON.stringify(state));
  console.log(`ReportGateHook: ${agentKey} idled without a delivered report`);
  process.exit(0);
}
```

Absence and exhaustion are different states and they must not share a representation. Clearing the entry throws away the only record that you already decided to stop.

Note also that giving up **logs to stdout rather than staying silent**. A gate that quietly surrenders is worse than no gate, because you believe you have enforcement you do not have.

The key includes both session and agent, `${session_id}:${agent_id}`, so one teammate exhausting its budget does not disarm the gate for its peers.

## Fail Open, Always

One design decision that is not about loops but will save you more grief than all three rules combined.

Every parse in this hook returns "a report was delivered" when anything goes wrong. Missing transcript, unreadable file, malformed JSON line, a file large enough that reading it is a bad idea:

```
if (!transcriptPath || !existsSync(transcriptPath)) return true;
if (statSync(transcriptPath).size > MAX_TRANSCRIPT_BYTES) return true;
// ...
} catch {
  return true;
}
```

The asymmetry is the point. A **false negative** costs you one missed report, which you will notice, and the lead can ask for it. A **false positive** traps an agent in a loop it cannot exit by doing the right thing, because doing the right thing is what your hook failed to detect. One is an inconvenience and one is a trap, so when your parser is uncertain, be uncertain in the direction of letting the agent go.

The same reasoning drives the per-line `try/catch` in the transcript walk. A single unparseable JSONL line should skip that line, not abort the analysis and take the whole gate down with it.

## Verify Against the Transcript, Not by Prompting

The method matters as much as the rules, because none of the three above were findable by testing the way most people test hooks.

The instinct is to run a session, watch what the agent does, and judge whether the hook helped. That does not work for any hook that injects context, and it especially does not work here. Everything the gate does happens upstream of what you see. A teammate that delivers its report might have done so because your feedback landed, or might have been going to anyway. A teammate that got pushed back five times looks, from the outside, like a teammate that took a while.

**Read the transcript file.** It is JSONL, one entry per line, and it contains the ground truth: your injected feedback verbatim, the teammate's `SendMessage` calls, and the exact ordering. All three bugs were visible there and invisible anywhere else. The self-reset was obvious the moment we printed the user-role entries in order and saw our own feedback text sitting where an assignment should be.

This generalises to the whole category. We reached the same conclusion independently while rebuilding the [skill activation hook](/blog/skill-activation-hook): a `UserPromptSubmit` hook cannot be evaluated by looking at Claude's answer, because the injected block is upstream of the answer and a good response proves nothing about whether the block helped. **If a hook modifies the conversation, the conversation file is your only instrument.**

A useful corollary: instrument the hook before you tune it. Logging what the gate decided and why, on every fire, turns "it sometimes misfires" into "it misfires when the transcript has not flushed," which is a fixable statement.

## The Complete Gate

Putting the three rules together, the shape is:

1. **Exit immediately if the mode is off.** Ours checks `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` and exits 0 when teams mode is not on, because in classic mode reports auto-return and the gate is solving a problem that does not exist. A hook that fires in a mode where it is meaningless is pure tax.
2. **Wait for the flush**, then read the transcript.
3. **Walk it, skipping tool results and your own feedback**, and compare the last `SendMessage` against the last real assignment.
4. **If a report exists**, clear the state entry entirely and exit 0.
5. **If not**, check for the exhausted sentinel, then the cap, then push back with exit 2 and increment.
6. **Fail open at every parse.**

Wire it in the usual way:

```
{
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/ReportGateHook/report-gate.mjs\""
          }
        ]
      }
    ]
  }
}
```

Use `node` directly rather than a shell wrapper, and handle platform differences inside the script. See [cross-platform hook patterns](/blog/cross-platform-hooks) for why `cmd /c` and `bash` wrappers break the moment the file is shared.

## Where Else These Rules Apply

`TeammateIdle` is the case we hit, but nothing above is specific to it. The rules apply to **any hook that can fire repeatedly on the same subject and maintains state across fires**, which includes `Stop`, `SubagentStop`, `TaskCompleted`, and `TaskCreated`.

Worth knowing: `Stop` has a built-in escape hatch that the others do not. The input carries a `stop_hook_active` flag, and checking it first is the standard advice for avoiding `Stop` loops. **That flag covers `Stop` and nothing else.** If you are gating `TeammateIdle`, `TaskCompleted`, or `SubagentStop`, you own loop safety yourself, and the three rules above are what that ownership looks like.

`TaskCompleted` is the one we would build next, and it has the same shape: exit 2 prevents a task from being marked complete, which is a genuinely useful gate for "the tests actually pass" enforcement, and it fires repeatedly on a subject that can retry. Everything here transfers.

## Next Steps

- Get the full event list and blocking semantics in the [Hooks Guide](/blog/hooks-guide)
- Understand the delivery gap this gate exists to close in [why your subagent reports done](/blog/subagent-reported-done)
- Apply the same transcript-verification discipline to the [skill activation hook](/blog/skill-activation-hook)
- See the `Stop` equivalent in [stop hook task enforcement](/blog/stop-hook-task-enforcement)
- Make your hooks portable with [cross-platform hook patterns](/blog/cross-platform-hooks)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
