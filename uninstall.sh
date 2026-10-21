#!/usr/bin/env bash
# Pilot Shell 11 uninstaller, kept at this path for Pilot Shell users.
#
# Pilot Shell's README, docs and its own messages tell users to run
#   curl -fsSL https://raw.githubusercontent.com/maxritter/qualitylayer/main/uninstall.sh | bash
# Now that main carries QualityLayer, this script downloads Pilot Shell's last uninstaller (v11.0.8),
# checks it against the SHA-256 below and runs it with the same options (--yes, --remove-tools,
# --purge-data, --help). QualityLayer itself uninstalls with `qualitylayer uninstall`.

set -euo pipefail

# PILOT_UNINSTALL_URL names a mirror for tests; whatever it serves must still match the checksum.
PILOT_UNINSTALL_URL="${PILOT_UNINSTALL_URL:-https://raw.githubusercontent.com/maxritter/qualitylayer/v11.0.8/uninstall.sh}"
PILOT_UNINSTALL_SHA256="eee6e1cf2a20c48af7dd7d4e9470437218591ed5c4f4a54a5d161618973cdc97"

script="$(mktemp "${TMPDIR:-/tmp}/pilot-uninstall.XXXXXX")"
trap 'rm -f -- "$script"' EXIT

if command -v curl >/dev/null 2>&1; then
	curl -fsSL "$PILOT_UNINSTALL_URL" -o "$script"
elif command -v wget >/dev/null 2>&1; then
	wget -qO "$script" "$PILOT_UNINSTALL_URL"
else
	echo "  [!!] curl or wget is needed to download the Pilot Shell uninstaller." >&2
	exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
	actual="$(sha256sum "$script" | cut -d' ' -f1)"
else
	actual="$(shasum -a 256 "$script" | cut -d' ' -f1)"
fi
if [ "$actual" != "$PILOT_UNINSTALL_SHA256" ]; then
	echo "  [!!] The Pilot Shell uninstaller did not match its checksum; nothing was removed." >&2
	exit 1
fi

bash "$script" "$@"
