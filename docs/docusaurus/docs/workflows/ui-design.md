---
sidebar_position: 6
title: UI Design Expertise
description: Conditional Claude Design-style product UI expertise for Claude Code and Codex, split across one path-gated rule and three progressively disclosed skills.
---

# UI Design Expertise

Pilot makes Claude Code and Codex strong product-design collaborators without putting a design system prompt in every session.

The integration separates stable visual judgment from task procedures:

| Layer | Loads when | Owns |
|---|---|---|
| `design-quality.md` rule | Matching UI component, markup, or style files become relevant | Product context, content discipline, hierarchy, system consistency, states, responsive/themes, contextual anti-template guidance |
| `ui-design` skill | A request creates or redesigns a product UI | Direction, wireframes, substantive variations, repository-native prototypes |
| `design-system` skill | A request extracts or normalizes visual structure | Tokens, themes, component inventories, variants, states, provenance |
| `ui-design-review` skill | A request audits or polishes a product UI | Accessibility, brand fidelity, hierarchy/rhythm, interaction states, runtime proof, final verdict |
| `claude-design` skill | The user names Claude Design, supplies a project URL, or asks Codex to interact with the service | On-demand project access, safe synchronization, tool discovery, and local implementation handoff |

Each skill has a compact router. Detailed reference material loads only for the selected lane, so an accessibility question does not also load prototype and token-extraction instructions.

## Use it

The skills activate automatically when their descriptions match, or explicitly:

```text
# Claude Code
/ui-design redesign the account settings flow
/design-system extract the current tokens and component contracts
/ui-design-review audit the finished UI before release
/claude-design read this Claude Design project without changing it

# Codex
$ui-design redesign the account settings flow
$design-system extract the current tokens and component contracts
$ui-design-review audit the finished UI before release
$claude-design read this Claude Design project without changing it
```

Near-misses remain direct work: a logic-only fix in TSX does not become a redesign, “system design” for software architecture does not invoke the visual design-system skill, and generic code review does not invoke UI design review.

## Context behavior

### Claude Code

- The full design rule loads only for its YAML `paths`.
- Skill descriptions participate in discovery; the body loads only on activation.
- The compact body routes to the minimum required files under `references/`.

### Codex

- Pilot writes the design rule to `~/.codex/rules/design-quality.md`; global `AGENTS.md` carries only the small path/index row telling Codex when to read it.
- The adapted skills install under `~/.agents/skills/` with generated `agents/openai.yaml` metadata.
- The same router/reference split provides progressive disclosure.

The deterministic asset validator checks positive and competing negative prompts so the new implicit skills do not collide with Pilot's existing workflow catalog.

## Claude Design on current Codex

Claude Design's remote MCP endpoint currently advertises an authorization-server issuer that native Codex rejects before browser login. Pilot does not patch Codex or keep a second token store. On macOS it reuses the scoped `designOauth` credential that Claude Code writes to Keychain after `/design-login`, then speaks MCP directly from the `pilot` process.

The `$claude-design` skill routes Codex through a progressive CLI:

```bash
pilot design status --json
pilot design tools --json
pilot design describe <tool-name> --json
pilot design call <tool-name> --args '<json-object>' --json
pilot design files <project-id> --path '<dir>' --depth -1 --json
pilot design pull <project-id> <remote-path> --output .pilot/design-scratch/<remote-path> --json
```

`tools` returns compact summaries; `describe` loads one live schema. The full remote catalog therefore never becomes standing Codex context. Claude Code continues to prefer its native `claude_design` tools and uses the same skill for safety and synchronization procedure.

For mirror or handoff workflows, `pilot design pull` writes a complete remote text file to a worktree-local scratch path without echoing its body. `pilot design push` reads worktree-local file bytes inside Pilot, requires a current etag per path, creates an exact-path plan internally, and refuses a changed base etag. Both helpers reject symlink components and paths outside the enclosing worktree (or current directory outside Git). `--allow-external-local-path <local-path>` is a separate, path-valued gate for one exact external operand the user explicitly authorized; repeat it per operand and never use it as a routine workaround. Files and signed tokens stay out of model context, and reused plan tokens enter only through `--plan-token -` on stdin. The inline helper is capped at 256 KiB; larger content uses Claude Design's server-side copy or native host transfer path.

The bridge never prints or stores the credential. Calls to tools not marked `readOnlyHint: true` fail unless an explicit gate is present. Mutations require `--allow-write`; the non-mutating `render_preview` uses a narrower `--allow-guarded` exception because its server annotation is conservative. A request to inspect, implement locally, download, or review is not remote-write authority. Authorized writes also use Claude Design's own `finalize_plan`, exact paths, etags, read-back, and durable preview URL.

If `pilot design status` reports a missing or expired credential, open Claude Code, run `/design-login`, and retry. Never copy a token into chat, configuration, or an environment variable.

## Design principles

- Existing product context controls visual decisions unless the user requests a change.
- Real components, tokens, content, assets, and interaction states replace approximate mockups and invented filler.
- Visual heuristics are contextual. An established font, gradient, card, or callout pattern is not rejected because it resembles a common AI output.
- Accessibility uses WCAG 2.2 facts with conformance levels kept distinct from platform recommendations.
- Review requests are report-only; editing begins only when the user asks to fix, polish, redesign, or implement.
- Runtime proof requires driving the interface and observing the resulting state. Source inspection and tests remain supporting evidence.

## Scope

This release targets product UI in web/app repositories: creation, visual exploration, interactive prototypes, visual-system extraction, review, and on-demand access to real Claude Design projects. It intentionally does not import the upstream HTML-deck workflow or its host-specific live-tweak protocol.

The design material is adapted from [Trystan Sarrade's claude-design-system-prompt](https://github.com/Trystan-SA/claude-design-system-prompt) at reviewed commit `3c3ddb07d7aa3fef051d83608596470c95cfd8fe`. Every installed skill carries the upstream MIT notice.
