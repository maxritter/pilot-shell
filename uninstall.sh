#!/bin/bash

set -e

PILOT_DIR="$HOME/.pilot"

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
else
	CLAUDE_DIR="$HOME/.claude"
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

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"

CODEX_PILOT_SKILLS=(
	"spec"
	"spec-plan"
	"spec-bugfix-plan"
	"spec-implement"
	"spec-verify"
	"spec-bugfix-verify"
	"fix"
	"prd"
	"benchmark"
	"setup-rules"
	"create-skill"
	"bot-boot"
	"bot-channel-task"
	"bot-defaults"
	"bot-heartbeat"
	"bot-jobs"
)

LSP_MARKETPLACE="claude-code-lsps"

EXTRA_PLUGIN_IDS=(
	"codex@openai-codex"
	"chrome-devtools-mcp@chrome-devtools-plugins"
)

LEGACY_PLUGIN_IDS=(
	"context-mode@context-mode"
)
LEGACY_MARKETPLACE_NAMES=(
	"context-mode"
)
LEGACY_HOOK_FILES=(
	"context-mode-cache-heal.mjs"
)

CLAUDE_ALIAS_MARKER="# Pilot Shell"
OLD_CLAUDE_PILOT_MARKER="# Claude Pilot"
OLD_CCP_MARKER="# Claude CodePro alias"

removed_items=()

has_codex_pilot_content() {
	if [ -f "$CODEX_DIR/hooks.json" ] && grep -q '/.pilot/' "$CODEX_DIR/hooks.json" 2>/dev/null; then
		return 0
	fi
	if [ -f "$CODEX_DIR/config.toml" ] && grep -q -e 'pilot-shell managed MCP servers' -e 'pilot-shell managed env vars' "$CODEX_DIR/config.toml" 2>/dev/null; then
		return 0
	fi
	if [ -f "$CODEX_DIR/AGENTS.md" ] && grep -q 'PILOT:START' "$CODEX_DIR/AGENTS.md" 2>/dev/null; then
		return 0
	fi
	for skill in "${CODEX_PILOT_SKILLS[@]}"; do
		if [ -d "$AGENTS_SKILLS_DIR/$skill" ]; then
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
		if [ -f "$config_file" ] && grep -q -e "$CLAUDE_ALIAS_MARKER" \
			-e "$OLD_CLAUDE_PILOT_MARKER" \
			-e "$OLD_CCP_MARKER" \
			-e "alias ccp=" \
			-e "alias pilot=" \
			-e "claude()" \
			-e "codex()" \
			-e "function claude" \
			-e "function codex" \
			-e 'PATH="$HOME/.pilot/bin' \
			-e 'PATH "$HOME/.pilot/bin' \
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
		echo "    • Remove ~/.pilot/ (binary, scripts, UI, MCP/app config)"
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

	if command -v claude >/dev/null 2>&1; then
		local extras_present=""
		local plugin_list
		plugin_list=$(claude plugins list 2>/dev/null)
		for plugin_id in "${EXTRA_PLUGIN_IDS[@]}" "${LEGACY_PLUGIN_IDS[@]}"; do
			if echo "$plugin_list" | grep -q "$plugin_id"; then
				extras_present="${extras_present}${plugin_id} "
			fi
		done
		if [ -n "$extras_present" ]; then
			echo "    • Uninstall Pilot-installed plugins: ${extras_present}"
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

		if ! grep -q -e "$CLAUDE_ALIAS_MARKER" \
			-e "$OLD_CLAUDE_PILOT_MARKER" \
			-e "$OLD_CCP_MARKER" \
			-e "alias ccp=" \
			-e "alias pilot=" \
			-e "claude()" \
			-e "codex()" \
			-e "function claude" \
			-e "function codex" \
			-e 'PATH="$HOME/.pilot/bin' \
			-e 'PATH "$HOME/.pilot/bin' \
			"$config_file" 2>/dev/null; then
			continue
		fi

		local tmp_file
		tmp_file=$(mktemp)

		awk '
		/# Pilot Shell/ { next }
		/# Claude Pilot/ { next }
		/# Claude CodePro alias/ { next }
		/^[[:space:]]*alias ccp=/ { next }
		/^[[:space:]]*alias pilot=/ { next }
		/^[[:space:]]*alias claude=/ { next }
		/^[[:space:]]*claude\(\)[[:space:]]*\{/ { next }
		/^[[:space:]]*codex\(\)[[:space:]]*\{/ { next }
		/^[[:space:]]*function[[:space:]]+claude([[:space:];]|$).*;[[:space:]]*end[[:space:]]*$/ { next }
		/^[[:space:]]*function[[:space:]]+codex([[:space:];]|$).*;[[:space:]]*end[[:space:]]*$/ { next }
		/^[[:space:]]*export PATH="\$HOME\/.pilot\/bin/ { next }
		/^[[:space:]]*set -gx PATH "\$HOME\/.pilot\/bin/ { next }
		/^[[:space:]]*export PATH="\$HOME\/.bun\/bin:\$PATH"/ { next }
		/^[[:space:]]*set -gx PATH "\$HOME\/.bun\/bin"/ { next }
		{ print }
		' "$config_file" >"$tmp_file"

		awk 'NR==1{print; next} /^[[:space:]]*$/{if(blank) next; blank=1; print; next} {blank=0; print}' "$tmp_file" >"${tmp_file}.clean"
		mv "${tmp_file}.clean" "$tmp_file"

		cp "$tmp_file" "$config_file"
		rm -f "$tmp_file"

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

	local entries
	entries=$(get_manifest_entries)
	if [ -z "$entries" ]; then
		return
	fi

	local removed_count=0
	while IFS= read -r entry; do
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

run_surgical_cleanup() {
	local target_file="$1"
	local baseline_file="$2"
	local display_path="$3"

	if [ ! -f "$target_file" ] || [ ! -f "$baseline_file" ]; then
		return
	fi

	if ! command -v python3 >/dev/null 2>&1; then
		return
	fi

	PILOT_TARGET="$target_file" PILOT_BASELINE_FILE="$baseline_file" PILOT_DISPLAY="$display_path" python3 -c '
import json, os, sys

target_file = os.environ["PILOT_TARGET"]
baseline_file = os.environ["PILOT_BASELINE_FILE"]
display_path = os.environ["PILOT_DISPLAY"]

def remove_baseline_entries(current, baseline):
    if not isinstance(current, dict) or not isinstance(baseline, dict):
        return current, current == baseline
    modified = False
    for key in list(baseline.keys()):
        if key not in current:
            continue
        if isinstance(baseline[key], dict) and isinstance(current[key], dict):
            current[key], fully_removed = remove_baseline_entries(current[key], baseline[key])
            if fully_removed or not current[key]:
                del current[key]
                modified = True
            else:
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
        elif current[key] == baseline[key]:
            del current[key]
            modified = True
    return current, not current

try:
    with open(target_file) as f:
        current = json.load(f)
    with open(baseline_file) as f:
        baseline = json.load(f)
    current, is_empty = remove_baseline_entries(current, baseline)
    if is_empty:
        os.remove(target_file)
        print(f"    [OK] Removed {display_path} (no user settings remained)")
    else:
        with open(target_file, "w") as f:
            json.dump(current, f, indent=2)
            f.write("\n")
        print(f"    [OK] Cleaned Pilot entries from {display_path} (user settings preserved)")
except Exception as e:
    print(f"    [!!] Could not clean {display_path}: {e}", file=sys.stderr)
' 2>&1
}

remove_pilot_settings() {
	local settings_file="$CLAUDE_DIR/settings.json"
	local baseline="$CLAUDE_DIR/.pilot-settings-baseline.json"

	if [ ! -f "$settings_file" ]; then
		return
	fi

	if [ -f "$baseline" ] && command -v python3 >/dev/null 2>&1; then
		run_surgical_cleanup "$settings_file" "$baseline" "${CLAUDE_DIR}/settings.json"
	else
		echo "    [!!] Skipped ~/.claude/settings.json (no baseline found, manual cleanup needed)"
	fi

	if [ -f "$settings_file" ] && [ -f "$HOOKS_BASELINE_FILE" ] && command -v python3 >/dev/null 2>&1; then
		PILOT_SETTINGS="$settings_file" PILOT_HOOKS_BASELINE="$HOOKS_BASELINE_FILE" python3 -c '
import json, os, sys

settings_path = os.environ["PILOT_SETTINGS"]
baseline_path = os.environ["PILOT_HOOKS_BASELINE"]

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
    sys.exit(0)

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

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

if removed > 0:
    print(f"    [OK] Removed {removed} Pilot hook entry(ies) from ~/.claude/settings.json")
'
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

	if [ -f "$mcp_baseline" ] && command -v python3 >/dev/null 2>&1; then
		PILOT_CLAUDE_JSON="$claude_json" PILOT_MCP_BASELINE="$mcp_baseline" python3 -c '
import json, os, sys

claude_json = os.environ["PILOT_CLAUDE_JSON"]
mcp_baseline = os.environ["PILOT_MCP_BASELINE"]

try:
    with open(claude_json) as f:
        current = json.load(f)
    with open(mcp_baseline) as f:
        baseline_mcp = json.load(f)
except Exception as e:
    print(f"    [!!] Could not read claude.json or MCP baseline: {e}", file=sys.stderr)
    sys.exit(0)

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

with open(claude_json, "w") as f:
    json.dump(current, f, indent=2)
    f.write("\n")
'
	fi

	if [ -f "$baseline" ]; then
		run_surgical_cleanup "$claude_json" "$baseline" "${CLAUDE_APP_CONFIG}"
	fi
	removed_items+=("${CLAUDE_APP_CONFIG}")
}

uninstall_lsp_plugins() {
	if [ ! -f "$LSP_MANIFEST_FILE" ]; then
		return
	fi

	if ! command -v claude >/dev/null 2>&1; then
		echo "    [!!] Skipped LSP plugin uninstall (claude CLI not found)"
		return
	fi

	local plugin_ids
	plugin_ids=$(grep -oE '"[a-z][a-z0-9-]*@'"$LSP_MARKETPLACE"'"' "$LSP_MANIFEST_FILE" 2>/dev/null | sed 's/"//g')
	if [ -z "$plugin_ids" ]; then
		rm -f "$LSP_MANIFEST_FILE"
		return
	fi

	local removed_count=0
	while IFS= read -r plugin_id; do
		[ -z "$plugin_id" ] && continue
		if claude plugins uninstall "$plugin_id" >/dev/null 2>&1; then
			removed_count=$((removed_count + 1))
		fi
	done <<<"$plugin_ids"

	if [ "$removed_count" -gt 0 ]; then
		echo "    [OK] Uninstalled $removed_count Pilot-installed LSP plugin(s)"
		removed_items+=("$removed_count LSP plugin(s)")
	fi
	rm -f "$LSP_MANIFEST_FILE"
}

uninstall_extra_plugins() {
	if ! command -v claude >/dev/null 2>&1; then
		echo "    [!!] Skipped non-LSP plugin uninstall (claude CLI not found)"
		return
	fi

	local removed_count=0
	local plugin_list
	plugin_list=$(claude plugins list 2>/dev/null)
	for plugin_id in "${EXTRA_PLUGIN_IDS[@]}" "${LEGACY_PLUGIN_IDS[@]}"; do
		if echo "$plugin_list" | grep -q "$plugin_id"; then
			if claude plugins uninstall "$plugin_id" -y >/dev/null 2>&1; then
				removed_count=$((removed_count + 1))
			fi
		fi
	done

	local marketplace_list
	marketplace_list=$(claude plugins marketplace list 2>/dev/null)
	for marketplace_name in "${LEGACY_MARKETPLACE_NAMES[@]}"; do
		if echo "$marketplace_list" | grep -q "$marketplace_name"; then
			claude plugins marketplace remove "$marketplace_name" >/dev/null 2>&1 || true
		fi
	done

	for hook_file in "${LEGACY_HOOK_FILES[@]}"; do
		rm -f "$CLAUDE_DIR/hooks/$hook_file"
	done

	if [ "$removed_count" -gt 0 ]; then
		echo "    [OK] Uninstalled $removed_count Pilot-installed plugin(s) (codex/chrome-devtools, plus legacy if present)"
		removed_items+=("$removed_count non-LSP plugin(s)")
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
	if [ -d "$PILOT_DIR" ]; then
		rm -rf "$PILOT_DIR"
		echo "    [OK] Removed ~/.pilot/"
		removed_items+=("~/.pilot/")
	fi
}

remove_codex_files() {
	if ! has_codex_pilot_content; then
		return
	fi

	# Remove Pilot-managed hook entries from ~/.codex/hooks.json.
	# Entries are identified by the presence of /.pilot/ in any hook command string,
	# mirroring _is_pilot_managed_entry in installer/steps/codex_files.py.
	local hooks_file="$CODEX_DIR/hooks.json"
	if [ -f "$hooks_file" ] && command -v python3 >/dev/null 2>&1 && grep -q '/.pilot/' "$hooks_file" 2>/dev/null; then
		PILOT_CODEX_HOOKS="$hooks_file" python3 -c '
import json, os, sys

hooks_path = os.environ["PILOT_CODEX_HOOKS"]
try:
    with open(hooks_path) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

hooks = data.get("hooks")
if not isinstance(hooks, dict):
    sys.exit(0)

removed = 0
for event in list(hooks.keys()):
    if not isinstance(hooks[event], list):
        continue
    filtered = []
    for entry in hooks[event]:
        is_pilot = any(
            "/.pilot/" in str(h.get("command", ""))
            for h in entry.get("hooks", [])
            if isinstance(h, dict)
        )
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

with open(hooks_path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

if removed > 0:
    print(f"    [OK] Removed {removed} Pilot hook(s) from ~/.codex/hooks.json")
' 2>&1
	fi

	# Remove Pilot managed MCP server and env var blocks from ~/.codex/config.toml.
	local config_file="$CODEX_DIR/config.toml"
	if [ -f "$config_file" ] && command -v python3 >/dev/null 2>&1 && grep -q -e 'pilot-shell managed MCP servers' -e 'pilot-shell managed env vars' "$config_file" 2>/dev/null; then
		PILOT_CODEX_CONFIG="$config_file" python3 -c '
import os, sys

config_path = os.environ["PILOT_CODEX_CONFIG"]
marker_pairs = [
    ("# --- pilot-shell managed MCP servers ---", "# --- end pilot-shell managed MCP servers ---"),
    ("# --- pilot-shell managed env vars ---", "# --- end pilot-shell managed env vars ---"),
]

try:
    with open(config_path) as f:
        content = f.read()
except Exception:
    sys.exit(0)

changed = False
for marker_start, marker_end in marker_pairs:
    if marker_start not in content:
        continue
    if marker_end not in content:
        # End marker missing (user edit, partial revert). Refuse to truncate the
        # rest of the file — preserve everything and continue with other blocks.
        continue

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

with open(config_path, "w") as f:
    f.write(content)

print("    [OK] Removed Pilot managed config block(s) from ~/.codex/config.toml")
' 2>&1
	fi

	# Remove <!-- PILOT:START --> ... <!-- PILOT:END --> block from ~/.codex/AGENTS.md.
	local agents_file="$CODEX_DIR/AGENTS.md"
	if [ -f "$agents_file" ] && command -v python3 >/dev/null 2>&1 && grep -q 'PILOT:START' "$agents_file" 2>/dev/null; then
		PILOT_CODEX_AGENTS="$agents_file" python3 -c '
import os, sys

agents_path = os.environ["PILOT_CODEX_AGENTS"]
marker_start = "<!-- PILOT:START -->"
marker_end = "<!-- PILOT:END -->"

try:
    with open(agents_path) as f:
        content = f.read()
except Exception:
    sys.exit(0)

if marker_start not in content or marker_end not in content:
    sys.exit(0)

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

if not result.strip():
    os.remove(agents_path)
    print("    [OK] Removed ~/.codex/AGENTS.md (no user content remained)")
else:
    with open(agents_path, "w") as f:
        f.write(result)
    print("    [OK] Removed Pilot managed block from ~/.codex/AGENTS.md (user content preserved)")
' 2>&1
	fi

	# Remove Pilot-installed SKILL.md files from ~/.agents/skills/.
	# The installer creates only SKILL.md inside each skill directory; user-added
	# files within the same directory are left intact. The directory itself is
	# removed only if it becomes empty after SKILL.md is deleted.
	local removed_skills=0
	for skill in "${CODEX_PILOT_SKILLS[@]}"; do
		local skill_dir="$AGENTS_SKILLS_DIR/$skill"
		local skill_file="$skill_dir/SKILL.md"
		if [ -f "$skill_file" ]; then
			rm -f "$skill_file"
			removed_skills=$((removed_skills + 1))
			if [ -d "$skill_dir" ] && [ -z "$(ls -A "$skill_dir" 2>/dev/null)" ]; then
				rmdir "$skill_dir" 2>/dev/null || true
			fi
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

	if [ ${#removed_items[@]} -eq 0 ]; then
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
	echo "    - Semble:         uv tool uninstall semble"
	echo "    - agent-browser:  npm uninstall -g agent-browser"
	echo "    - vtsls:          npm uninstall -g @vtsls/language-server typescript"
	echo "    - prettier:       npm uninstall -g prettier"
	echo "    - golangci-lint:  rm -f \$(go env GOPATH)/bin/golangci-lint"
	echo "    - Python tools:   uv tool uninstall ruff basedpyright"
	echo ""
	echo "  Homebrew packages (git, node, bun, go, etc.) were left intact."
	echo ""
	echo "  Please restart your terminal or run 'source ~/.zshrc' to apply changes."
	echo ""
	echo "======================================================================"
	echo ""
}

SKIP_CONFIRM=false
while [ $# -gt 0 ]; do
	case "$1" in
	--yes | -y)
		SKIP_CONFIRM=true
		shift
		;;
	--help | -h)
		echo "Usage: uninstall.sh [--yes|-y]"
		echo ""
		echo "Uninstall Pilot Shell and remove all installed files."
		echo ""
		echo "Options:"
		echo "  --yes, -y    Skip confirmation prompt"
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

if ! [ -d "$PILOT_DIR" ] && ! [ -d "$PILOT_PLUGIN_DIR" ] && ! [ -f "$MANIFEST_FILE" ] && ! [ -f "$HOOKS_BASELINE_FILE" ] && ! [ -f "$MCP_BASELINE_FILE" ] && ! [ -f "$LSP_MANIFEST_FILE" ] && ! has_codex_pilot_content; then
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
remove_pilot_baselines
remove_pilot_plugin
remove_pilot_dir
remove_codex_files

print_summary
