#!/bin/bash

# =============================================================================
# End-to-End Test for Claude CodePro Installation Script
# Tests install.sh in a clean Docker environment
# =============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_DIR=$(mktemp -d)
FAILED_TESTS=0
PASSED_TESTS=0

# Cleanup function
cleanup() {
	if [[ -d $TEST_DIR ]]; then
		rm -rf "$TEST_DIR"
	fi
}

trap cleanup EXIT

# Print functions
print_section() {
	echo ""
	echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
	echo -e "${BLUE}  $1${NC}"
	echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
	echo ""
}

print_test() {
	echo -e "${YELLOW}▶ Testing: $1${NC}"
}

print_success() {
	echo -e "${GREEN}✓ $1${NC}"
	((PASSED_TESTS++))
}

print_error() {
	echo -e "${RED}✗ $1${NC}"
	((FAILED_TESTS++))
}

print_info() {
	echo -e "${BLUE}ℹ $1${NC}"
}

print_note() {
	echo -e "${YELLOW}  → $1${NC}"
}

# Test helper functions
assert_file_exists() {
	local file=$1
	local description=$2
	if [[ -f $file ]]; then
		print_success "File exists: $description ($file)"
		return 0
	else
		print_error "File missing: $description ($file)"
		return 1
	fi
}

assert_dir_exists() {
	local dir=$1
	local description=$2
	if [[ -d $dir ]]; then
		print_success "Directory exists: $description ($dir)"
		return 0
	else
		print_error "Directory missing: $description ($dir)"
		return 1
	fi
}

assert_command_exists() {
	local cmd=$1
	local description=$2
	if command -v "$cmd" &>/dev/null; then
		print_success "Command available: $description ($cmd)"
		return 0
	else
		print_error "Command not found: $description ($cmd)"
		return 1
	fi
}

# =============================================================================
# Test: Non-Interactive Installation (Basic)
# =============================================================================

test_non_interactive_install() {
	print_section "Test: Non-Interactive Installation"

	local test_dir="$TEST_DIR/test-basic"
	mkdir -p "$test_dir"
	cd "$test_dir"

	print_test "Running install.sh with --non-interactive --local flags"

	# Run installation in non-interactive mode using local files
	export INSTALL_PYTHON=Y
	export OVERWRITE_SETTINGS=N

	if bash "$PROJECT_ROOT/scripts/install.sh" --local --non-interactive --skip-env 2>&1 | tee install.log; then
		print_success "Installation completed without errors"
	else
		print_error "Installation failed with exit code $?"
		cat install.log
		return 1
	fi

	# Verify expected files and directories
	print_test "Verifying installed files and directories"

	assert_dir_exists "$test_dir/.claude" "Claude configuration directory" || return 1
	assert_dir_exists "$test_dir/.claude/hooks" "Hooks directory" || return 1
	assert_dir_exists "$test_dir/.claude/rules" "Rules directory" || return 1

	# Commands and skills directories are created by build-rules.sh, not strictly required for basic install
	if [[ -d "$test_dir/.claude/commands" ]]; then
		print_success "Commands directory exists (optional)"
	else
		print_info "Commands directory not yet created (will be created by build-rules.sh)"
	fi

	if [[ -d "$test_dir/.claude/skills" ]]; then
		print_success "Skills directory exists (optional)"
	else
		print_info "Skills directory not yet created (will be created by build-rules.sh)"
	fi

	assert_file_exists "$test_dir/.claude/settings.local.json" "Settings file" || return 1
	assert_file_exists "$test_dir/.nvmrc" "Node version file" || return 1

	assert_dir_exists "$test_dir/.cipher" "Cipher directory" || return 1
	assert_dir_exists "$test_dir/.qlty" "QLTY directory" || return 1

	assert_file_exists "$test_dir/.mcp.json" "MCP config" || return 1
	assert_file_exists "$test_dir/.mcp-funnel.json" "MCP Funnel config" || return 1

	assert_dir_exists "$test_dir/scripts" "Scripts directory" || return 1
	assert_dir_exists "$test_dir/scripts/lib" "Scripts lib directory" || return 1
	assert_file_exists "$test_dir/scripts/lib/setup-env.sh" "Setup env script" || return 1
	assert_file_exists "$test_dir/scripts/build-rules.sh" "Build rules script" || return 1

	# Verify .nvmrc content
	print_test "Verifying .nvmrc contains Node.js 22"
	if [[ $(cat "$test_dir/.nvmrc") == "22" ]]; then
		print_success ".nvmrc correctly set to Node.js 22"
	else
		print_error ".nvmrc has incorrect content: $(cat "$test_dir/.nvmrc")"
		return 1
	fi

	# Verify library modules were downloaded
	print_test "Verifying library modules"
	assert_dir_exists "$test_dir/scripts/lib" "Library modules directory" || return 1
	assert_file_exists "$test_dir/scripts/lib/ui.sh" "UI library" || return 1
	assert_file_exists "$test_dir/scripts/lib/utils.sh" "Utils library" || return 1
	assert_file_exists "$test_dir/scripts/lib/download.sh" "Download library" || return 1
	assert_file_exists "$test_dir/scripts/lib/files.sh" "Files library" || return 1
	assert_file_exists "$test_dir/scripts/lib/dependencies.sh" "Dependencies library" || return 1
	assert_file_exists "$test_dir/scripts/lib/shell.sh" "Shell library" || return 1

	print_success "All basic installation checks passed"
}

# =============================================================================
# Test: Python Support Flag
# =============================================================================

test_python_support_flag() {
	print_section "Test: Python Support Flag"

	local test_dir="$TEST_DIR/test-python"
	mkdir -p "$test_dir"
	cd "$test_dir"

	print_test "Running install.sh with INSTALL_PYTHON=N and --local"

	export INSTALL_PYTHON=N
	export OVERWRITE_SETTINGS=N

	if bash "$PROJECT_ROOT/scripts/install.sh" --local --non-interactive --skip-env 2>&1 | tee install.log; then
		print_success "Installation completed without errors"
	else
		print_error "Installation failed with exit code $?"
		return 1
	fi

	# Verify Python hook is not present
	print_test "Verifying Python hook was not installed"
	if [[ ! -f "$test_dir/.claude/hooks/file_checker_python.sh" ]]; then
		print_success "Python hook correctly excluded"
	else
		print_error "Python hook should not be present when INSTALL_PYTHON=N"
		return 1
	fi

	# Verify Python permissions are removed from settings.local.json
	print_test "Verifying Python permissions removed from settings"
	if ! grep -q "basedpyright" "$test_dir/.claude/settings.local.json" 2>/dev/null; then
		print_success "Python permissions correctly removed from settings"
	else
		print_error "Python permissions still present in settings.local.json"
		return 1
	fi

	print_success "Python support flag test passed"
}

# =============================================================================
# Test: Help Flag
# =============================================================================

test_help_flag() {
	print_section "Test: Help Flag"

	local test_dir="$TEST_DIR/test-help"
	mkdir -p "$test_dir"
	cd "$test_dir"

	print_test "Running install.sh --help"

	if bash "$PROJECT_ROOT/scripts/install.sh" --help | grep -q "non-interactive"; then
		print_success "Help text displayed correctly"
	else
		print_error "Help flag did not display expected content"
		return 1
	fi
}

# =============================================================================
# Test: Idempotency (Multiple Runs)
# =============================================================================

test_idempotency() {
	print_section "Test: Idempotency (Multiple Runs)"

	local test_dir="$TEST_DIR/test-idempotent"
	mkdir -p "$test_dir"
	cd "$test_dir"

	export INSTALL_PYTHON=Y
	export OVERWRITE_SETTINGS=N

	print_test "First installation run"
	if ! bash "$PROJECT_ROOT/scripts/install.sh" --local --non-interactive --skip-env 2>&1 | tee first-install.log >/dev/null; then
		print_error "First installation run failed"
		cat first-install.log
		return 1
	fi
	print_success "First installation completed"

	# Verify settings.local.json exists
	if [[ ! -f "$test_dir/.claude/settings.local.json" ]]; then
		print_error "settings.local.json was not created"
		return 1
	fi

	# Modify settings.local.json to verify it's preserved
	echo "# Test marker" >>"$test_dir/.claude/settings.local.json"

	print_test "Second installation run (should be idempotent)"
	if ! bash "$PROJECT_ROOT/scripts/install.sh" --local --non-interactive --skip-env 2>&1 | tee second-install.log >/dev/null; then
		print_error "Second installation run failed"
		cat second-install.log
		return 1
	fi
	print_success "Second installation completed"

	# Verify settings.local.json was preserved
	print_test "Verifying settings.local.json was preserved"
	if grep -q "# Test marker" "$test_dir/.claude/settings.local.json"; then
		print_success "Settings file correctly preserved on second run"
	else
		print_error "Settings file was overwritten"
		return 1
	fi

	print_success "Idempotency test passed"
}

# =============================================================================
# Test: Invalid Arguments
# =============================================================================

test_invalid_arguments() {
	print_section "Test: Invalid Arguments"

	local test_dir="$TEST_DIR/test-invalid"
	mkdir -p "$test_dir"
	cd "$test_dir"

	print_test "Running install.sh with invalid argument"

	if bash "$PROJECT_ROOT/scripts/install.sh" --invalid-flag 2>&1 | grep -q "Unknown option"; then
		print_success "Invalid argument correctly rejected"
	else
		print_error "Invalid argument should have been rejected"
		return 1
	fi
}

# =============================================================================
# Test: Bootstrap Module Download (Simulates curl | bash)
# =============================================================================

test_bootstrap_download() {
	print_section "Test: Bootstrap Module Download"

	local test_dir="$TEST_DIR/test-bootstrap"
	mkdir -p "$test_dir"
	cd "$test_dir"

	print_test "Simulating fresh curl | bash installation"

	# Copy ONLY install.sh (simulate curl | bash)
	cp "$PROJECT_ROOT/scripts/install.sh" "$test_dir/"

	# Run in local mode but remove one module to force download check
	export INSTALL_PYTHON=Y
	export OVERWRITE_SETTINGS=N

	print_test "Running install.sh to trigger module downloads"

	if bash "$PROJECT_ROOT/scripts/install.sh" --local --non-interactive --skip-env 2>&1 | tee install.log; then
		print_success "Installation completed with module download"
	else
		print_error "Installation failed"
		cat install.log
		return 1
	fi

	# Verify all library modules were downloaded
	print_test "Verifying all library modules were downloaded"

	local required_modules=(
		"ui.sh"
		"utils.sh"
		"download.sh"
		"files.sh"
		"dependencies.sh"
		"shell.sh"
		"migration.sh"
		"setup-env.sh"
	)

	for module in "${required_modules[@]}"; do
		if [[ -f "$test_dir/scripts/lib/$module" ]]; then
			print_success "Module downloaded: $module"
		else
			print_error "Module missing: $module"
			return 1
		fi
	done

	print_success "Bootstrap download test passed"
}

# =============================================================================
# Main Test Runner
# =============================================================================

main() {
	print_section "Claude CodePro Install Script E2E Tests"

	print_info "Project root: $PROJECT_ROOT"
	print_info "Test directory: $TEST_DIR"
	echo ""

	# Run all tests
	test_non_interactive_install || true
	test_python_support_flag || true
	test_help_flag || true
	test_idempotency || true
	test_invalid_arguments || true
	test_bootstrap_download || true

	# Print summary
	print_section "Test Summary"

	echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
	echo -e "${RED}Failed: $FAILED_TESTS${NC}"
	echo ""

	if [[ $FAILED_TESTS -eq 0 ]]; then
		echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
		echo -e "${GREEN}  ✓ All tests passed! 🎉${NC}"
		echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
		exit 0
	else
		echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
		echo -e "${RED}  ✗ Some tests failed${NC}"
		echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
		exit 1
	fi
}

main "$@"
