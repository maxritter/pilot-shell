---
slug: "statusline-guide"
title: "Claude Code Status Line Setup Guide (Scripts + Examples)"
description: "Set up a custom Claude Code status line showing model name, git branch, cost, and context usage. Includes ready-to-copy scripts."
date: "2026-02-03"
author: "Max Ritter"
tags: [Guide, Tools]
readingTime: 10
keywords: "claude, code, examples, guide, line, scripts, setup, status, statusline"
---

# Claude Code Status Line: Display Model, Cost, and Git Branch in Your Terminal

Set up a custom Claude Code status line showing model name, git branch, cost, and context usage. Includes ready-to-copy scripts.

Your Claude Code terminal is missing useful information. The status line fixes that by putting model name, git branch, session cost, and context usage right at the bottom of the interface.

Think of it like PS1 for Claude Code. If you've ever customized a shell prompt with Oh-my-zsh or Starship, this is the same idea. One line of real-time info that keeps you oriented while you work.

## [What the Status Line Shows](#what-the-status-line-shows)

The status line sits at the bottom of the Claude Code interface and updates every time the conversation changes. It can display anything your script outputs: the current model, which git branch you're on, how much you've spent this session, or how full your [context window](/blog/guide/mechanics/context-buffer-management) is.

Here's what a configured status line looks like in practice:

```p-4
[Opus] my-project | main | $0.42 | Context: 37%
```

That single line tells you the model, the project folder, the git branch, the session cost so far, and the percentage of your context window used. All updated automatically.

## [Quick Setup with /statusline](#quick-setup-with-statusline)

The fastest path to a working status line is the built-in `/statusline` command. Type it directly into Claude Code and it generates a script for you.

```p-4
/statusline
```

Claude Code will create a status line script that mirrors your terminal prompt by default. But you can also give it specific instructions:

```p-4
/statusline show the model name in orange
```

```p-4
/statusline display git branch and session cost
```

```p-4
/statusline show context window percentage with color coding
```

That's it. Claude Code writes the script, configures the settings, and the status line appears. If you want more control, keep reading for manual setup.

## [Manual Setup via settings.json](#manual-setup-via-settingsjson)

For full control, add a `statusLine` entry to your project's `.claude/settings.json` (or your global `~/.claude/settings.json` for all projects):

```p-4
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0
  }
}
```

Three fields to know:

- **type**: Always `"command"` for script-based status lines
- **command**: Path to the script that generates your status line output
- **padding**: Number of empty lines above the status line (0 is typical)

After adding this, create the script file and make it executable:

```p-4
touch ~/.claude/statusline.sh
chmod +x ~/.claude/statusline.sh
```

The `chmod +x` step matters. If your status line doesn't appear, a missing execute permission is almost always the reason.

## [How the Status Line Engine Works](#how-the-status-line-engine-works)

Understanding the mechanics helps when debugging or building custom scripts:

- **Update trigger**: The status line refreshes whenever conversation messages change
- **Throttle**: Updates run at most every 300ms to avoid performance issues
- **Output handling**: Only the first line of stdout from your script becomes the status line text
- **Colors**: Full ANSI color code support for styling
- **Input**: Claude Code pipes a JSON object with session data into your script via stdin

That last point is the key. Your script receives structured JSON containing the current model, workspace paths, session cost, context window stats, and more. Parse it, format it, print one line to stdout.

## [The JSON Input Your Script Receives](#the-json-input-your-script-receives)

Every time the status line updates, your script gets this JSON structure via stdin:

```p-4
{
  "hook_event_name": "Status",
  "session_id": "abc123...",
  "cwd": "/current/working/directory",
  "model": {
    "id": "claude-opus-4-1",
    "display_name": "Opus"
  },
  "workspace": {
    "current_dir": "/current/working/directory",
    "project_dir": "/original/project/directory"
  },
  "version": "1.0.80",
  "cost": {
    "total_cost_usd": 0.01234,
    "total_duration_ms": 45000,
    "total_api_duration_ms": 2300,
    "total_lines_added": 156,
    "total_lines_removed": 23
  },
  "context_window": {
    "total_input_tokens": 15234,
    "total_output_tokens": 4521,
    "context_window_size": 200000,
    "used_percentage": 42.5,
    "remaining_percentage": 57.5,
    "current_usage": {
      "input_tokens": 8500,
      "output_tokens": 1200,
      "cache_creation_input_tokens": 5000,
      "cache_read_input_tokens": 2000
    }
  }
}
```

The fields that matter most for practical status lines:

- **model.display\_name**: Short model name like "Opus" or "Sonnet"
- **workspace.current\_dir**: Where you're working right now
- **cost.total\_cost\_usd**: Running cost of the session in dollars
- **cost.total\_lines\_added / total\_lines\_removed**: Track code changes
- **context\_window.used\_percentage**: Pre-calculated context usage (0-100)
- **context\_window.context\_window\_size**: Total context window capacity

## [Status Line Scripts You Can Copy](#status-line-scripts-you-can-copy)

Here are complete, runnable scripts in multiple languages. Pick the one that fits your setup.

### [Simple Bash Status Line](#simple-bash-status-line)

The simplest useful status line. Shows model name and current directory:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')
 
echo "[$MODEL] ${CURRENT_DIR##*/}"
```

**Output**: `[Opus] my-project`

This script uses `jq` for JSON parsing. If you don't have it installed, run `brew install jq` on macOS or `sudo apt install jq` on Ubuntu.

### [Git-Aware Bash Status Line](#git-aware-bash-status-line)

Adds the current git branch, which is useful when you're juggling feature branches:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')
 
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH=" | $BRANCH"
    fi
fi
 
echo "[$MODEL] ${CURRENT_DIR##*/}$GIT_BRANCH"
```

**Output**: `[Opus] my-project | feature/auth`

### [Full-Featured Bash Status Line](#full-featured-bash-status-line)

Model, git branch, cost, and context percentage all in one line:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
PERCENT_USED=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
 
# Git branch
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH=" | $BRANCH"
    fi
fi
 
# Format cost to 2 decimal places
COST_FMT=$(printf '%.2f' "$COST")
 
# Round context percentage
PERCENT_INT=$(printf '%.0f' "$PERCENT_USED")
 
echo "[$MODEL] ${CURRENT_DIR##*/}$GIT_BRANCH | \$${COST_FMT} | Ctx: ${PERCENT_INT}%"
```

**Output**: `[Opus] my-project | main | $0.42 | Ctx: 37%`

### [Bash with ANSI Colors](#bash-with-ansi-colors)

Color-coded output makes information scannable at a glance:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
PERCENT_USED=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
 
# ANSI colors
ORANGE='\033[38;5;208m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'
 
# Color context percentage based on usage
PERCENT_INT=$(printf '%.0f' "$PERCENT_USED")
if [ "$PERCENT_INT" -lt 50 ]; then
    CTX_COLOR=$GREEN
elif [ "$PERCENT_INT" -lt 80 ]; then
    CTX_COLOR=$YELLOW
else
    CTX_COLOR=$RED
fi
 
COST_FMT=$(printf '%.2f' "$COST")
 
echo -e "${ORANGE}[$MODEL]${RESET} ${CURRENT_DIR##*/} ${CYAN}\$${COST_FMT}${RESET} ${CTX_COLOR}Ctx:${PERCENT_INT}%${RESET}"
```

The context percentage turns green below 50%, yellow between 50-80%, and red above 80%. You can immediately see when it's time to [manage your context window](/blog/guide/mechanics/context-buffer-management).

### [Helper Function Approach for Complex Scripts](#helper-function-approach-for-complex-scripts)

When your status line script grows, helper functions keep things readable:

```p-4
#!/bin/bash
input=$(cat)
 
# Helper functions for clean extraction
get_model()     { echo "$input" | jq -r '.model.display_name'; }
get_dir()       { echo "$input" | jq -r '.workspace.current_dir'; }
get_cost()      { echo "$input" | jq -r '.cost.total_cost_usd // 0'; }
get_context()   { echo "$input" | jq -r '.context_window.used_percentage // 0'; }
get_added()     { echo "$input" | jq -r '.cost.total_lines_added // 0'; }
get_removed()   { echo "$input" | jq -r '.cost.total_lines_removed // 0'; }
get_version()   { echo "$input" | jq -r '.version'; }
 
MODEL=$(get_model)
DIR=$(get_dir)
COST=$(printf '%.2f' "$(get_cost)")
CTX=$(printf '%.0f' "$(get_context)")
ADDED=$(get_added)
REMOVED=$(get_removed)
 
echo "[$MODEL] ${DIR##*/} | \$$COST | Ctx:${CTX}% | +$ADDED/-$REMOVED"
```

**Output**: `[Opus] my-project | $0.42 | Ctx:37% | +156/-23`

The `+156/-23` shows lines added and removed in the session. A quick way to gauge how much code has changed.

### [Python Status Line](#python-status-line)

If you prefer Python over bash:

```p-4
#!/usr/bin/env python3
import json
import sys
import os
import subprocess
 
data = json.load(sys.stdin)
 
model = data["model"]["display_name"]
current_dir = os.path.basename(data["workspace"]["current_dir"])
cost = data.get("cost", {}).get("total_cost_usd", 0)
ctx_pct = data.get("context_window", {}).get("used_percentage", 0)
 
# Get git branch
git_branch = ""
try:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, timeout=2
    )
    if result.returncode == 0 and result.stdout.strip():
        git_branch = f" | {result.stdout.strip()}"
except Exception:
    pass
 
print(f"[{model}] {current_dir}{git_branch} | ${cost:.2f} | Ctx:{ctx_pct:.0f}%")
```

### [Node.js Status Line](#nodejs-status-line)

For JavaScript developers:

```p-4
#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
 
let input = "";
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  const data = JSON.parse(input);
 
  const model = data.model.display_name;
  const currentDir = path.basename(data.workspace.current_dir);
  const cost = (data.cost?.total_cost_usd || 0).toFixed(2);
  const ctxPct = Math.round(data.context_window?.used_percentage || 0);
 
  // Get git branch
  let gitBranch = "";
  try {
    const branch = execSync("git branch --show-current", {
      encoding: "utf8",
      timeout: 2000,
    }).trim();
    if (branch) gitBranch = ` | ${branch}`;
  } catch (e) {}
 
  console.log(
    `[${model}] ${currentDir}${gitBranch} | $${cost} | Ctx:${ctxPct}%`,
  );
});
```

## [Tracking Context Window Usage](#tracking-context-window-usage)

Watching your context window is one of the most practical uses for the status line. When context fills up, Claude Code compacts the conversation and you lose detail. Knowing where you stand helps you decide when to [start fresh or compact strategically](/blog/guide/mechanics/context-management).

**Simple approach** using the pre-calculated percentage:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
PERCENT_USED=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
 
echo "[$MODEL] Context: ${PERCENT_USED}%"
```

**Advanced approach** with manual calculation from raw token counts:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size')
USAGE=$(echo "$input" | jq '.context_window.current_usage')
 
if [ "$USAGE" != "null" ]; then
    CURRENT_TOKENS=$(echo "$USAGE" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    PERCENT_USED=$((CURRENT_TOKENS * 100 / CONTEXT_SIZE))
    echo "[$MODEL] Context: ${PERCENT_USED}% (${CURRENT_TOKENS}/${CONTEXT_SIZE} tokens)"
else
    echo "[$MODEL] Context: 0%"
fi
```

The manual approach lets you see raw token numbers alongside the percentage. Useful when you want to know exactly how many tokens you have left, especially when picking between [different models with different context sizes](/blog/models/model-selection).

## [Tracking Session Cost](#tracking-session-cost)

The `cost.total_cost_usd` field updates in real time. Displaying it in your status line keeps spending visible without needing to check the dashboard:

```p-4
#!/bin/bash
input=$(cat)
 
MODEL=$(echo "$input" | jq -r '.model.display_name')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
COST_FMT=$(printf '%.2f' "$COST")
 
echo "[$MODEL] Session: \$${COST_FMT}"
```

If you're on a budget or tracking costs per feature, this is immediately useful. Pair it with [model selection strategies](/blog/models/model-selection) to switch models when a task doesn't need the most expensive option.

## [Troubleshooting](#troubleshooting)

**Status line doesn't appear at all**

The most common cause is a missing execute permission on the script file. Fix it with:

```p-4
chmod +x ~/.claude/statusline.sh
```

**Script runs but output is empty**

Your script might be writing to stderr instead of stdout. The status line only reads the first line of stdout. Add a simple `echo "test"` to verify output, then build from there.

**Testing your script manually**

You can test without running Claude Code by piping mock JSON into your script:

```p-4
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"/test"},"cost":{"total_cost_usd":0.5},"context_window":{"used_percentage":25}}' | ~/.claude/statusline.sh
```

If that prints the expected output, the script works. If it doesn't, the issue is in parsing.

**jq not found**

Install it with your package manager:

```p-4
# macOS
brew install jq
 
# Ubuntu/Debian
sudo apt install jq
 
# Windows (via scoop)
scoop install jq
```

## [Creative Status Line Ideas](#creative-status-line-ideas)

Once you have the basics working, here are some ideas to make your status line more useful:

- **Lines changed tracker**: Show `+added/-removed` to monitor session productivity
- **Session duration**: Calculate elapsed time from `total_duration_ms`
- **Model ID display**: Show the full model identifier when testing different [model configurations](/blog/models/model-selection)
- **Project vs current directory**: Show both when Claude Code navigates into subdirectories
- **Cost-per-minute**: Divide `total_cost_usd` by `total_duration_ms` to see burn rate
- **Context window bar**: Replace the percentage with a visual bar like `[========--]`
- **Conditional warnings**: Flash a color when context exceeds 80% or cost passes a threshold

The status line runs a script you control. If you can write it in bash, Python, or Node.js, you can display it.

## [What to Try Next](#what-to-try-next)

Your status line is set up. Here are natural next steps:

- **Manage context proactively**: Use your context percentage display alongside [context buffer management strategies](/blog/guide/mechanics/context-buffer-management)
- **Set up the terminal environment**: Learn [terminal control techniques](/blog/guide/mechanics/terminal-main-thread) for a complete Claude Code workspace
- **Configure project settings**: Make sure your [configuration basics](/blog/guide/configuration-basics) are solid so every session starts with the right context

Last updated on

[Previous

Keyboard Shortcuts](/blog/tools/keybindings-guide)[Next

Hooks Guide](/blog/tools/hooks/hooks-guide)
