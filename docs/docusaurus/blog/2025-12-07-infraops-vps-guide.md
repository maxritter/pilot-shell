---
title: "Claude Code VPS Setup: Deploy and Run on Remote Servers"
description: "Run Claude Code on a VPS with SSH, Docker, and headless mode. Setup guide with real commands, monitoring, and security hardening."
slug: infraops-vps-guide
date: 2025-12-07
authors:
  - max-ritter
tags:
  - guide
  - development
---

Run Claude Code on a VPS with SSH, Docker, and headless mode. Setup guide with real commands, monitoring, and security hardening.

<!-- truncate -->

**Problem**: You can build apps with Claude Code locally, but running it on a remote server feels like uncharted territory. Maybe you want Claude Code available 24/7 for long-running tasks. Maybe you need it accessible from multiple machines without syncing environments. Or maybe you just want to keep resource-heavy AI work off your laptop.

Running Claude Code on a VPS is straightforward once you know the moving parts: SSH access, Node.js, authentication, and optionally Docker for isolation. This guide walks through the entire process with real commands you can run on a fresh Ubuntu server.

## Prerequisites and VPS Selection

Claude Code needs more resources than a typical Node.js app. The AI model runs remotely on Anthropic's servers, but the local process still handles context management, file operations, and tool execution.

**Minimum VPS specs**:

- 2 vCPUs (4 recommended for multi-agent workloads)
- 4 GB RAM (8 GB recommended)
- 40 GB SSD storage
- Ubuntu 22.04 or 24.04 LTS

**Providers that work well**: Any major VPS provider handles this fine. AWS Lightsail, DigitalOcean, Hetzner, and Linode all offer plans in the $10-20/month range that meet these specs. Hetzner gives the best price-to-performance ratio for European developers. Lightsail is the simplest if you're already in the AWS ecosystem.

**What you'll need before starting**:

- An Anthropic API key (from console.anthropic.com) or a Pro/Max subscription
- SSH access to your server
- A domain name (optional, for [Remote Control](/blog/remote-control-guide) access)

## SSH Setup and Secure Access

Start with a fresh Ubuntu server. Most providers give you root access via password. Your first job is making it secure.

```
# Connect to your new server
ssh root@your-server-ip
 
# Create a non-root user
adduser deploy
usermod -aG sudo deploy
 
# Set up SSH key authentication
mkdir -p /home/deploy/.ssh
# Copy your public key (run this from your LOCAL machine instead):
# ssh-copy-id deploy@your-server-ip
 
# Disable password authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

**Set up a basic firewall** before installing anything else:

```
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

From this point forward, always connect as your non-root user: `ssh deploy@your-server-ip`.

## Installing Claude Code on a Headless Server

Claude Code requires Node.js 18+. Install it with the NodeSource repository for the latest LTS version:

```
# Install Node.js 22 LTS
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
 
# Verify installation
node --version  # Should show v22.x
npm --version
 
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code
 
# Verify Claude Code installed
claude --version
```

**Authentication**: On a headless server without a browser, you'll need to authenticate using an API key. For background on how Claude Code manages credentials and permissions, see the permission management guide.

```
# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."
 
# Or for persistent sessions, add to your shell profile
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

If you have a Pro or Max subscription and want to use OAuth instead, run `claude` once, copy the auth URL it provides, open it in a browser on any device, and paste the code back into the terminal.

## Running Claude Code in Non-Interactive Mode

On a server, you'll typically run Claude Code in headless mode rather than interactive chat. If you're new to the CLI, the installation guide covers the basics. This is where it gets useful for automation.

**Single command execution**:

```
# Run a single task and exit
claude -p "Review the codebase in /opt/apps/myproject and list any security issues"
 
# Pipe input for processing
cat error-log.txt | claude -p "Analyze these errors and suggest fixes"
```

**The `-p` flag** (print mode) runs Claude Code non-interactively. It processes the prompt, outputs the result, and exits. No chat interface, no waiting for input.

**Combining with SSH for remote management**: This is where a VPS-hosted Claude Code becomes powerful. From your local machine:

```
# Run Claude Code on your server from your laptop
ssh deploy@your-server "cd /opt/apps/myproject && claude -p 'Run the test suite and fix any failures'"
```

You can also use [Remote Control](/blog/remote-control-guide) to connect to a running interactive session from your phone or another device, which is useful for monitoring long-running agent tasks.

## Docker Deployment Workflow

Docker adds isolation and reproducibility. If something goes wrong, you tear down the container and start fresh. No cleaning up a polluted server environment.

**Create a `docker-compose.yml`** for your Claude Code workspace:

```
version: "3.8"
services:
  claude-workspace:
    image: node:22-slim
    container_name: claude-code
    working_dir: /workspace
    volumes:
      - ./projects:/workspace
      - claude-cache:/home/node/.claude
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - NODE_ENV=production
    command: >
      bash -c "
        npm install -g @anthropic-ai/claude-code &&
        tail -f /dev/null
      "
    restart: unless-stopped
 
volumes:
  claude-cache:
```

**Start the workspace and use it**:

```
# Start the container
docker compose up -d
 
# Execute Claude Code inside the container
docker exec -it claude-code claude -p "List all files in the workspace"
 
# Open an interactive session
docker exec -it claude-code claude
 
# View container logs
docker logs claude-code
```

The `tail -f /dev/null` command keeps the container running so you can exec into it repeatedly. The `claude-cache` volume persists Claude's authentication and session data between container restarts.

**For project-specific containers**, create separate compose files per project. Each gets its own isolated environment with only the files it needs mounted.

## Monitoring and Log Management

Long-running Claude Code sessions on a VPS need monitoring. You don't want a process to crash silently at 3 AM.

**Use tmux or screen** for persistent sessions that survive SSH disconnects:

```
# Start a new tmux session
tmux new -s claude-session
 
# Run Claude Code inside tmux
cd /opt/apps/myproject
claude
 
# Detach: Ctrl+B, then D
# Reattach later:
tmux attach -t claude-session
```

**Systemd service** for always-on Claude Code workers:

```
# /etc/systemd/system/claude-worker.service
[Unit]
Description=Claude Code Worker
After=network.target
 
[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/apps/myproject
Environment=ANTHROPIC_API_KEY=sk-ant-...
ExecStart=/usr/bin/claude -p "Analyze /var/log/app.log for errors since the last check and write a summary to /opt/apps/myproject/issues/latest-report.md"
Restart=always
RestartSec=3600
 
[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable claude-worker
sudo systemctl start claude-worker
 
# Check status
sudo systemctl status claude-worker
 
# View logs
journalctl -u claude-worker -f
```

## Common Errors and Real Fixes

**"EACCES: permission denied, mkdir '/usr/lib/node_modules'"**

You installed Node.js as root but npm needs write access for global installs. Fix with:

```
sudo chown -R $(whoami) /usr/lib/node_modules
# Or better: use a node version manager like nvm
```

**"Error: Unable to open browser for authentication"**

Expected on headless servers. Use the API key method described above, or copy the auth URL to a device with a browser.

**Claude Code process killed by OOM (Out of Memory)**

Your VPS doesn't have enough RAM. Multi-agent sessions that spawn many sub-agents consume memory per agent. Solutions:

```
# Check current memory usage
free -h
 
# Add swap space if you don't have it
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**SSH connection drops during long Claude Code sessions**

Configure SSH keep-alive on your local machine:

```
# ~/.ssh/config
Host your-server
    HostName your-server-ip
    User deploy
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Or use tmux (described above) so the session persists regardless of your SSH connection.

## Security Considerations

Running an AI coding agent on a server with real credentials requires extra caution.

**Never store API keys in committed files**. Use environment variables or a secrets manager:

```
# Use a .env file that's gitignored
echo "ANTHROPIC_API_KEY=sk-ant-..." > /opt/apps/myproject/.env
 
# Load in your shell
set -a; source /opt/apps/myproject/.env; set +a
```

**Restrict Claude Code's file access** when running automated tasks. The `--sandbox` flag limits filesystem and network access:

```
claude --sandbox -p "Analyze this codebase for security issues"
```

**Set up Fail2ban** to block brute-force SSH attempts:

```
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Keep your server updated**:

```
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

## What's Next

A VPS-hosted Claude Code opens up workflows that aren't possible locally: 24/7 availability, [scheduled tasks](/blog/scheduled-tasks) that run while you sleep, and multi-agent sessions that don't drain your laptop battery. Pair it with [git worktrees](/blog/worktree-guide) for isolated branch work, or use [Remote Control](/blog/remote-control-guide) to manage sessions from your phone.

Start simple. Get Claude Code running on a basic VPS with SSH access. Add Docker once you need isolation. Add systemd services once you need automation. Scale up from there.

[Opus 4.7 Best Practices](/blog/opus-4-7-best-practices)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
