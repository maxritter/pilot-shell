---
title: "Claude Code Skills Not Activating? The Real Fix"
description: "Guaranteed loading was the wrong goal. Word-boundary matching, trigger scoring, a cap of three, and advisory voice make skill activation accurate."
slug: skill-activation-hook
date: 2025-12-07
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Guaranteed loading was the wrong goal. Word-boundary matching, trigger scoring, a cap of three, and advisory voice make skill activation accurate.

<!-- truncate -->

**Problem**: You tell Claude Code to load a skill. It forgets. You add instructions to CLAUDE.md. It ignores them. You end up manually reminding Claude about skills that should be automatic.

**Quick Win**: A `UserPromptSubmit` hook matches your prompt against a rules file and surfaces the skills that apply, before Claude ever sees the message. Claude does not have to remember, because the reminder arrives attached to your prompt.

That is the mechanism, and it works. The harder question, which took us eighteen months and a rewrite to answer honestly, is what the hook should say when it fires.

## What This Post Used to Say

This page shipped in December 2025 titled "Guarantee 100% Skill Loading." The hook it documented used bare substring matching, injected a block headed `CRITICAL SKILLS (REQUIRED)` ending in `ACTION: Use Skill tool BEFORE responding`, and had no limit on how many skills it could name at once.

Every one of those choices was wrong, and they were wrong in the same direction: **they optimised for firing rather than for being right.** A hook that fires on everything has 100% recall and is useless, because the model learns that the block is noise and starts discounting all of it, including the times it was correct.

The rewrite below is what the hook looks like now. The goal changed from guaranteed loading to accurate loading, and the interesting part is that accurate loading produces better actual loading, because a signal the model trusts is a signal it acts on.

## How It Works

The hook uses Claude Code's `UserPromptSubmit` event. Every prompt you send triggers this flow:

1. **You type a message** - your natural language request
2. **Hook intercepts** - before Claude sees anything
3. **Pattern matching** - the hook checks `skill-rules.json` for keyword and intent matches
4. **Score and cap** - matches are ranked, and only the top three survive
5. **Claude receives both** - your prompt plus a short advisory list

The hook runs in milliseconds. You will not notice any delay.

## The Matching System

Two strategies work together, and the first one has a trap in it.

**Keyword matching with word boundaries.** The naive implementation is `prompt.includes(keyword)`, and it is what this page originally recommended. It produces a specific and very common class of false positive: a keyword that is a substring of an unrelated word. The trigger `plan` fires on "explanation." The trigger `test` fires on "latest" and "contest." The trigger `api` fires on "rapid" and "therapist." None of these are exotic; they show up in ordinary prompts constantly, and each one burns a slot in the injected block.

The fix is a word-boundary regex, with the keyword escaped so a trigger containing `.` or `+` cannot corrupt the pattern:

```
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
 
function wordBoundaryMatch(prompt, keyword) {
  return new RegExp(`\\b${escapeRegex(keyword.toLowerCase())}\\b`, "i").test(
    prompt,
  );
}
```

That single change removed the large majority of spurious activations in our own logs, and it costs nothing.

**Intent patterns** are regex for natural language variation. A pattern like `(implement|build).*?feature` catches "let's implement this feature" and "build a new feature for me." Wrap the test in a `try/catch`: a malformed pattern in the rules file should skip that one trigger, not crash the hook and swallow your prompt.

### Scoring by Distinct Triggers

Once you have matches, you need an order. The useful signal is **how many distinct triggers a skill hit**, not whether it hit at all. A skill that matched four separate keywords is far more likely to be the right one than a skill that matched a single generic word, and priority alone cannot express that.

```
const score = keywordHits.length + intentHits;
```

Priority becomes the tiebreak rather than the primary sort, which is the correct relationship: priority is a static property of the skill, and score is evidence from the actual prompt. Evidence should win.

```
matched.sort(
  (a, b) =>
    b.score - a.score ||
    (PRIORITY_WEIGHT[b.priority] || 0) - (PRIORITY_WEIGHT[a.priority] || 0),
);
```

## Cap the Output at Three

This is the change with the largest effect and the least intuition behind it.

An uncapped hook on a mature rules file will routinely surface six or eight skills for a single prompt. That is not helpful context, it is a second prompt competing with the one you wrote. The model now has to triage a list before it can start, and the skills it most needed are buried among the ones that matched on one weak keyword.

```
const MAX_RECOMMENDATIONS = 3;
const top = matched.slice(0, MAX_RECOMMENDATIONS);
```

Three is not a magic number, but the principle is: **the cap should be low enough that the list stays readable at a glance.** If the right skill is not in the top three by distinct-trigger score, your triggers are the problem, and raising the cap only hides it.

## Advisory Voice, Not Imperative

The original injected block read like this:

```
CRITICAL SKILLS (REQUIRED):
  -> session-management

ACTION: Use Skill tool BEFORE responding
```

The current one reads like this:

```
Possibly relevant skills (load what genuinely applies, skip the rest):
  → session-management (matched: feature, implement, 1 intent match)
```

Three differences, all deliberate.

**It states what matched.** Showing the actual trigger hits lets the model evaluate the recommendation instead of taking it on faith, and it lets *you* debug your rules file by reading the transcript.

**It grants permission to skip.** A hook is a keyword matcher. It does not know what you are doing. Telling a model that a keyword match is `REQUIRED` asks it to follow an instruction that is sometimes plainly wrong for the task in front of it, and the model now has to reconcile your imperative against its own judgment on every single prompt.

**It stops shouting.** `CRITICAL`, `REQUIRED`, and `BEFORE responding` are emphasis borrowed from a period when models needed steering to comply at all. On the [Claude 5 generation](/blog/claude-5-context-engineering) that pressure inverts: an instruction that overrides judgment makes behaviour worse, not more reliable. The advisory phrasing is not politeness, it is accuracy about what the hook actually knows.

## Configuration: skill-rules.json

Every skill has triggers defined in `.claude/skills/skill-rules.json`:

```
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

Priority levels now act as the tiebreak in scoring rather than as a hard grouping:

- **Critical** - wins ties, load-bearing for most sessions
- **High** - strongly relevant when it matches
- **Medium** - helpful context
- **Low** - optional enhancement

## Trigger Drift: Content With No Way In

Here is the failure mode nobody warns you about, and it is the inverse of a false positive.

**Content added to a skill body without a matching trigger update is unreachable.** The skill exists, the file is on disk, the section is well written, and no prompt you can type will ever surface it, because the hook only knows the keywords in `skill-rules.json`.

We shipped a 400-line analytics section into a skill and never touched its triggers. It sat there for weeks, fully written and completely invisible. No error, no warning, no failed lookup. Nothing distinguishes an unreachable section from one that simply never came up, which is exactly why the drift can run for months.

Two habits fix it:

1. **Update triggers in the same commit as the content.** Adding a section to a skill is not done until a prompt someone would plausibly type reaches it.
2. **Periodically read your triggers against your skill bodies.** Ask what a user would type to want each major section, then check that string against the rules file. This takes ten minutes and it consistently finds something.

Trigger drift generalises past this hook. Any retrieval layer keyed on hand-maintained metadata has the same failure: the content and the index drift apart silently, and only the index is consulted.

## What We Deleted

The hook used to recommend sub-agents alongside skills, mapping prompt patterns to specialist agent types. That half was removed outright in July 2026.

The reason it went is worth stating plainly: **it never once changed a routing decision.** In every session where it fired, the lead either had already decided to delegate or correctly decided not to, and the hook's suggestion was noise in both cases. Worse, it had a consistent bias toward delegating, so the only pressure it applied was toward over-delegation, which costs real money.

A hook that fires reliably and changes nothing is not a neutral feature. It is a permanent tax on every prompt, and it trains the model to skim the injected block that also carries the skill recommendations. Deleting it made the remaining signal stronger.

The general test, which we now apply to every hook we keep: **can you name a decision this changed?** If not, it is not earning its place in the context window.

## Customization for Your Speech Patterns

The hook adapts to how you talk. If you always say "push my code" instead of "git push", add it:

```
"keywords": ["commit", "git push", "push my code", "commit changes"]
```

With word-boundary matching in place you can afford more specific multi-word triggers, because they no longer risk substring collisions. Prefer two or three precise phrases over one broad word: precise triggers raise a skill's score when they genuinely hit, while a broad word like `build` matches everything and mostly generates noise for other skills to outrank.

## Session Intelligence

The hook tracks what it already surfaced. If it named `session-management` earlier in your conversation, it will not repeat it. Less noise, same coverage.

Session state lives in `recommendation-log.json` and auto-cleans after 7 days.

This is a real accuracy mechanism, not just tidiness. Repetition is how an injected block becomes wallpaper: a recommendation the model has already seen and already acted on adds nothing on the tenth prompt except a reason to stop reading the block.

The hook is pre-configured. Verify your `.claude/settings.local.json` includes:

```
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/SkillActivationHook/skill-activation-prompt.mjs\""
          }
        ]
      }
    ]
  }
}
```

One config, every platform. An earlier version of this page gave separate Windows and Linux/Mac commands wrapping `cmd /c` and `bash`, which breaks the moment the file is shared across a mixed team. Invoke `node` directly and handle platform differences inside the script with `os.homedir()`, `os.tmpdir()`, and `path.join()`. The `$CLAUDE_PROJECT_DIR` prefix matters too: a bare relative path throws `MODULE_NOT_FOUND` as soon as the session's working directory moves into a subdirectory. See [cross-platform hook patterns](/blog/cross-platform-hooks) for the full treatment.

## Common Issues

**No suggestions appearing**
Check that your keywords match your actual speech patterns. Run the hook manually to test:

```
echo '{"session_id":"test","prompt":"implement a feature"}' | node .claude/hooks/SkillActivationHook/skill-activation-prompt.mjs
```

**A skill you expected never appears, ever**
Suspect trigger drift before suspecting the hook. Grep `skill-rules.json` for a word from the section you wanted. If it is not there, the content has no way in.

**Suggestions appearing when not needed**
Check whether the trigger is a substring of an ordinary word. If you are still on `includes()` matching, switch to word boundaries first; that alone resolves most of these.

**The right skill loses to a wrong one**
Look at the `matched:` list in the injected block. The winner hit more distinct triggers. Add specific triggers to the skill you wanted rather than deleting triggers from the one that won.

**Duplicate suggestions**
The hook might be configured in both global and project settings. Keep it in one location only.

## Verify Against the Transcript, Not the Vibe

One process note, because it is how every finding above was actually established.

You cannot evaluate a `UserPromptSubmit` hook by prompting Claude and judging the answer. The injected block is upstream of everything you see, and a good response tells you nothing about whether the block helped, hurt, or was ignored. Read the transcript. The block is in there verbatim, with the matched triggers listed, and comparing what was injected against what the session then did is the only measurement that means anything.

That is the same discipline that surfaced the agent-recommendation deletion: the suggestion was in every transcript, and the routing decision never once followed it.

## Next Actions

1. Switch your matcher to word boundaries if it still uses `includes()`
2. Cap the injected list at three and sort by distinct-trigger count
3. Soften the voice from `REQUIRED` to "possibly relevant, skip what does not apply"
4. Audit your skill bodies for trigger drift, then update `skill-rules.json` in the same commit
5. Set up the main [Hooks Guide](/blog/hooks-guide) for complete hook coverage
6. Review the [skills guide](/blog/claude-skills-guide) if you need to create new skills

The Skill Activation Hook removes human memory from the equation, but only if what it injects is worth reading. Accuracy is what makes an automatic signal trustworthy, and trust is what makes it get used. Aim for a block that is right three times out of three, not one that fires every time.

[Context Recovery Hook](/blog/context-recovery-hook)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
