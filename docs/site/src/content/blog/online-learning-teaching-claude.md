# Online Learning: Teaching Claude Your Patterns

Every team has unique patterns — internal APIs, deployment processes, coding conventions that aren't in any documentation. Claude doesn't know these. Online learning captures them automatically so Claude gets smarter with every session.

## The Problem

You explain the same things repeatedly:

- "Our API uses snake_case, not camelCase"
- "Always use the `ServiceBase` class for new services"
- "Deploy commands must include the `--region` flag"

Rules help, but they're static. You have to anticipate what Claude needs to know. Online learning captures knowledge dynamically — from the work itself.

## How It Works

When a session involves non-obvious problem-solving, Pilot's `/learn` command extracts the knowledge into a reusable skill:

1. **Detection** — Pilot recognizes when a session produced reusable knowledge (workarounds, debugging solutions, multi-step workflows)
2. **Extraction** — The knowledge is captured with context: what the problem was, what the solution was, and when to apply it
3. **Storage** — Skills are saved as structured files that Claude loads in future sessions
4. **Application** — When a similar situation arises, Claude already knows the solution

## What Gets Captured

| Trigger | Example |
|---------|---------|
| Non-obvious debugging | "The 403 error was actually a CORS issue with the CDN, not an auth problem" |
| Workarounds | "The library's `parse()` function silently drops null values — use `safeParse()` instead" |
| Multi-step workflows | "Deploying to staging requires: build → test → push → wait for CI → promote" |
| Tool integrations | "To query the internal API, use header X-Service-Token, not Authorization" |

## Skills vs Rules

| Aspect | Rules | Skills |
|--------|-------|--------|
| Created by | You, manually | Automatically from sessions |
| Content | Instructions and constraints | Procedures and knowledge |
| Scope | Always active | Activated when relevant |
| Updates | Manual edits | New versions from new learnings |

Rules tell Claude what to do. Skills teach Claude how to do things it's learned from experience.

## Team Sharing

Skills can be shared across your team using Pilot's vault system. When one developer discovers a workaround, the whole team benefits:

```bash
# Share a learned skill with the team
sx add .claude/skills/deploy-staging --type skill --name "deploy-staging"

# Team members install shared skills
sx install --repair
```

## The Flywheel

The more you use Claude with Pilot, the more knowledge it accumulates:

1. Session produces non-obvious solution
2. `/learn` captures it as a skill
3. Future sessions apply the skill automatically
4. New sessions build on previous knowledge

After a few weeks, Claude knows your project's quirks, your team's conventions, and your infrastructure's gotchas — without anyone maintaining a documentation wiki.
