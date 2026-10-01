#!/usr/bin/env bash
# QualityLayer installer.
#
#   curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash
#
# Downloads the binary for this machine from GitHub Releases, verifies it
# against its published SHA-256 (mandatory), and lets the binary install
# itself: `qualitylayer install` places the binary under ~/.qualitylayer,
# adds the skill for each installed agent, and records every file it wrote so
# `qualitylayer uninstall` can remove exactly those.
#
# Pilot Shell 11's updater downloads and runs this script with its own flags
# (--auto-update --non-interactive --quiet); they are accepted and ignored.
# With Pilot Shell 11 installed, the binary shows its upgrade screen once and
# moves the machine to QualityLayer without asking anything.
#
# Environment: VERSION (e.g. 12.0.0-beta.1; default: the newest v12 release),
# QUALITYLAYER_RELEASE_BASE and QUALITYLAYER_RELEASE_API (mirrors and tests).

set -euo pipefail

REPO="maxritter/pilot-shell"
RELEASE_BASE="${QUALITYLAYER_RELEASE_BASE:-https://github.com/${REPO}/releases}"
RELEASE_API="${QUALITYLAYER_RELEASE_API:-https://api.github.com/repos/${REPO}/releases?per_page=30}"
VERSION="${VERSION:-}"
VERSION="${VERSION#v}"

say() { printf '  %s\n' "$*"; }
fail() {
	printf '  [!!] %s\n' "$*" >&2
	exit 1
}

case "${HOME:-}" in
/*) ;;
*) fail "HOME must be an absolute path, got: '${HOME:-}'" ;;
esac
[ -d "$HOME" ] || fail "HOME must name an existing directory, got: '$HOME'"
HOME="$(cd -- "$HOME" && pwd -P)"
[ "$HOME" != "/" ] || fail "HOME resolves to the filesystem root; refusing to install."
export HOME

case "$(uname -s)" in
Darwin) os="darwin" ;;
Linux) os="linux" ;;
*) fail "QualityLayer runs on macOS and Linux (on Windows, inside WSL)." ;;
esac
case "$(uname -m)" in
arm64 | aarch64) arch="arm64" ;;
x86_64 | amd64) arch="x64" ;;
*) fail "unsupported CPU: $(uname -m)" ;;
esac
# An arm64 Mac running this shell under Rosetta still wants the arm64 binary.
if [ "$os" = "darwin" ] && [ "$arch" = "x64" ] && [ "$(sysctl -n sysctl.proc_translated 2>/dev/null || true)" = "1" ]; then
	arch="arm64"
fi
asset="qualitylayer-${os}-${arch}"

fetch() {
	if command -v curl >/dev/null 2>&1; then
		curl -fsSL --retry 2 -o "$2" "$1"
	elif command -v wget >/dev/null 2>&1; then
		wget -q -O "$2" "$1"
	else
		fail "curl or wget is required"
	fi
}

sha256_of() {
	if command -v sha256sum >/dev/null 2>&1; then
		sha256sum "$1" | awk '{print $1}'
	elif command -v shasum >/dev/null 2>&1; then
		shasum -a 256 "$1" | awk '{print $1}'
	else
		fail "sha256sum or shasum is required to verify the download"
	fi
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

if [ -z "$VERSION" ]; then
	fetch "$RELEASE_API" "$work/releases.json" || fail "cannot reach the release list at $RELEASE_API"
	VERSION="$(grep -o '"tag_name": *"v12[^"]*"' "$work/releases.json" | head -n 1 | sed 's/.*"v\(.*\)"/\1/' || true)"
	[ -n "$VERSION" ] || fail "no QualityLayer 12 release was found"
fi

say "Downloading QualityLayer ${VERSION} (${asset})"
base="${RELEASE_BASE}/download/v${VERSION}"
fetch "${base}/${asset}" "$work/qualitylayer" || fail "download failed: ${base}/${asset}"
fetch "${base}/${asset}.sha256" "$work/qualitylayer.sha256" || fail "the checksum is missing: ${base}/${asset}.sha256; nothing was installed"

expected="$(awk '{print $1; exit}' "$work/qualitylayer.sha256")"
actual="$(sha256_of "$work/qualitylayer")"
case "$expected" in
[0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) ;;
*) fail "${asset}.sha256 holds no checksum; nothing was installed" ;;
esac
[ "${#expected}" -eq 64 ] || fail "${asset}.sha256 holds no checksum; nothing was installed"
[ "$expected" = "$actual" ] || fail "checksum mismatch for ${asset} (expected ${expected}, got ${actual}); nothing was installed"
say "Checksum verified"

chmod 755 "$work/qualitylayer"

# Pilot Shell 11 is still installed: the binary shows its upgrade screen and moves
# the machine over, with or without a terminal. Nothing is asked.
v11=""
[ -e "$HOME/.pilot/bin/pilot" ] && v11=yes

# Under `curl | bash` stdin is this script: the installer's questions are answered from the terminal.
if [ -t 1 ] && (exec </dev/tty) 2>/dev/null; then
	"$work/qualitylayer" install ${v11:+--upgrade-v11} </dev/tty
else
	"$work/qualitylayer" install ${v11:+--upgrade-v11}
fi
