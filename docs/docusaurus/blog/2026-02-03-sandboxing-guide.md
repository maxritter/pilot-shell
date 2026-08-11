---
title: "Claude Code Sandbox Guide: Setup, Config & Security (2026)"
description: "Set up Claude Code sandboxing for filesystem and network isolation. Covers macOS Seatbelt, Linux bubblewrap, and security config."
slug: sandboxing-guide
date: 2026-02-03
authors:
  - max-ritter
tags:
  - guide
---

Set up Claude Code sandboxing for filesystem and network isolation. Covers macOS Seatbelt, Linux bubblewrap, and security config.

<!-- truncate -->

Running an AI agent with unrestricted access to your filesystem and network is a liability you can't afford to ignore. Every `npm install` pulls untrusted code. Every build script executes with your user permissions. Every prompt injection attempt gets the same access you do. Without boundaries, a single compromised dependency can read your SSH keys, exfiltrate environment variables, or backdoor your shell configuration.

Claude Code's sandboxing feature solves this with OS-level enforcement that restricts filesystem and network access at the kernel level, not through trust or prompt engineering.

**Quick setup**: Enable sandboxing right now with a single command:

```
> /sandbox
```

This opens a menu to choose your sandbox mode. On macOS, it works immediately. On Linux or WSL2, you'll need `bubblewrap` and `socat` installed first (instructions below).

## Why Permission Prompts Alone Aren't Enough

If you've used Claude Code for any real project, you know the drill. Claude needs to run a command. Click approve. Write a file. Click approve. Run tests. Click approve. Thirty approvals later, you're rubber-stamping everything without reading it.

This is approval fatigue, and it's a security problem disguised as a safety feature.

The more prompts you approve, the less attention you pay to each one. Research in security UX consistently shows that frequent permission dialogs train users to click through them reflexively. You end up with the worst of both worlds: interrupted flow AND reduced security.

Sandboxing flips this model entirely. Instead of asking "can I do this specific thing?" for every action, you define boundaries upfront: "here's where you can read, here's where you can write, here's what you can access on the network." Everything inside those boundaries runs freely. Everything outside gets blocked at the OS level, not at the prompt level.

The result: fewer interruptions, stronger security, and an agent that can actually work autonomously within safe limits. This is the same defense-in-depth approach that production systems use. You don't rely on a single checkpoint. You layer restrictions so that even if one fails, the others hold.

## How Claude Code Sandboxing Works

The sandbox operates through two isolation mechanisms that work together. Both are critical. Removing either one creates exploitable gaps.

### Filesystem Isolation

The sandboxed bash tool restricts file access to specific directories:

- **Write access** defaults to the current working directory and its subdirectories
- **Read access** covers the entire system, except directories you've explicitly denied
- **Blocked modifications** prevent changes outside the working directory without explicit permission
- **Custom paths** let you expand or restrict access through settings

This means Claude can read your project files and modify code within your repo, but can't touch `~/.bashrc`, `/usr/local/bin`, or your SSH keys. Even if a malicious npm package tries to write outside the sandbox boundaries, the OS blocks it.

### Network Isolation

Network access runs through a proxy server outside the sandbox:

- **Domain restrictions** limit which hosts processes can reach
- **New domain requests** trigger permission prompts so you see exactly what's being contacted
- **All child processes** inherit the same restrictions, so a subprocess spawned by a build script can't circumvent the rules
- **Custom proxy support** lets enterprises route traffic through their own inspection infrastructure

Without network isolation, filesystem protection alone isn't enough. A compromised agent could still exfiltrate your source code to an attacker-controlled server. Without filesystem isolation, network restrictions alone aren't enough either, because a compromised agent could modify system binaries to gain network access through another path.

Both layers must work together. This is a core principle of the design.

### OS-Level Enforcement

The sandbox doesn't rely on application-level checks that a clever exploit could bypass. It uses kernel-level security primitives:

- **macOS**: Uses [Seatbelt](https://reverse.put.as/wp-content/uploads/2011/09/Apple-Sandbox-Guide-v1.0.pdf), the same sandbox framework that isolates App Store applications
- **Linux**: Uses [bubblewrap](https://github.com/containers/bubblewrap) (`bwrap`), a lightweight unprivileged sandboxing tool used by Flatpak
- **WSL2**: Uses bubblewrap, same as native Linux

WSL1 is not supported because bubblewrap requires kernel features (user namespaces, mount namespaces) only available in WSL2. Native Windows support is planned but not yet available.

Every child process spawned by a sandboxed command inherits the same restrictions. Running `npm install` inside the sandbox means every postinstall script also runs inside the sandbox.

## Prerequisites and Installation

### macOS

Nothing to install. Sandboxing works out of the box using the built-in Seatbelt framework. Just run `/sandbox` and pick your mode.

### Linux and WSL2

Install bubblewrap for filesystem isolation and socat for network proxy communication:

**Ubuntu/Debian:**

```
sudo apt-get install bubblewrap socat
```

**Fedora:**

```
sudo dnf install bubblewrap socat
```

After installing, run `/sandbox` inside Claude Code. If dependencies are missing, the menu displays platform-specific installation instructions.

## Sandbox Modes: Auto-Allow vs Regular Permissions

Claude Code offers two sandbox modes. Both enforce the same filesystem and network restrictions. The difference is whether sandboxed commands need manual approval.

### Auto-Allow Mode

Bash commands attempt to run inside the sandbox and are automatically allowed without prompting. If a command needs access to a non-allowed network host, it falls back to the regular permission flow. Any explicit ask/deny rules you've already configured still apply.

This is the mode most developers want. It gives Claude maximum autonomy within the sandbox boundaries while still prompting for anything outside them.

One important detail: auto-allow works independently of your permission mode setting. Even if you haven't enabled "accept edits" mode, sandboxed bash commands run automatically when auto-allow is on. File edits through Claude's Edit tool still follow your normal permission settings, but bash commands within sandbox boundaries execute freely.

### Regular Permissions Mode

All bash commands go through the standard permission flow, even when sandboxed. You still get filesystem and network isolation, but every command requires explicit approval.

Use this when you want the security benefits of sandboxing without giving up manual control over command execution. Good for high-security environments or when you're first testing your sandbox configuration.

## Configuring Your Sandbox

Customize sandbox behavior through your `settings.json` file. Here's a practical configuration:

```
{
  "sandbox": {
    "mode": "auto-allow",
    "allowedDomains": ["registry.npmjs.org", "api.github.com", "pypi.org"],
    "network": {
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}
```

### Key Settings

**`mode`**: Set to `"auto-allow"` or `"regular"` to control whether sandboxed commands auto-execute.

**`allowedDomains`**: Domains that bash commands can reach without prompting. As you work, new domain requests trigger prompts, and granting permission adds them here for future sessions.

**`allowUnixSockets`**: Controls Unix socket access. Be careful: allowing `/var/run/docker.sock` effectively grants host system access through the Docker socket, bypassing sandbox isolation.

**`allowUnsandboxedCommands`**: Defaults to `true`. When a command fails due to sandbox restrictions, Claude can retry it outside the sandbox (with your permission). Set to `false` to disable this escape hatch entirely.

**`excludedCommands`**: Commands that should always run outside the sandbox. Useful for tools incompatible with sandboxing, like `docker`.

**`enableWeakerNestedSandbox`**: A Linux-only option for unprivileged Docker environments. This weakens security considerably and should only be used when the Docker container itself provides additional isolation.

### Configuration Locations

Settings follow a priority hierarchy. See configuration basics for the full breakdown:

| Location | Scope | Priority |
| --- | --- | --- |
| Managed policy | Enterprise | Highest |
| `.claude/settings.json` | Project (shared) | High |
| `.claude/settings.local.json` | Project (personal) | Medium |
| `~/.claude/settings.json` | All projects | Lowest |

## How Sandboxing Complements Permissions

Sandboxing and the permission system are separate security layers that reinforce each other:

**Permissions** control which tools Claude Code can use. They're evaluated before any tool runs and apply to all tools: Bash, Read, Edit, WebFetch, MCP tools, and others.

**Sandboxing** provides OS-level enforcement restricting what Bash commands can actually access at the filesystem and network level. It applies only to Bash commands and their child processes.

Think of it as defense-in-depth. Permissions are the first gate: "Should this tool run at all?" Sandboxing is the second gate: "If it runs, what can it touch?"

You can configure restrictions through both systems:

- Use `Read` and `Edit` deny rules to block file access across all tools
- Use `WebFetch` allow/deny rules to control which domains non-Bash tools can reach
- Use sandbox `allowedDomains` to control which domains Bash commands specifically can reach

For the strongest security posture, use both. [Hooks](/blog/hooks-guide) add a third layer by letting you inspect and block specific operations programmatically.

## Security Benefits

### Prompt Injection Protection

Prompt injection is the most significant security risk with AI agents. An attacker embeds instructions in a file, README, or web page that Claude reads, tricking it into executing malicious commands.

With sandboxing enabled, even a successful prompt injection hits hard limits:

**Filesystem protection:**

- Cannot modify critical config files like `~/.bashrc` or `~/.zshrc`
- Cannot alter system binaries in `/bin/` or `/usr/local/bin/`
- Cannot read files denied in your permission settings

**Network protection:**

- Cannot exfiltrate data to attacker-controlled servers
- Cannot download malicious scripts from unauthorized domains
- Cannot make API calls to unapproved services
- Cannot contact any domain not explicitly allowed

**Monitoring:**

- All access attempts outside the sandbox are blocked at the OS level
- You receive immediate notifications when boundaries are tested
- You can deny, allow once, or permanently update your configuration

### Reduced Attack Surface

Beyond prompt injection, sandboxing limits damage from:

- **Malicious dependencies**: npm packages, pip packages, or other libraries with harmful postinstall scripts
- **Compromised build scripts**: Tools with security vulnerabilities that execute during builds
- **Social engineering**: Attacks that trick users into running dangerous commands
- **Supply chain attacks**: Compromised upstream packages that inject code during installation

## Security Limitations You Should Know

No sandbox is perfect. Understanding the limitations helps you make informed decisions about your threat model.

### Domain Fronting

The network filter restricts which domains processes can connect to, but it doesn't deep-inspect traffic. Domain fronting, where traffic appears to go to one domain but actually reaches another, can potentially bypass filtering. Be cautious about allowing broad domains like `github.com` that could be used for data exfiltration.

### Unix Socket Escalation

The `allowUnixSockets` setting can inadvertently grant powerful access. Allowing `/var/run/docker.sock` gives the sandboxed process full Docker API access, which effectively means host system access. Only allow Unix sockets you fully understand and trust.

### Filesystem Permission Escalation

Overly broad write permissions create escalation paths. Allowing writes to directories containing executables in `$PATH`, system configuration directories, or user shell config files can lead to code execution in a different security context. Keep write permissions as narrow as possible.

### Linux Weaker Nested Sandbox

The `enableWeakerNestedSandbox` option exists for unprivileged Docker environments where full bubblewrap isolation isn't available. This substantially weakens security. Only use it when the Docker container itself enforces additional isolation.

## Practical Tips and Compatibility

### Docker Incompatibility

Docker commands can't run inside the sandbox because they need direct access to the Docker daemon. Add `docker` to your `excludedCommands` to force it outside the sandbox:

```
{
  "sandbox": {
    "excludedCommands": ["docker"]
  }
}
```

Docker commands will then go through the normal permission flow instead.

### Watchman Incompatibility

Facebook's `watchman` file watching service is incompatible with sandboxed execution. If you're running Jest with watchman, use the `--no-watchman` flag:

```
jest --no-watchman
```

### The Escape Hatch

When a command fails due to sandbox restrictions, Claude can analyze the failure and retry with `dangerouslyDisableSandbox`. This runs the command outside the sandbox but still requires your explicit permission through the normal approval flow.

If you want to eliminate this escape entirely:

```
{
  "sandbox": {
    "allowUnsandboxedCommands": false
  }
}
```

With this set, sandbox failures are final. No retries outside the sandbox. This is the most restrictive option and the safest choice for high-security environments.

## Custom Proxy Configuration for Enterprises

Organizations with advanced network security requirements can route sandbox traffic through a custom proxy for traffic inspection, logging, and integration with existing security infrastructure:

```
{
  "sandbox": {
    "network": {
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}
```

This lets you:

- Decrypt and inspect HTTPS traffic
- Apply custom filtering rules beyond domain-level blocking
- Log all network requests for audit trails
- Integrate with existing SIEM and security infrastructure
- Enforce enterprise-wide security policies through managed settings

## Open Source Sandbox Runtime

The sandbox runtime is available as an open source npm package. You can use it in your own agent projects, not just Claude Code:

```
npx @anthropic-ai/sandbox-runtime <command-to-sandbox>
```

The source code is at [github.com/anthropic-experimental/sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime). If you're building tools that execute untrusted code or run agent-generated commands, this gives you the same isolation primitives that Claude Code uses internally.

## Setting Up Your First Sandbox

Here's the practical path to get started:

1. **Install prerequisites** (Linux/WSL2 only): `sudo apt-get install bubblewrap socat`
2. **Run `/sandbox`** inside Claude Code to open the mode selection menu
3. **Choose auto-allow mode** for the best balance of security and productivity
4. **Work normally** and approve domain requests as they appear
5. **Review your configuration** after a few sessions to verify allowed domains make sense
6. **Tighten restrictions** by removing domains you don't actively need

Start restrictive and expand as needed. It's always easier to allow something than to undo damage from something you shouldn't have allowed.

The sandbox won't slow you down. Performance overhead is minimal. But it will stop you from being the developer who rubber-stamps `rm -rf /` because it was the 47th approval prompt of the hour.

## Next Steps

- Set up permission management for defense-in-depth with tool-level controls
- Configure [hooks](/blog/hooks-guide) to automate security blocking and safe command approval
- Review configuration basics for the complete Claude Code settings hierarchy
- Read the installation guide if you haven't set up Claude Code yet
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
