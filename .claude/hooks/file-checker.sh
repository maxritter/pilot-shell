#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Find most recently modified file (within last minute, excluding cache/build dirs)
files=$(find . -type f -mmin -1 -not -path '*/.ruff_cache/*' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' -not -path '*/build/*' -exec ls -t {} + 2>/dev/null | head -1)

# If no files found, still provide feedback
if [[ -z "$files" ]]; then
  echo "" >&2
  echo -e "${GREEN}✅ No recently modified files to check${NC}" >&2
  exit 0
fi

# Get absolute path of the file
file_abs_path=$(realpath "$files")

# Skip checks for test files
if [[ "$file_abs_path" == *test* ]] || [[ "$file_abs_path" == *spec* ]]; then
  echo "" >&2
  echo -e "${GREEN}✅ Test file - skipping checks${NC}" >&2
  exit 0
fi

# Find the nearest .venv by walking up from the file's directory
# This ensures we use the correct venv for nested project structures
PROJECT_ROOT=""
current_dir=$(dirname "$file_abs_path")
while [[ "$current_dir" != "/" ]]; do
  if [[ -d "$current_dir/.venv" ]]; then
    PROJECT_ROOT="$current_dir"
    break
  fi
  current_dir=$(dirname "$current_dir")
done

# Find binaries with fallback paths
RUFF_BIN=""
BASEDPYRIGHT_BIN=""
MYPY_BIN=""
QLTY_BIN=""

# Try to find ruff (prefer project venv)
if [[ -n "$PROJECT_ROOT" ]] && [[ -x "$PROJECT_ROOT/.venv/bin/ruff" ]]; then
  RUFF_BIN="$PROJECT_ROOT/.venv/bin/ruff"
elif command -v ruff >/dev/null 2>&1; then
  RUFF_BIN="ruff"
elif [[ -x "/root/.local/bin/ruff" ]]; then
  RUFF_BIN="/root/.local/bin/ruff"
fi

# Try to find basedpyright (prefer project venv)
if [[ -n "$PROJECT_ROOT" ]] && [[ -x "$PROJECT_ROOT/.venv/bin/basedpyright" ]]; then
  BASEDPYRIGHT_BIN="$PROJECT_ROOT/.venv/bin/basedpyright"
elif command -v basedpyright >/dev/null 2>&1; then
  BASEDPYRIGHT_BIN="basedpyright"
elif [[ -x "/root/.local/bin/basedpyright" ]]; then
  BASEDPYRIGHT_BIN="/root/.local/bin/basedpyright"
fi

# Try to find mypy (prefer project venv - CRITICAL for type checking)
if [[ -n "$PROJECT_ROOT" ]] && [[ -x "$PROJECT_ROOT/.venv/bin/mypy" ]]; then
  MYPY_BIN="$PROJECT_ROOT/.venv/bin/mypy"
elif command -v mypy >/dev/null 2>&1; then
  MYPY_BIN="mypy"
elif [[ -x "/root/.local/bin/mypy" ]]; then
  MYPY_BIN="/root/.local/bin/mypy"
fi

# Try to find qlty
if command -v qlty >/dev/null 2>&1; then
  QLTY_BIN="qlty"
elif [[ -x "/root/.qlty/bin/qlty" ]]; then
  QLTY_BIN="/root/.qlty/bin/qlty"
fi

# Auto-format Python files before checks
if [[ "$files" == *.py ]] && [[ -n "$RUFF_BIN" ]]; then
  $RUFF_BIN check --select I,RUF022 --fix "$files" >/dev/null 2>&1 || true
  $RUFF_BIN format "$files" >/dev/null 2>&1 || true
fi

# Run qlty linting checks (if available)
check_output=""
has_issues=false

if [[ -n "$QLTY_BIN" ]] && [[ -d ".qlty" ]]; then
  check_output=$($QLTY_BIN check --no-formatters "$files" 2>&1)
  check_exit_code=$?
  [[ "$check_output" != *"No issues"* || $check_exit_code -ne 0 ]] && has_issues=true
fi

# Run Python-specific checks
ruff_output=""
ruff_issues=false
basedpyright_output=""
basedpyright_issues=false
mypy_output=""
mypy_issues=false

if [[ "$files" == *.py ]]; then
  # Run ruff
  if [[ -n "$RUFF_BIN" ]]; then
    ruff_output=$($RUFF_BIN check "$files" 2>&1 || true)
    if [[ -n "$ruff_output" ]] && [[ "$ruff_output" != *"All checks passed"* ]]; then
      ruff_issues=true
      has_issues=true
    fi
  fi

  # Run basedpyright
  if [[ -n "$BASEDPYRIGHT_BIN" ]]; then
    basedpyright_output=$($BASEDPYRIGHT_BIN --outputjson "$files" 2>&1 || true)
    if echo "$basedpyright_output" | grep -qE '"errorCount":\s*[1-9]' || [[ "$basedpyright_output" == *" error"* ]]; then
      basedpyright_issues=true
      has_issues=true
    fi
  fi

  # Run mypy
  if [[ -n "$MYPY_BIN" ]]; then
    mypy_output=$($MYPY_BIN "$files" 2>&1 || true)
    if echo "$mypy_output" | grep -qE 'error:' && [[ "$mypy_output" != *"Success:"* ]]; then
      mypy_issues=true
      has_issues=true
    fi
  fi
fi

# Display results
if [[ $has_issues == true ]]; then
  echo "" >&2
  echo -e "${RED}🛑 STOP - Issues found in: $files${NC}" >&2
  echo -e "${RED}The following MUST BE FIXED:${NC}" >&2
  echo "" >&2

  # Show ruff issues
  if [[ $ruff_issues == true ]]; then
    error_count=$(echo "$ruff_output" | grep -c "^\s*[0-9]" 2>/dev/null || echo "0")
    error_lines=$(echo "$ruff_output" | grep -E "^\s*[0-9]|error:|warning:" | head -5)

    echo "🔧 Ruff Issues: ($error_count found)" >&2
    if [[ -n "$error_lines" ]]; then
      echo "$error_lines" >&2
    else
      echo "$ruff_output" | head -5 >&2
    fi
    echo "" >&2
  fi

  # Show qlty linting issues
  if [[ "$check_output" != *"No issues"* ]]; then
    issue_lines=$(echo "$check_output" | grep -E "^\s*[0-9]+:[0-9]+\s+|high\s+|medium\s+|low\s+" | head -3)
    remaining_issues=$(echo "$check_output" | grep -c "high\|medium\|low" 2>/dev/null || echo "0")

    echo "🔍 QLTY Linting Issues: ($remaining_issues remaining)" >&2

    if [[ -n "$issue_lines" ]]; then
      echo "$issue_lines" >&2
      [[ $remaining_issues -gt 3 ]] && echo "... and $((remaining_issues - 3)) more issues" >&2
    else
      echo "$check_output" | head -5 >&2
    fi
    echo "" >&2
  fi

  # Show BasedPyright type errors
  if [[ $basedpyright_issues == true ]]; then
    error_count=$(echo "$basedpyright_output" | grep -oP '"errorCount":\s*\K\d+' | head -1)
    [[ -z "$error_count" ]] && error_count=$(echo "$basedpyright_output" | grep -oP '\d+(?= error)' | head -1)
    error_lines=$(echo "$basedpyright_output" | grep -E '"message":|"file":' | head -10)

    echo "🐍 BasedPyright Type Errors: ($error_count found)" >&2
    if [[ -n "$error_lines" ]]; then
      echo "$error_lines" | sed 's/"message":/  /g' | sed 's/"file":/  File:/g' | head -5 >&2
      [[ $error_count -gt 3 ]] && echo "... and $((error_count - 3)) more errors" >&2
    else
      echo "$basedpyright_output" | tail -5 >&2
    fi
    echo "" >&2
  fi

  # Show Mypy type errors
  if [[ $mypy_issues == true ]]; then
    error_count=$(echo "$mypy_output" | grep -c "error:" 2>/dev/null || echo "0")
    error_lines=$(echo "$mypy_output" | grep "error:" | head -5)

    echo "🔍 Mypy Type Errors: ($error_count found)" >&2
    if [[ -n "$error_lines" ]]; then
      echo "$error_lines" >&2
      [[ $error_count -gt 5 ]] && echo "... and $((error_count - 5)) more errors" >&2
    else
      echo "$mypy_output" | head -10 >&2
    fi
    echo "" >&2
  fi

  echo -e "${RED}Fix all issues above before continuing${NC}" >&2
  exit 1  # Exit with error code when issues found
else
  echo "" >&2
  echo -e "${GREEN}✅ Code quality good. Continue${NC}" >&2
  exit 0  # Exit successfully when no issues
fi
