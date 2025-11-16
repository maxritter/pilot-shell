#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Change to workspace root if not already there
if [[ -d "/workspaces/claude-codepro" ]]; then
	cd /workspaces/claude-codepro || exit 1
fi

# Find THE most recently modified file (excluding cache/build dirs)
if [[ "$OSTYPE" == "darwin"* ]]; then
	# macOS version
	files=$(find . -type f -not -path '*/.ruff_cache/*' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.git/*' -exec stat -f '%m %N' {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
else
	# Linux version
	files=$(find . -type f -not -path '*/.ruff_cache/*' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.git/*' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
fi

# If no files found, exit silently
if [[ -z $files ]]; then
	exit 0
fi

# Skip Python files (handled by Python hook), test files, and scripts directory
if [[ $files == *.py ]] || [[ $files == *test* ]] || [[ $files == *scripts/* ]]; then
	exit 0
fi

# Try to find qlty
QLTY_BIN=""
if command -v qlty >/dev/null 2>&1; then
	QLTY_BIN="qlty"
elif [[ -x "/root/.qlty/bin/qlty" ]]; then
	QLTY_BIN="/root/.qlty/bin/qlty"
fi

# If QLTY not available, exit silently
if [[ -z $QLTY_BIN ]] || [[ ! -d ".qlty" ]]; then
	exit 0
fi

# Run qlty linting checks
check_output=$($QLTY_BIN check --no-formatters "$files" 2>&1)
check_exit_code=$?

# Check if there are issues
if [[ $check_output == *"No issues"* ]] && [[ $check_exit_code -eq 0 ]]; then
	echo "" >&2
	echo -e "${GREEN}✅ QLTY: No issues${NC}" >&2
	exit 2
fi

# Show issues
issue_lines=$(echo "$check_output" | grep -E "^\s*[0-9]+:[0-9]+\s+|high\s+|medium\s+|low\s+" | head -5)
remaining_issues=$(echo "$check_output" | grep -c "high\|medium\|low" 2>/dev/null || echo "0")

echo "" >&2
echo -e "${RED}🛑 QLTY Issues found in: $files${NC}" >&2
echo -e "${RED}Issues: $remaining_issues${NC}" >&2
echo "" >&2

if [[ -n $issue_lines ]]; then
	echo "$issue_lines" >&2
	[[ $remaining_issues -gt 5 ]] && echo "... and $((remaining_issues - 5)) more issues" >&2
else
	echo "$check_output" | head -5 >&2
fi

echo "" >&2
echo -e "${RED}Fix QLTY issues above before continuing${NC}" >&2
exit 2
