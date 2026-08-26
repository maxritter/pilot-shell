---
name: investigate
description: Evidence-backed, read-only answers about how an existing codebase works. Runs only when the user explicitly types /investigate to ask whether code behaves a certain way, how a feature or data flow works, where behavior is implemented, or why the current code produces an outcome. Not for implementing changes, fixing bugs, reviewing a diff, or open-ended external research.
argument-hint: "question about the current codebase"
user-invocable: true
disable-model-invocation: true
---

# /investigate — Evidence-Backed Codebase Investigation

Answer one question about the code that exists now. The conversation is the artifact: do not create a report file, plan, task list, patch, or implementation unless the user separately asks for one after the investigation.

## Investigation Contract

1. **Read-only means no tracked changes.** Read files, inspect history, and run bounded non-mutating checks. Do not edit, format, generate, migrate, install, commit, or clean up.
2. **Trace behavior, not keywords.** A matching symbol is a lead. Follow the active path through callers, branches, configuration, boundaries, and observable output until the question is answered.
3. **Match evidence to the claim.** Static source proves code shape. A fresh focused command proves runtime or current-state behavior. Tests prove only the cases they exercise.
4. **Reopen load-bearing evidence.** Search indexes, generated summaries, and delegated findings are hypotheses. Read the cited source or command output before relying on them.
5. **Claim only recorded work.** “Ran”, “passed”, “confirmed”, and “verified” require a tool call plus its result in this invocation. A command written in the answer but absent from the transcript did not run.
6. **Calibrate the conclusion.** Label facts, inferences, and unresolved gaps. Low confidence is a prompt for more evidence, not more confident prose.

## Keep It Proportional

- A named symbol or file gets a targeted read and one nearby cross-check.
- A cross-layer or unfamiliar flow gets an end-to-end trace.
- Use one bounded read-only explorer only when breadth would flood the current context or independent areas can be searched in parallel. Tell it not to invoke `/investigate`, delegate again, or write files. Verify its decisive citations yourself.
- Stop when every load-bearing part of the answer has supporting evidence and an additional search is unlikely to change the conclusion.

## Common Shortcuts That Produce Wrong Answers

| Shortcut | Why it fails | Required replacement |
|---|---|---|
| “I found the function, so that is the behavior” | Callers, defaults, feature flags, or an inactive path can change the outcome | Trace one complete active path |
| “A test exists, so production does this” | The test may mock the decisive boundary or cover a different branch | Read the assertion and name exactly what it proves |
| “The source says it, so the installed artifact matches” | Compilation, code generation, packaging, or upgrade transforms may intervene | Inspect the generated or installed artifact |
| “The library probably works this way” | Installed versions and provider behavior drift | Check the locked version and its primary documentation or runtime |
| “Another agent confirmed it” | Delegated summaries can misread or mis-cite evidence | Reopen the load-bearing citation |
| “The command is obvious, so I can report its expected result” | Plausible commands and imagined output are fabricated evidence | Run it and read the result, or state that it was not run |

Complete Steps 1–4 in order.
