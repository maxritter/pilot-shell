## Step 4: Report the Answer

Use this compact shape, omitting empty sections:

```markdown
<Direct answer in the first sentence. No readiness, process, or evidence-status preamble.>

### How it works

1. <entry point and evidence>
2. <decisive branch or boundary and evidence>
3. <observable outcome and evidence>

### Cross-check

- **Observed:** <independent source or actual command result>
- **Inferred:** <implication, or "None">
- **Runtime check:** <exact command and result, or "Not run — <reason>">

### Confidence

<High | Medium | Low> — <specific reason>.

### Not verified

<Only material gaps that could change the answer.>
```

### Reporting Rules

- Link or cite every load-bearing source with a real file path and line number. Do not invent line numbers.
- Begin with the answer itself. A sentence such as “I now have enough evidence” or “This confirms the trace” is not the answer.
- Make the opening paragraph branch-complete: if the question names several cases or conditions, state the outcome for every one before `### How it works`.
- Keep the **Observed**, **Inferred**, and **Runtime check** labels in the Cross-check section. Use `None` or `Not run` rather than dropping a label.
- Report an exact focused command and result only when the transcript contains that tool call and result. Otherwise write `Runtime check: Not run` and the reason.
- Answer the question asked. Do not append implementation recommendations, unrelated findings, or “want me to fix it?” unless the user requested next steps.
- If the investigation reveals a bug, explain the evidence and stop read-only. A later implementation request starts a separate task.
- Do not create a Markdown report file unless the user explicitly asks to persist the investigation.

**Completion:** the first sentence answers the question, every load-bearing claim is checkable, confidence matches the evidence, and the worktree has no investigation-created tracked changes.

## When Not to Use

- Implementing or changing behavior.
- Fixing a confirmed defect.
- Reviewing a diff, pull request, or security finding.
- Producing an implementation plan or product requirements document.
- Open-ended web or literature research without a concrete codebase question.
- A trivial exact-symbol location when the user did not explicitly invoke `/investigate`.

## Examples

- `/investigate Does another session's active plan satisfy this validator?`
- `/investigate How does a CLI flag become persisted configuration?`
- `/investigate Does the installed Codex skill preserve this Claude frontmatter?`
- `/investigate Is this behavior proven at runtime, or only possible from the static path?`
