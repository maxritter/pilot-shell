---
slug: "claude-skills-guide"
title: "Claude Skills: Stop Repeating Instructions Forever"
description: "Skills are Claude Code's missing link between prompts and MCP. Load instructions on-demand, save context, give Claude domain expertise."
date: "2025-12-07"
author: "Max Ritter"
tags: [Guide, Workflow]
readingTime: 4
keywords: "claude, forever, guide, instructions, repeating, skills, stop"
---

Mechanics

# Claude Skills: Stop Repeating Instructions Forever

Skills are Claude Code's missing link between prompts and MCP. Load instructions on-demand, save context, give Claude domain expertise.

**Problem**: You type the same instructions into Claude Code every session. "Follow our brand guidelines." "Use our deployment process." "Check security patterns first." Context wasted. Time lost. Instructions forgotten.

**Quick Win**: Create your first skill right now:

```p-4
.claude/skills/my-skill/SKILL.md
```

```p-4
---
name: code-review
description: Reviews code for security and performance issues
---
 
# Code Review Process
 
1. Check for SQL injection vulnerabilities
2. Verify input validation exists
3. Confirm error handling patterns
```

That is a complete skill. Drop it in your project, and Claude automatically loads it when you ask for code review.

## [What Are Skills?](#what-are-skills)

**Skills are folders containing instructions that Claude discovers and loads dynamically.** Think of them as specialized training manuals Claude references only when needed.

Unlike prompts (which disappear after each conversation) or [MCP servers](/blog/tools/mcp-extensions/mcp-basics) (which connect to external tools), skills teach Claude *how to do things*. They encode procedural knowledge: workflows, guidelines, checklists, and domain expertise.

Simon Willison noted this efficiency: "Each skill only takes up a few dozen extra tokens, with the full details only loaded in should the user request a task that the skill can help solve."

## [How Progressive Disclosure Works](#how-progressive-disclosure-works)

Skills use a two-stage loading system that saves your [context window](/blog/guide/performance/context-preservation):

**Stage 1 - Metadata Only (~100 tokens)**: Claude sees skill names and descriptions. Just enough to know what is available.

**Stage 2 - Full Instructions (when needed)**: Only when Claude determines a skill matches your task does it load full instructions—typically under 5,000 tokens.

```p-4
my-skill/
├── SKILL.md              # Core instructions (loads when needed)
├── scripts/              # Automation scripts
├── references/           # Documentation Claude can read
└── assets/               # Templates and files
```

This architecture means you can have dozens of skills available without overwhelming Claude's working memory.

## [Skills vs Everything Else](#skills-vs-everything-else)

Where do skills fit in Claude's ecosystem?

| Feature | Skills | Prompts | Projects | MCP |
| --- | --- | --- | --- | --- |
| **What it provides** | Procedural knowledge | Moment instructions | Background knowledge | Tool connectivity |
| **Persistence** | Across conversations | Single conversation | Within project | Always connected |
| **When it loads** | Dynamically, as needed | Each turn | Always in project | Always available |
| **Best for** | Workflows and expertise | Quick requests | Reference documents | External data access |

**Key distinction**: Projects say "here's what you need to know." Skills say "here's how to do things." [MCP](/blog/tools/mcp-extensions/mcp-basics) says "here's how to connect."

## [When to Create a Skill](#when-to-create-a-skill)

**The rule**: If you type the same prompt across multiple conversations, create a skill instead.

**Good candidates for skills**:

- Brand guidelines and style rules
- Code review checklists
- Deployment procedures
- Security audit patterns
- Documentation templates
- [Git commit conventions](/blog/guide/development/git-integration)

**Not ideal for skills**:

- One-time requests
- Project-specific context (use Projects instead)
- External API access (use MCP instead)

## [Writing an Effective SKILL.md](#writing-an-effective-skillmd)

Every skill needs three components:

```p-4
---
name: my-skill
description: What it does and WHEN to trigger it
allowed-tools: "Read,Write,Bash"
---
 
# Clear Purpose Statement
 
## Step-by-Step Instructions
 
1. First action
2. Second action
3. Expected output
```

**Critical**: The `description` field determines when Claude activates your skill. Be specific about triggers: "When user requests code review" beats "Helps with code."

## [Pre-Built Skills from Anthropic](#pre-built-skills-from-anthropic)

Anthropic maintains official skills you can use immediately:

- **pdf**: Extract text and tables from PDF documents
- **docx**: Create and edit Word documents with tracked changes
- **xlsx**: Manipulate Excel spreadsheets
- **pptx**: Generate PowerPoint presentations
- **brand-guidelines**: Apply consistent styling

Find them at [github.com/anthropics/skills](https://github.com/anthropics/skills) or create your own following their patterns.

## [Common Mistakes](#common-mistakes)

**Vague descriptions**: "This skill helps with documents" will not trigger reliably. Be specific.

**Overloaded instructions**: Keep SKILL.md under 5,000 words. Use reference files for detailed documentation.

**Missing boundaries**: Tell Claude what the skill does NOT do. Prevents inappropriate activation.

## [Your Next Steps](#your-next-steps)

1. **Create one skill** for your most repeated instruction
2. **Test triggering** with natural requests (not just explicit commands)
3. **Iterate** based on how it performs in real sessions
4. Explore [context management](/blog/guide/mechanics/context-management) to maximize your skill efficiency
5. Learn how skills fit into [context engineering](/blog/guide/mechanics/context-engineering) for production AI

Skills transform Claude from a general assistant into a specialized expert without burning context tokens on repeated explanations. Your expertise becomes portable, reusable, and always available.

Skills are one of five techniques that top agentic engineers use daily. See all five in our [Claude Code best practices](/blog/guide/development/agentic-engineering-best-practices) guide.

Last updated on

[Previous

Context Buffer Management](/blog/guide/mechanics/context-buffer-management)[Next

Dynamic Starting Context](/blog/guide/mechanics/claude-code-session-context)
