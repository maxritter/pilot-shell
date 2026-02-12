# Sandboxing Claude Code for Safe Execution

Claude Code runs shell commands on your machine. While it follows safety rules, defense in depth means adding OS-level sandboxing. This guide covers filesystem and network isolation on macOS and Linux.

## Why Sandbox?

Claude Code has built-in safeguards — permission prompts, tool restrictions, and rules. But these are software-level controls. Sandboxing adds OS-level enforcement:

- **Filesystem isolation** — Claude can only access project files, not your home directory secrets
- **Network restrictions** — Prevent unintended external connections
- **Process limits** — Contain resource usage

## macOS Seatbelt

macOS includes a sandboxing framework called Seatbelt. Create a profile that restricts Claude Code:

```scheme
;; claude-sandbox.sb
(version 1)
(deny default)

;; Allow read/write to project directory
(allow file-read* file-write*
  (subpath "/Users/you/projects/my-app"))

;; Allow read to system libraries and tools
(allow file-read*
  (subpath "/usr/lib")
  (subpath "/usr/bin")
  (subpath "/usr/local"))

;; Allow network for API calls
(allow network-outbound
  (remote tcp "*:443"))

;; Allow process execution
(allow process-exec)
```

Run Claude Code with the sandbox:

```bash
sandbox-exec -f claude-sandbox.sb claude
```

## Linux Bubblewrap

On Linux, use `bubblewrap` (bwrap) for namespace-based isolation:

```bash
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --bind ~/projects/my-app ~/projects/my-app \
  --dev /dev \
  --proc /proc \
  --tmpfs /tmp \
  --unshare-net \
  claude
```

Key flags:
- `--ro-bind` — Read-only access to system directories
- `--bind` — Read-write access to your project
- `--unshare-net` — No network access (remove if Claude needs API access)
- `--tmpfs /tmp` — Isolated temporary directory

## Docker-Based Isolation

For the most portable approach, run Claude Code in a container:

```dockerfile
FROM node:20-slim
RUN npm install -g @anthropic-ai/claude-code
WORKDIR /app
ENTRYPOINT ["claude"]
```

```bash
docker run -it \
  -v $(pwd):/app \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  claude-sandbox
```

## Permission Configuration

Complement sandboxing with Claude Code's built-in permissions:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Bash(npm test)",
      "Bash(npm run build)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  }
}
```

## Which Approach to Use

| Concern | Solution |
|---------|----------|
| General safety | Claude Code permissions (built-in) |
| Filesystem protection | Seatbelt (macOS) or bwrap (Linux) |
| Network isolation | bwrap `--unshare-net` or firewall rules |
| Full isolation | Docker container |
| Team standardization | Docker + shared config |

Start with permissions. Add OS-level sandboxing for sensitive projects or shared machines.
