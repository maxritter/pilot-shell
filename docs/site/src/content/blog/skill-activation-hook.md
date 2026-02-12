---
slug: "skill-activation-hook"
title: "Claude Code Skill Hook: Guarantee 100% Loading"
description: "Stop Claude from ignoring your skills. The Skill Activation Hook appends recommendations to prompts before Claude sees them. Zero memory reliance."
date: "2025-12-07"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 4
keywords: "100, activation, claude, code, guarantee, hook, loading, skill"
---

Hooks

# Claude Code Skill Activation Hook: Guarantee 100% Skill Loading

Stop Claude from ignoring your skills. The Skill Activation Hook appends recommendations to prompts before Claude sees them. Zero memory reliance.

**Problem**: You tell Claude Code to load a skill. It forgets. You add instructions to CLAUDE.md. It ignores them. You end up manually reminding Claude about skills that should be automatic.

**Quick Win**: The Skill Activation Hook intercepts your prompts and appends skill recommendations before Claude sees the message. Claude can't forget because it never had to remember.

When you type "help me implement a feature", Claude actually sees:

```p-4
help me implement a feature

SKILL ACTIVATION CHECK

CRITICAL SKILLS (REQUIRED):
  -> session-management

RECOMMENDED SKILLS:
  -> git-commits

ACTION: Use Skill tool BEFORE responding
```

Claude now knows exactly which skills to load. No guessing. No forgetting.

## [How It Works](#how-it-works)

The hook uses Claude Code's `UserPromptSubmit` event. Every prompt you send triggers this flow:

1. **You type a message** - Your natural language request
2. **Hook intercepts** - Before Claude sees anything
3. **Pattern matching** - Hook checks `skill-rules.json` for keyword and intent matches
4. **Append recommendations** - Matching skills get added to your message
5. **Claude receives both** - Your prompt plus skill guidance

The hook runs in milliseconds. You won't notice any delay.

## [The Matching System](#the-matching-system)

Two strategies work together:

**Keyword Matching** - Simple string matching. If your prompt contains "commit" or "git push", the `git-commits` skill triggers.

**Intent Patterns** - Regex for natural language variation. A pattern like `(implement|build).*?feature` catches "let's implement this feature" and "build a new feature for me".

## [Configuration: skill-rules.json](#configuration-skill-rulesjson)

Every skill has triggers defined in `.claude/skills/skill-rules.json`:

```p-4
{
  "skills": {
    "session-management": {
      "enforcement": "suggest",
      "priority": "critical",
      "promptTriggers": {
        "keywords": ["feature", "implement", "build", "refactor"],
        "intentPatterns": ["(implement|build).*?feature"]
      }
    },
    "git-commits": {
      "enforcement": "suggest",
      "priority": "high",
      "promptTriggers": {
        "keywords": ["commit", "git push", "commit changes"],
        "intentPatterns": ["(create|make).*?commit"]
      }
    }
  }
}
```

Priority levels control how the hook groups suggestions:

- **Critical** - Must load before any work
- **High** - Strongly recommended
- **Medium** - Helpful context
- **Low** - Optional enhancement

## [Customization for Your Speech Patterns](#customization-for-your-speech-patterns)

The hook adapts to how you talk. If you always say "push my code" instead of "git push", add it:

```p-4
"keywords": ["commit", "git push", "push my code", "commit changes"]
```

After creating any new skill, update its triggers in `skill-rules.json`. Then read those triggers and keep those speech patterns in mind when prompting.

## [Session Intelligence](#session-intelligence)

The hook tracks what it already recommended. If it suggested `session-management` earlier in your conversation, it won't repeat the suggestion. Less noise, same coverage.

Session state lives in `recommendation-log.json` and auto-cleans after 7 days.

## [Common Issues](#common-issues)

**No suggestions appearing**
Check that your keywords match your actual speech patterns. Run the hook manually to test:

```p-4
echo '{"session_id":"test","prompt":"implement a feature"}' | node .claude/hooks/SkillActivationHook/skill-activation-prompt.mjs
```

**Suggestions appearing when not needed**
Your keywords may be too broad. Use more specific terms or intent patterns.

**Duplicate suggestions**
The hook might be configured in both global and project settings. Keep it in one location only.

## [Next Actions](#next-actions)

1. Check your `skill-rules.json` matches your vocabulary
2. Add keywords for new skills you create
3. Set up the main [Hooks Guide](/blog/tools/hooks/hooks-guide) for complete hook coverage
4. Configure the [Stop Hook](/blog/tools/hooks/stop-hook-task-enforcement) to enforce task completion
5. Learn more about [CLAUDE.md configuration](/blog/guide/mechanics/claude-md-mastery) to complement the hook
6. Review the [skills guide](/blog/guide/mechanics/claude-skills-guide) if you need to create new skills

The Skill Activation Hook removes human memory from the equation. You focus on describing what you need. The framework handles which skills Claude should use. That's the point of a framework.

Last updated on

[Previous

Context Recovery Hook](/blog/tools/hooks/context-recovery-hook)[Next

Permission Hook](/blog/tools/hooks/permission-hook-guide)
