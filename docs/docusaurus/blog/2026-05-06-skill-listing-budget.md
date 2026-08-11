---
title: "Claude Code's Hidden Skill Budget Setting (May 2026)"
description: "Claude Code 2.1.129 added skillListingBudgetFraction, silently dropping skills past 1% of context. Exact settings.json format to raise it."
slug: skill-listing-budget
date: 2026-05-06
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code 2.1.129 added skillListingBudgetFraction, silently dropping skills past 1% of context. Exact settings.json format to raise it.

<!-- truncate -->

Claude Code shipped a new setting this week in v2.1.129 that controls how many of your skills survive into the system prompt. **It is not in the public changelog yet.** It is not documented on Anthropic's site. The first time most users see it is when this warning fires on session start:

```
Skill listing will be truncated
10 descriptions dropped (full descriptions kept for most-used skills) (1.3%/1% of context):
  visual-explainer, mobile-design, react, +7 more
run /skills to disable some, or raise skillListingBudgetFraction (currently 1%) in settings.json
Opting in would cost ~3k tokens for skills every session and uses rate limits faster
```

If you have more than a handful of [Claude Code skills](/blog/claude-skills-guide) installed, you may have already lost half of them to this budget without knowing it.

We confirmed the setting by extracting it directly from the **Claude Code 2.1.129 native binary** since no public documentation exists yet. The Zod schema lives in the binary itself and tells us exactly what shape it accepts. The two settings, the defaults, and the exact `settings.json` format are below, verified against the binary and tested against a live session.

## What These Two Settings Actually Do

Two related settings control the skill listing. Most coverage online discusses only one. Both ship in 2.1.129.

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `skillListingBudgetFraction` | decimal `0 < x ≤ 1` | `0.01` (1%) | Caps total skill metadata at this fraction of the context window. Excess skills lose their description entirely. |
| `skillListingMaxDescChars` | positive integer | `1536` | Per-skill description character cap. Descriptions longer than this are truncated, not dropped. |

The two interact. First, every individual description that runs longer than `skillListingMaxDescChars` is shortened. Then the total skill listing is checked against `skillListingBudgetFraction`. If it still exceeds the budget, the lowest-priority full descriptions get dropped until the listing fits.

This is why the warning has two flavors visible in the binary:

- **"Skill listing will be truncated"** - the budget fraction was hit; some skills go fully dark
- **"Some skill descriptions will be shortened"** - the per-skill cap was hit; descriptions get trimmed but every skill stays visible

You only see the first one when you have a lot of skills. The second one fires when you have a few skills with very long descriptions.

## Exact `settings.json` Format

Edit `~/.claude/settings.json` (or your project's `.claude/settings.json` for project-level overrides):

```
{
  "skillListingBudgetFraction": 0.02,
  "skillListingMaxDescChars": 2048
}
```

Format rules pulled directly from the binary's Zod schema:

- `skillListingBudgetFraction` must be `> 0` and `<= 1`. It is a **decimal fraction**, not a percentage. `0.02` means 2%, not 2 (which would be invalid). The validator will reject `0`, `1.5`, or any string.
- `skillListingMaxDescChars` must be a **positive integer**. `1536` is the default, `2048` is a reasonable raise, `4096` is aggressive.

Both settings are optional. Omit either to keep its default.

You can also override the budget at runtime with the environment variable `SLASH_COMMAND_TOOL_CHAR_BUDGET` (a raw character count, not a fraction). Setting this env var skips the fraction calculation entirely:

```
# Linux/macOS
export SLASH_COMMAND_TOOL_CHAR_BUDGET=20000
 
# Windows PowerShell
$env:SLASH_COMMAND_TOOL_CHAR_BUDGET = "20000"
```

Use the env var for one-off scripted runs. Use `settings.json` for persistent defaults.

## Confirming It Works

Three ways to verify the setting took effect, in order of effort:

**1. Restart Claude Code and watch the warning.** If the warning previously said `(1.3%/1% of context)` and now says `(1.3%/2% of context)` with no skills dropped, you raised the budget successfully. If the warning stops appearing entirely, you cleared the threshold.

**2. Check `/context` at the top of a fresh session.** Look at the Skills line:

```
System prompt: 2.7k tokens (1.3%)
System tools: 16.8k tokens (8.4%)
Skills: 2.3k tokens (1.2%)
Autocompact buffer: 33.0k tokens (16.5%)
```

The Skills percentage should now be free to grow up to your new fraction. On a 200K Sonnet session at `0.02`, Skills can hit ~4,000 tokens (2%) before getting capped.

**3. Read the binary's runtime state.** This is overkill for most users, but if you want to confirm the binary is reading your override:

```
# Unix/macOS
grep -aoE "skillListing[A-Za-z]+" "$(which claude)" | sort -u
 
# Windows PowerShell
$bin = (Get-Command claude).Source
Select-String -Path $bin -Pattern 'skillListing[A-Za-z]+' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Sort-Object -Unique
```

Both should return `skillListingBudgetFraction` and `skillListingMaxDescChars`, confirming the binary has them. If you see only one or neither, your Claude Code is older than 2.1.129 and the settings will not apply.

## How the Budget Math Works

The fraction is a percentage of the **total context window**. That number changes per model.

| Model | Context Window | 1% Default Budget | 2% (Doubled) | 5% (Aggressive) |
| --- | --- | --- | --- | --- |
| Sonnet 4.6 (200K) | 200,000 tokens | ~2,000 tokens | ~4,000 tokens | ~10,000 tokens |
| Sonnet 4.6 [1M] | 1,000,000 | ~10,000 tokens | ~20,000 | ~50,000 |
| Opus 4.7 (1M) | 1,000,000 | ~10,000 tokens | ~20,000 | ~50,000 |
| Haiku 4.5 (200K) | 200,000 | ~2,000 tokens | ~4,000 | ~10,000 |

A typical skill description runs 200-400 characters, which is roughly 50-100 tokens. Add the XML wrapper Claude Code uses around each entry - skill name, location, frontmatter overhead - and each skill consumes about **75-150 tokens** in the listing.

That math gives you a back-of-envelope ceiling at the default 1%:

- **2,000-token budget (1% on 200K)**: Around 15-25 skills before truncation
- **10,000-token budget (1% on 1M)**: Around 75-125 skills before truncation

Hit that ceiling and the warning fires.

## Why Drop Instead of Truncate?

Earlier Claude Code versions capped each description at 250 characters, then 1,536 and silently truncated overflow. The current 2.1.129 approach is a meaningful upgrade: it drops entire descriptions for low-use skills rather than cutting all descriptions in half.

This trade-off matters. Truncated descriptions silently lose trigger keywords from the back half of the text - the skill stays "visible" but Claude can no longer match user intent against the missing keywords. Dropped descriptions keep your most-used skills fully discoverable at the cost of newer or experimental skills going dark, which is honest and explicit.

The selection logic uses recency and frequency. Claude Code tracks which skills you invoke and ranks descriptions by usage. Most-invoked survives. Least-invoked gets cut.

## Three Ways to Fix the Warning

When you see it, you have three real options. Pick based on whether you actually need those dropped skills.

### Option 1: Disable Skills You Do Not Need (Free)

```
/skills
```

The `/skills` command opens a picker where you can toggle individual skills on or off. Disabled skills are removed from the listing entirely - they do not count against your budget.

This is the **default recommendation**. Most users have skills installed they have not used in a month. Disable those and the budget warning vanishes without any session-cost penalty.

Look for:

- Plugin skills you tested once and never returned to
- Agent skills overlapping with built-in tools
- Project-specific skills you only need in certain repos (move them to that repo's `.claude/skills/` instead of the user-level `~/.claude/skills/`)

Project-scoped skills only count against the budget when you are inside that project. User-scoped skills count in every session. The simplest cleanup is moving rarely-needed skills into the projects that actually use them.

### Option 2: Raise the Budget in `settings.json` (Costly)

```
{
  "skillListingBudgetFraction": 0.02,
  "skillListingMaxDescChars": 2048
}
```

Every increment costs tokens **on every single session**, even ones where you write zero code.

The warning quantifies it: `~3k tokens for skills every session`. That number changes based on how many skills you have. If you raise the fraction high enough to fit all your descriptions, expect to pay the full cost every time you start Claude Code.

Multiplied across a Pro subscription's weekly cap (45 hours of Sonnet) or a Max plan's cap, this matters. A 3K-token-per-session overhead on 100 sessions per week is 300K extra prompt tokens per week. Real budget pressure if you sit near your weekly limit.

Raise the fraction only when:

- You have 50+ legitimately useful skills
- You are on a 1M context model where the percentage is more forgiving
- You hit weekly limits rarely or operate on usage-based billing

Otherwise, choose Option 1 or 3.

### Option 3: Tighten Skill Descriptions (Free, Sustainable)

The cheapest fix is making your descriptions shorter and more keyword-dense.

Each skill's `description` field in its frontmatter has one job: tell Claude when to load this skill. It does **not** need to explain how the skill works, list all features, or include marketing prose. It needs trigger keywords.

```
# Bad: 380 characters, marketing-style
---
name: code-review
description: A comprehensive code review skill that analyzes your codebase for security vulnerabilities, performance issues, code smells, accessibility problems, and architectural concerns. Use this whenever you want a thorough review of any code changes you have made or are about to ship.
---
# Good: 110 characters, keyword-dense
---
name: code-review
description: Reviews code for security, performance, and architecture issues. Use when reviewing PRs or pre-ship changes.
---
```

The good version is 70% smaller, still mentions every primary trigger word (`reviews code`, `security`, `performance`, `architecture`, `PRs`, `pre-ship`), and is more reliable for skill matching. Front-loading triggers also helps - if `skillListingMaxDescChars` truncation kicks in, the front of your description is what survives.

Run a budget audit by listing your skill description lengths:

```
# Unix/macOS
find ~/.claude/skills -name "SKILL.md" -exec sh -c \
  'echo "$(wc -c < "$1") chars: $1"' _ {} \; | sort -rn | head -20
 
# Windows PowerShell
Get-ChildItem ~\.claude\skills -Recurse -Filter SKILL.md |
  Sort-Object Length -Descending | Select -First 20 Name, Length
```

Anything with a description over 200 characters is a candidate for trimming.

## How to Predict the Warning Before It Fires

Run `/context` at session start. The output includes a `Skills:` line:

```
Skills: 1.0k tokens (0.5%)
```

If that percentage approaches `skillListingBudgetFraction` (1% by default), you are close. Once it crosses, the warning fires.

The `1.3%/1%` ratio in the warning message tells you exactly how much you are over. A `1.05%/1%` is barely over - one skill description trim probably resolves it. A `2.5%/1%` is significantly over and either needs Option 1 or Option 3.

## Context Window Math, End to End

This budget interacts with [Claude Code's auto-compact buffer](/blog/context-buffer-management) and the [main thread context layout](/blog/claude-code-session-context). On a 200K Sonnet session:

| Reservation | Tokens | % of 200K |
| --- | --- | --- |
| System prompt | ~2,700 | 1.4% |
| System tools | ~17,000 | 8.4% |
| Custom agents | ~1,300 | 0.7% |
| Memory files (CLAUDE.md) | ~7,400 | 3.7% |
| **Skills (this budget)** | **~2,000** | **1.0%** |
| Autocompact buffer | ~33,000 | 16.5% |
| **Available for messages** | ~136,600 | **68.3%** |

Bumping `skillListingBudgetFraction` to `0.02` steals 2,000 tokens from your messages window. Bumping to `0.05` steals 8,000 tokens. On a tight session at 167K (just before compaction), that overhead pushes the auto-compact trigger forward by an entire turn or two.

If you are already fighting context limits on long sessions, raising the fraction is not free even setting aside the rate-limit cost.

## Best Practices for Skill Inventory Management

1. **Move project-specific skills into projects** - User-level `~/.claude/skills/` should hold genuinely cross-project tools. Repo-specific patterns belong in `.claude/skills/` of that repo
2. **Front-load triggers in descriptions** - First 50 characters should contain the most important match keywords
3. **Cap descriptions at 150 characters** for skills you ship to others, even if your local budget allows more
4. **Audit quarterly** - Run `/skills` and disable anything you have not invoked in 90 days. Re-enable on demand, never proactively
5. **Use the [library meta-skill](/blog/library-meta-skill) for distribution** - Centralize reusable skills in a library and pull only the active ones into each project

## Why This Setting Matters Now

Earlier Claude Code versions silently truncated long skill descriptions at fixed character caps - first 250 characters in v2.1.86, later raised to 1,536 in v2.1.105 - and emitted a startup warning when truncation happened. Users still complained that important trigger keywords disappeared from the back of their descriptions.

The 2.1.129 `skillListingBudgetFraction` approach inverts the trade-off:

- **Old (≤2.1.128)**: Every skill survives, but every description gets shorter
- **New (2.1.129+)**: Every description stays full, but low-use skills disappear

For users with 5-10 skills, both approaches behave identically - nothing gets cut. For users with 50+ skills, the new approach is strictly better. Most-invoked skills retain full match keywords, and you get an explicit warning naming exactly which skills went dark, with three actionable fixes.

The setting is exposed but conservative by default at 1%, on the assumption that most users have a small focused skill set rather than a sprawling library. Once your library outgrows that assumption, you opt in to a higher fraction and accept the per-session cost. Expect this to land in the official changelog within the next few releases.

## TL;DR

- Two new settings in 2.1.129: `skillListingBudgetFraction` (default `0.01`) and `skillListingMaxDescChars` (default `1536`)
- Edit `~/.claude/settings.json` to raise either: `{ "skillListingBudgetFraction": 0.02 }`
- Format is a **decimal between 0 and 1**, not a percentage. `0.02` means 2%
- Optionally set `SLASH_COMMAND_TOOL_CHAR_BUDGET` as a raw character count override
- Cheap fix: `/skills` and disable unused skills
- Expensive fix: raise the fraction (~3K extra tokens per session, faster rate-limit burn)
- Sustainable fix: tighten descriptions to 100-150 chars with trigger keywords front-loaded

If you maintain a large skill collection, run options 1 + 3 first, leave option 2 as a last resort for users on 1M context models or usage-based billing.

For deeper context, read [Claude Skills Guide](/blog/claude-skills-guide), [Context Buffer Management](/blog/context-buffer-management), and [Claude Code Session Context](/blog/claude-code-session-context).
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
