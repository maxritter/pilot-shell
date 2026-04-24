# Step 3 — Author evals

Draft 3 realistic prompts with **falsifiable**, **discriminating** assertions. This is the highest-leverage step — bad assertions produce noise, not signal.

## Structure of evals.json

```json
{
  "target": {
    "type": "skill",
    "path": "pilot/skills/create-skill",
    "name": "create-skill"
  },
  "evals": [
    {
      "id": 1,
      "name": "short-descriptive-name",
      "prompt": "Realistic user task — phrased the way a real engineer would type it. Save outputs to {sandbox}/<filename>.",
      "expected_output": "1-line description of what success looks like",
      "expectations": [
        "Specific, observable assertion 1",
        "Specific, observable assertion 2",
        "Specific, observable assertion 3"
      ]
    }
  ]
}
```

## ⛔ Path isolation — required

Each run gets its own filesystem sandbox. Prompts must reference that sandbox, not a shared absolute path, or the `with` and `without` runs will read each other's outputs.

Two safe ways to specify where outputs go:

| Approach | Example | When to use |
|----------|---------|-------------|
| **Relative paths** (preferred) | `Save the result to slugify.py` | The subprocess cwd is already the per-run sandbox, so bare filenames land in the right place. Simpler, fewer tokens. |
| **`{sandbox}` placeholder** | `Save to {sandbox}/slugify.py` | Use when the prompt genuinely needs an absolute path — the runner substitutes `{sandbox}` with the per-run directory before executing. |

⛔ **Never write `/tmp/<fixed-name>/file.py` in a prompt.** The runner emits a warning and proceeds, but the benchmark is invalid — both configs write to the same path.

## What makes an assertion good

**Discriminating.** The baseline (`without`) must plausibly FAIL the assertion. If both configs always pass it, the assertion measures nothing. The modern models already know "write tests, mock subprocess, use descriptive names" — assertions have to reach further than baseline habits to detect the rule's effect.

**Observable.** The grader reads the transcript and output files. Assertions like "the output is high quality" are unverifiable. Assertions like "the plan file contains sections named `## Summary`, `## Scope`, and `## Risks and Mitigations`" are observable.

**Genuine signal, not surface compliance.** "The output file is named `plan.md`" can pass by coincidence. Prefer "the plan.md contains a ### Task N heading for at least 3 tasks" — would pass only if the skill actually did structured task breakdown.

**Rule-specific, not industry common sense.** If the assertion tests common knowledge the base model already has (write some tests, avoid bare except), baseline passes and your rule gets no credit for teaching. Aim for the parts of the rule that are project-specific, stricter, or surprising — pytest marker requirements, exact naming patterns with multiple segments, coverage gates, property-based testing for parsers, mock-audit procedures.

## The falsifiability gate — mandatory

Before committing to a full eval set:

1. Hand-author one eval for this target.
2. Run baseline only:
   ```bash
   PYTHONPATH=~/.claude/skills/benchmark uv run python -m scripts.runner \
       --config benchmarks/<target>/evals.json --configs without --runs 1 \
       --skip-permissions
   ```
3. Inspect the baseline output (read `grading.json` for each run). If baseline passes 3/3 assertions, **rewrite the assertions** — they're not discriminating.

Only after the baseline fails at least one assertion do you have evidence that the eval measures something real. Skip the gate only when the user explicitly says they want a quick smoke test.

## Examples by type

**Skill target** (e.g., `/create-skill`):
- "Response includes a complete SKILL.md with `---` frontmatter containing `name:` and `description:` fields"
- "Response references the existing skill-creation pattern from `pilot/skills/create-skill/orchestrator.md`"
- "Response suggests at least one test prompt for the new skill"

**Rules target** (e.g., `testing.md` — aim past baseline habits):
- "Each new test function is decorated with `@pytest.mark.unit` — baseline Claude rarely adds this marker by default"
- "Test names match the regex `test_[a-z]+_[a-z_]+_[a-z_]+` (≥4 underscore-separated segments after `test`)"
- "The test file contains at least one property-based test using `hypothesis` (`@given(...)`) for parser/serializer behavior"
- "A coverage invocation like `pytest --cov-fail-under=80` appears in the transcript or a generated script"

## Commit the config

Save to `benchmarks/<target-name>/evals.json`. Show the user the final config and get explicit sign-off before spending compute in Step 4.

## Exit

Go to Step 4 (execute).
