---
title: "Stop Hooks That Rewrite Your CLAUDE.md"
description: "Your CLAUDE.md goes stale fast. A stop hook can spawn a headless Claude session to review changes and propose rule updates after each turn."
slug: self-improving-claude-md
date: 2026-05-21
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Your CLAUDE.md goes stale fast. A stop hook can spawn a headless Claude session to review changes and propose rule updates after each turn.

<!-- truncate -->

You wrote a careful CLAUDE.md three months ago. It told Claude how the auth module worked, where the env vars lived, why the legacy webhook handler still needed manual retries. Then the team refactored auth, moved the env loader, and replaced the webhook handler with a queue. The CLAUDE.md never changed.

That is the **self improving claude md** problem, and it is mostly invisible. The file still loads every session. Claude still treats every line as authoritative. The rules just happen to describe a codebase that no longer exists. Cole Medin put it bluntly in his demo of the `helpline` reference repo: "as you evolve your codebase, your rules must evolve too; it is really bad when your CLAUDE.md goes stale."

The fix is a stop hook that fires at the end of every turn, spawns a separate headless Claude session, reads the diff plus the relevant CLAUDE.md files, and proposes edits in a review file you can act on later. This post walks through how the pattern works, the script behind it, and when the extra tokens are worth it.

## How the Pattern Works

The mechanics are simple. Claude finishes its turn. The `Stop` hook fires. A small Python script collects the recent git diff and the contents of every CLAUDE.md file that lives above any changed path. It pipes that bundle into a fresh `claude -p` invocation. That headless session does one job: compare what just happened in the code to what the rules currently claim, and write its findings to a review file.

The review file is the output, not the trigger. Nothing auto-edits your CLAUDE.md. You read the review at your own pace, accept what makes sense, ignore what does not. The hook keeps the conversation flowing while quietly maintaining a paper trail of conventions that have drifted.

Two things make this safer than it sounds. First, the headless session is gated by an environment variable so the proposer never recursively spawns itself. Second, if the `claude` CLI is unavailable for any reason, the script falls back to a deterministic note listing the changed areas, no LLM needed. That detail matters in CI and in offline environments where the hook should degrade gracefully instead of crashing your turn.

This is one of the highest-leverage patterns in the [AI layer Anthropic now calls the harness](/blog/the-ai-layer), because it keeps the harness itself from drifting silently.

## Setting Up the Hook

You need three pieces: a settings entry, a script that builds the prompt, and a prompt that produces useful output.

### The settings.json entry

The hook lives in `.claude/settings.json`. Cole's helpline uses the same `Stop` event documented in our [hooks-lifecycle reference](/blog/session-lifecycle-hooks):

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory \"$CLAUDE_PROJECT_DIR\" python .claude/hooks/propose_claude_md.py"
          }
        ]
      }
    ]
  }
}
```

The `$CLAUDE_PROJECT_DIR` variable matters. Hooks run from an undefined working directory, and the proposer needs to find the right CLAUDE.md hierarchy. If you skip this and the hook can't locate the file, you'll get silent no-ops every turn.

### The reviewer script

The script does four things in order: collect the git diff, walk up from each changed file to find every CLAUDE.md that governs it, build a prompt, and pipe it into a headless Claude session. Helpline caps the diff at roughly 12,000 characters so the headless call stays cheap, then invokes:

```
subprocess.run(
    ["claude", "-p", "--output-format", "text"],
    input=prompt,
    env={**os.environ, "HELPLINE_AILAYER_REFLECT_LOCK": "1"},
    capture_output=True,
)
```

The lock env var is the recursion guard. The spawned session sees it, and any nested hook checks for it and exits early. Without that fence, you'd have stop hooks proposing CLAUDE.md edits about stop hooks proposing CLAUDE.md edits.

### The reviewer prompt

The prompt frames the headless session as an auditor, not an editor. Cole's working version sounds roughly like this:

```
You are auditing whether the project's CLAUDE.md files still match
reality after a coding session.

For each changed area, return exactly one of:
  1. "No change needed" if existing conventions still hold, OR
  2. A concrete proposed edit, with the target file path, the
     specific lines to change, and a one-sentence rationale.

Only flag genuine new conventions, gotchas, commands, or constraints
that are missing from CLAUDE.md. Do not suggest stylistic rewrites.
Do not propose edits for code style, only for documented rules that
no longer hold.

Output to .claude/claude-md-review.md.
```

Two design choices in that prompt do most of the work. The "no change needed" option keeps the reviewer honest, since "no change" should be the most common result. And the explicit ban on stylistic rewrites stops the reviewer from inflating review files with cosmetic suggestions you'd never apply.

## Sample Reviewer Output

A real review file from a session that touched the billing service and one shared util looks something like this:

```
# CLAUDE.md Review 2026-05-21 14:08
 
## packages/billing/CLAUDE.md
 
No change needed. Convention "all amounts in cents, never floats"
still holds across the diff.
 
## packages/shared/CLAUDE.md
 
Propose edit. Lines 12-14 currently say "use `loadEnv()` from
`config/env.ts`". The diff renames that helper to `getEnv()` and
moves it to `config/runtime.ts`. Update the path and helper name.
Rationale: the old reference would mislead future sessions.
```

Most turns produce the first kind of entry. That is the point. The reviewer is a watchdog, not a refactorer. The signal-to-noise ratio is high precisely because "no change" is allowed as an answer.

## When a Self-Improving CLAUDE.md Is Worth the Cost

The headless session adds tokens to every turn. That is a real cost on long sessions and on Pro plans. The pattern earns its keep when:

- The codebase is actively evolving, with new conventions emerging weekly.
- The CLAUDE.md hierarchy is layered, so [subdirectory CLAUDE.md files](/blog/subdirectory-claude-md) drift independently.
- Multiple developers share the same CLAUDE.md and need a neutral auditor catching changes nobody documented.
- The project is past the early prototype phase, where every commit invalidates yesterday's rules.

It is overkill when you are a solo developer working on a stable side project with one short root CLAUDE.md. In that case, [the foundational CLAUDE.md mastery guide](/blog/claude-md-mastery) plus a periodic manual review is plenty.

## Extending the Pattern

The same shape works for more than CLAUDE.md. Swap the prompt and you can audit:

- **Skills** that no longer describe their domain accurately.
- **Permissions policy** that grants more than the project actually needs.
- **Start-hook context** by reversing the direction (load git status, recent commits, Confluence pages per developer) the way Cole's `session_start_context.py` does.

The principle is the meta-level: any rule file that lives next to code should be audited by something that reads both. The [stop hook task enforcement pattern](/blog/stop-hook-task-enforcement) is the cousin that audits work, not rules. Together they cover the two failure modes Anthropic flagged in their large-codebase guide.

## Pitfalls

A few traps show up the first time teams adopt this:

- **Reviewer that proposes too much.** Tighten the prompt, lower the temperature, narrow the "what counts as a change" definition.
- **Reviewer that runs on every micro-edit.** Gate the hook behind a diff-size or file-count threshold so it doesn't fire when you fixed a typo.
- **Reviewer that auto-applies its own diffs.** Never let it. Queue everything for human review. The whole point is a paper trail.
- **Reviewer that reads the entire CLAUDE.md every turn.** Walk the path hierarchy and read only files above changed paths.

The [hooks complete guide](/blog/hooks-guide) covers the broader settings.json structure and exit-code patterns that keep hook errors from breaking your turn.

## Where This Fits in the Harness

Hooks are one part of the [seven-part harness model](/blog/the-ai-layer). They sit next to CLAUDE.md, skills, MCP servers, sub-agents, LSP, and plugins. Most hooks enforce something. This one improves something. That makes it the highest-leverage hook in the set, because it keeps the rest of the harness from rotting on the shelf.

For teams running on large codebases, this pattern pairs naturally with the [large codebase playbook](/blog/large-codebase-playbook): the playbook tells you to layer CLAUDE.md, and the stop hook tells you when that layering has drifted.

## A Harness That Maintains Itself

Most rule files in software die the same way: written once, treated as permanent, ignored until they actively mislead someone. CLAUDE.md is unusually exposed to this failure because every session quietly reinforces stale rules. A stop hook that audits the rules against the code closes that loop without adding maintenance work.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
