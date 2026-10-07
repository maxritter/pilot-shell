#!/usr/bin/env bash
# Native Claude Code's mod-test SDK, pinned and isolated from the runner's normal HOME.
set -euo pipefail

ql_claude_home="${1:?usage: setup-claude-code.sh <isolated home>}"
ql_claude_version=2.1.292
ql_claude_scratch="$(mktemp -d)"
trap 'rm -rf "${ql_claude_scratch:?}"' EXIT
mkdir -p "$ql_claude_home"
curl --retry 3 -fsSL https://claude.ai/install.sh -o "$ql_claude_scratch/install.sh"
if [ ! -s "$ql_claude_scratch/install.sh" ]; then
  echo "Claude Code installer was empty; native mod tests cannot run" >&2
  exit 1
fi
HOME="$ql_claude_home" DISABLE_AUTOUPDATER=1 bash "$ql_claude_scratch/install.sh" "$ql_claude_version" < /dev/null
ql_claude_native="$ql_claude_home/.local/share/claude/versions/$ql_claude_version"
test -x "$ql_claude_native"
HOME="$ql_claude_home" DISABLE_AUTOUPDATER=1 "$ql_claude_native" --version | grep -F "$ql_claude_version"
if [ -n "${GITHUB_ENV:-}" ]; then
  printf 'QUALITYLAYER_ACTIVATION_CLAUDE=%s\n' "$ql_claude_native" >> "$GITHUB_ENV"
  printf '%s\n' 'QUALITYLAYER_REQUIRE_MOD_TEST=1' 'DISABLE_AUTOUPDATER=1' >> "$GITHUB_ENV"
fi
