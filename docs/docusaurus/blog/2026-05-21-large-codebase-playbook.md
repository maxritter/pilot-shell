---
title: "Claude Code in Large Codebases: 8 Strategies"
description: "How to run Claude Code in monorepos, legacy codebases, and enterprise repos. 8 strategies for navigating millions of lines at scale."
slug: large-codebase-playbook
date: 2026-05-21
authors:
  - max-ritter
tags:
  - guide
  - development
---

How to run Claude Code in monorepos, legacy codebases, and enterprise repos. 8 strategies for navigating millions of lines at scale.

<!-- truncate -->

Your weekend project ran on Claude Code beautifully. Then you opened the 200k-line monorepo at work and the same agent felt like it had brain damage. It grep-searched into a wall of irrelevant matches, asked questions about modules that were not relevant, and burned through tokens before producing anything useful.

This is the most common Claude Code failure mode, and it has nothing to do with the model. It is about the absence of a harness. **Yes, Claude Code can handle large codebases**, including monorepos and legacy systems running into millions of lines. But the default setup is tuned for the median project, not the enterprise edge case. The fix is not better prompting. It is a deliberate eight-part configuration that turns Claude from a confused intern into a senior who knows where everything lives.

## Why Default Claude Code Setup Breaks at Scale

The biggest misconception about Claude Code at scale: people assume it indexes your repo the way Sourcegraph or Cursor does, vectorizing every file into an embeddings store. **It does not.** As Anthropic describes it, Claude Code "navigates a codebase the way a software engineer would: it traverses the file system, reads files, uses grep to find exactly what it needs."

That design choice is a feature on small projects. No stale index, no embedding pipeline, no cache invalidation. But it has a clear breaking point. Once your repo crosses roughly 30,000 lines, the agent can no longer hold a useful mental map in its head. It grep-searches for symbols, returns thousands of false positives, reads dozens of files to triangulate, and torches context for every guess.

The fix is to do the curation work that an index would have done for you, but at the harness layer instead of the model layer. This is what [context engineering](/blog/context-engineering) looks like at scale: deliberate shaping of what enters the agent's window instead of dumping the whole tree at it. The eight strategies below are how you do it, ordered from "free wins everyone should do" to "patterns reserved for serious scale."

## Strategy 1: Lean and Layered CLAUDE.md

CLAUDE.md is your single most important harness component and the most commonly misused. Teams put everything into it. Tech stack. Coding conventions. Deployment commands. Folder explanations. Anti-patterns. By month three the file is 600 lines, loads on every session, and degrades performance because Claude has to wade through prose looking for the rule that applies.

The pattern that actually scales is layering. Keep the root CLAUDE.md under 100 lines and reserve it for cross-cutting context: the stack, the one-sentence purpose of each top-level folder, and conventions that apply everywhere. Then drop a focused CLAUDE.md into each major subdirectory. The frontend folder gets frontend rules. The payments service gets payment rules. The infrastructure folder gets deployment notes. The deeper philosophy of treating CLAUDE.md as your operating system rather than project documentation is covered in our [CLAUDE.md mastery guide](/blog/claude-md-mastery), and it is worth reading before you start the layering work.

Claude walks the directory tree from wherever you start the session, loading every CLAUDE.md it encounters on the way up. That walk-up behavior is what makes the layering work. Each session ends up with exactly the rules that apply to the code you are touching, and nothing else.

```
my-repo/
  CLAUDE.md                    # 80 lines: stack, top-level map, global conventions
  packages/
    api/
      CLAUDE.md                # 40 lines: API conventions, test command, gotchas
      handlers/
        ...
    web/
      CLAUDE.md                # 50 lines: React conventions, design tokens
      app/
        ...
  infrastructure/
    CLAUDE.md                  # 30 lines: deploy targets, dangerous commands
    terraform/
      ...
```

The full mechanics of this pattern (when to layer, when not to, how Claude decides what to load) live in our [subdirectory CLAUDE.md guide](/blog/subdirectory-claude-md). The point for this playbook is that one bloated file at the root is the symptom most teams need to fix before any other strategy will pay off.

A useful litmus test: if you grep your CLAUDE.md for "payments" and find rules that only matter inside `packages/payments/`, those rules belong in `packages/payments/CLAUDE.md`, not at the root. Move them. Watch session quality climb.

## Strategy 2: Initialize Claude in the Right Directory

This one is almost too simple to call a strategy, except that most teams miss it for months. When you start a Claude Code session, the directory you run it from defines its default scope. Run `claude` at the repo root and the agent treats the whole 200k-line tree as fair game. Run `claude` inside `packages/payments/` and the agent scopes its default reads to that subtree while still walking up to load every parent CLAUDE.md it finds.

Anthropic's position: "Claude works best when it's scoped to the part of the codebase that's actually relevant to the task."

The practical workflow looks like this:

```
# You know the work is in the API package
cd packages/api
claude
 
# Or for a specific service
cd services/billing
claude "audit the webhook retry logic"
```

When you initialize this way, three things happen. Claude's first grep does not span unrelated services. The implicit "this is my world" anchor is local, so the agent stops trying to refactor across module boundaries unprompted. And the context window stays cleaner because the agent is not pulling in cross-cutting file reads it does not need.

Root initialization still has its place. Architectural reviews, cross-package refactors, and global searches all benefit from full-tree scope. The point is to make the choice deliberately. If a task lives inside one slice of the repo, start the session there.

## Strategy 3: Codebase Maps That Earn Their Place in Context

For repos with dozens of top-level folders, no amount of CLAUDE.md layering helps Claude understand the geography unless it has been told what each folder is for. The pattern from the Anthropic playbook is "a lightweight markdown file at the repo root listing each top-level folder with a one-line description." That single file becomes Claude's wayfinding map.

Keep it surgical. One line per folder, with the line answering one question: what kind of code lives here? Avoid the temptation to expand it into a full architecture doc. A map is not a tour.

```
# Repo Map
 
- `apps/`: Deployable applications (web, mobile, admin)
- `packages/api/`: tRPC API, request handlers, validation schemas
- `packages/billing/`: Polar checkout integration, subscription lifecycle
- `packages/db/`: Drizzle schema, migrations, query helpers
- `packages/ui/`: Shared Radix component library
- `infrastructure/`: Terraform, Coolify configs, deploy scripts
- `scripts/`: One-off operational scripts
- `docs/`: Internal team documentation, ADRs
```

For monorepos with hundreds of top-level folders, layer the maps. Top-level map points at sections. Each section has its own map. The same walk-up logic that CLAUDE.md uses applies: Claude reaches the relevant map by traversing the tree.

The signal you need a map: Claude keeps asking "where is the auth code?" or grepping into the wrong package. The cost is fifteen minutes of writing. The savings compound across every future session.

## Strategy 4: Ignore Files and Permission Denies

Two thirds of the noise Claude wades through in most large repos is not source code at all. It is `node_modules` mirrors. Generated TypeScript from protobuf definitions. Build artifacts. Third-party vendored libraries. Snapshots. Coverage reports. Every grep that returns 8,000 hits is usually 7,000 hits in code Claude should never have read.

Two tools handle this. The first is the `.ignore` file at the repo root, which tells Claude to skip entire directory trees during its file system traversal. Treat it like an aggressive `.gitignore`, scoped to "things Claude should not even consider."

```
# .ignore
node_modules/
dist/
build/
.next/
coverage/
*.generated.ts
vendor/
public/static/
third-party/
```

The second tool is `permissions.deny` in `.claude/settings.json`. This is where you list commands and file paths Claude should refuse to touch. Anthropic's recommendation here is specific. "Committing `permissions.deny` rules in `.claude/settings.json` means the exclusions are version-controlled." This matters because permissions configured per developer drift. Permissions committed to the repo enforce themselves on every contributor, every CI run, every new hire who clones tomorrow.

```
{
  "permissions": {
    "deny": [
      "Edit(**/migrations/*.sql)",
      "Edit(**/generated/**)",
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Bash(terraform destroy:*)"
    ]
  }
}
```

For the full pattern (including the allow list complement and how to layer permissions per environment), see our permission management guide. For this playbook, the rule is simpler: anything you would not want a sleep-deprived engineer to touch at 2am, lock it down here and commit it.

## Strategy 5: Scoped Commands per Subdirectory

The fastest feedback loop on a monorepo is the test command for the one slice you are editing, not the test command for the whole tree. If a CLAUDE.md three folders up says `pnpm test` and that runs 4,000 tests across 12 packages, Claude will dutifully kick that off and then sit for nine minutes waiting for results before it can iterate.

The cleaner pattern: define the test and lint commands inside the local CLAUDE.md, scoped to that subdirectory.

```
# packages/api/CLAUDE.md
 
## Commands
 
- Tests: `pnpm --filter @repo/api test`
- Lint: `pnpm --filter @repo/api lint`
- Type-check: `pnpm --filter @repo/api typecheck`
- Dev: `pnpm --filter @repo/api dev`
 
## Conventions
 
- All routes registered through the trpc router in `src/router/`
- Validation schemas live alongside the route file as `<route>.schema.ts`
- New endpoints require a corresponding integration test in `__tests__/`
```

This works cleanly for repos where packages are independent. It breaks down in compiled-language monorepos with deep cross-directory dependencies, where building one package transparently rebuilds half the tree. For those, scope the commands you can scope, and add an explicit note in the CLAUDE.md telling Claude when a global build is unavoidable.

If your monorepo uses Turborepo, Nx, Bazel, or Pants, the scoped command usually looks like `<tool> run test --filter=<package>`. Codify the exact incantation. Otherwise Claude will reinvent it badly on each session.

## Strategy 6: LSP for Symbol-Level Search

This is the strategy most teams sleep on, and the one that pays off most at serious scale. At 50,000 lines, grep is fine. At 500,000 lines, grep stops being a tool and becomes a tax. "Find all references to handlePayment" returns 3,000 matches across string literals, log lines, comments, vendored dependencies, and three different `handlePayment` functions that have nothing to do with each other. Claude reads ten of them, gets confused, and burns 8,000 tokens doing it.

The Language Server Protocol is what every IDE uses for go-to-definition and find-references. It knows about scopes, types, imports, and inheritance, so it answers "where is the canonical `handlePayment` defined" with one definition and three real references. You expose LSP to Claude through an MCP server that wraps a language server binary (rust-analyzer, tsserver, gopls, clangd, whatever your stack uses) and surfaces `find_definition`, `find_references`, `find_implementations`. If MCP itself is unfamiliar territory, start with our MCP basics primer before tackling a custom LSP integration.

Anthropic's own deployment example: one enterprise customer deployed LSP org-wide before broad rollout of Claude Code specifically for C and C++ navigation reliability. Their codebase was too large for grep to remain useful, and their language too syntactically dense for pattern matching to disambiguate symbols. LSP was the unlock. The same logic applies to any monorepo past the half-million-LOC mark. We cover the build pattern in detail in our LSP MCP server guide, including the helpline reference implementation as a working starting point.

One detail teams miss: you need to tell Claude when to prefer LSP over grep. Add a one-line rule to your CLAUDE.md. "For symbol lookups, use the LSP MCP. For string literal or comment searches, use grep." Without that rule the agent will default to grep out of habit, even with the tools available.

## Strategy 7: Sub-agents for Exploration vs. Editing

Anthropic was direct about this one. The two activities you should never combine in a single Claude session are mapping a subsystem and editing it. Exploration eats context. Editing needs context. Run them together and you end up with an agent that has read 40 files to understand the architecture, then has no room left to think clearly about the change it needs to make.

The pattern is to spin up a read-only sub-agent for the exploration phase. That sub-agent has its own fresh context window, traverses the relevant code, and produces a focused report: findings, file paths, key functions, gotchas. The parent agent receives only the report (a few hundred tokens) and uses the freed-up context to do the actual edit. On a 200k-line repo, an exploration sub-agent might read 50 files and produce a 600-word summary. The parent agent reads the summary, reads three target files, and edits cleanly. The exploration tokens stay front-loaded in the sub-agent's disposable window, not eating your main session.

For the full taxonomy of when to spawn one sub-agent versus a team versus a parallel batch, see our [sub-agent patterns guide](/blog/sub-agent-best-practices) and the broader task distribution playbook. The cost of the discipline is real: sub-agents burn extra tokens. The payoff is that you stop watching your main session collapse halfway through a task because it ran out of room. On large codebases, that is the trade worth making every time.

## Strategy 8: Path-Scoped Skills

CLAUDE.md handles conventions. Skills handle workflows. The distinction matters and most teams collapse it. Conventions are things that are always true. Workflows are repeatable processes for specific task types. A naming rule belongs in CLAUDE.md. The seven-step API endpoint creation process belongs in a skill.

Skills load on demand based on the task description, not on every session. That alone makes them cheaper than CLAUDE.md for anything that does not apply universally. But for monorepos, the leverage gets bigger when you scope skills by file path. A "create API endpoint" skill scoped to `packages/api/**` will not load when you are editing a React component. A "design tokens" skill scoped to `packages/ui/**` will not load when you are touching the database schema.

```
---
name: create-api-endpoint
description: Scaffold a new tRPC endpoint with validation, tests, and docs
paths: packages/api/**
---
 
When creating a new API endpoint:
 
1. Add route to router in src/router/<domain>.ts
2. Create Zod schema in same directory as <route>.schema.ts
3. Write integration test in `__tests__/<route>.test.ts`
4. Update OpenAPI doc generation if endpoint is public
5. Run pnpm --filter @repo/api test to verify
```

The full mechanics of path scoping (glob patterns, discovery cost, when the predicate fires) live in our [path-scoped skills guide](/blog/path-scoped-skills). For this playbook, the takeaway is that path-scoped skills plus layered CLAUDE.md plus codebase maps give you per-directory conventions, per-directory workflows, and per-directory navigation. That is what makes the harness actually scale.

## When the Playbook Breaks Down

Honesty matters more than completeness. There are real situations where everything above hits a wall. Anthropic flagged the limit directly: "codebases with hundreds of thousands of folders and millions of files." Past that threshold, hierarchical CLAUDE.md loading becomes a session-startup cost in its own right.

Other failure modes worth naming:

- **Non-git version control**: The Anthropic playbook assumes git. Teams on Perforce, Mercurial, or Plastic SCM need custom hooks or have to accept that some defaults will not fire. Anthropic shipped native Perforce support only after one customer built a hook that intercepted file writes to enforce `p4 edit`. Expect that kind of workaround until first-party support catches up.
- **Game engines with binary assets**: Repos that are mostly `.fbx`, `.psd`, or `.uasset` throw off Claude's traversal heuristics. Use `.ignore` aggressively and map the binary directories so Claude knows not to read them.
- **Non-engineer contributors**: Heavy contribution from designers, PMs, or marketers makes Claude's assumptions about file structure wobble in those folders. Local CLAUDE.md files tuned to non-engineering conventions help.

None of these are dealbreakers. They are points where you should expect to do more setup work than the default playbook describes.

## Languages Worth Calling Out

One observation from the Anthropic deployment data deserves its own section because it surprises teams. Claude Code performs better than most teams expect on **C, C++, C#, Java, PHP**, particularly as of recent model releases. The conventional assumption is that AI coding tools work best on Python, TypeScript, and Go because those languages are over-represented in training data. That assumption has aged poorly for the languages above.

If your enterprise codebase is in C or C++ and you have been holding off on Claude Code because you assumed the experience would be worse, run a real benchmark before deciding. Pair LSP integration with the rest of the playbook and the gap closes faster than most teams predict. The C/C++ case is exactly where LSP shifts from "nice to have" to "non-negotiable," but the underlying model performance is no longer the bottleneck.

For Java enterprise codebases (typically the largest single-language monorepos in the wild), the same pattern holds. Combine subdirectory initialization with layered CLAUDE.md and an LSP MCP server, and Claude handles Spring Boot or Quarkus repos comfortably.

## The Configuration Review Cadence

Harnesses rot. The rules you wrote in February to constrain a less capable model may now constrain a more capable one unnecessarily, and you will be paying the cost on every session.

Anthropic's recommendation here is concrete: schedule a meaningful harness review "every three to six months," and also after every major model release. The example they cite is worth keeping in mind. "A CLAUDE.md rule that tells Claude to break every refactor into single-file changes" was a useful constraint on older models that struggled with cross-file edits. On a newer model that handles them well, that same rule becomes friction. You are forcing the agent to be slower and worse than it could be, because the rule no longer matches the model.

Some patterns to bake into the review:

- Read every CLAUDE.md file end to end. Ask "would I still write this rule today?"
- Audit `permissions.deny` for rules that protected against bugs the current model no longer has.
- Check every hook for behavior the platform now does natively. Anthropic shipped first-party Perforce support after one customer's hook became redundant.
- Look at the skills list and prune ones that have not loaded in 90 days.

If you want the review itself to be partially automated, the pattern is a stop hook that proposes CLAUDE.md updates while session context is still fresh. We cover the full setup in our [self-improving CLAUDE.md guide](/blog/self-improving-claude-md), and the hook is one of the highest-leverage additions you can make to a large-codebase harness because it keeps the rules from drifting between scheduled reviews.

## Pre-Built vs. Roll-Your-Own

Every strategy in this playbook is achievable on your own. They are documented, open patterns, none of which require anything more than time and discipline. Teams that have invested the months tend to end up with a harness that is between 70 and 90 percent the same regardless of stack, because the underlying problem is the same.

The case for rolling your own: full control, customization to your stack, and a learning curve that pays off in fluency. The case against: months of iteration to get past the obvious mistakes, evolving conventions to propagate, and fragile coordination across team members who configure things slightly differently.

## The Pattern Worth Internalizing

Every team that succeeds with Claude Code at scale has invested in their harness. There are no exceptions. The teams that struggle are not running into a model limitation. They are running an unconfigured agent against a repo that demands configuration, and blaming the agent.

A year ago, "AI coding tool" meant something you opened, prompted, and read suggestions from. Today it means an agent with file system access, command execution rights, and a context window that needs to be curated like an engineer's working memory. The model is one ingredient. The harness around it is the rest. CLAUDE.md tells Claude the rules. Subdirectory initialization tells it the scope. Codebase maps tell it the geography. Ignore files and permissions tell it the boundaries. Scoped commands tell it the feedback loop. LSP tells it about symbols. Sub-agents give it more context window. Path-scoped skills give it the workflows. None of these are revolutionary on their own. Combined, they are the difference between an agent that works on toy projects and an agent that ships features in your monorepo.

If you want the framework that ties all of this together (the harness as a unified concept rather than eight separate tactics), read our [AI layer pillar](/blog/the-ai-layer). If you want to understand the [agent manager role](/blog/agent-manager-role) that owns this stack inside an org, we have written about that too. And once your team has a harness worth standardizing on, our plugin distribution guide covers how to ship it as a single installable bundle so every engineer starts from the same baseline instead of evolving private variants.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
