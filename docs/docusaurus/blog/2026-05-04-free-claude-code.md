---
title: "Free Claude Code: Run Claude Code on Any Model"
description: "Free Claude Code routes the Claude Code API to NIM, OpenRouter, DeepSeek, or local models. Setup walkthrough plus the harness for cheap models."
slug: free-claude-code
date: 2026-05-04
authors:
  - max-ritter
tags:
  - tools
  - customization
---

Free Claude Code routes the Claude Code API to NIM, OpenRouter, DeepSeek, or local models. Setup walkthrough plus the harness for cheap models.

<!-- truncate -->

A Python proxy called **Free Claude Code** went from zero to 20,900 stars in fourteen weeks. It does one thing: intercepts Claude Code's Anthropic Messages API calls and forwards them to NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp, or Ollama. You keep the Claude Code interface, the slash commands, the agent SDK, and the whole Claude Code workflow. You swap out the brain.

The repo's surge is not a coincidence. After Anthropic's April 4, 2026 policy change blocked Pro and Max subscribers from running their subscriptions through most third-party agent frameworks, two camps formed. One paid up. The other started looking for ways to keep building without the metered API or the quota throttling. Free Claude Code is the path the second camp picked.

## What Free Claude Code Actually Does

Claude Code speaks the Anthropic Messages API protocol. So does any proxy that pretends to be Anthropic. Free Claude Code is a FastAPI server that listens on `localhost:8082` and exposes the routes Claude Code expects (`/v1/messages`, `/v1/messages/count_tokens`, `/v1/models`). When a request hits the proxy, it picks an upstream provider based on the model tier (Opus, Sonnet, Haiku, or fallback) and translates the call.

```
Claude Code CLI / IDE
        │
        │  Anthropic Messages API
        ▼
Free Claude Code proxy  (localhost:8082)
        │
        │  provider-specific adapter
        ▼
NIM ▪ OpenRouter ▪ DeepSeek ▪ LM Studio ▪ llama.cpp ▪ Ollama
```

The translation layer matters. NVIDIA NIM speaks OpenAI chat-completions, so the proxy converts streaming chunks back into Anthropic SSE events. OpenRouter, DeepSeek, LM Studio, llama.cpp, and Ollama can all speak Anthropic Messages directly, so the proxy mostly normalizes thinking blocks, tool calls, and token-usage metadata into the shape Claude Code expects.

What you get out of the deal:

- Native Claude Code `/model` picker support through the proxy's `/v1/models` endpoint
- Streaming, tool use, and reasoning block handling preserved
- Per-tier routing (send Opus traffic to Kimi K2, Sonnet to DeepSeek, Haiku to a local GLM)
- Optional Discord and Telegram bot wrappers for remote sessions
- Optional voice-note transcription via local Whisper or NVIDIA NIM

The whole project is MIT-licensed Python 3.14 with FastAPI under the hood and `uv` for dependency management. The codebase is small enough to read in an afternoon, which is a meaningful answer to the "would I trust this with my API keys" question.

## Why the Surge Right Now

Three pressures stacked on top of each other.

**The April 4 policy shift.** Anthropic's terms now prohibit using Pro and Max subscriptions through most third-party agent frameworks. Subscribers who built tooling around routing tools like cc-mirror or vibeproxy suddenly had to switch back to metered API billing or stop using their wrappers. Free Claude Code skips the Anthropic bill entirely.

**The cost ceiling.** Claude Code is the strongest agent on the market, and Opus 4.7 charges accordingly. A real session with multiple subagents, large file reads, and heavy thinking can chew through tokens fast enough that a $200/month Max plan still feels constraining. Routing the same workflow through DeepSeek V4 or a free NVIDIA NIM tier replaces dollars per session with cents per session.

**Quality fluctuation complaints.** Anthropic's load-balancing has been a recurring discussion thread on Reddit and X for months. Some users want determinism more than they want the best model. A self-hosted proxy gives them direct provider control.

The repo doesn't claim quality parity with Opus. Nobody serious does. The pitch is closer to: pay 2 to 5 percent of the cost, get 70 to 85 percent of the result, and decide on a per-task basis whether that math works for you.

## The Provider Lineup

Each provider has a different cost-quality-control profile.

| Provider | Cost | Best For | Notes |
| --- | --- | --- | --- |
| **NVIDIA NIM** | Free tier or paid | Trying it without a credit card | Z.AI GLM-4.7 is currently free on the NIM tier |
| **OpenRouter** | $0.10 to $1.50 / M tokens | Drop-in plug-and-play, lots of model choice | DeepSeek V4 Flash, Kimi K2, GLM, Llama variants |
| **DeepSeek (direct)** | $0.14 / M input typical | Cheapest hosted with native Anthropic API | Uses DeepSeek's Anthropic-compatible endpoint |
| **LM Studio** | Hardware cost only | Desktop GUI for local models | Tool-use support depends on the loaded model |
| **llama.cpp** | Hardware cost only | Maximum control, embedded use cases | Needs `--ctx-size` tuning for Claude Code prompts |
| **Ollama** | Hardware cost only | Easiest local setup | Slower without a discrete GPU |

The killer feature is per-tier routing. Drop this into your `.env` and Claude Code's internal model decisions get distributed across providers automatically:

```
NVIDIA_NIM_API_KEY="nvapi-your-key"
OPENROUTER_API_KEY="sk-or-your-key"
 
MODEL_OPUS="nvidia_nim/moonshotai/kimi-k2.5"
MODEL_SONNET="open_router/deepseek/deepseek-chat:free"
MODEL_HAIKU="lmstudio/unsloth/GLM-4.7-Flash-GGUF"
MODEL="nvidia_nim/z-ai/glm4.7"
```

Heavy reasoning gets a strong frontier-adjacent model. Sub-tasks get a cheap or free one. Trivial Haiku-tier probes hit your local box and never touch the network. The same per-tier pattern is what Anthropic's Agent Teams architecture uses internally, and it's the same logic that drives intelligent agent orchestration in serious Claude Code setups.

## Setup in Five Steps

The full README has every flag. This is the path that gets you running.

**1. Install prerequisites.** You need Claude Code itself (install in 30 seconds) plus `uv` and Python 3.14.

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv python install 3.14
```

PowerShell:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv self update
uv python install 3.14
```

**2. Clone and configure.**

```
git clone https://github.com/Alishahryar1/free-claude-code.git
cd free-claude-code
cp .env.example .env
```

**3. Pick a provider and edit `.env`.** The simplest free path is NVIDIA NIM with GLM-4.7. Get a key at [build.nvidia.com](https://build.nvidia.com/settings/api-keys), then:

```
NVIDIA_NIM_API_KEY="nvapi-your-key"
MODEL="nvidia_nim/z-ai/glm4.7"
ANTHROPIC_AUTH_TOKEN="freecc"
```

The `ANTHROPIC_AUTH_TOKEN` value is whatever string you want. Claude Code will send it back to your local proxy on every request, which is how the proxy distinguishes its own traffic from anything else.

**4. Start the proxy.**

```
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

**5. Run Claude Code with the redirect environment.** Open a second terminal and point Claude Code at your proxy. The base URL is the proxy root, not `/v1`.

```
ANTHROPIC_AUTH_TOKEN="freecc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

PowerShell:

```
$env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; claude
```

That's it. Run `/model` and the picker should show the provider models the proxy discovered. Both VS Code and JetBrains ACP support the same redirect via their environment-variable settings, so the proxy works across every Claude Code surface.

## Where Free Claude Code Breaks Down

This is the section you don't see in tutorial videos.

**Tool-use reliability drops on cheaper models.** Claude Code leans on tool calls for almost everything: file reads, edits, bash, grep. Models with shaky tool-call formatting will return malformed deltas, omit tool names, or emit tool calls as plain text inside content. The proxy can't fix what the upstream model never produced. DeepSeek and Kimi K2 generally hold up. Smaller distilled models do not.

**Context windows shrink.** Opus runs comfortably with 200K tokens, and the [1M context window](/blog/1m-context-ga) is now generally available for Sonnet. Most cheap or free providers cap at 32K to 128K. Long sessions will hit ceilings and need aggressive context management sooner than you're used to.

**Quality is genuinely lower.** GLM-4.7 is impressive for a free model. It is not Opus 4.7. Multi-step refactors, subtle bug hunts, and architectural decisions degrade noticeably. The "80 to 90 percent of Opus quality" pitch you hear in YouTube videos is best-case for narrow tasks.

**Local models are slow.** Running Gemma or Llama 3.1 on a MacBook is a real option for trivial work. It is not a real option for a workflow that fires twenty tool calls per minute. A discrete GPU helps. A consumer laptop tries its best.

**Streaming weirdness.** The proxy normalizes most provider quirks, but a small subset of upstream models still trip Claude Code with malformed `input_tokens` or `$.speed` errors. The README documents the fixes (update to latest commit, drop the `/v1` suffix, check upstream HTTP status), and most fail loudly enough to debug in minutes.

The honest framing: cheaper models work great for execution-heavy tasks (refactor this file, write this CRUD endpoint, port this snippet), and they degrade fast on planning-heavy or judgment-heavy work.

## The Harness Multiplier

Here is the part everyone misses.

When you swap Opus for a weaker model, you lose intelligence per token. You can claw it back by giving the model a better harness. A frontier model can paper over a sloppy prompt and a missing system message. A cheap model cannot. Cheap models perform dramatically better when they're given:

- A clear role definition with explicit constraints
- Pre-structured planning before execution
- Subagent decomposition so each call has a narrow scope
- Hooks that catch tool misuse before it propagates
- Skills that load only the context relevant to the current step

This is not a theoretical claim. Anthropic's own published numbers on Claude Code Agent Teams show 15 percent quality lift from pairing a stronger orchestrator with weaker subagent workers, versus a single model doing everything. The same multiplier applies in reverse: pairing a weaker model with a strong harness recovers a meaningful chunk of the gap.

That includes every backend Free Claude Code routes to.

The video tutorials that demonstrate Free Claude Code by asking DeepSeek to "build me a habit tracker" are showing you the floor, not the ceiling. The same DeepSeek call inside a kit that decomposes the task into a plan, dispatches a frontend specialist for the UI, a backend engineer for the data layer, and a quality engineer for validation will produce dramatically better output. Same model. Same cost. Different harness.

## When Not to Use Free Claude Code

A short list.

- **You're shipping production code under deadline.** Use the real model. Save the experimentation for side projects.
- **Your work is judgment-heavy.** Architecture reviews, security audits, and ambiguous bug hunts need the strongest model you can get.
- **You don't want operational complexity.** A proxy is one more thing that can break. If you don't enjoy debugging FastAPI tracebacks, the $20 Pro plan is a great deal.
- **Your tasks are tiny and rare.** Pay-as-you-go API access is already cheap for light usage. The proxy economics only matter at volume.

The right mental model: Free Claude Code is a high-leverage tool for high-volume, lower-stakes work. It is not a Claude Code replacement for production engineering.

## The Verdict

Free Claude Code is the most credible "use Claude Code without paying Anthropic" project that exists in May 2026. It is well-built, well-tested, MIT-licensed, and small enough to audit. The provider lineup covers the full range from free hosted (NIM) to paid plug-and-play (OpenRouter) to fully local (Ollama, llama.cpp, LM Studio). Per-tier routing is genuinely innovative.

It is also not a free replacement for Opus. The model gap is real, the tool-use reliability varies, and the operational overhead is non-trivial. Use it for high-volume execution work, prototyping, learning, side projects, or any workflow where the cost of an Anthropic API call started to feel like friction. Pair it with a strong agent harness if you want the cheap model to actually behave.

The bigger story is that Claude Code's Anthropic Messages API has become a de facto standard. Once a project's interface is portable, the model behind it stops being the lock-in. That's healthy for the ecosystem, healthy for users, and an explicit reason that frameworks built on Claude Code itself, not on a specific model, age well.

## Next Steps

- Compare the customization landscape: tweakcc, cc-mirror, vibeproxy and more covers the broader provider-routing scene
- Pick the right model when you do go back to Anthropic: read model selection for Claude Code
- Tighten your context strategy for smaller windows: [context engineering basics](/blog/context-engineering)
- Get more out of any model with skills: [Claude Code skills guide](/blog/claude-skills-guide)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** is a single install on top of Claude Code that adds `/spec`, `/fix`, `/prd`, project-aware rules, persistent memory across sessions, and a configured hook pipeline. Open source, MIT-licensed.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
