#!/bin/bash

set -e

# All destructive paths derive from HOME. Fail closed before constructing any
# target when the environment is malformed or points at the filesystem root.
case "${HOME:-}" in
/*) ;;
*)
	echo "  [!!] HOME must be an absolute path, got: '${HOME:-}'" >&2
	echo "       Refusing to uninstall - no files were removed." >&2
	exit 1
	;;
esac
if [ ! -d "$HOME" ]; then
	echo "  [!!] HOME must name an existing user directory, got: '$HOME'" >&2
	echo "       Refusing to uninstall - no files were removed." >&2
	exit 1
fi
HOME_CANONICAL=$(cd -- "$HOME" && pwd -P) || {
	echo "  [!!] Could not resolve HOME safely: '$HOME'" >&2
	exit 1
}
if [ "$HOME_CANONICAL" = "/" ]; then
	echo "  [!!] HOME resolves to the filesystem root; refusing to uninstall." >&2
	exit 1
fi
HOME="$HOME_CANONICAL"
export HOME

PILOT_DIR="$HOME/.pilot"
INSTALL_LOCK_DIR="$PILOT_DIR/.bin-install.lock"
if [ -L "$PILOT_DIR" ]; then
	echo "  [!!] ~/.pilot is a symlink; refusing recursive uninstall through an untrusted root." >&2
	exit 1
fi

# Every path below feeds an `rm`, so validate BEFORE deriving any of them.
# A relative CLAUDE_CONFIG_DIR would resolve rm targets against the current
# working directory; falling back to ~/.claude on a bad value would clean the
# personal profile the user set the variable to protect. Fail closed instead.
if [ -n "${CLAUDE_CONFIG_DIR+x}" ]; then
	case "$CLAUDE_CONFIG_DIR" in
	/*) ;;
	*)
		echo "  [!!] CLAUDE_CONFIG_DIR must be an absolute path, got: '${CLAUDE_CONFIG_DIR}'" >&2
		echo "       Refusing to uninstall - no files were removed." >&2
		exit 1
		;;
	esac
	if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
		echo "  [!!] CLAUDE_CONFIG_DIR does not exist: '${CLAUDE_CONFIG_DIR}'" >&2
		echo "       Refusing to uninstall - no files were removed." >&2
		exit 1
	fi
	# Canonicalize so the manifest check and the later rm agree on one path.
	CLAUDE_DIR="$(cd "$CLAUDE_CONFIG_DIR" && pwd -P)"
	if [ "$CLAUDE_DIR" = "/" ]; then
		echo "  [!!] CLAUDE_CONFIG_DIR resolves to the filesystem root; refusing to uninstall." >&2
		exit 1
	fi
else
	CLAUDE_DIR="$HOME/.claude"
fi
if [ -d "$CLAUDE_DIR" ]; then
	CLAUDE_DIR_CANONICAL=$(cd -- "$CLAUDE_DIR" && pwd -P) || {
		echo "  [!!] Could not resolve Claude config directory safely: '$CLAUDE_DIR'" >&2
		exit 1
	}
	if [ "$CLAUDE_DIR_CANONICAL" = "/" ]; then
		echo "  [!!] Claude config directory resolves to the filesystem root; refusing to uninstall." >&2
		exit 1
	fi
	CLAUDE_DIR="$CLAUDE_DIR_CANONICAL"
fi

# Claude Code's app config: <config dir>/.config.json when present, else
# (CLAUDE_CONFIG_DIR or $HOME)/.claude.json. Same rule as
# installer/claude_paths.py:get_claude_app_config_path - keep the two in lockstep.
if [ -f "$CLAUDE_DIR/.config.json" ]; then
	CLAUDE_APP_CONFIG="$CLAUDE_DIR/.config.json"
else
	CLAUDE_APP_CONFIG="${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json"
fi

PILOT_PLUGIN_DIR="$CLAUDE_DIR/pilot"
MANIFEST_FILE="$CLAUDE_DIR/.pilot-manifest.json"

# When the user explicitly names a profile, that profile must actually contain a
# Pilot install. Otherwise they have pointed the uninstaller at the wrong
# directory and would get a half-clean ("removed 0 files") with the real install
# left behind. Only enforced when CLAUDE_CONFIG_DIR is set: an unset value must
# stay tolerant, because legacy pre-manifest installs have no manifest and still
# need ~/.pilot, the shell aliases and the Codex tree cleaned up.
if [ -n "${CLAUDE_CONFIG_DIR+x}" ] && [ ! -f "$MANIFEST_FILE" ]; then
	echo "  [!!] No Pilot install found in CLAUDE_CONFIG_DIR: ${CLAUDE_DIR}" >&2
	echo "       (expected $(basename "$MANIFEST_FILE"))" >&2
	echo "       Refusing to uninstall - no files were removed." >&2
	echo "       Unset CLAUDE_CONFIG_DIR to uninstall from \$HOME/.claude instead." >&2
	exit 1
fi
HOOKS_BASELINE_FILE="$CLAUDE_DIR/.pilot-hooks-baseline.json"
MCP_BASELINE_FILE="$CLAUDE_DIR/.pilot-mcp-baseline.json"
LSP_MANIFEST_FILE="$PILOT_DIR/.pilot-lsp-plugins.json"

if [ -n "${CODEX_HOME+x}" ]; then
	case "$CODEX_HOME" in
	/*) ;;
	*)
		echo "  [!!] CODEX_HOME must be an absolute path, got: '$CODEX_HOME'" >&2
		echo "       Refusing to uninstall - no files were removed." >&2
		exit 1
		;;
	esac
	if [ ! -d "$CODEX_HOME" ]; then
		echo "  [!!] CODEX_HOME must name an existing directory, got: '$CODEX_HOME'" >&2
		echo "       Refusing to uninstall - no files were removed." >&2
		exit 1
	fi
	CODEX_HOME_CANONICAL=$(cd -- "$CODEX_HOME" && pwd -P) || {
		echo "  [!!] Could not resolve CODEX_HOME safely: '$CODEX_HOME'" >&2
		exit 1
	}
	if [ "$CODEX_HOME_CANONICAL" = "/" ]; then
		echo "  [!!] CODEX_HOME resolves to the filesystem root; refusing to uninstall." >&2
		exit 1
	fi
	CODEX_HOME="$CODEX_HOME_CANONICAL"
	export CODEX_HOME
fi
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
if [ -d "$CODEX_DIR" ]; then
	CODEX_DIR_CANONICAL=$(cd -- "$CODEX_DIR" && pwd -P) || {
		echo "  [!!] Could not resolve Codex config directory safely: '$CODEX_DIR'" >&2
		exit 1
	}
	if [ "$CODEX_DIR_CANONICAL" = "/" ]; then
		echo "  [!!] Codex config directory resolves to the filesystem root; refusing to uninstall." >&2
		exit 1
	fi
	CODEX_DIR="$CODEX_DIR_CANONICAL"
fi
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
if [ -d "$AGENTS_SKILLS_DIR" ]; then
	AGENTS_SKILLS_CANONICAL=$(cd -- "$AGENTS_SKILLS_DIR" && pwd -P) || {
		echo "  [!!] Could not resolve Codex skills directory safely: '$AGENTS_SKILLS_DIR'" >&2
		exit 1
	}
	if [ "$AGENTS_SKILLS_CANONICAL" = "/" ]; then
		echo "  [!!] Codex skills directory resolves to the filesystem root; refusing to uninstall." >&2
		exit 1
	fi
	AGENTS_SKILLS_DIR="$AGENTS_SKILLS_CANONICAL"
fi

PILOT_PYTHON_MODE=""
PILOT_UV_BIN=""
if command -v python3 >/dev/null 2>&1 && python3 -c "import json" >/dev/null 2>&1; then
	PILOT_PYTHON_MODE="python3"
elif command -v uv >/dev/null 2>&1; then
	PILOT_PYTHON_MODE="uv"
	PILOT_UV_BIN=$(command -v uv)
elif [ -x "$HOME/.local/bin/uv" ]; then
	PILOT_PYTHON_MODE="uv"
	PILOT_UV_BIN="$HOME/.local/bin/uv"
fi

pilot_python_available() {
	[ -n "$PILOT_PYTHON_MODE" ]
}

pilot_python() {
	case "$PILOT_PYTHON_MODE" in
	python3) python3 "$@" ;;
	uv) "$PILOT_UV_BIN" run --python 3.12 --no-project --no-config python "$@" ;;
	*) return 127 ;;
	esac
}

CODEX_PILOT_SKILLS=(
	"spec"
	"spec-plan"
	"spec-bugfix-plan"
	"spec-implement"
	"spec-verify"
	"spec-bugfix-verify"
	"fix"
	"build"
	"prd"
	"investigate"
	"cleanup"
	"benchmark"
	"setup-rules"
	"create-skill"
	"bot-boot"
	"bot-channel-task"
	"bot-defaults"
	"bot-heartbeat"
	"bot-jobs"
)

CODEX_PILOT_REVIEW_AGENTS=(
	"build-review"
	"changes-review"
	"spec-review"
)

LSP_MARKETPLACE="claude-code-lsps"

LEGACY_HOOK_FILES=(
	"context-mode-cache-heal.mjs"
)

CLAUDE_ALIAS_MARKER="# Pilot Shell"
OLD_CLAUDE_PILOT_MARKER="# Claude Pilot"
OLD_CCP_MARKER="# Claude CodePro alias"

removed_items=()
UNINSTALL_LOCK_OWNED=false
cleanup_failed=false

mark_cleanup_failure() {
	cleanup_failed=true
	echo "    [!!] $1"
}

release_uninstall_lock() {
	trap - EXIT HUP INT TERM
	if [ "$UNINSTALL_LOCK_OWNED" = true ]; then
		local owner_pid=""
		if [ -f "$INSTALL_LOCK_DIR/pid" ]; then
			owner_pid=$(sed -n '1p' "$INSTALL_LOCK_DIR/pid") || true
		fi
		if [ "$owner_pid" = "$$" ]; then
			rm -rf "$INSTALL_LOCK_DIR"
		else
			echo "  [!!] Uninstall lock ownership changed; preserving $INSTALL_LOCK_DIR" >&2
		fi
		rmdir "$PILOT_DIR" 2>/dev/null || true
		UNINSTALL_LOCK_OWNED=false
	fi
}

acquire_uninstall_lock() {
	if mkdir -p "$PILOT_DIR" && mkdir "$INSTALL_LOCK_DIR" 2>/dev/null; then
		if ! printf "%s\n" "$$" >"$INSTALL_LOCK_DIR/pid"; then
			echo "  [!!] Failed to initialise the Pilot uninstall lock" >&2
			rm -rf "$INSTALL_LOCK_DIR"
			return 1
		fi
		UNINSTALL_LOCK_OWNED=true
		trap release_uninstall_lock EXIT
		trap 'release_uninstall_lock; exit 1' HUP INT TERM
		return 0
	fi

	local install_pid=""
	if [ -f "$INSTALL_LOCK_DIR/pid" ]; then
		install_pid=$(sed -n '1p' "$INSTALL_LOCK_DIR/pid") || true
	fi
	if [ -z "$install_pid" ]; then
		echo "  [!!] Pilot's install lock has no owner yet: $INSTALL_LOCK_DIR" >&2
		echo "       An install may be initialising. Refusing to uninstall - no files were removed." >&2
		return 1
	fi
	if kill -0 "$install_pid" 2>/dev/null; then
		echo "  [!!] A Pilot install or update is currently running (PID $install_pid)." >&2
		echo "       Refusing to uninstall - no files were removed." >&2
		return 1
	fi

	echo "  [!!] A previous Pilot install left a stale lock: $INSTALL_LOCK_DIR" >&2
	echo "       If no installer is running, remove that directory and re-run uninstall." >&2
	return 1
}

has_codex_pilot_content() {
	if [ -f "$CODEX_DIR/.pilot-hooks-baseline.json" ]; then
		return 0
	fi
	if [ -f "$CODEX_DIR/hooks.json" ] && grep -q '/.pilot/' "$CODEX_DIR/hooks.json" 2>/dev/null; then
		return 0
	fi
	if [ -f "$CODEX_DIR/config.toml" ] && grep -q -e 'pilot-shell managed MCP servers' -e 'pilot-shell managed env vars' -e '.pilot-model-catalog.json' "$CODEX_DIR/config.toml" 2>/dev/null; then
		return 0
	fi
	if [ -f "$CODEX_DIR/.pilot-model-catalog.json" ]; then
		return 0
	fi
	if [ -f "$CODEX_DIR/AGENTS.md" ] && grep -q 'PILOT:START' "$CODEX_DIR/AGENTS.md" 2>/dev/null; then
		return 0
	fi
	if [ -f "$CODEX_DIR/rules/.pilot-rules.json" ]; then
		return 0
	fi
	for agent in "${CODEX_PILOT_REVIEW_AGENTS[@]}"; do
		if [ -f "$CODEX_DIR/agents/$agent.toml" ] && grep -q 'pilot-shell managed Codex review agent' "$CODEX_DIR/agents/$agent.toml" 2>/dev/null; then
			return 0
		fi
	done
	for skill in "${CODEX_PILOT_SKILLS[@]}"; do
		if [ -f "$AGENTS_SKILLS_DIR/$skill/.pilot-resources.json" ]; then
			return 0
		fi
	done
	return 1
}

get_pilot_version() {
	local pilot_path="$PILOT_DIR/bin/pilot"
	if [ -x "$pilot_path" ]; then
		local version
		version=$("$pilot_path" --version 2>/dev/null | sed -n 's/.* v\([^ ]*\).*/\1/p') || true
		if [ -n "$version" ]; then
			echo "$version"
			return
		fi
	fi
	echo "unknown"
}

get_manifest_entries() {
	if [ ! -f "$MANIFEST_FILE" ]; then
		return
	fi
	grep -oE '"[a-z]+/[^"]+"' "$MANIFEST_FILE" 2>/dev/null | sed 's/"//g' || true
}

get_affected_shell_configs() {
	local config_files=(
		"$HOME/.bashrc"
		"$HOME/.bash_profile"
		"$HOME/.zshrc"
		"$HOME/.config/fish/config.fish"
	)
	for config_file in "${config_files[@]}"; do
		# shellcheck disable=SC2016 # Match literal $HOME text in shell config files.
		if [ -f "$config_file" ] && grep -q -e "$CLAUDE_ALIAS_MARKER" \
			-e "$OLD_CLAUDE_PILOT_MARKER" \
			-e "$OLD_CCP_MARKER" \
			-e '/.pilot/bin' \
			-e 'PILOT_SESSION_ID' \
			"$config_file" 2>/dev/null; then
			basename "$config_file"
		fi
	done
}

confirm_uninstall() {
	local version
	version=$(get_pilot_version)

	echo ""
	echo "======================================================================"
	echo "  Pilot Shell Uninstaller (v${version})"
	echo "======================================================================"
	echo ""

	# Always name the profile being cleaned - with CLAUDE_CONFIG_DIR set, the
	# user needs to see WHICH Claude directory this touches before confirming.
	echo "  Claude config directory: ${CLAUDE_DIR}"
	echo "  Claude app config:       ${CLAUDE_APP_CONFIG}"
	if [ -n "${CLAUDE_CONFIG_DIR+x}" ]; then
		echo "  (from CLAUDE_CONFIG_DIR - \$HOME/.claude will not be modified)"
	fi
	echo ""

	echo "  Uninstalling will:"
	echo ""

	if [ -d "$PILOT_DIR" ]; then
		if [ "$PURGE_DATA" = true ]; then
			echo "    • Remove all of ~/.pilot/ including memory, sessions, logs, and user configuration"
		else
			echo "    • Remove Pilot runtime files from ~/.pilot/"
			echo "    • Preserve memory, sessions, logs, configuration, and unknown user-owned files"
		fi
	fi

	if [ -d "$PILOT_PLUGIN_DIR" ]; then
		echo "    • Remove legacy ${CLAUDE_DIR}/pilot/ directory"
	fi

	local entries
	entries=$(get_manifest_entries)
	if [ -n "$entries" ]; then
		echo "$entries" | grep -q '^commands/' && echo "    • Remove Pilot-managed commands from ${CLAUDE_DIR}/commands/"
		echo "$entries" | grep -q '^skills/' && echo "    • Remove Pilot-managed skills from ${CLAUDE_DIR}/skills/"
		echo "$entries" | grep -q '^rules/' && echo "    • Remove Pilot-managed rules from ${CLAUDE_DIR}/rules/"
		echo "$entries" | grep -q '^agents/' && echo "    • Remove Pilot-managed agents from ${CLAUDE_DIR}/agents/"
		echo "$entries" | grep -q '^hooks/' && echo "    • Remove Pilot-managed hooks from ${CLAUDE_DIR}/hooks/"
	fi

	if [ -f "$CLAUDE_DIR/settings.json" ]; then
		echo "    • Clean Pilot-added entries from ${CLAUDE_DIR}/settings.json (including merged hooks)"
	fi

	if [ -f "$CLAUDE_APP_CONFIG" ] && { [ -f "$CLAUDE_DIR/.pilot-claude-baseline.json" ] || [ -f "$MCP_BASELINE_FILE" ]; }; then
		echo "    • Clean Pilot-added keys (and mcpServers) from ${CLAUDE_APP_CONFIG}"
	fi

	if [ -f "$LSP_MANIFEST_FILE" ]; then
		local lsp_ids
		lsp_ids=$(grep -oE '"[a-z][a-z0-9-]*@'"$LSP_MARKETPLACE"'"' "$LSP_MANIFEST_FILE" 2>/dev/null | sed 's/"//g' | tr '\n' ' ')
		if [ -n "$lsp_ids" ]; then
			echo "    • Uninstall Pilot-installed LSP plugins: ${lsp_ids}"
		fi
	fi

	local baseline_files=""
	for f in "$CLAUDE_DIR/.pilot-settings-baseline.json" "$CLAUDE_DIR/.pilot-claude-baseline.json" "$HOOKS_BASELINE_FILE" "$MCP_BASELINE_FILE" "$MANIFEST_FILE"; do
		if [ -f "$f" ]; then
			baseline_files="$baseline_files $(basename "$f")"
		fi
	done
	if [ -n "$baseline_files" ]; then
		echo "    • Remove Pilot metadata:${baseline_files}"
	fi

	local affected_shells
	affected_shells=$(get_affected_shell_configs)
	if [ -n "$affected_shells" ]; then
		local shell_list
		shell_list=$(echo "$affected_shells" | tr '\n' ', ' | sed 's/,$//')
		echo "    • Remove 'pilot' and 'ccp' aliases from ${shell_list}"
	fi

	if has_codex_pilot_content; then
		echo "    • Clean Pilot-managed entries from ~/.codex/ (hooks.json, config.toml, AGENTS.md)"
		if [ -f "$CODEX_DIR/rules/.pilot-rules.json" ]; then
			echo "    • Remove Pilot-managed stack rules from ~/.codex/rules/"
		fi
		local codex_skills_count=0
		for skill in "${CODEX_PILOT_SKILLS[@]}"; do
			[ -d "$AGENTS_SKILLS_DIR/$skill" ] && codex_skills_count=$((codex_skills_count + 1))
		done
		if [ "$codex_skills_count" -gt 0 ]; then
			echo "    • Remove ${codex_skills_count} Pilot-managed Codex skill(s) from ~/.agents/skills/"
		fi
	fi

	echo ""

	confirm=""
	if [ -t 0 ]; then
		printf "  Continue? [y/N]: "
		read -r confirm
	elif [ -e /dev/tty ]; then
		printf "  Continue? [y/N]: "
		read -r confirm </dev/tty
	else
		echo "  No interactive terminal available. Use --yes to skip confirmation."
		exit 1
	fi

	case "$confirm" in
	[Yy] | [Yy][Ee][Ss]) ;;
	*)
		echo "  Cancelled."
		exit 0
		;;
	esac
}

remove_shell_aliases() {
	local config_files=(
		"$HOME/.bashrc"
		"$HOME/.bash_profile"
		"$HOME/.zshrc"
		"$HOME/.config/fish/config.fish"
	)

	for config_file in "${config_files[@]}"; do
		if [ ! -f "$config_file" ]; then
			continue
		fi
		local config_target="$config_file"
		if [ -L "$config_file" ]; then
			if ! pilot_python_available; then
				mark_cleanup_failure "Skipped symlinked shell config (Python runner unavailable): $config_file"
				continue
			fi
			if ! config_target=$(PILOT_CONFIG_PATH="$config_file" pilot_python -c 'import os; print(os.path.realpath(os.environ["PILOT_CONFIG_PATH"]))'); then
				mark_cleanup_failure "Could not resolve symlinked shell config: $config_file"
				continue
			fi
		fi

		# shellcheck disable=SC2016 # Match literal $HOME text in shell config files.
		if ! grep -q -e "$CLAUDE_ALIAS_MARKER" \
			-e "$OLD_CLAUDE_PILOT_MARKER" \
			-e "$OLD_CCP_MARKER" \
			-e '/.pilot/bin' \
			-e 'PILOT_SESSION_ID' \
			"$config_target" 2>/dev/null; then
			continue
		fi

		local tmp_file
		tmp_file=$(mktemp "${config_target}.pilot-uninstall.XXXXXX")

		awk '
		function owned(text) {
			return text ~ /(PILOT_SESSION_ID|CLAUDE_CODE_TASK_LIST_ID|\/\.pilot\/bin|wrapper\.py)/
		}
		function brace_delta(text, opens, closes) {
			opens = gsub(/\{/, "{", text)
			closes = gsub(/\}/, "}", text)
			return opens - closes
		}
		function flush_buffer() {
			if (!owned(buffer)) printf "%s", buffer
			buffer = ""
			in_brace = 0
			in_fish = 0
			depth = 0
		}
		/^[[:space:]]*# Pilot Shell[[:space:]]*$/ || /^[[:space:]]*# End Pilot Shell[[:space:]]*$/ || /^[[:space:]]*# Claude Pilot[[:space:]]*$/ || /^[[:space:]]*# Claude CodePro alias[[:space:]]*$/ { next }
		in_brace {
			buffer = buffer $0 ORS
			depth += brace_delta($0)
			if (depth <= 0) flush_buffer()
			next
		}
		in_fish {
			buffer = buffer $0 ORS
			if ($0 ~ /^[[:space:]]*end[[:space:]]*$/) flush_buffer()
			next
		}
		/^[[:space:]]*export PATH="\$HOME\/\.pilot\/bin:\$HOME\/\.bun\/bin:\$PATH"[[:space:]]*$/ { next }
		/^[[:space:]]*export PATH="\$HOME\/\.pilot\/bin:\$PATH"[[:space:]]*$/ { next }
		/^[[:space:]]*set -gx PATH "\$HOME\/\.pilot\/bin" "\$HOME\/\.bun\/bin" \$PATH[[:space:]]*$/ { next }
		/^[[:space:]]*alias (pilot|ccp)=.*\/\.pilot\/bin\/pilot/ { next }
		/^[[:space:]]*alias ccp=.*wrapper\.py/ { next }
		/^[[:space:]]*(ccp|claude|codex|pilot)[[:space:]]*\(\).*(PILOT_SESSION_ID|CLAUDE_CODE_TASK_LIST_ID)/ { next }
		/^[[:space:]]*function[[:space:]]+(ccp|claude|codex|pilot).*(PILOT_SESSION_ID|CLAUDE_CODE_TASK_LIST_ID)/ { next }
		/^[[:space:]]*(ccp|claude|codex|pilot)[[:space:]]*\(\)[[:space:]]*\{/ {
			buffer = $0 ORS
			depth = brace_delta($0)
			if (depth > 0) in_brace = 1; else flush_buffer()
			next
		}
		/^[[:space:]]*function[[:space:]]+(ccp|claude|codex|pilot)([[:space:];]|$)/ {
			buffer = $0 ORS
			if ($0 ~ /;[[:space:]]*end[[:space:]]*$/) flush_buffer(); else in_fish = 1
			next
		}
		{ print }
		END { if (buffer != "") flush_buffer() }
		' "$config_target" >"$tmp_file"

		awk 'NR==1{print; next} /^[[:space:]]*$/{if(blank) next; blank=1; print; next} {blank=0; print}' "$tmp_file" >"${tmp_file}.clean"
		mv "${tmp_file}.clean" "$tmp_file"

		local original_mode=""
		original_mode=$(stat -f '%Lp' "$config_target" 2>/dev/null) || original_mode=$(stat -c '%a' "$config_target" 2>/dev/null) || true
		if [ -n "$original_mode" ]; then
			chmod "$original_mode" "$tmp_file"
		fi
		mv "$tmp_file" "$config_target"

		local name
		name=$(basename "$config_file")
		echo "    [OK] Cleaned $name"
		removed_items+=("shell aliases in $name")
	done
}

remove_manifest_files() {
	if [ ! -f "$MANIFEST_FILE" ]; then
		return
	fi
	if ! pilot_python_available; then
		mark_cleanup_failure "Skipped Claude manifest cleanup (python3 missing)"
		return
	fi

	local entries
	if ! entries=$(PILOT_MANIFEST_FILE="$MANIFEST_FILE" pilot_python -c '
import json, os, stat, sys, tempfile
try:
    with open(os.environ["PILOT_MANIFEST_FILE"]) as f:
        data = json.load(f)
except Exception:
    sys.exit(1)
files = data.get("files") if isinstance(data, dict) else None
if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
    sys.exit(1)
print("\n".join(files))
'); then
		mark_cleanup_failure "Could not read Pilot ownership manifest: $MANIFEST_FILE"
		return
	fi
	if [ -z "$entries" ]; then
		return
	fi

	local removed_count=0
	while IFS= read -r entry; do
		if ! is_safe_manifest_entry "$entry"; then
			echo "    [!!] Skipped unsafe manifest entry: $entry"
			continue
		fi
		local file_path="$CLAUDE_DIR/$entry"
		if [ -f "$file_path" ]; then
			rm -f "$file_path"
			removed_count=$((removed_count + 1))
		fi
	done <<<"$entries"

	if [ "$removed_count" -gt 0 ]; then
		echo "    [OK] Removed $removed_count Pilot-managed file(s) from ~/.claude/"
		removed_items+=("$removed_count file(s) from ~/.claude/")
	fi

	for subdir in "commands" "skills" "rules" "agents" "hooks"; do
		local dir="$CLAUDE_DIR/$subdir"
		if [ -d "$dir" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
			rmdir "$dir" 2>/dev/null || true
		fi
	done
}

is_safe_manifest_entry() {
	local entry="$1"
	local parent="$CLAUDE_DIR"
	local remaining="$entry"
	local segment

	case "$entry" in
	commands/* | skills/* | rules/* | agents/* | hooks/*) ;;
	*) return 1 ;;
	esac
	case "/$entry/" in
	*"/../"* | *"/./"* | *"//"*) return 1 ;;
	esac
	case "$entry" in
	*\\*) return 1 ;;
	esac

	while [ "$remaining" != "${remaining#*/}" ]; do
		segment="${remaining%%/*}"
		parent="$parent/$segment"
		if [ -L "$parent" ]; then
			return 1
		fi
		remaining="${remaining#*/}"
	done
	return 0
}

run_surgical_cleanup() {
	local target_file="$1"
	local baseline_file="$2"
	local display_path="$3"

	if [ ! -f "$target_file" ] || [ ! -f "$baseline_file" ]; then
		return
	fi

	if ! pilot_python_available; then
		return
	fi

	PILOT_TARGET="$target_file" PILOT_BASELINE_FILE="$baseline_file" PILOT_DISPLAY="$display_path" pilot_python -c '
import json, os, stat, sys, tempfile

logical_target_file = os.environ["PILOT_TARGET"]
target_file = os.path.realpath(logical_target_file)
baseline_file = os.path.realpath(os.environ["PILOT_BASELINE_FILE"])
display_path = os.environ["PILOT_DISPLAY"]

def remove_baseline_entries(current, baseline):
    if not isinstance(current, dict) or not isinstance(baseline, dict):
        return current, current == baseline
    modified = False
    for key in list(baseline.keys()):
        if key not in current:
            continue
        if current[key] == baseline[key]:
            del current[key]
            modified = True
        elif isinstance(baseline[key], dict) and isinstance(current[key], dict):
            if key in {"statusLine", "fileSuggestion", "spinnerTipsOverride"}:
                continue
            current[key], fully_removed = remove_baseline_entries(current[key], baseline[key])
            if fully_removed or not current[key]:
                del current[key]
            modified = True
        elif isinstance(baseline[key], list) and isinstance(current[key], list):
            baseline_set = set(
                json.dumps(x, sort_keys=True) if isinstance(x, (dict, list)) else str(x)
                for x in baseline[key]
            )
            new_list = [
                x for x in current[key]
                if (json.dumps(x, sort_keys=True) if isinstance(x, (dict, list)) else str(x)) not in baseline_set
            ]
            if len(new_list) != len(current[key]):
                modified = True
                if new_list:
                    current[key] = new_list
                else:
                    del current[key]
        # Cohesive command objects are preserved whole when modified; deleting
        # baseline-equal siblings can invalidate them (for example statusLine
        # still needs type/padding after the user changes only command).
    return current, not current

try:
    with open(target_file) as f:
        current = json.load(f)
    with open(baseline_file) as f:
        baseline = json.load(f)
    current, is_empty = remove_baseline_entries(current, baseline)
    if is_empty and not os.path.islink(logical_target_file):
        os.remove(target_file)
        print(f"    [OK] Removed {display_path} (no user settings remained)")
    else:
        if is_empty:
            current = {}
        fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(target_file))
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(current, f, indent=2)
                f.write("\n")
            os.chmod(temp_path, stat.S_IMODE(os.stat(target_file).st_mode))
            os.replace(temp_path, target_file)
        except Exception:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
        print(f"    [OK] Cleaned Pilot entries from {display_path} (user settings preserved)")
except Exception as e:
    print(f"    [!!] Could not clean {display_path}: {e}", file=sys.stderr)
    sys.exit(1)
' 2>&1
}

remove_pilot_settings() {
	local settings_file="$CLAUDE_DIR/settings.json"
	local baseline="$CLAUDE_DIR/.pilot-settings-baseline.json"

	if [ ! -f "$settings_file" ]; then
		return
	fi

	if [ -f "$baseline" ] && pilot_python_available; then
		if ! run_surgical_cleanup "$settings_file" "$baseline" "${CLAUDE_DIR}/settings.json"; then
			mark_cleanup_failure "Could not clean ${CLAUDE_DIR}/settings.json"
		fi
	else
		mark_cleanup_failure "Skipped ${CLAUDE_DIR}/settings.json (baseline or python3 missing)"
	fi

	if [ -f "$settings_file" ] && [ -f "$HOOKS_BASELINE_FILE" ] && pilot_python_available; then
		if ! PILOT_SETTINGS="$settings_file" PILOT_HOOKS_BASELINE="$HOOKS_BASELINE_FILE" pilot_python -c '
import json, os, stat, sys, tempfile

settings_path = os.path.realpath(os.environ["PILOT_SETTINGS"])
baseline_path = os.path.realpath(os.environ["PILOT_HOOKS_BASELINE"])

def signature(entry):
    matcher = entry.get("matcher") or ""
    if not isinstance(matcher, str):
        matcher = str(matcher)
    cmds = []
    for h in entry.get("hooks", []) or []:
        if isinstance(h, dict):
            cmd = h.get("command")
            if isinstance(cmd, str):
                cmds.append(cmd)
    return (matcher, tuple(sorted(cmds)))

try:
    with open(settings_path) as f:
        settings = json.load(f)
    with open(baseline_path) as f:
        baseline_hooks = json.load(f)
except Exception as e:
    print(f"    [!!] Could not read settings.json or hooks baseline: {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(settings, dict) or not isinstance(baseline_hooks, dict):
    sys.exit(0)

current_hooks = settings.get("hooks")
if not isinstance(current_hooks, dict):
    sys.exit(0)

removed = 0
for event_key, baseline_entries in baseline_hooks.items():
    if event_key not in current_hooks or not isinstance(current_hooks[event_key], list):
        continue
    pilot_sigs = {signature(e) for e in (baseline_entries or [])}
    user_only = [e for e in current_hooks[event_key] if signature(e) not in pilot_sigs]
    pilot_removed = len(current_hooks[event_key]) - len(user_only)
    removed += pilot_removed
    if user_only:
        current_hooks[event_key] = user_only
    else:
        del current_hooks[event_key]

if not current_hooks:
    del settings["hooks"]

fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(settings_path))
try:
    with os.fdopen(fd, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    os.chmod(temp_path, stat.S_IMODE(os.stat(settings_path).st_mode))
    os.replace(temp_path, settings_path)
except Exception:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    raise

if removed > 0:
    print(f"    [OK] Removed {removed} Pilot hook entry(ies) from ~/.claude/settings.json")
'; then
			mark_cleanup_failure "Could not clean Pilot hooks from ${CLAUDE_DIR}/settings.json"
		fi
	elif [ -f "$settings_file" ] && [ -f "$HOOKS_BASELINE_FILE" ]; then
		mark_cleanup_failure "Skipped Pilot hook cleanup (python3 missing)"
	fi

	removed_items+=("${CLAUDE_DIR}/settings.json")
}

remove_claude_json_keys() {
	local claude_json="$CLAUDE_APP_CONFIG"
	local baseline="$CLAUDE_DIR/.pilot-claude-baseline.json"
	local mcp_baseline="$MCP_BASELINE_FILE"

	if [ ! -f "$claude_json" ]; then
		return
	fi

	if [ -f "$mcp_baseline" ] && pilot_python_available; then
		if ! PILOT_CLAUDE_JSON="$claude_json" PILOT_MCP_BASELINE="$mcp_baseline" pilot_python -c '
import json, os, stat, sys, tempfile

claude_json = os.path.realpath(os.environ["PILOT_CLAUDE_JSON"])
mcp_baseline = os.path.realpath(os.environ["PILOT_MCP_BASELINE"])

try:
    with open(claude_json) as f:
        current = json.load(f)
    with open(mcp_baseline) as f:
        baseline_mcp = json.load(f)
except Exception as e:
    print(f"    [!!] Could not read claude.json or MCP baseline: {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(current, dict) or not isinstance(baseline_mcp, dict):
    sys.exit(0)

current_mcp = current.get("mcpServers")
if not isinstance(current_mcp, dict):
    sys.exit(0)

removed = 0
preserved_modified = 0
for name, baseline_value in baseline_mcp.items():
    if name in current_mcp:
        if current_mcp[name] == baseline_value:
            del current_mcp[name]
            removed += 1
        else:
            preserved_modified += 1
if not current_mcp:
    del current["mcpServers"]
if removed > 0:
    print(f"    [OK] Removed {removed} Pilot MCP server(s) from ~/.claude.json")
if preserved_modified > 0:
    print(f"    [OK] Preserved {preserved_modified} user-modified MCP server(s) in ~/.claude.json")

fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(claude_json))
try:
    with os.fdopen(fd, "w") as f:
        json.dump(current, f, indent=2)
        f.write("\n")
    os.chmod(temp_path, stat.S_IMODE(os.stat(claude_json).st_mode))
    os.replace(temp_path, claude_json)
except Exception:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    raise
'; then
			mark_cleanup_failure "Could not clean Pilot MCP servers from ${CLAUDE_APP_CONFIG}"
		fi
	elif [ -f "$mcp_baseline" ]; then
		mark_cleanup_failure "Skipped Pilot MCP cleanup (python3 missing)"
	fi

	if [ -f "$baseline" ]; then
		if pilot_python_available; then
			if ! run_surgical_cleanup "$claude_json" "$baseline" "${CLAUDE_APP_CONFIG}"; then
				mark_cleanup_failure "Could not clean ${CLAUDE_APP_CONFIG}"
			fi
		else
			mark_cleanup_failure "Skipped ${CLAUDE_APP_CONFIG} cleanup (python3 missing)"
		fi
	fi
	removed_items+=("${CLAUDE_APP_CONFIG}")
}

uninstall_lsp_plugins() {
	if [ ! -f "$LSP_MANIFEST_FILE" ]; then
		return
	fi

	if ! command -v claude >/dev/null 2>&1; then
		mark_cleanup_failure "Skipped LSP plugin uninstall (claude CLI not found)"
		return
	fi

	local plugin_ids
	if ! plugin_ids=$(PILOT_LSP_MANIFEST="$LSP_MANIFEST_FILE" pilot_python -c '
import json, os, stat, sys, tempfile
allowed = {
    "vtsls@claude-code-lsps",
    "basedpyright@claude-code-lsps",
    "gopls@claude-code-lsps",
}
try:
    with open(os.environ["PILOT_LSP_MANIFEST"]) as f:
        data = json.load(f)
except Exception:
    sys.exit(1)
plugins = data.get("plugins") if isinstance(data, dict) else None
if not isinstance(plugins, list) or not all(isinstance(value, str) for value in plugins):
    sys.exit(1)
if len(plugins) != len(set(plugins)):
    sys.exit(1)
if any(value not in allowed for value in plugins):
    sys.exit(1)
print("\n".join(plugins))
'); then
		mark_cleanup_failure "Could not read Pilot LSP ownership manifest"
		return
	fi
	if [ -z "$plugin_ids" ]; then
		rm -f "$LSP_MANIFEST_FILE"
		return
	fi

	local removed_count=0
	local failed_count=0
	local failed_ids=""
	while IFS= read -r plugin_id; do
		[ -z "$plugin_id" ] && continue
		if claude plugins uninstall "$plugin_id" >/dev/null 2>&1; then
			removed_count=$((removed_count + 1))
		else
			failed_count=$((failed_count + 1))
			failed_ids="${failed_ids}|${plugin_id}"
		fi
	done <<<"$plugin_ids"

	if [ "$removed_count" -gt 0 ]; then
		echo "    [OK] Uninstalled $removed_count Pilot-installed LSP plugin(s)"
		removed_items+=("$removed_count LSP plugin(s)")
	fi
	if [ "$failed_count" -gt 0 ]; then
		if ! PILOT_LSP_MANIFEST="$LSP_MANIFEST_FILE" PILOT_FAILED_PLUGINS="$failed_ids" pilot_python -c '
import json, os, stat, sys, tempfile
manifest = os.path.realpath(os.environ["PILOT_LSP_MANIFEST"])
plugins = [value for value in os.environ["PILOT_FAILED_PLUGINS"].split("|") if value]
fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(manifest))
try:
    with os.fdopen(fd, "w") as f:
        json.dump({"plugins": sorted(set(plugins))}, f, indent=2)
        f.write("\n")
    os.chmod(temp_path, stat.S_IMODE(os.stat(manifest).st_mode))
    os.replace(temp_path, manifest)
except Exception:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    sys.exit(1)
'; then
			mark_cleanup_failure "Could not update failed LSP ownership manifest"
			return
		fi
		mark_cleanup_failure "Could not uninstall $failed_count Pilot-owned LSP plugin(s)"
		return
	fi
	rm -f "$LSP_MANIFEST_FILE"
}

uninstall_extra_plugins() {
	# Historical installs did not record whether these plugins pre-dated Pilot.
	# Presence is not ownership, so preserve plugins/marketplaces and remove only
	# the exact legacy hook file Pilot created. Manual commands are printed later.
	local removed_count=0
	for hook_file in "${LEGACY_HOOK_FILES[@]}"; do
		if [ -f "$CLAUDE_DIR/hooks/$hook_file" ]; then
			rm -f "$CLAUDE_DIR/hooks/$hook_file"
			removed_count=$((removed_count + 1))
		fi
	done

	if [ "$removed_count" -gt 0 ]; then
		echo "    [OK] Removed $removed_count legacy Pilot plugin hook file(s)"
		removed_items+=("$removed_count legacy plugin hook file(s)")
	fi
}

remove_pilot_baselines() {
	local files=(
		"$CLAUDE_DIR/.pilot-settings-baseline.json"
		"$CLAUDE_DIR/.pilot-claude-baseline.json"
		"$HOOKS_BASELINE_FILE"
		"$MCP_BASELINE_FILE"
		"$CLAUDE_DIR/.pilot-manifest.json"
	)

	for file in "${files[@]}"; do
		if [ -f "$file" ]; then
			rm -f "$file"
			echo "    [OK] Removed $(basename "$file")"
			removed_items+=("$(basename "$file")")
		fi
	done
}

remove_pilot_plugin() {
	# Legacy directory from pre-9.x installs; modern Pilot does not create it.
	# Kept here so `uninstall.sh` cleans up after users who haven't run a recent
	# install (which would have removed it as part of the post-install migration).
	if [ -d "$PILOT_PLUGIN_DIR" ]; then
		rm -rf "$PILOT_PLUGIN_DIR"
		echo "    [OK] Removed legacy ${CLAUDE_DIR}/pilot/"
		removed_items+=("${CLAUDE_DIR}/pilot/ (legacy)")
	fi
}

remove_pilot_dir() {
	if [ ! -d "$PILOT_DIR" ]; then
		return
	fi
	if [ "$PURGE_DATA" = true ]; then
		local purge_entry
		for purge_entry in "$PILOT_DIR"/* "$PILOT_DIR"/.[!.]* "$PILOT_DIR"/..?*; do
			if [ ! -e "$purge_entry" ] && [ ! -L "$purge_entry" ]; then
				continue
			fi
			if [ "$purge_entry" = "$INSTALL_LOCK_DIR" ]; then
				continue
			fi
			rm -rf "$purge_entry"
		done
		echo "    [OK] Removed ~/.pilot/ including Pilot user data"
		removed_items+=("Pilot home and user data (~/.pilot/)")
		return
	fi

	# Remove only runtime/distributable entries. Data and unknown files remain
	# unless the user explicitly requested --purge-data.
	local managed_entries=(
		"agents"
		"bin"
		"codex"
		"hooks"
		"installer"
		"node_modules"
		"rules"
		"scripts"
		"skills"
		"ui"
		"bun.lock"
		"claude.json"
		"package-lock.json"
		"package.json"
		".mcp.json"
	)
	local entry
	for entry in "${managed_entries[@]}"; do
		rm -rf "${PILOT_DIR:?}/$entry"
	done
	rm -rf "$PILOT_DIR"/.bin-stage.* "$PILOT_DIR"/.bin-backup.* "$PILOT_DIR"/.bin-committed-backup.*

	local has_preserved_data=false
	for entry in "$PILOT_DIR"/* "$PILOT_DIR"/.[!.]* "$PILOT_DIR"/..?*; do
		if { [ -e "$entry" ] || [ -L "$entry" ]; } && [ "$entry" != "$INSTALL_LOCK_DIR" ]; then
			has_preserved_data=true
			break
		fi
	done
	if [ "$has_preserved_data" = false ]; then
		echo "    [OK] Removed ~/.pilot/ runtime"
		removed_items+=("Pilot runtime (~/.pilot/)")
	else
		echo "    [OK] Removed Pilot runtime; User data preserved in ~/.pilot/"
		removed_items+=("Pilot runtime (user data preserved in ~/.pilot/)")
	fi
}

remove_codex_files() {
	if ! has_codex_pilot_content; then
		return
	fi
	if ! pilot_python_available; then
		mark_cleanup_failure "Skipped Codex cleanup (working python3 not available)"
		return
	fi

	# Remove Pilot-managed hook entries from ~/.codex/hooks.json by the exact
	# signatures recorded at install time. A narrow path heuristic is retained
	# only for legacy installs that predate the baseline file.
	local hooks_file="$CODEX_DIR/hooks.json"
	local hooks_baseline="$CODEX_DIR/.pilot-hooks-baseline.json"
	if [ -f "$hooks_file" ] && [ ! -f "$hooks_baseline" ]; then
		mark_cleanup_failure "Skipped Codex hook cleanup (ownership baseline missing)"
	elif [ -f "$hooks_file" ]; then
		if ! PILOT_CODEX_HOOKS="$hooks_file" PILOT_CODEX_HOOKS_BASELINE="$hooks_baseline" pilot_python -c '
import json, os, stat, sys, tempfile

hooks_path = os.path.realpath(os.environ["PILOT_CODEX_HOOKS"])
baseline_path = os.path.realpath(os.environ["PILOT_CODEX_HOOKS_BASELINE"])
try:
    with open(hooks_path) as f:
        data = json.load(f)
except Exception:
    sys.exit(1)

if not isinstance(data, dict):
    sys.exit(1)

hooks = data.get("hooks")
if not isinstance(hooks, dict):
    sys.exit(1)

def signature(entry):
    matcher = entry.get("matcher") or ""
    commands = sorted(
        h.get("command") for h in entry.get("hooks", [])
        if isinstance(h, dict) and isinstance(h.get("command"), str)
    )
    return (str(matcher), tuple(commands))

try:
    with open(baseline_path) as f:
        baseline = json.load(f)
    if not isinstance(baseline, dict):
        baseline = {}
except Exception:
    sys.exit(1)

baseline_sigs = {
    event: {signature(entry) for entry in entries if isinstance(entry, dict)}
    for event, entries in baseline.items() if isinstance(entries, list)
}

removed = 0
for event in list(hooks.keys()):
    if not isinstance(hooks[event], list):
        continue
    filtered = []
    for entry in hooks[event]:
        if not isinstance(entry, dict):
            filtered.append(entry)
            continue
        is_pilot = signature(entry) in baseline_sigs.get(event, set())
        if is_pilot:
            removed += 1
        else:
            filtered.append(entry)
    if filtered:
        hooks[event] = filtered
    else:
        del hooks[event]

if not hooks:
    del data["hooks"]

fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(hooks_path))
try:
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.chmod(temp_path, stat.S_IMODE(os.stat(hooks_path).st_mode))
    os.replace(temp_path, hooks_path)
except Exception:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    raise

if removed > 0:
    print(f"    [OK] Removed {removed} Pilot hook(s) from ~/.codex/hooks.json")
' 2>&1; then
			mark_cleanup_failure "Could not clean Pilot hooks from $hooks_file"
		else
			rm -f "$hooks_baseline"
		fi
	elif [ -f "$hooks_baseline" ]; then
		rm -f "$hooks_baseline"
	fi

	# Remove Pilot managed MCP server and env var blocks from ~/.codex/config.toml.
	local config_file="$CODEX_DIR/config.toml"
	if [ -f "$config_file" ] && pilot_python_available && grep -q -e 'pilot-shell managed MCP servers' -e 'pilot-shell managed env vars' "$config_file" 2>/dev/null; then
		if ! PILOT_CODEX_CONFIG="$config_file" pilot_python -c '
import os, stat, sys, tempfile

config_path = os.path.realpath(os.environ["PILOT_CODEX_CONFIG"])
marker_pairs = [
    ("# --- pilot-shell managed MCP servers ---", "# --- end pilot-shell managed MCP servers ---"),
    ("# --- pilot-shell managed env vars ---", "# --- end pilot-shell managed env vars ---"),
]

try:
    with open(config_path) as f:
        content = f.read()
except Exception:
    sys.exit(1)

changed = False
for marker_start, marker_end in marker_pairs:
    start_count = content.count(marker_start)
    end_count = content.count(marker_end)
    if start_count == 0 and end_count == 0:
        continue
    if start_count != 1 or end_count != 1 or content.index(marker_start) > content.index(marker_end):
        print(f"Malformed Pilot marker pair in {config_path}; preserving file", file=sys.stderr)
        sys.exit(1)

    start_idx = content.index(marker_start)
    end_idx = content.index(marker_end) + len(marker_end)

    before = content[:start_idx].rstrip("\n")
    after = content[end_idx:].lstrip("\n")

    if before and after.strip():
        content = before + "\n\n" + after
    elif before:
        content = before + "\n"
    else:
        content = after
    changed = True

if not changed:
    sys.exit(0)

fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(config_path))
try:
    with os.fdopen(fd, "w") as f:
        f.write(content)
    os.chmod(temp_path, stat.S_IMODE(os.stat(config_path).st_mode))
    os.replace(temp_path, config_path)
except Exception:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    raise

print("    [OK] Removed Pilot managed config block(s) from ~/.codex/config.toml")
' 2>&1; then
			mark_cleanup_failure "Could not safely clean Pilot blocks from $config_file"
		fi
	fi

	# Remove the generated expanded-context catalog and only the exact config
	# pointer written by installer/steps/codex_files.py. User catalog settings
	# with any other path remain untouched.
	local model_catalog_file="$CODEX_DIR/.pilot-model-catalog.json"
	if { [ -f "$model_catalog_file" ] || grep -q '.pilot-model-catalog.json' "$config_file" 2>/dev/null; } && pilot_python_available; then
		if ! PILOT_CODEX_CONFIG="$config_file" PILOT_CODEX_MODEL_CATALOG="$model_catalog_file" pilot_python -c '
import json, os, stat, sys, tempfile

config_path = os.path.realpath(os.environ["PILOT_CODEX_CONFIG"])
catalog_path = os.path.realpath(os.environ["PILOT_CODEX_MODEL_CATALOG"])

if os.path.exists(config_path):
    try:
        with open(config_path) as f:
            lines = f.readlines()
    except OSError:
        sys.exit(1)
else:
    lines = []

filtered = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith("model_catalog_json") and "=" in stripped:
        try:
            configured = json.loads(stripped.split("=", 1)[1].strip())
        except Exception:
            configured = None
        if isinstance(configured, str) and os.path.realpath(configured) == catalog_path:
            continue
    filtered.append(line)
if filtered != lines:
    fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(config_path))
    try:
        with os.fdopen(fd, "w") as f:
            f.writelines(filtered)
        os.chmod(temp_path, stat.S_IMODE(os.stat(config_path).st_mode))
        os.replace(temp_path, config_path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise

try:
    os.remove(catalog_path)
except FileNotFoundError:
    pass
except OSError:
    sys.exit(1)

print("    [OK] Removed Pilot managed Codex model catalog")
' 2>&1; then
			mark_cleanup_failure "Could not safely remove Pilot Codex model catalog"
		fi
	fi

	# Remove <!-- PILOT:START --> ... <!-- PILOT:END --> block from ~/.codex/AGENTS.md.
	local agents_file="$CODEX_DIR/AGENTS.md"
	if [ -f "$agents_file" ] && pilot_python_available && grep -q 'PILOT:START' "$agents_file" 2>/dev/null; then
		if ! PILOT_CODEX_AGENTS="$agents_file" pilot_python -c '
import os, stat, sys, tempfile

logical_agents_path = os.environ["PILOT_CODEX_AGENTS"]
agents_path = os.path.realpath(logical_agents_path)
marker_start = "<!-- PILOT:START -->"
marker_end = "<!-- PILOT:END -->"

try:
    with open(agents_path) as f:
        content = f.read()
except Exception:
    sys.exit(1)

if content.count(marker_start) != 1 or content.count(marker_end) != 1:
    print(f"Malformed Pilot markers in {agents_path}; preserving file", file=sys.stderr)
    sys.exit(1)
if content.index(marker_start) > content.index(marker_end):
    print(f"Reversed Pilot markers in {agents_path}; preserving file", file=sys.stderr)
    sys.exit(1)

start_idx = content.index(marker_start)
end_idx = content.index(marker_end) + len(marker_end)

before = content[:start_idx].rstrip("\n")
after = content[end_idx:].lstrip("\n")

if before and after.strip():
    result = before + "\n\n" + after
elif before:
    result = before + "\n"
else:
    result = after

if not result.strip() and not os.path.islink(logical_agents_path):
    os.remove(agents_path)
    print("    [OK] Removed ~/.codex/AGENTS.md (no user content remained)")
else:
    if not result.strip():
        result = ""
    fd, temp_path = tempfile.mkstemp(prefix=".pilot-uninstall-", dir=os.path.dirname(agents_path))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(result)
        os.chmod(temp_path, stat.S_IMODE(os.stat(agents_path).st_mode))
        os.replace(temp_path, agents_path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise
    print("    [OK] Removed Pilot managed block from ~/.codex/AGENTS.md (user content preserved)")
' 2>&1; then
			mark_cleanup_failure "Could not safely clean Pilot block from $agents_file"
		fi
	fi

	# Remove Pilot-managed stack rules from ~/.codex/rules/.
	# Scope comes from the .pilot-rules.json sidecar the installer writes, so a
	# user file dropped in the same directory is never touched. The directory is
	# removed only once nothing but the manifest remains.
	local codex_rules_manifest="$CODEX_DIR/rules/.pilot-rules.json"
	if [ -f "$codex_rules_manifest" ] && [ -L "$CODEX_DIR/rules" ]; then
		mark_cleanup_failure "Skipped Codex rules cleanup (rules directory is a symlink)"
	elif [ -f "$codex_rules_manifest" ] && pilot_python_available; then
		if ! PILOT_CODEX_RULES="$codex_rules_manifest" pilot_python -c '
import json, os, sys

manifest_path = os.environ["PILOT_CODEX_RULES"]
rules_dir = os.path.dirname(manifest_path)

try:
    with open(manifest_path) as f:
        names = json.load(f)
except Exception:
    sys.exit(1)

if not isinstance(names, list):
    sys.exit(1)

removed = 0
for name in names:
    target = os.path.join(rules_dir, str(name))
    if os.path.dirname(target) != rules_dir:
        continue
    try:
        os.remove(target)
        removed += 1
    except FileNotFoundError:
        pass
    except OSError:
        sys.exit(1)

try:
    os.remove(manifest_path)
except OSError:
    sys.exit(1)

try:
    os.rmdir(rules_dir)
except OSError:
    pass

if removed > 0:
    print(f"    [OK] Removed {removed} Pilot stack rule(s) from ~/.codex/rules/")
' 2>&1; then
			mark_cleanup_failure "Could not safely remove Pilot Codex stack rules"
		fi
	fi

	# Remove only Pilot-recorded files from managed ~/.agents/skills/ entries.
	# SKILL.md and agents/openai.yaml are generated by Pilot; runtime resources are
	# scoped by .pilot-resources.json. User-added siblings keep the directory alive.
	local removed_skills=0
	local removed_agents=0
	if [ -L "$CODEX_DIR/agents" ]; then
		mark_cleanup_failure "Skipped Codex review-agent cleanup (agents directory is a symlink)"
	else
	for agent in "${CODEX_PILOT_REVIEW_AGENTS[@]}"; do
		local agent_file="$CODEX_DIR/agents/$agent.toml"
		if [ -f "$agent_file" ] && grep -q 'pilot-shell managed Codex review agent' "$agent_file" 2>/dev/null; then
			rm -f "$agent_file"
			removed_agents=$((removed_agents + 1))
		fi
	done
	if [ "$removed_agents" -gt 0 ]; then
		echo "    [OK] Removed ${removed_agents} Pilot-managed Codex review agent(s)"
		removed_items+=("${removed_agents} Codex review agent(s)")
	fi
	rmdir "$CODEX_DIR/agents" 2>/dev/null || true
	fi

	for skill in "${CODEX_PILOT_SKILLS[@]}"; do
		local skill_dir="$AGENTS_SKILLS_DIR/$skill"
		local skill_file="$skill_dir/SKILL.md"
		local resources_manifest="$skill_dir/.pilot-resources.json"
		if [ ! -f "$resources_manifest" ]; then
			continue
		fi
		if [ -L "$skill_dir" ]; then
			mark_cleanup_failure "Skipped Codex skill cleanup for symlinked directory: $skill_dir"
			continue
		fi
		if [ -L "$skill_dir/agents" ]; then
			mark_cleanup_failure "Skipped Codex skill cleanup with symlinked agents directory: $skill_dir"
			continue
		fi
		if [ -f "$resources_manifest" ] && pilot_python_available; then
			if ! PILOT_CODEX_SKILL_DIR="$skill_dir" pilot_python -c '
import json, os, sys

root = os.path.realpath(os.environ["PILOT_CODEX_SKILL_DIR"])
manifest = os.path.join(root, ".pilot-resources.json")
try:
    with open(manifest) as f:
        data = json.load(f)
except Exception:
    sys.exit(1)
if not isinstance(data, dict):
    sys.exit(1)

def safe_path(value):
    if not isinstance(value, str) or not value:
        return None
    parts = value.replace("\\", "/").split("/")
    if value.startswith(("/", "\\")) or ".." in parts:
        return None
    target = os.path.abspath(os.path.join(root, *parts))
    try:
        if os.path.commonpath([root, target]) != root:
            return None
    except ValueError:
        return None
    parent = root
    for part in parts[:-1]:
        parent = os.path.join(parent, part)
        if os.path.islink(parent):
            return None
    return target

files = data.get("files", [])
files = files if isinstance(files, list) else []
for relative in sorted(files, key=lambda value: (-str(value).count("/"), str(value))):
    target = safe_path(relative)
    if target and (os.path.isfile(target) or os.path.islink(target)):
        try:
            os.remove(target)
        except FileNotFoundError:
            pass
        except OSError:
            sys.exit(1)

directories = data.get("directories", [])
directories = directories if isinstance(directories, list) else []
for relative in sorted(directories, key=lambda value: (-str(value).count("/"), str(value))):
    target = safe_path(relative)
    if target and os.path.isdir(target) and not os.path.islink(target):
        try:
            os.rmdir(target)
        except OSError:
            pass
' 2>&1; then
				mark_cleanup_failure "Could not safely remove resources for Codex skill $skill"
				continue
			fi
		fi

		local removed_skill=false
		if [ -f "$skill_file" ]; then
			rm -f "$skill_file"
			removed_skill=true
		fi
		if [ -f "$skill_dir/agents/openai.yaml" ]; then
			rm -f "$skill_dir/agents/openai.yaml"
			removed_skill=true
		fi
		rm -f "$resources_manifest"
		rmdir "$skill_dir/agents" 2>/dev/null || true
		if [ "$removed_skill" = true ]; then
			removed_skills=$((removed_skills + 1))
		fi
		if [ -d "$skill_dir" ] && [ -z "$(ls -A "$skill_dir" 2>/dev/null)" ]; then
			rmdir "$skill_dir" 2>/dev/null || true
		fi
	done
	if [ "$removed_skills" -gt 0 ]; then
		echo "    [OK] Removed ${removed_skills} Pilot skill(s) from ~/.agents/skills/"
		removed_items+=("${removed_skills} Codex skill(s) from ~/.agents/skills/")
	fi

	removed_items+=("Codex integration (~/.codex/)")
}

print_summary() {
	echo ""
	echo "======================================================================"

	if [ "$cleanup_failed" = true ]; then
		echo "  Pilot Shell was partially uninstalled."
		echo "  Recovery metadata and ~/.pilot runtime/data were preserved so you can retry safely."
	elif [ ${#removed_items[@]} -eq 0 ]; then
		echo "  Nothing to remove. Pilot Shell does not appear to be installed."
	else
		echo "  Pilot Shell has been uninstalled."
		echo ""
		echo "  Removed ${#removed_items[@]} items:"
		for item in "${removed_items[@]}"; do
			echo "    - $item"
		done
	fi

	echo ""
	if [ -f "$CODEX_DIR/config.toml" ]; then
		echo "  Note: ~/.codex/config.toml may still contain settings that Pilot added"
		echo "  (approval_policy, sandbox_mode, model config, [features], [tui], etc.)."
		echo "  These are standard Codex settings and were intentionally left intact."
		echo "  Edit ~/.codex/config.toml manually if you want to revert them."
		echo ""
	fi

	echo "  To fully clean up third-party tools installed by Pilot:"
	echo "    - Claude Code:    npm uninstall -g @anthropic-ai/claude-code"
	echo "    - Codex plugin:   claude plugins uninstall codex@openai-codex -y"
	echo "    - Chrome plugin:  claude plugins uninstall chrome-devtools-mcp@chrome-devtools-plugins -y"
	echo "    - CodeGraph:      npm uninstall -g @colbymchenry/codegraph"
	echo "    - Semble setup:   semble uninstall"
	echo "    - Semble indexes: semble clear all  # optional; deletes cached indexes"
	echo "    - Semble:         uv tool uninstall semble"
	echo "    - Semble uv cache: uv cache clean semble  # optional package-download cache"
	echo "    - RTK Claude:     rtk init -g --uninstall"
	echo "    - RTK Codex:      rtk init -g --codex --uninstall"
	echo "    - better-sqlite3: npm uninstall -g better-sqlite3  # legacy Pilot installs only"
	echo "    - agent-browser:  npm uninstall -g agent-browser"
	echo "    - playwright-cli: npm uninstall -g @playwright/cli"
	echo "    - impeccable:     npm uninstall -g impeccable"
	echo "    - fast-check:     npm uninstall -g fast-check"
	echo "    - vtsls:          npm uninstall -g @vtsls/language-server typescript"
	echo "    - prettier:       npm uninstall -g prettier"
	echo "    - golangci-lint:  rm -f \$(go env GOPATH)/bin/golangci-lint"
	echo "    - Python tools:   uv tool uninstall ruff basedpyright"
	echo "    - Hypothesis:     uv tool uninstall hypothesis"
	echo ""
	echo "  Project indexes (.codegraph/) were intentionally left intact."
	echo "  Remove an index only from inside that project with 'codegraph uninit'."
	echo ""
	echo "  Homebrew packages (git, node, bun, go, etc.) were left intact."
	echo ""
	echo "  Please restart your terminal or run 'source ~/.zshrc' to apply changes."
	echo ""
	echo "======================================================================"
	echo ""
}

SKIP_CONFIRM=false
PURGE_DATA=false
while [ $# -gt 0 ]; do
	case "$1" in
	--yes | -y)
		SKIP_CONFIRM=true
		shift
		;;
	--purge-data)
		PURGE_DATA=true
		shift
		;;
	--help | -h)
		echo "Usage: uninstall.sh [--yes|-y] [--purge-data]"
		echo ""
		echo "Uninstall Pilot Shell and remove all installed files."
		echo ""
		echo "Options:"
		echo "  --yes, -y    Skip confirmation prompt"
		echo "  --purge-data Also delete memory, sessions, logs, configuration, and unknown files in ~/.pilot"
		echo "  --help, -h   Show this help message"
		exit 0
		;;
	*)
		echo "Unknown option: $1"
		echo "Run with --help for usage information."
		exit 1
		;;
	esac
done

if ! [ -d "$PILOT_DIR" ] && ! [ -d "$PILOT_PLUGIN_DIR" ] && ! [ -f "$MANIFEST_FILE" ] && ! [ -f "$CLAUDE_DIR/.pilot-settings-baseline.json" ] && ! [ -f "$CLAUDE_DIR/.pilot-claude-baseline.json" ] && ! [ -f "$HOOKS_BASELINE_FILE" ] && ! [ -f "$MCP_BASELINE_FILE" ] && ! [ -f "$LSP_MANIFEST_FILE" ] && [ -z "$(get_affected_shell_configs)" ] && ! has_codex_pilot_content; then
	echo ""
	echo "======================================================================"
	echo "  Pilot Shell Uninstaller"
	echo "======================================================================"
	echo ""
	echo "  Nothing to remove. Pilot Shell does not appear to be installed."
	echo ""
	echo "======================================================================"
	echo ""
	exit 0
fi

acquire_uninstall_lock

if [ "$SKIP_CONFIRM" = false ]; then
	confirm_uninstall
else
	echo ""
	echo "======================================================================"
	echo "  Pilot Shell Uninstaller"
	echo "======================================================================"
fi

echo ""
echo "  Uninstalling Pilot Shell..."
echo ""

remove_shell_aliases
remove_manifest_files
remove_pilot_settings
remove_claude_json_keys
uninstall_lsp_plugins
uninstall_extra_plugins
remove_codex_files

if [ "$cleanup_failed" = false ]; then
	remove_pilot_baselines
	remove_pilot_plugin
	remove_pilot_dir
else
	echo "    [!!] Preserved Pilot baselines and ~/.pilot because cleanup was incomplete"
fi

print_summary

if [ "$cleanup_failed" = true ]; then
	exit 1
fi
