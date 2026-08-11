---
title: "Claude Code Library: Sync .claude Configs Across Projects"
description: "Build a central library to manage .claude folders across projects. One repo for skills, agents, commands, hooks, and configs."
slug: library-meta-skill
date: 2026-03-24
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Build a central library to manage .claude folders across projects. One repo for skills, agents, commands, hooks, and configs.

<!-- truncate -->

You have 10 codebases. Each one has a `.claude` folder with skills, agents, commands, hooks, and a CLAUDE.md file. Some folders are current. Most drifted weeks ago. You improved your code review agent in one project and forgot to copy it to the other nine. Your teammate built a planning command you never knew existed because it lives in their repo, not yours.

This is the `.claude` folder distribution problem. It gets worse with every project you add.

**Quick Win**: Build a private Git repo that holds all your `.claude` content centrally, with a `map.json` that controls which project gets which items:

```
{
  "projects": {
    "~/projects/webapp": {
      "claude-md": "web-full",
      "skills": ["git-commits", "react", "frontend-design"],
      "agents": ["visual-explainer"],
      "commands": ["team-plan", "build"]
    }
  }
}
```

Run one sync command and the project's `.claude` folder matches the map. Modify a skill or agent locally, push it back to the library, and every project that uses it picks up the change on next sync.

## Why .claude Folder Management Matters

If you work in a single codebase, your skills, agents, and commands live right next to your code. Everything is findable, everything is current.

Once you pass five or six projects, things break down:

- **Duplication everywhere.** The same git-commits skill exists in 8 repos, each slightly different.
- **Version drift.** You improved your planning command last week, but only in one project. The other repos still run the old version.
- **No coordination.** Your teammate built a database migration agent. You built your own because you didn't know theirs existed.
- **Configuration sprawl.** It's not just skills. It's hooks, settings.json, CLAUDE.md files, agent definitions, and slash commands. Each project needs a different combination.

The instinct is to copy files. It's fast, it works in the moment, and it falls apart within a month. Every engineer running multi-repo agent setups has been there.

[IndyDevDan](https://github.com/disler/the-library) identified this problem early and built a pure-agentic solution using a YAML catalog of references. His approach proved the pattern works. But after adopting it across 10+ projects with 30+ skills and 19 agents, I needed something with more structure: actual file management, variant support, full `.claude` folder coverage, and a real sync engine.

## The Library Architecture

The library is a private Git repo that stores your complete `.claude` configuration. Not references or pointers to other repos. The actual files. One canonical copy of every skill folder, every agent definition, every slash command, every hook, every CLAUDE.md, and every settings.json.

A `map.json` at the root defines which project gets which items. A sync script copies the right files to the right places. A manifest in each project tracks what the library owns so local files are never touched.

```
your-library/
├── map.json                    # Which projects get what
├── sync.mjs                    # Node.js sync engine
│
├── skills/                     # All skill folders
│   ├── git-commits/
│   ├── agentic-builder/
│   ├── react/
│   ├── growth-kit/
│   ├── session-management/
│   └── ... (31 skills in my library)
│
├── agents/                     # All agent .md files
│   ├── frontend-specialist.md
│   ├── backend-engineer.md
│   ├── security-auditor.md
│   ├── master-orchestrator.md
│   └── ... (19 agents in my library)
│
├── commands/                   # All slash commands
│   ├── team-plan.md
│   ├── build.md
│   ├── team-build.md
│   └── ... (16 commands in my library)
│
├── hooks/                      # All hook folders
│   ├── SkillActivationHook/
│   ├── ContextRecoveryHook/
│   └── Validators/
│
├── claude-mds/                 # CLAUDE.md variants (full replacement per project)
│   ├── CLAUDE--web-full.md
│   └── CLAUDE--product.md
│
├── settings/                   # settings.json variants
│   ├── settings--web.json
│   └── settings--product.json
│
└── rules/                      # .claude/rules/ files
    ├── repo-primer--webapp.md
    └── repo-primer--product.md
```

Eight content categories (skills, agents, commands, hooks, rules, claude-mds, settings, and arbitrary files), all managed through one repo. When you sync a project, the engine reads `map.json`, finds the project's configuration, and copies exactly the items listed. Nothing more, nothing less.

## The Map: Controlling What Goes Where

The `map.json` is the brain of the system. Each project entry lists exactly which items it receives:

```
{
  "$schema": "library-map-v1",
  "projects": {
    "C:/Github/my-webapp": {
      "claude-md": "CLAUDE--web-full",
      "settings": "settings--web",
      "skills": [
        "git-commits",
        "react",
        "frontend-design",
        "session-management"
      ],
      "agents": ["frontend-specialist", "quality-engineer"],
      "commands": ["team-plan", "build", "team-build"],
      "hooks": ["SkillActivationHook", "Validators"],
      "rules": [],
      "files": {}
    }
  }
}
```

A different project might use a completely different selection. A SaaS project gets `backend-engineer`, `supabase-specialist`, and `security-auditor` agents with `postgres-best-practices` and `auth` skills. A marketing-focused repo gets `growth-kit`, `seo-specialist`, and `content-writer` instead. A product repo gets a stripped-down set with a different [CLAUDE.md](/blog/claude-md-mastery) and different hooks. The library holds everything; each project picks what it needs.

You can also define **profiles** for common configurations that multiple projects share:

```
{
  "profiles": {
    "web-default": {
      "claude-md": "CLAUDE--web-full",
      "settings": "settings--web",
      "skills": [
        "git-commits",
        "react",
        "frontend-design",
        "session-management"
      ],
      "agents": ["frontend-specialist", "quality-engineer"],
      "commands": ["team-plan", "build"],
      "hooks": ["SkillActivationHook", "Validators"]
    }
  }
}
```

Initialize a new project with `--profile web-default` and it gets the full web stack in one command.

## Variants: When One Version Isn't Enough

Here's the problem profiles don't solve: your `git-commits` skill works great across most projects, but your blog project needs a modified version with extra commit patterns for MDX content. You don't want to fork the skill into a separate entity. You want the same skill, just a project-specific version.

Variants use a `name--variant` naming convention. The double dash separates the base name from the variant tag:

```
skills/
├── git-commits/                    # Base version
│   └── SKILL.md
├── git-commits--blog/              # Variant for blog projects
│   ├── SKILL.md                    # Modified version
│   └── references/
│       └── mdx-patterns.md         # Extra file this variant needs
```

In `map.json`, you reference the full name:

```
{
  "skills": ["git-commits--blog", "react", "frontend-design"]
}
```

When synced, `git-commits--blog` deploys as `.claude/skills/git-commits/`. The `--blog` suffix is a library concept only. The project never sees it. The variant is a complete, independent folder. It can have different files, different structure, different content. It just shares a deploy name with its base.

The power of this shows up during push. You modify `.claude/skills/git-commits/` in your blog project. The sync engine reads the manifest, sees that `git-commits` maps to `git-commits--blog` in the library, and pushes changes to the right place. Your other projects still pull the base version.

## Operations

The sync engine is a Node.js script with zero external dependencies. Eight operations cover the full lifecycle:

| Operation | What It Does |
| --- | --- |
| **sync** | Copy items from library to project based on map.json |
| **push** | Copy local changes back to library (respects variant mapping) |
| **diff** | Hash-compare each managed item, show what's changed |
| **list** | Show all library contents and which projects use what |
| **add** | Add an item to a project's map, then sync it |
| **remove** | Remove an item from map and delete from project |
| **init** | Register a new project in map.json |
| **seed** | Import an existing project's .claude/ into the library |

The `seed` operation is how you bootstrap. Point it at a project that already has a well-configured `.claude` folder and it imports everything into the library, creates the map.json entry, and writes the manifest. From that point on, the library is the source of truth.

The `diff` operation uses content hashing to compare library and project versions. It reports `in-sync`, `local-changes`, or `library-ahead` for each item, so you always know what's drifted before you sync or push.

## The Manifest: Tracking What the Library Owns

Every synced project gets a `.claude/.library-manifest.json`:

```
{
  "library_path": "/path/to/your-library",
  "synced_at": "2026-03-24T10:30:00Z",
  "library_commit": "abc123",
  "managed": {
    "skills": {
      "git-commits": "git-commits--blog",
      "react": "react",
      "frontend-design": "frontend-design"
    },
    "agents": {
      "frontend-specialist": "frontend-specialist"
    },
    "claude-md": "CLAUDE--web-full",
    "settings": "settings--web"
  }
}
```

The manifest maps deploy names to library names. This is how push knows that your local `git-commits/` folder should go back to `git-commits--blog/` in the library, not the base version.

Anything in `.claude/` that's not in the manifest is invisible to the library. Local tasks, backups, project-specific experiments all survive syncs untouched. The library only manages what it placed there.

## Natural Language Interface

Beyond the CLI, the system includes a `/library` slash command that deploys to every synced project. Instead of remembering flags, you speak naturally:

```
/library sync
/library I modified the blog command, push it back
/library add the payment-processing skill to this project
/library what's out of sync?
/library create a variant of react for this project
/library show me everything available
```

Claude reads the manifest, locates the library, interprets the intent, and calls the sync engine. For destructive operations (removing items, overwriting), it confirms before proceeding.

This is the interaction model that makes the system practical for daily use. You don't leave your Claude Code session to manage your library. You just tell it what you need.

## Getting Started

Building your own library takes about 30 minutes:

1. **Create a private repo** with the folder structure: `skills/`, `agents/`, `commands/`, `hooks/`, `claude-mds/`, `settings/`
2. **Seed from your best project.** Take the project with the most complete `.claude` folder and import it. This becomes your initial library content.
3. **Write your map.json.** Start with one project entry. List every skill, agent, command, hook, and configuration file it should have.
4. **Build the sync script.** The core is straightforward: read map.json, parse item names (splitting on `--` for variants), copy files to the right places, write a manifest. Git pull before sync, git commit and push after push.
5. **Add the `/library` command** to the library itself. It syncs to every project automatically, giving you the natural language interface from day one.
6. **Add a second project** with a different selection. This is where the system proves its value. Two projects, same library, different configurations, always in sync.

The key design decision: store actual files, not references. References add an indirection layer that makes variants harder and pushes more complex. When the files live in the library, sync is just a copy, push is just a copy back, and diff is just a hash comparison.

## Why This Matters at Scale

Once the library is running, behaviors change. For reference, my library currently manages 31 skills, 19 agents, 16 commands, 4 hook systems, and project-specific CLAUDE.md and settings.json files across 3 active projects. Here is what that looks like in practice:

**Improvements propagate.** Fix a bug in your code review agent, push it, and the next sync brings it to every project that uses it. No more "I fixed this somewhere but I don't remember where."

**New projects start fast.** Initialize with a profile and your full [agent team](/blog/team-orchestration), hooks, settings, and [CLAUDE.md](/blog/claude-md-mastery) are ready in seconds. No more spending the first hour of a new project copying configuration files.

**Variants prevent forking.** When a project needs a modified version of something, you create a variant instead of diverging silently. The relationship between base and variant is explicit in the library. A year from now, you can see exactly which projects use which versions.

**The library self-distributes.** The `/library` command is itself managed by the library. When you improve the command, it propagates to every project on next sync. The distribution system distributes itself.

The `.claude` folder distribution problem is a symptom of a deeper shift. As [agentic engineering](/blog/agentic-engineering-best-practices) matures, your entire `.claude` configuration becomes real infrastructure: skills, agents, commands, hooks, rules, CLAUDE.md, and settings. They deserve the same management rigor as your application code. A central library with variant support and bidirectional sync is one way to give them that.

## Frequently Asked Questions

### What is a Claude Code library system?

A library system is a private Git repository that stores all your `.claude` folder content centrally: skills, agents, commands, hooks, CLAUDE.md files, and settings. A map.json file controls which items each project receives, and a sync engine copies the right files to the right places.

### How is this different from IndyDevDan's the-library?

[IndyDevDan's approach](https://github.com/disler/the-library) stores references (pointers to GitHub repos or local paths) in a YAML catalog. The library system described here stores the actual files in one repo, adds a variant naming convention for project-specific versions, includes a manifest for bidirectional sync, and covers all `.claude` content categories (skills, agents, commands, hooks, rules, CLAUDE.md, settings, and arbitrary files).

### Do I need to open source my library?

No. The library works best as a private repo because it contains your specialized skills, project-specific [CLAUDE.md configurations](/blog/claude-md-mastery), and potentially sensitive agent instructions. Keep it private. If you later want to share individual skills publicly, you can extract them.

### How do variants work?

Variants use a `name--variant` naming convention. A folder called `react--strict/` in the library deploys as `.claude/skills/react/` in the project. The variant is a complete, independent copy with its own files and structure. The manifest tracks the mapping so push operations send changes back to the correct variant.

### Can multiple people share one library?

Yes. Since the library is a Git repo, your team clones it and syncs from it. When someone improves a skill, they push it back. The whole team gets the improvement on their next sync. The map.json can have entries for each team member's projects.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
